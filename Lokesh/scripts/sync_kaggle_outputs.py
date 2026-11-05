#!/usr/bin/env python3
"""Sync experiment outputs, metrics, and logs from kaggle_two_t4_runner.ipynb into local repo.

Features:
- Extracts per-stage payloads (=== STAGE_SYNC_PAYLOAD_START: <stage> ===)
- Extracts full payloads (=== LOCAL_REPO_SYNC_PAYLOAD_START ===)
- Rescues markdown reports from interactive dashboard outputs if payloads are missing
- Auto-stages and commits extracted results to git
- Optional --watch mode to continuously sync in the background while experiments run!
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "followup_experiments" / "kaggle_two_t4_runner.ipynb"
TARGET_DIR = ROOT / "followup_experiments"


def extract_payloads_from_notebook(nb_path: Path) -> list[tuple[str, str]]:
    """Returns list of (label, base64_payload) found in notebook cell outputs."""
    if not nb_path.is_file():
        return []

    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Warning: could not parse notebook {nb_path}: {e}")
        return []

    payloads: list[tuple[str, str]] = []
    seen = set()

    for cell in nb.get("cells", []):
        for out in cell.get("outputs", []):
            texts = out.get("text", [])
            full_text = "".join(texts)

            # 1. Search for per-stage payloads
            pattern = re.compile(
                r"===\s*STAGE_SYNC_PAYLOAD_START:\s*([^\s=]+)\s*===\s*\n?(.*?)\n?===\s*STAGE_SYNC_PAYLOAD_END:\s*\1\s*===",
                re.DOTALL,
            )
            for m in pattern.finditer(full_text):
                stage_label = m.group(1).strip()
                b64 = m.group(2).strip()
                if b64 and b64 not in seen:
                    payloads.append((stage_label, b64))
                    seen.add(b64)

            # 2. Search for monolithic payload
            if "=== LOCAL_REPO_SYNC_PAYLOAD_START ===" in full_text:
                start = full_text.find("=== LOCAL_REPO_SYNC_PAYLOAD_START ===") + len("=== LOCAL_REPO_SYNC_PAYLOAD_START ===")
                end = full_text.find("=== LOCAL_REPO_SYNC_PAYLOAD_END ===")
                if end > start:
                    b64 = full_text[start:end].strip()
                    if b64 and b64 not in seen:
                        payloads.append(("all", b64))
                        seen.add(b64)

    return payloads


def rescue_reports_from_dashboard(nb_path: Path) -> int:
    """Extracts rendered Markdown reports from the results dashboard cell if present."""
    if not nb_path.is_file():
        return 0

    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    rescued = 0
    experiments = [
        ("01_scale_only_protocol", "run_20261105_155600"),
        ("02_domain_conditioned_gate", "run_20261105_160335"),
        ("03_panda_style_finetuning", "evaluation_20261105_173454"),
        ("04_mono360_20view", "run_20261105_162943"),
        ("05_fov_resolution_sweep", "run_20261105_165811"),
    ]

    for cell in nb.get("cells", []):
        if cell.get("id") == "interactive-results":
            idx = 0
            for out in cell.get("outputs", []):
                if out.get("output_type") == "display_data":
                    md = "".join(out.get("data", {}).get("text/markdown", []))
                    if md.startswith("## Experiment"):
                        first_nl = md.find("\n\n")
                        if first_nl != -1:
                            md = md[first_nl + 2:]
                    if idx < len(experiments):
                        folder, run_dir = experiments[idx]
                        out_path = TARGET_DIR / folder / "outputs" / run_dir / "REPORT.md"
                        if not out_path.is_file() or out_path.read_text(encoding="utf-8") != md:
                            out_path.parent.mkdir(parents=True, exist_ok=True)
                            out_path.write_text(md, encoding="utf-8")
                            print(f"  [RESCUED] Saved {out_path.relative_to(ROOT)}")
                            rescued += 1
                        idx += 1
    return rescued


def extract_zip_payload(label: str, payload_b64: str) -> int:
    """Decodes base64 zip and unpacks files into TARGET_DIR."""
    try:
        raw_zip = base64.b64decode(payload_b64)
    except Exception as e:
        print(f"Error decoding base64 for {label}: {e}")
        return 0

    extracted = 0
    try:
        with zipfile.ZipFile(io.BytesIO(raw_zip)) as zf:
            names = zf.namelist()
            print(f"Extracting {len(names)} files from '{label}' bundle into {TARGET_DIR}...")
            for name in names:
                dest = TARGET_DIR / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(name) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                print(f"  -> {name}")
                extracted += 1
    except Exception as e:
        print(f"Error unpacking zip archive for {label}: {e}")
        return 0

    return extracted


def commit_to_git(summary_label: str) -> None:
    """Stages and commits any updated files in followup_experiments."""
    repo_root = ROOT.parent
    try:
        status = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain", "Lokesh/followup_experiments/"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        if not status.stdout.strip():
            print("Git repository working tree is clean; no new changes to commit.")
            return

        subprocess.run(
            ["git", "-C", str(repo_root), "add", "Lokesh/followup_experiments/"],
            check=True,
        )
        commit_msg = f"record(followup): auto-sync Kaggle experiment outputs ({summary_label})"
        subprocess.run(
            ["git", "-C", str(repo_root), "commit", "-m", commit_msg],
            check=True,
        )
        print(f"[OK] Git commit created: {commit_msg}")
    except Exception as e:
        print(f"Note: Git commit notice: {e}. Output files are safely preserved on disk.")


def sync_once() -> int:
    if not NB_PATH.is_file():
        print(f"Notebook not found: {NB_PATH}")
        return 0

    payloads = extract_payloads_from_notebook(NB_PATH)
    total_files = 0
    labels = []

    for label, b64 in payloads:
        n = extract_zip_payload(label, b64)
        if n > 0:
            total_files += n
            labels.append(label)

    rescued = rescue_reports_from_dashboard(NB_PATH)
    total_files += rescued

    if total_files > 0:
        summary_label = ", ".join(labels) if labels else "dashboard reports"
        print(f"\nSuccessfully synchronized {total_files} files from Kaggle!")
        commit_to_git(summary_label)
    else:
        print("No new sync payloads found in notebook outputs.")
        print("Tip: If experiments are running, you can keep this running with:")
        print("  python Lokesh/scripts/sync_kaggle_outputs.py --watch")

    return total_files


def watch_mode(interval_sec: float = 5.0) -> None:
    print(f"Watching {NB_PATH} every {interval_sec}s for completed experiment runs...")
    print("Press Ctrl+C to stop.")
    last_mtime = 0.0
    processed_payloads: set[str] = set()

    while True:
        try:
            if NB_PATH.is_file():
                current_mtime = NB_PATH.stat().st_mtime
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    payloads = extract_payloads_from_notebook(NB_PATH)
                    new_extracted = 0
                    new_labels = []
                    for label, b64 in payloads:
                        h = b64[:64]
                        if h not in processed_payloads:
                            n = extract_zip_payload(label, b64)
                            if n > 0:
                                new_extracted += n
                                new_labels.append(label)
                                processed_payloads.add(h)

                    rescued = rescue_reports_from_dashboard(NB_PATH)
                    new_extracted += rescued

                    if new_extracted > 0:
                        lbl = ", ".join(new_labels) if new_labels else "dashboard reports"
                        commit_to_git(lbl)
            time.sleep(interval_sec)
        except KeyboardInterrupt:
            print("\nStopped watcher.")
            break
        except Exception as e:
            print(f"Watcher loop notice: {e}")
            time.sleep(interval_sec)


def main():
    parser = argparse.ArgumentParser(description="Synchronize Kaggle experiment outputs to local Git repository.")
    parser.add_argument("--watch", action="store_true", help="Continuously monitor notebook for new stage outputs.")
    parser.add_argument("--interval", type=float, default=5.0, help="Poll interval in seconds for --watch.")
    args = parser.parse_args()

    if args.watch:
        watch_mode(args.interval)
    else:
        sync_once()


if __name__ == "__main__":
    main()
