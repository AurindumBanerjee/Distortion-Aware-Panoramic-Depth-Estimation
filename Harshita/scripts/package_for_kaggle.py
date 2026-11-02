"""Bundle the code (no data, weights or results) into kaggle_upload/dad-code.zip.

Upload that zip as a private Kaggle dataset (e.g. "dad-code"); notebooks/kaggle_acgf.ipynb finds it
under /kaggle/input automatically. The Holo360D split lists are copied to lists/holo360d/ because
they are not inside holo360d.zip.

    python scripts/package_for_kaggle.py
"""
from __future__ import annotations

import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIRS = ["configs", "datasets", "evaluation", "experiments", "geometry", "inference", "models", "scripts",
             "tests", "third_party/midas_repo", "visualization", "notebooks"]
TOP_FILES = ["run_experiment.py", "requirements.txt", "README.md", "RESULTS.md"]
LISTS = {"data/holo360d": "lists/holo360d", "data/structured3d": "lists/structured3d"}


def main():
    out_dir = os.path.join(ROOT, "kaggle_upload")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "dad-code.zip")
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for d in CODE_DIRS:
            for base, dirs, files in os.walk(os.path.join(ROOT, d)):
                dirs[:] = [x for x in dirs if x not in ("__pycache__", ".ipynb_checkpoints", "DAP")]
                for f in files:
                    if f.endswith((".pyc", ".png", ".npz")):
                        continue
                    p = os.path.join(base, f)
                    z.write(p, os.path.relpath(p, ROOT))
                    n += 1
        for f in TOP_FILES:
            z.write(os.path.join(ROOT, f), f)
            n += 1
        for src, dst in LISTS.items():
            for f in sorted(os.listdir(os.path.join(ROOT, src))):
                if f.endswith(".txt"):
                    z.write(os.path.join(ROOT, src, f), f"{dst}/{f}")
                    n += 1
    print(f"wrote {out}: {n} files, {os.path.getsize(out) / 2 ** 20:.1f} MB")


if __name__ == "__main__":
    main()
