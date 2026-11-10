"""Scene-level validation: an ERP rendered by ray casting, re-projected to a tangent view, must
match a pinhole image rendered *directly* by ray casting the same scene (exact GT both ways)."""
import numpy as np

from pano.datasets.synthetic import _texture_bank, random_scene, render_erp, render_perspective
from pano.geometry.tangent_plane import (erp_to_tangent, generate_tangent_plane, range_to_z, tangent_to_erp,
                                    tangent_world_dirs, z_to_range)


def test_tangent_matches_direct_render():
    bank = _texture_bank(0)
    sc = random_scene(np.random.default_rng(7), len(bank))
    H, W = 512, 1024
    _, depth = render_erp(sc, bank, H, W, ss=1)
    for lon, lat in [(0, 0), (40, 70), (0, 90), (179, -60)]:
        p = generate_tangent_plane(lon, lat, 90, 128)
        _, r_direct = render_perspective(sc, bank, tangent_world_dirs(p).numpy())
        r_proj = erp_to_tangent(depth.astype(np.float64), p, mode="nearest")
        rel = np.abs(r_proj - r_direct) / r_direct
        # nearest sampling: only pixels at depth edges may differ
        assert np.median(rel) < 2e-3, (lon, lat, np.median(rel))
        assert (rel < 0.02).mean() > 0.95
        # planar-depth round trip through the tangent image back to ERP
        z = range_to_z(r_direct, p)
        back = tangent_to_erp(z_to_range(z, p), p, H, W, mode="nearest")
        rel2 = np.abs(back.values - depth)[back.valid] / depth[back.valid]
        assert np.median(rel2) < 2e-3 and (rel2 < 0.02).mean() > 0.95
