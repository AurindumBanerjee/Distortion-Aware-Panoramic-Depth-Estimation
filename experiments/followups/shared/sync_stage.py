File: Distortion-Aware-Panoramic-Depth-Estimation/experiments/followups/shared/sync_stage.py

#!/usr/bin/env python3
"""Auto-sync script: packages and streams experiment outputs immediately after each run.

Designed for remote execution (e.g. Kaggle / Colab / remote Linux VM).
Emits 76-char wrapped base64 payloads to stdout so that VS Code Jupyter client
automatically saves them into the local .ipynb file in real time without UI lag.
Also creates physical zip archives in /kaggle/working. Git operations are deliberately disabled.
"""
from __future__ import annotations

import base64
import io
import sys
import zipfile
from pathlib import Path

from pano.paths import FOLLOWUP_RESULTS, ROOT

EXP_ROOT = ROOT / "experiments" / "followups"

STAGE_MAP = {
    "01": "scale_only_protocol",
    "02": "domain_conditioned_gate",
    "03": "panda_style_finetuning",
    "04": "mono360_20view",
    "05": "fov_resolution_sweep",
    "06": "structure_at_poles_gate",
    "07": "real_nyc_20view",
    "08": "paired_panox_analysis",
    "scale_only_protocol": "scale_only_protocol",
    "domain_conditioned_gate": "domain_conditioned_gate",
    "panda_style_finetuning": "panda_style_finetuning",
    "mono360_20view": "mono360_20view",
    "fov_resolution_sweep": "fov_resolution_sweep",
    "structure_at_poles_gate": "structure_at_poles_gate",
    "real_nyc_20view": "real_nyc_20view",
    "paired_panox_analysis": "paired_panox_analysis",
}


def sync_stage(stage_key: str, working_dir: Path | None = None) -> int:
    stage_dir_name = STAGE_MAP.get(stage_key, stage_key)
    res_path = FOLLOWUP_RESULTS / stage_dir_name
    exp_path = EXP_ROOT / stage_dir_name

    outputs_dir = res_path / "outputs" if (res_path / "outputs").is_dir() else exp_path / "outputs"
    logs_dir = res_path / "logs" if (res_path / "logs").is_dir() else exp_path / "logs"

    if not outputs_dir.is_dir() and not logs_dir.is_dir():
        print(f"[AUTO-SYNC] Warning: output/log directory does not exist for: {stage_dir_name}", flush=True)
        return 0

    files_to_pack: list[Path] = []

    # Target only the latest run directory to ensure instant synchronization
    if outputs_dir.is_dir():
        run_folders = sorted(
            [d for d in outputs_dir.iterdir() if d.is_dir()],
            key=lambda p: p.stat().st_mtime,
        )
        if run_folders:
            latest_run = run_folders[-1]
            for f in latest_run.rglob("*"):
                if f.is_file() and f.suffix.lower() not in {".pt", ".pth", ".bin"}:
                    files_to_pack.append(f)

    if logs_dir.is_dir():
        log_files = sorted(
            [f for f in logs_dir.iterdir() if f.is_file() and f.suffix == ".log"],
            key=lambda p: p.stat().st_mtime,
        )
        if log_files:
            files_to_pack.append(log_files[-1])

    if not files_to_pack:
        print(f"[AUTO-SYNC] No output files found for {stage_dir_name}", flush=True)
        return 0

    files_to_pack.sort(key=lambda p: p.stat().st_mtime)

    # 1. In-memory zip for base64 payload
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files_to_pack:
            try:
                rel = f.relative_to(FOLLOWUP_RESULTS)
            except ValueError:
                rel = f.relative_to(ROOT)
            zf.write(f, arcname=str(rel))

    zip_bytes = buf.getvalue()
    # Use MIME 76-character line wrapping to prevent Monaco editor / VS Code layout freezes
    payload = base64.encodebytes(zip_bytes).decode("ascii")

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
                    try:
                        rel = str(f.relative_to(FOLLOWUP_RESULTS))
                    except ValueError:
                        rel = str(f.relative_to(ROOT))
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
    print(f"[AUTO-SYNC] Stage {stage_dir_name} sync payload streamed to local client!\n", flush=True)

    # Git stage/commit/push is intentionally disabled. Syncing artifacts must never
    # mutate a Git index, create commits, alter remotes, or push from Kaggle.

    return len(files_to_pack)



def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "all":
        for k in ["01", "02", "04", "05", "03"]:
            sync_stage(k)
    else:
        sync_stage(stage)


if __name__ == "__main__":
    main()