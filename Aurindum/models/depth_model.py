"""Model-agnostic depth model interface.

Every correction strategy in `inference/` talks to models ONLY through
`DepthModelWrapper.predict / predict_batch`. Swapping the foundation model means
writing one small subclass; nothing in geometry/inference/evaluation changes.

Each wrapper declares what its numbers mean, because fusing predictions from
different projections requires converting them to a common quantity:

  space     'depth'     -> value grows with distance (metres, or up to scale)
            'disparity' -> value is (affine in) inverse distance (MiDaS-style)
  geometry  'range'     -> distance along the pixel ray (Euclidean; ERP convention)
            'planar'    -> distance along the optical axis (z-buffer; pinhole convention)
  scale     'metric' | 'scale' (unknown global scale) | 'affine' (unknown scale and shift)

`geometry` can differ per input type (an ERP model fed a pinhole image), so it is
reported separately for ERP and perspective inputs.
"""
from __future__ import annotations

import contextlib
import os
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Sequence

import cv2
import numpy as np
import torch
import torch.nn.functional as F


def get_device(pref: str = "auto") -> torch.device:
    if pref != "auto":
        return torch.device(pref)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@dataclass
class OutputSpec:
    space: str  # 'depth' | 'disparity'
    scale: str  # 'metric' | 'scale' | 'affine'
    geometry_erp: str  # 'range' | 'planar' : meaning when the input is an ERP panorama
    geometry_perspective: str  # meaning when the input is a pinhole (tangent) image


def as_uint8_rgb(im: np.ndarray) -> np.ndarray:
    """All wrappers expect uint8 RGB in [0, 255] and divide by 255 themselves.

    A float image in [0, 1] (e.g. the v1 Structured3D loader) would otherwise be divided by 255
    a second time, i.e. the model would see an almost black image. Such inputs are rescaled here.
    """
    if im.dtype == np.uint8:
        return im
    x = np.asarray(im, dtype=np.float32)
    finite = x[np.isfinite(x)]
    if finite.size and finite.max() <= 1.0 + 1e-3 and not np.array_equal(finite, np.rint(finite)):
        x = x * 255.0  # non-integer values in [0, 1]: a normalised image (0/1-valued arrays are left alone)
    return np.clip(np.rint(np.nan_to_num(x)), 0, 255).astype(np.uint8)


class DepthModelWrapper(ABC):
    """Frozen black-box depth estimator."""

    name: str = "base"
    spec: OutputSpec

    def __init__(self, device: str = "auto"):
        self.device = get_device(device)
        self.n_calls = 0  # number of forward passes (images), for compute accounting
        self.total_time = 0.0

    @abstractmethod
    def _forward(self, images: List[np.ndarray], kind: str) -> List[np.ndarray]:
        """images: list of HxWx3 uint8 RGB. Returns list of HxW float32 at the input resolution."""

    def predict(self, image: np.ndarray, kind: str = "erp") -> np.ndarray:
        return self.predict_batch([image], kind)[0]

    @torch.no_grad()
    def predict_batch(self, images: Sequence[np.ndarray], kind: str = "erp", batch_size: int = 4) -> List[np.ndarray]:
        """kind: 'erp' (equirectangular panorama) or 'perspective' (tangent/pinhole view)."""
        out: List[np.ndarray] = []
        images = [as_uint8_rgb(im) for im in images]
        for s in range(0, len(images), batch_size):
            chunk = list(images[s:s + batch_size])
            if self.device.type == "cuda":
                torch.cuda.synchronize()
            t0 = time.perf_counter()
            out.extend(self._forward(chunk, kind))
            if self.device.type == "cuda":
                torch.cuda.synchronize()
            self.total_time += time.perf_counter() - t0
            self.n_calls += len(chunk)
        return out

    def reset_counters(self):
        self.n_calls, self.total_time = 0, 0.0

    def geometry(self, kind: str) -> str:
        return self.spec.geometry_erp if kind == "erp" else self.spec.geometry_perspective

    def describe(self) -> dict:
        return {"name": self.name, **self.spec.__dict__, "device": str(self.device)}


# ----------------------------------------------------------------------------
# MiDaS (perspective relative-depth model, weights on GitHub releases)
# ----------------------------------------------------------------------------

_MIDAS_CFG = {
    # model_type: (backbone, net_w, net_h, keep_aspect, mean/std)
    "dpt_hybrid_384": ("vitb_rn50_384", 384, 384, True, 0.5),
    "dpt_large_384": ("vitl16_384", 384, 384, True, 0.5),
    "dpt_swin2_tiny_256": ("swin2t16_256", 256, 256, False, 0.5),
    "midas_v21_small_256": ("efficientnet_lite3", 256, 256, True, None),
}


class MiDaSWrapper(DepthModelWrapper):
    """MiDaS v2.1 / v3 / v3.1 (Ranftl et al.). Output: relative inverse depth (affine-invariant disparity).

    Included (a) as a lightweight local baseline and (b) as an architecturally distinct
    perspective model for the generalisation study. Because it is a *perspective*
    model, running it on a full ERP is itself out of distribution; that is an explicit property
    of the evaluated baseline.
    """

    def __init__(self, model_type: str = "dpt_hybrid_384", weights: str = "weights/dpt_hybrid_384.pt",
                 device: str = "auto", repo: Optional[str] = None, erp_net_height: Optional[int] = None):
        super().__init__(device)
        repo = repo or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "third_party",
                                    "midas_repo")
        if repo not in sys.path:
            sys.path.insert(0, repo)
        backbone, self.net_w, self.net_h, self.keep_aspect, norm = _MIDAS_CFG[model_type]
        self.model_type = model_type
        self.name = f"midas_{model_type}"
        self.spec = OutputSpec(space="disparity", scale="affine", geometry_erp="range", geometry_perspective="planar")
        self.erp_net_height = erp_net_height or self.net_h
        if model_type == "midas_v21_small_256":
            from midas.midas_net_custom import MidasNet_small
            m = MidasNet_small(weights, features=64, backbone="efficientnet_lite3", exportable=True,
                               non_negative=True, blocks={"expand": True})
            self.mean, self.std = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])
        else:
            from midas.dpt_depth import DPTDepthModel
            m = DPTDepthModel(path=weights, backbone=backbone, non_negative=True)
            self.mean = self.std = np.array([0.5, 0.5, 0.5])
        self.model = m.eval().to(self.device)

    def _net_size(self, h, w, kind):
        mult = 32
        if not self.keep_aspect:  # fixed-size backbones (Swin2): the image is squashed, as in MiDaS
            return self.net_h, self.net_w
        if kind == "erp":
            nh = self.erp_net_height
            nw = int(round(nh * w / h / mult)) * mult
            return max(mult, int(round(nh / mult)) * mult), nw
        if not self.keep_aspect:
            return self.net_h, self.net_w
        s = max(self.net_h / h, self.net_w / w)
        return int(np.ceil(h * s / mult) * mult), int(np.ceil(w * s / mult) * mult)

    def _forward(self, images, kind):
        h, w = images[0].shape[:2]
        nh, nw = self._net_size(h, w, kind)
        batch = []
        for im in images:
            x = cv2.resize(im.astype(np.float32) / 255.0, (nw, nh), interpolation=cv2.INTER_CUBIC)
            x = (x - self.mean) / self.std
            batch.append(torch.from_numpy(x.transpose(2, 0, 1).astype(np.float32)))
        x = torch.stack(batch).to(self.device)
        pred = self.model(x)
        if pred.dim() == 3:
            pred = pred[:, None]
        pred = F.interpolate(pred, size=(h, w), mode="bicubic", align_corners=False)
        return [p[0].float().cpu().numpy().clip(min=1e-6) for p in pred]


# ----------------------------------------------------------------------------
# DAP: Depth Any Panoramas (Lin et al., CVPR 2026) -- the target panoramic foundation model
# ----------------------------------------------------------------------------

class DAPWrapper(DepthModelWrapper):
    """Wrapper around the official DAP repository (github.com/Insta360-Research-Team/DAP).

    Facts taken from the official code (test/infer.py, test/eval.py, networks/dap.py,
    datasets/stanford2d3d.py, config/infer.yaml):
      * input: ERP RGB, 512 x 1024 (config/infer.yaml), float in [0,1];
        test/eval.py additionally applies ImageNet mean/std normalisation while
        test/infer.py does not -> configurable via `imagenet_normalize` (default True,
        i.e. the evaluation protocol).
      * output: dict with 'pred_depth' (B,1,H,W) = Euclidean range / 100 m, clipped to
        [0, max_depth=1], and 'pred_mask' (sky / beyond-100 m logits). Pixels with
        (1 - pred_mask) <= 0.5 are invalid (set to 1 = 100 m by the official code).
      * the model is ERP-native (trained on ERP); no arbitrary-rotation handling is built in.
    Returns metres (x100). Invalid (mask) pixels are returned as NaN.

    Setup:
        git clone https://github.com/Insta360-Research-Team/DAP third_party/DAP
        download model.pth from https://huggingface.co/Insta360-Research/DAP-weights
    """

    def __init__(self, repo: str = "third_party/DAP", weights: str = "weights/dap/model.pth", device: str = "auto",
                 midas_model_type: str = "vitl", height: int = 512, width: int = 1024, imagenet_normalize: bool = True,
                 max_depth_m: float = 100.0, perspective_geometry: str = "range", use_mask: bool = True):
        super().__init__(device)
        self.name = "dap"
        self.spec = OutputSpec(space="depth", scale="metric", geometry_erp="range",
                               geometry_perspective=perspective_geometry)
        self.h, self.w = height, width
        self.imagenet_normalize = imagenet_normalize
        self.max_depth_m = max_depth_m
        self.use_mask = use_mask
        repo = os.path.abspath(repo)
        if not os.path.isdir(repo):
            raise FileNotFoundError(f"DAP repo not found at {repo}. git clone https://github.com/Insta360-Research-Team/DAP")
        if not os.path.isfile(weights):
            raise FileNotFoundError(f"DAP weights not found at {weights}. Download model.pth from "
                                    "https://huggingface.co/Insta360-Research/DAP-weights")
        if repo not in sys.path:
            sys.path.insert(0, repo)
        with _chdir(repo):  # DAP resolves its DINOv3 code with a relative path
            from networks.models import make  # type: ignore
            model = make({"name": "dap", "args": {"midas_model_type": midas_model_type, "fine_tune_type": "hypersim",
                                                  "min_depth": 0.01, "max_depth": 1.0, "train_decoder": True}})
        state = torch.load(os.path.abspath(weights), map_location="cpu")
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        state = {k[7:] if k.startswith("module.") else k: v for k, v in state.items()}
        msd = model.state_dict()
        missing = [k for k in msd if k not in state]
        model.load_state_dict({k: v for k, v in state.items() if k in msd}, strict=False)
        if missing:
            print(f"[DAPWrapper] warning: {len(missing)} parameters not found in checkpoint (e.g. {missing[:3]})")
        self.model = model.eval().to(self.device)
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=self.device).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=self.device).view(1, 3, 1, 1)

    def _forward(self, images, kind):
        h, w = images[0].shape[:2]
        if kind == "erp":
            nh, nw = self.h, self.w
        else:  # square tangent views: keep the model's native height, multiple of 16 (DINOv3 patch)
            nh = nw = int(round(self.h / 16)) * 16
        x = np.stack([cv2.resize(im, (nw, nh), interpolation=cv2.INTER_CUBIC) for im in images]).astype(np.float32)
        x = torch.from_numpy(x / 255.0).permute(0, 3, 1, 2).to(self.device)
        if self.imagenet_normalize:
            x = (x - self.mean) / self.std
        out = self.model(x)
        d = out["pred_depth"].float()
        if self.use_mask and "pred_mask" in out:
            valid = (1 - out["pred_mask"].float()) > 0.5
            d = torch.where(valid, d, torch.full_like(d, float("nan")))
        d = d * self.max_depth_m
        # nearest keeps NaN masks crisp; bilinear on the finite part
        d_up = F.interpolate(torch.nan_to_num(d, nan=0.0), size=(h, w), mode="bilinear", align_corners=False)
        m_up = F.interpolate(torch.isfinite(d).float(), size=(h, w), mode="nearest") > 0.5
        d_up = torch.where(m_up, d_up, torch.full_like(d_up, float("nan")))
        return [p[0].cpu().numpy() for p in d_up]


# ----------------------------------------------------------------------------
# DA360 (Jiang et al., arXiv 2512.22819) and DA^2 (Li et al., ICLR 2026): panoramic models for the polar audit
# ----------------------------------------------------------------------------

def _purge_modules(prefixes):
    """DAP, DA360 and DA^2 all ship top-level packages with generic names (networks, ...); one model per process."""
    for k in list(sys.modules):
        if any(k == p or k.startswith(p + ".") for p in prefixes):
            del sys.modules[k]


class DA360Wrapper(DepthModelWrapper):
    """DA360: Depth Anything V2 fine-tuned on ERP (Structured3D + TartanAir v2), circular padding, learned shift.

    Facts from the official repo (test.py, checkpoint.py, datasets/real.py):
      * checkpoint dict carries net / dinov2_encoder / height (518) / width (1036) next to the tensors;
      * input: RGB resized (cubic) to 518 x 1036, /255, ImageNet mean/std;
      * output: outputs['pred_disp'] = scale-invariant disparity (inverse range up to one global scale).
    NOTE: DA360 was trained on Structured3D, so the Structured3D evaluation is IN-DOMAIN for it.
    Setup: git clone https://github.com/Insta360-Research-Team/DA360 third_party/DA360
           hf download hljiang/DA360 DA360_large.pth --local-dir weights/da360
    """

    def __init__(self, repo: str = "third_party/DA360", weights: str = "weights/da360/DA360_large.pth",
                 device: str = "auto"):
        super().__init__(device)
        self.name = "da360"
        # scale-invariant disparity: the evaluation protocol fits an affine map for every disparity model (as for MiDaS),
        # which is at least as lenient as DA360's native median-scale protocol
        self.spec = OutputSpec(space="disparity", scale="affine", geometry_erp="range", geometry_perspective="range")
        repo = os.path.abspath(repo)
        if not os.path.isdir(repo):
            raise FileNotFoundError(f"DA360 repo not found at {repo}")
        if not os.path.isfile(weights):
            raise FileNotFoundError(f"DA360 weights not found at {weights}")
        _purge_modules(["networks", "checkpoint", "depth_anything_v2"])
        sys.path.insert(0, repo)
        with _chdir(repo):
            import networks as da360_networks  # type: ignore
            from checkpoint import checkpoint_meta, state_dict_from_checkpoint  # type: ignore
        ckpt = torch.load(os.path.abspath(weights), map_location="cpu")
        meta = checkpoint_meta(ckpt)
        self.h, self.w = int(meta["height"]), int(meta["width"])
        net = getattr(da360_networks, meta["net"])(self.h, self.w, dinov2_encoder=meta["dinov2_encoder"])
        net.load_state_dict(state_dict_from_checkpoint(ckpt, net.state_dict()), strict=False)
        self.model = net.eval().to(self.device)
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=self.device).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=self.device).view(1, 3, 1, 1)

    def _forward(self, images, kind):
        if kind != "erp":
            raise ValueError("DA360 is an ERP model; use rotated-ERP polar views (polar_source: rotated_erp)")
        h, w = images[0].shape[:2]
        x = np.stack([cv2.resize(im, (self.w, self.h), interpolation=cv2.INTER_CUBIC) for im in images])
        x = torch.from_numpy(x.astype(np.float32) / 255.0).permute(0, 3, 1, 2).to(self.device)
        d = self.model((x - self.mean) / self.std)["pred_disp"].float()
        if d.dim() == 3:
            d = d[:, None]
        d = F.interpolate(d, size=(h, w), mode="bilinear", align_corners=False)
        return [p[0].cpu().numpy().clip(min=1e-6) for p in d]


class DA2Wrapper(DepthModelWrapper):
    """DA^2 (Depth Anything in Any Direction): SphereViT with spherical direction embeddings, ERP input.

    Facts from the official repo (src/da2/model/spherevit.py, utils/model.py, utils/io.py, configs/infer.json):
      * SphereViT.from_pretrained('haodongli/DA-2', config=<configs/infer.json>);
      * input: RGB / 255 as (B, 3, H, W); the model resizes to ~0.6 MP and applies ImageNet normalisation itself;
      * output: (B, H, W) distance (range) up to scale (their evaluation uses median alignment).
    Setup: git clone https://github.com/EnVision-Research/DA-2 third_party/DA2 && pip install -e third_party/DA2/src
           (needs huggingface.co, or `hf_id` pointing at a local snapshot of haodongli/DA-2)
    """

    def __init__(self, repo: str = "third_party/DA2", hf_id: str = "haodongli/DA-2", device: str = "auto"):
        super().__init__(device)
        import json
        self.name = "da2"
        self.spec = OutputSpec(space="depth", scale="scale", geometry_erp="range", geometry_perspective="range")
        repo = os.path.abspath(repo)
        cfg_path = os.path.join(repo, "configs", "infer.json")
        if not os.path.isfile(cfg_path):
            raise FileNotFoundError(f"DA^2 config not found at {cfg_path}")
        src = os.path.join(repo, "src")
        if src not in sys.path:
            sys.path.insert(0, src)
        from da2.model.spherevit import SphereViT  # type: ignore
        config = json.load(open(cfg_path))
        model = SphereViT.from_pretrained(hf_id, config=config).to(self.device)
        self.dtype = next(model.parameters()).dtype
        config["spherevit"]["dtype"] = self.dtype
        self.model = model.eval()

    def _forward(self, images, kind):
        if kind != "erp":
            raise ValueError("DA^2 is an ERP model; use rotated-ERP polar views (polar_source: rotated_erp)")
        x = torch.from_numpy(np.stack(images).astype(np.float32) / 255.0).permute(0, 3, 1, 2)
        d = self.model(x.to(self.device).to(self.dtype)).float()
        return [p.cpu().numpy().clip(min=1e-6) for p in d]


def build_panoramic_model(cfg_model: dict, root: str) -> Optional[DepthModelWrapper]:
    """DA360 / DA^2 from a config block (paths relative to the repository root); None for other names."""
    name = str(cfg_model.get("name", "")).lower()
    rel = lambda p: p if os.path.isabs(p) else os.path.join(root, p)
    dev = cfg_model.get("device", "auto")
    if name.startswith("da360"):
        return DA360Wrapper(repo=rel(cfg_model.get("repo", "third_party/DA360")),
                            weights=rel(cfg_model.get("weights", "weights/da360/DA360_large.pth")), device=dev)
    if name in ("da2", "da-2", "da_2"):
        return DA2Wrapper(repo=rel(cfg_model.get("repo", "third_party/DA2")),
                          hf_id=cfg_model.get("hf_id", "haodongli/DA-2"), device=dev)
    return None


# ----------------------------------------------------------------------------
# Depth Anything V2 metric (perspective) via Hugging Face transformers -- optional tangent-view model
# ----------------------------------------------------------------------------

class DepthAnythingV2Wrapper(DepthModelWrapper):
    """Perspective metric depth (z-buffer, metres). Optional second model for tangent views.

    Requires `pip install transformers` and access to huggingface.co (not available in the
    environment where this repository was developed, so this wrapper is untested there).
    """

    def __init__(self, hf_id: str = "depth-anything/Depth-Anything-V2-Metric-Indoor-Large-hf", device: str = "auto"):
        super().__init__(device)
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation  # type: ignore
        self.name = "dav2_" + hf_id.split("/")[-1]
        self.spec = OutputSpec(space="depth", scale="metric", geometry_erp="range", geometry_perspective="planar")
        self.proc = AutoImageProcessor.from_pretrained(hf_id)
        self.model = AutoModelForDepthEstimation.from_pretrained(hf_id).eval().to(self.device)

    def _forward(self, images, kind):
        inputs = self.proc(images=list(images), return_tensors="pt").to(self.device)
        pred = self.model(**inputs).predicted_depth[:, None]
        h, w = images[0].shape[:2]
        pred = F.interpolate(pred, size=(h, w), mode="bicubic", align_corners=False)
        return [p[0].float().cpu().numpy().clip(min=1e-3) for p in pred]


# ----------------------------------------------------------------------------
# Encoded-depth oracle -- ONLY for testing the correction pipeline
# ----------------------------------------------------------------------------

def encode_depth_as_image(depth: np.ndarray, dmin: float = 0.3, dmax: float = 30.0) -> np.ndarray:
    """Encode range into an RGB uint8 image (log scale, all three channels identical)."""
    x = (np.log(np.clip(depth, dmin, dmax)) - np.log(dmin)) / (np.log(dmax) - np.log(dmin))
    g = (x * 255 + 0.5).astype(np.uint8)
    return np.repeat(g[..., None], 3, -1)


class EncodedDepthOracle(DepthModelWrapper):
    """A black-box "model" for pipeline tests: it decodes depth from images made by
    `encode_depth_as_image`, then corrupts it with multiplicative noise whose amplitude grows
    with the latitude *inside an ERP input* (no corruption for perspective inputs).

    Because it sees only pixels, it exercises exactly the same code paths as a real model
    (projection, rotation, reprojection, alignment, fusion). If the correction machinery is
    right, it must reduce polar error for this oracle. Never report it as a result.
    """

    def __init__(self, device: str = "cpu", strength: float = 0.3, dmin: float = 0.3, dmax: float = 30.0,
                 seed: int = 0, power: float = 2.0):
        super().__init__(device)
        self.name = "encoded_oracle"
        self.spec = OutputSpec(space="depth", scale="metric", geometry_erp="range", geometry_perspective="range")
        self.strength, self.dmin, self.dmax, self.power = strength, dmin, dmax, power
        self.seed = seed

    def _forward(self, images, kind):
        outs = []
        for k, im in enumerate(images):
            x = im[..., 0].astype(np.float64) / 255.0
            d = np.exp(np.log(self.dmin) + x * (np.log(self.dmax) - np.log(self.dmin)))
            h, w = d.shape
            if kind == "erp":
                lat = np.degrees(np.pi / 2 - (np.arange(h) + 0.5) / h * np.pi)[:, None].repeat(w, 1)
                amp = self.strength * (np.abs(lat) / 90.0) ** self.power
                rng = np.random.default_rng(self.seed + self.n_calls + k)
                noise = cv2.GaussianBlur(rng.normal(0, 1, (h, w)), (0, 0), 3) * 3
                d = d * np.exp(amp * noise)
            outs.append(d.astype(np.float32))
        return outs


@contextlib.contextmanager
def _chdir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def build_model(cfg: dict) -> DepthModelWrapper:
    name = cfg["name"].lower()
    kw = {k: v for k, v in cfg.items() if k != "name"}
    if name.startswith("midas"):
        return MiDaSWrapper(**kw)
    if name == "dap":
        return DAPWrapper(**kw)
    if name in ("dav2", "depth_anything_v2"):
        return DepthAnythingV2Wrapper(**kw)
    if name == "oracle":
        return EncodedDepthOracle(**kw)
    raise ValueError(f"unknown model {name}")
