#!/usr/bin/env python3
"""Sync experiment outputs, metrics, and logs from kaggle_two_t4_runner.ipynb into local repo."""
from __future__ import annotations

import base64
import io
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "followup_experiments" / "kaggle_two_t4_runner.ipynb"
TARGET_DIR = ROOT / "followup_experiments"


def main():
    if not NB_PATH.is_file():
        raise FileNotFoundError(f"Notebook not found: {NB_PATH}")

    with open(NB_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    payload_b64 = None
    for cell in nb.get("cells", []):
        for out in cell.get("outputs", []):
            texts = out.get("text", [])
            full_text = "".join(texts)
            if "=== LOCAL_REPO_SYNC_PAYLOAD_START ===" in full_text:
                start = full_text.find("=== LOCAL_REPO_SYNC_PAYLOAD_START ===") + len("=== LOCAL_REPO_SYNC_PAYLOAD_START ===")
                end = full_text.find("=== LOCAL_REPO_SYNC_PAYLOAD_END ===")
                if end > start:
                    payload_b64 = full_text[start:end].strip()
                    break
        if payload_b64:
            break

    if not payload_b64:
        print("No sync payload found in notebook outputs.")
        print("To generate the sync bundle:")
        print("1. Open Lokesh/followup_experiments/kaggle_two_t4_runner.ipynb in VS Code.")
        print("2. Run the 'Export Outputs & Logs' cell (Cell 9).")
        print("3. Run this script again: python Lokesh/scripts/sync_kaggle_outputs.py")
        return

    raw_zip = base64.b64decode(payload_b64)
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as zf:
        names = zf.namelist()
        print(f"Extracting {len(names)} files into {TARGET_DIR}...")
        for name in names:
            dest = TARGET_DIR / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as src, open(dest, "wb") as dst:
                dst.write(src.read())
            print(f"  -> {name}")

    print("\nAll outputs and logs synchronized successfully into local repo!")
    print("Staging and committing to git...")
    try:
        subprocess.run(["git", "-C", str(ROOT), "add", "followup_experiments/"], check=True)
        subprocess.run(
            ["git", "-C", str(ROOT), "commit", "-m", "record(followup): archive Kaggle experiment outputs, metrics, and logs"],
            check=False,
        )
        print("Git commit completed!")
    except Exception as e:
        print(f"Note: Git commit skipped or failed ({e}). Files are preserved on disk.")


if __name__ == "__main__":
    main()

