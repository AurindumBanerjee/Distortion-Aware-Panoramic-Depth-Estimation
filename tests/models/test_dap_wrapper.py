"""Plumbing test for DAPWrapper against a stand-in repository with DAP's output contract."""
import os

import numpy as np
import torch

from pano.models.depth_model import DAPWrapper


def test_dap_wrapper_contract(tmp_path):
    from pano.paths import ROOT
    repo = str(ROOT / "tests" / "fake_dap_repo")
    w = tmp_path / "model.pth"
    torch.save({"module.scale": torch.tensor(0.05)}, w)
    m = DAPWrapper(repo=repo, weights=str(w), device="cpu", height=64, width=128)
    out = m.predict(np.zeros((256, 512, 3), np.uint8), "erp")
    assert out.shape == (256, 512)
    assert np.isnan(out[:8]).all()  # masked rows -> NaN at input resolution
    assert np.allclose(out[32:], 5.0)  # x 100 m
    assert m.spec.space == "depth" and m.spec.scale == "metric"
