"""End-to-end pipeline tests with a black-box oracle whose error is latitude-dependent by construction.

If projection, rotation, reprojection, alignment and fusion are all correct, the corrected
prediction must have much lower polar error than the baseline, and must not change the
equatorial region (where w(phi) = 0).
"""
import numpy as np
import pytest

from datasets.synthetic import _texture_bank, random_scene, render_erp
from evaluation.latitude_analysis import per_band_metrics
from inference.pipeline import DistortionAwareInference, MethodConfig
from models.depth_model import EncodedDepthOracle, encode_depth_as_image


@pytest.fixture(scope="module")
def scene():
    bank = _texture_bank(0)
    rng = np.random.default_rng(3)
    sc = random_scene(rng, len(bank))
    _, depth = render_erp(sc, bank, 128, 256, ss=1)
    return depth


@pytest.mark.parametrize("method,extra", [
    ("tangent", {}), ("rotation", {"rotations": [[0, 90, 0], [90, 90, 0]]}),
    ("hybrid", {"rotations": [[0, 90, 0]]}),
])
@pytest.mark.parametrize("fusion", ["hard", "cosine", "confidence"])
def test_correction_reduces_polar_error(scene, method, extra, fusion):
    depth = scene
    rgb = encode_depth_as_image(depth)
    model = EncodedDepthOracle(strength=0.4)
    dai = DistortionAwareInference(model, batch_size=4)
    valid = np.isfinite(depth)
    base = dai.run(rgb, "s", MethodConfig("baseline"))
    cfg = MethodConfig(method, lat_threshold=45, views_per_pole=1, tangent_size=128, fusion=fusion, **extra)
    out = dai.run(rgb, "s", cfg)
    mb = per_band_metrics(base["pred"], depth, valid)
    mc = per_band_metrics(out["pred"], depth, valid)
    assert mc["75-90"]["abs_rel"] < 0.6 * mb["75-90"]["abs_rel"]
    assert mc["60-75"]["abs_rel"] < mb["60-75"]["abs_rel"]
    if fusion != "confidence":  # equatorial pixels are untouched by latitude fusion
        assert abs(mc["0-15"]["abs_rel"] - mb["0-15"]["abs_rel"]) < 1e-9
