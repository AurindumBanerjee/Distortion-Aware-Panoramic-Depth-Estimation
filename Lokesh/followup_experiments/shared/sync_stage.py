#!/usr/bin/env python3
"""Auto-sync script: packages and streams experiment outputs immediately after each run.

Designed for remote execution (e.g. Kaggle / Colab / remote Linux VM).
Emits base64 payloads to stdout so that VS Code Jupyter client automatically
saves them into the local .ipynb file in real time. Also creates physical zip
archives in /kaggle/working and optionally performs git commit/push if GITHUB_PAT is set.
"""
from __future__ import annotations

import base64
import io
import os
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP_ROOT = HERE.parent
LOKESH_ROOT = EXP_ROOT.parent

STAGE_MAP = {
    "01": "01_scale_only_protocol",
    "02": "02_domain_conditioned_gate",
    "03": "03_panda_style_finetuning",
    "04": "04_mono360_20view",
    "05": "05_fov_resolution_sweep",
    "01_scale_only_protocol": "01_scale_only_protocol",
    "02_domain_conditioned_gate": "02_domain_conditioned_gate",
    "03_panda_style_finetuning": "03_panda_style_finetuning",
    "04_mono360_20view": "04_mono360_20view",
    "05_fov_resolution_sweep": "05_fov_resolution_sweep",
}


def sync_stage(stage_key: str, working_dir: Path | None = None) -> int:
    stage_dir_name = STAGE_MAP.get(stage_key, stage_key)
    stage_path = EXP_ROOT / stage_dir_name

    if not stage_path.is_dir():
        print(f"[AUTO-SYNC] Warning: directory does not exist: {stage_path}", flush=True)
        return 0

    outputs_dir = stage_path / "outputs"
    logs_dir = stage_path / "logs"

    files_to_pack: list[Path] = []
    if outputs_dir.is_dir():
        for f in outputs_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() not in {".pt", ".pth", ".bin"}:
                files_to_pack.append(f)
    if logs_dir.is_dir():
        for f in logs_dir.rglob("*.log"):
            if f.is_file():
                files_to_pack.append(f)

    if not files_to_pack:
        print(f"[AUTO-SYNC] No output files found for {stage_dir_name}", flush=True)
        return 0

    # Sort files by modification time
    files_to_pack.sort(key=lambda p: p.stat().st_mtime)

    # 1. In-memory zip for base64 payload
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files_to_pack:
            rel = f.relative_to(EXP_ROOT)
            zf.write(f, arcname=str(rel))

    zip_bytes = buf.getvalue()
    payload = base64.b64encode(zip_bytes).decode("ascii")

    # 2. Save physical zip archives
    working = working_dir or Path("/kaggle/working")
    if working.is_dir():
        stage_zip = working / f"sync_{stage_dir_name}.zip"
        try:
            stage_zip.write_bytes(zip_bytes)
        except Exception:
            pass

        # Update cumulative all_followup_outputs.zip
        cum_zip_path = working / "all_followup_outputs.zip"
        try:
            with zipfile.ZipFile(cum_zip_path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
                existing = set(zf.namelist())
                for f in files_to_pack:
                    rel = str(f.relative_to(EXP_ROOT))
                    if rel not in existing:
                        zf.write(f, arcname=rel)
        except Exception:
            pass

    # 3. Stream payload to stdout with clear delimiters
    print("\n" + "=" * 70, flush=True)
    print(f"🚀 [AUTO-SYNC] Instant Stage Output Synchronization: {stage_dir_name}", flush=True)
    print(f"   Files packaged: {len(files_to_pack)} ({len(zip_bytes) / 1024:.1f} KB)", flush=True)
    print("=" * 70, flush=True)
    print(f"=== STAGE_SYNC_PAYLOAD_START: {stage_dir_name} ===", flush=True)
    print(payload, flush=True)
    print(f"=== STAGE_SYNC_PAYLOAD_END: {stage_dir_name} ===", flush=True)
    print(f"✅ [AUTO-SYNC] Stage {stage_dir_name} sync payload streamed to local client!\n", flush=True)

    # 4. Optional direct Git push if GITHUB_PAT is available in environment
    try_git_push(stage_dir_name)

    return len(files_to_pack)


def try_git_push(stage_dir_name: str) -> None:
    pat = os.environ.get("GITHUB_PAT", "").strip()
    repo_url = os.environ.get(
        "REPO_URL",
        "https://github.com/AurindumBanerjee/Distortion-Aware-Panoramic-Depth-Estimation.git",
    ).strip()

    git_dir = LOKESH_ROOT.parent / ".git"
    if not git_dir.is_dir():
        return

    try:
        if pat and "github.com" in repo_url:
            auth_url = repo_url.replace("https://", f"https://{pat}@")
            subprocess.run(
                ["git", "remote", "set-url", "origin", auth_url],
                cwd=LOKESH_ROOT.parent,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        # Stage only outputs and logs of this stage
        stage_rel = f"Lokesh/followup_experiments/{stage_dir_name}"
        subprocess.run(
            ["git", "add", f"{stage_rel}/outputs", f"{stage_rel}/logs"],
            cwd=LOKESH_ROOT.parent,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        commit_proc = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"auto-sync(followup): archive {stage_dir_name} outputs from remote run [skip ci]",
            ],
            cwd=LOKESH_ROOT.parent,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if commit_proc.returncode == 0:
            print(f"[AUTO-SYNC] Committed {stage_dir_name} outputs locally.", flush=True)
            if pat:
                push_proc = subprocess.run(
                    ["git", "push", "origin", "HEAD"],
                    cwd=LOKESH_ROOT.parent,
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if push_proc.returncode == 0:
                    print(f"✅ [AUTO-SYNC] Pushed {stage_dir_name} outputs directly to GitHub!", flush=True)
                else:
                    print(f"[AUTO-SYNC] Git push skipped/failed: {push_proc.stderr.strip()}", flush=True)
    except Exception as e:
        print(f"[AUTO-SYNC] Git push notice: {e}", flush=True)


def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "all":
        for k in ["01", "02", "04", "05", "03"]:
            sync_stage(k)
    else:
        sync_stage(stage)


if __name__ == "__main__":
    main()

