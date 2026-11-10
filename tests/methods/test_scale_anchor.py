import numpy as np

from pano.inference.alignment import align_view_to_reference


def test_scale_invariant_disparity_anchor_has_no_intercept():
    rng = np.random.default_rng(7)
    view = rng.uniform(0.1, 2.0, size=(32, 64))
    anchor = np.ones_like(view, dtype=bool)
    reference = 3.25 * view
    aligned, info = align_view_to_reference(
        view, reference, anchor, space="disparity", mode="scale", min_anchor=32
    )
    assert len(info["coef"]) == 1
    assert np.allclose(aligned, reference, atol=1e-8)


def test_scale_invariant_disparity_does_not_fit_shift():
    rng = np.random.default_rng(9)
    view = rng.uniform(0.1, 2.0, size=(32, 64))
    anchor = np.ones_like(view, dtype=bool)
    reference = 3.25 * view + 0.4
    aligned, info = align_view_to_reference(
        view, reference, anchor, space="disparity", mode="scale", min_anchor=32
    )
    assert len(info["coef"]) == 1
    assert not np.allclose(aligned, reference, atol=1e-3)


def test_scale_invariant_planar_disparity_uses_cos_weighted_source():
    rng = np.random.default_rng(11)
    view = rng.uniform(0.1, 2.0, size=(32, 64))
    cos_axis = rng.uniform(0.5, 1.0, size=view.shape)
    anchor = np.ones_like(view, dtype=bool)
    reference = 2.5 * cos_axis * view
    aligned, info = align_view_to_reference(
        view, reference, anchor, space="disparity", mode="scale",
        geometry="planar", cos_axis=cos_axis, min_anchor=32
    )
    assert len(info["coef"]) == 1
    assert np.allclose(aligned, reference, atol=1e-8)
