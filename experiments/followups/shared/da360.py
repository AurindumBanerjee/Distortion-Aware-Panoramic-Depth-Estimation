"""Minimal DA360 wrapper local to the follow-up experiment bundle.

Based on the model/checkpoint interface used in the primary DA360 wrapper.
"""
from __future__ import annotations

import os
import sys
from typing import List

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from pano.models.depth_model import DepthModelWrapper, OutputSpec


class DA360Wrapper(DepthModelWrapper):
    """DA360 ERP wrapper. Output is scale-invariant disparity (not metric depth)."""

    def __init__(self, repo: str = "third_party/DA360",
                 weights: str = "weights/da360/DA360_large.pth", device: str = "auto"):
        super().__init__(device)
        self.name = "da360"
        self.spec = OutputSpec(space="disparity", scale="scale",
                               geometry_erp="range", geometry_perspective="range")
        repo, weights = os.path.abspath(repo), os.path.abspath(weights)
        if not os.path.isdir(repo):
            raise FileNotFoundError(f"DA360 official repo missing: {repo}")
        if not os.path.isfile(weights):
            raise FileNotFoundError(f"DA360 checkpoint missing: {weights}")

        # DA360's repository uses top-level module names (networks/checkpoint).
        for module_name in list(sys.modules):
            if module_name in {"networks", "checkpoint", "datasets"} or module_name.startswith(("networks.", "checkpoint.", "datasets.")):
                del sys.modules[module_name]
        sys.path.insert(0, repo)
        old = os.getcwd()
        try:
            os.chdir(repo)
            import networks as da360_networks  # type: ignore
            from checkpoint import checkpoint_meta, state_dict_from_checkpoint  # type: ignore
            try:
                ckpt = torch.load(weights, map_location="cpu", weights_only=False)
            except TypeError:
                ckpt = torch.load(weights, map_location="cpu")
            meta = checkpoint_meta(ckpt)
            self.h, self.w = int(meta["height"]), int(meta["width"])
            net_cls = getattr(da360_networks, meta["net"])
            net = net_cls(self.h, self.w, dinov2_encoder=meta["dinov2_encoder"])
            net.load_state_dict(state_dict_from_checkpoint(ckpt, net.state_dict()), strict=False)
        finally:
            os.chdir(old)
            if repo in sys.path:
                sys.path.remove(repo)
            # Remove any shadowed modules that DA360 imported
            for module_name in list(sys.modules):
                if module_name in {"datasets", "data", "utils"} or module_name.startswith(("datasets.", "data.", "utils.")):
                    mod = sys.modules[module_name]
                    if getattr(mod, "__file__", None) and str(repo) in str(mod.__file__):
                        del sys.modules[module_name]

        self.model = net.eval().to(self.device)
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=self.device).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=self.device).view(1, 3, 1, 1)

    def _forward(self, images: List[np.ndarray], kind: str):
        if kind != "erp":
            raise ValueError("DA360 is ERP-native; use rotated-ERP TTA, not tangent inputs.")
        h, w = images[0].shape[:2]
        x = np.stack([cv2.resize(im, (self.w, self.h), interpolation=cv2.INTER_CUBIC)
                      for im in images]).astype(np.float32)
        x = torch.from_numpy(x / 255.0).permute(0, 3, 1, 2).to(self.device)
        out = self.model((x - self.mean) / self.std)
        disp = out["pred_disp"].float()
        if disp.dim() == 3:
            disp = disp[:, None]
        disp = F.interpolate(disp, size=(h, w), mode="bilinear", align_corners=False)
        return [p[0].detach().cpu().numpy().clip(min=1e-6) for p in disp]
