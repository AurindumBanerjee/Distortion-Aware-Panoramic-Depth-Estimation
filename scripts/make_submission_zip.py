"""Package the codebase into a clean, lightweight submission archive (< 9.5 MB) using git archive."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ZIP = ROOT / "submission_code.zip"


def make_zip(out_path: Path = OUTPUT_ZIP) -> Path:
    print(f"Building submission zip -> {out_path.name} via git archive...")
    # Obtain a commit-ish capturing the current working tree + staged index
    stash_proc = subprocess.run(
        ["git", "stash", "create"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    commit = stash_proc.stdout.strip().splitlines()[-1].strip() if stash_proc.stdout.strip() else ""
    if not commit or len(commit) != 40:
        commit = "HEAD"

    # git archive respects .gitattributes (export-ignore)
    archive_cmd = [
        "git",
        "archive",
        "--format=zip",
        "-o",
        str(out_path),
        commit,
    ]
    res = subprocess.run(archive_cmd, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"git archive failed: {res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)

    if not out_path.is_file():
        print(f"Error: Expected archive {out_path} was not created.", file=sys.stderr)
        sys.exit(1)

    size_bytes = out_path.stat().st_size
    size_mb = size_bytes / 1e6
    print(f"Archive created: {out_path.name} ({size_mb:.2f} MB, {size_bytes} bytes)")
    if size_mb >= 9.5:
        print(f"ERROR: Archive size {size_mb:.2f} MB exceeds 9.5 MB hard limit.", file=sys.stderr)
        sys.exit(1)
    print("Verification: Archive is strictly under 9.5 MB.")
    return out_path


if __name__ == "__main__":
    make_zip()
