"""Union regression test validating imports, invariants, and merged components."""
from __future__ import annotations

import math
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import torch

from pano.paths import ROOT, ARTIFACTS, DATA, CONFIGS, REPORT
from pano.geometry.spherical import erp_lonlat_grid, latitude_map
from pano.models.depth_model import DepthModelWrapper, EncodedDepthOracle, OutputSpec
from pano.geometry.tangent_plane import (
    generate_tangent_plane,
    sample_view_on_erp,
    tangent_geometry_on_erp,
    tangent_to_erp,
)
from pano.geometry.stereographic import (
    erp_to_stereo,
    generate_stereo_view,
    magnification,
    stereo_to_erp,
)
from pano.inference.alignment import align_view_to_reference, robust_lstsq
from pano.inference.pipeline import MethodConfig
from pano.datasets.synthetic import _texture_bank, random_scene, render_erp


def test_pano_imports_and_paths():
    assert ROOT.is_dir()
    assert CONFIGS.is_dir()
    assert REPORT.is_dir()


def test_pano_geometry():
    lat = latitude_map(32, 64)
    assert lat.shape == (32, 64)
    lon, lat2 = erp_lonlat_grid(32, 64)
    assert lon.shape == (32, 64)


def test_pano_models():
    m = EncodedDepthOracle(strength=0.1)
    rgb = np.zeros((32, 64, 3), dtype=np.uint8)
    out = m.predict(rgb, "erp")
    assert out.shape == (32, 64)


def test_methods_modules_import():
    import methods.capture_faults
    import methods.mobius_tta
    import methods.polar_fusion
    import methods.projection
    from methods.capture_faults.catalogue import CATALOGUE
    assert len(CATALOGUE) >= 8


def test_experiments_modules_import():
    import experiments.benchmark
    import experiments.followups
    import experiments.projection
    from experiments.benchmark.tracker import BestModelTracker
    from experiments.projection.common import load_config
    cfg = load_config("configs/projection/default.yaml")
    assert "model" in cfg


def test_scripts_modules_import():
    from scripts.analysis.final_summary import CORE, EXT
    assert len(CORE) == 4
    assert len(EXT) == 2


# -----------------------------------------------------------------------------
# 8 Merged Module Invariant Tests
# -----------------------------------------------------------------------------

def test_depth_model_wrapper_appearance_scale_law():
    """DepthModelWrapper defaults to appearance_scale_law=True; oracle disables it."""
    class DummyWrapper(DepthModelWrapper):
        def _forward(self, images, kind):
            return [np.ones((16, 32), dtype=np.float32) for _ in images]

    dummy = DummyWrapper()
    assert dummy.appearance_scale_law is True

    oracle = EncodedDepthOracle(strength=0.2)
    assert oracle.appearance_scale_law is False

    # Pipeline logic check: auto activates law if appearance_scale_law is True
    cfg_auto = MethodConfig(method="acgf", acgf_law="auto")
    law_dummy = cfg_auto.acgf_law == "on" or (cfg_auto.acgf_law == "auto" and dummy.appearance_scale_law)
    law_oracle = cfg_auto.acgf_law == "on" or (cfg_auto.acgf_law == "auto" and oracle.appearance_scale_law)
    assert law_dummy is True
    assert law_oracle is False


def test_alignment_mode_scale_in_disparity_space():
    """Alignment mode='scale' fits a single scale factor in disparity space vs affine (scale+shift)."""
    rng = np.random.default_rng(42)
    ref = 0.5 + 0.2 * rng.uniform(0.1, 1.0, size=(30, 60))
    # view has ground-truth scale 2.0 and intercept 0.4
    view = 2.0 * ref + 0.4
    anchor = np.ones((30, 60), dtype=bool)

    # 1. Scale-only mode (1 coefficient, no free shift)
    out_scale, info_scale = align_view_to_reference(view, ref, anchor, space="disparity", mode="scale")
    assert len(info_scale["coef"]) == 1
    # Inline formula check: A = view[anchor, None]; coef, _ = robust_lstsq(A, ref[anchor])
    A_scale = view[anchor, None]
    expected_coef_scale, _ = robust_lstsq(A_scale, ref[anchor])
    expected_scale = expected_coef_scale[0] * view
    assert np.allclose(out_scale, expected_scale)
    # Scale-only cannot absorb intercept 0.4 perfectly
    assert not np.allclose(out_scale, ref, atol=1e-3)

    # 2. Affine mode (default, 2 coefficients: scale + shift)
    out_affine, info_affine = align_view_to_reference(view, ref, anchor, space="disparity", mode="affine")
    assert len(info_affine["coef"]) == 2
    assert np.allclose(out_affine, ref, atol=1e-4)


def test_stereographic_roundtrip():
    """Forward stereographic projection and inverse backward warp round-trip near the view centre."""
    H, W = 64, 128
    view = generate_stereo_view(lon_deg=0.0, lat_deg=90.0, fov_deg=120.0, size=64)

    # Create smooth spherical test pattern
    lat_t, lon_t = erp_lonlat_grid(H, W)
    lat = lat_t.numpy()
    lon = lon_t.numpy()
    erp_pattern = np.cos(np.radians(lat)) * np.sin(np.radians(lon)) + np.sin(np.radians(lat))

    stereo_img = erp_to_stereo(erp_pattern, view, mode="bilinear")
    assert stereo_img.shape == (64, 64)

    res = stereo_to_erp(stereo_img, view, height=H, width=W, mode="bilinear")
    vals = np.asarray(res.values)
    assert vals.shape == (H, W)

    # Near north pole (|lat| > 70 deg, within view frustum), reconstruction error is small
    near_pole = res.valid & (res.alpha_deg < 25.0)
    assert near_pole.sum() > 20
    err = np.abs(vals[near_pole] - erp_pattern[near_pole])
    assert float(np.mean(err)) < 0.05

    # Check analytic magnification values: k = sec^2(alpha / 2)
    assert np.isclose(magnification(0.0), 1.0)
    assert np.isclose(magnification(60.0), 4.0 / 3.0)
    assert np.allclose(res.magnification, magnification(res.alpha_deg))


def test_tangent_to_erp_delegating_to_sample_view_on_erp():
    """tangent_to_erp delegation produces results identical to direct sampling."""
    plane = generate_tangent_plane(lon_deg=0.0, lat_deg=90.0, fov_deg=90.0, size=32)
    rng = np.random.default_rng(123)
    tan_img = rng.standard_normal((32, 32)).astype(np.float32)

    res = tangent_to_erp(tan_img, plane, height=32, width=64, mode="bilinear")

    # Direct reference computation matching old formulation
    j, i, inside, cos_axis, radial = tangent_geometry_on_erp(plane, 32, 64)
    expected_vals, expected_valid = sample_view_on_erp(tan_img, j, i, inside, plane.size, mode="bilinear")

    assert np.array_equal(res.values, expected_vals)
    assert np.array_equal(res.valid, expected_valid)
    assert np.array_equal(res.cos_axis, cos_axis)
    assert np.array_equal(res.radial, radial)


def test_synthetic_fallback_without_skimage():
    """Synthetic dataset procedural fallback executes when scikit-image is unavailable."""
    with patch.dict(sys.modules, {"skimage": None, "skimage.data": None}):
        textures = _texture_bank(seed=0)
        assert len(textures) >= 8
        for tex in textures:
            assert tex.ndim == 3 and tex.shape[2] == 3
            assert tex.min() >= 0.0 and tex.max() <= 1.0

        rng = np.random.default_rng(42)
        scene = random_scene(rng, len(textures))
        rgb, depth = render_erp(scene, textures, 32, 64)
        assert rgb.shape == (32, 64, 3)
        assert depth.shape == (32, 64)
        assert np.all(np.isfinite(depth)) and np.all(depth > 0)


def test_make_dataset_exr_scale_passthrough(tmp_path):
    """make_dataset correctly forwards exr_scale to PanoramaDataset."""
    from experiments.projection.common import make_dataset

    # Create dummy directory and split list
    data_dir = tmp_path / "dummy_data"
    data_dir.mkdir()
    list_file = data_dir / "test.txt"
    list_file.write_text("rgb/001.png depth/001.exr\n", encoding="utf-8")

    cfg = {
        "dataset": {
            "root": str(data_dir),
            "list": "test.txt",
            "name": "panox",
            "height": 64,
            "width": 128,
            "exr_scale": 0.025,
            "depth_scale": 1.0,
            "max_depth": 100.0,
            "min_depth": 0.05,
        }
    }
    ds = make_dataset(cfg)
    assert ds.exr_scale == 0.025


def test_pipeline_method_config_fields_defaults():
    """MethodConfig contains expected defaults for ACGF and mono360 fields."""
    cfg = MethodConfig(method="acgf")
    assert cfg.acgf_domain == "gradient"
    assert cfg.acgf_screen == "value"
    assert cfg.acgf_gate is True
    assert cfg.acgf_law == "auto"
    assert cfg.acgf_lambda_cap == 5.0
    assert cfg.acgf_lambda_edge == 50.0
    assert cfg.acgf_gate_sigma == 3.0
    assert cfg.acgf_irls == 1
    assert cfg.acgf_work == "log"
    assert cfg.acgf_gate_mode == "edge"
    assert cfg.acgf_source == "pole"
    assert cfg.acgf_ico_align == "affine"
    assert cfg.acgf_scope == "polar"
    assert cfg.acgf_ico_lam_smooth == 40.0
    assert cfg.acgf_ico_lam_scale == 0.007
    assert cfg.mono360_padding == 0.3


def test_range_guard_default_off():
    """MethodConfig range_guard defaults to False."""
    cfg = MethodConfig()
    assert cfg.range_guard is False
