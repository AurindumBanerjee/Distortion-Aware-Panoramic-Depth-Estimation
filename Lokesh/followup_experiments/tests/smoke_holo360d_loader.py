"""CPU smoke test for the Holo360D three-column RGB / mesh-depth / mask loader."""
from __future__ import annotations

import tempfile
from pathlib import Path

import cv2
import numpy as np

from datasets.panorama import PanoramaDataset


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="holo360d_loader_smoke_") as td:
        root = Path(td)
        scene = root / "Indoor_001" / "Indoor_001"
        (scene / "rgb").mkdir(parents=True)
        (scene / "depth" / "mesh_depth").mkdir(parents=True)
        (scene / "mask").mkdir(parents=True)

        rgb = np.zeros((12, 24, 3), dtype=np.uint8)
        depth = np.full((12, 24), 2.0, dtype=np.float32)
        mask = np.zeros((12, 24), dtype=np.uint8)
        mask[:, 12:] = 255

        cv2.imwrite(str(scene / "rgb" / "frame_0001.jpg"), rgb)
        np.save(scene / "depth" / "mesh_depth" / "frame_0001.npy", depth)
        cv2.imwrite(str(scene / "mask" / "frame_0001.jpg"), mask)

        (root / "indoor.txt").write_text(
            "Indoor_001/Indoor_001/rgb/frame_0001.jpg "
            "Indoor_001/Indoor_001/depth/mesh_depth/frame_0001.npy "
            "Indoor_001/Indoor_001/mask/frame_0001.jpg\n",
            encoding="utf-8",
        )

        ds = PanoramaDataset(str(root), "indoor.txt", height=6, width=12, name="holo360d")
        sample = ds[0]
        assert sample.id == "Indoor_001_frame_0001", sample.id
        assert sample.valid.shape == (6, 12)
        assert np.all(sample.valid[:, :6] == 0), "mask-invalid pixels were retained"
        assert np.all(sample.valid[:, 6:] == 1), "mask-valid pixels were dropped"
        assert np.allclose(sample.depth[sample.valid], 2.0)
        assert np.isnan(sample.depth[~sample.valid]).all()

    print("PASS: Holo360D preset, nested scene ID, third-column mask and invalid-depth masking")


if __name__ == "__main__":
    main()
