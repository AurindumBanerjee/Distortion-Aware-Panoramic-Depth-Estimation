#!/usr/bin/env python3
"""Robust fetch of the NYC panorama pairs from the Hugging Face dataset Coaa1/DAP_data.

    python scripts/hf_fetch_retry.py --out data/nyc_dap --step 5 --max_id 1907

What it handles
  * network trouble (timeouts, resets, 429 / 5xx): retried with exponential backoff and jitter, resumable
  * a file that is listed but whose blob is gone (HTTP 404 from the CDN): retried a few times, then given up on;
    the id is replaced by the next id inside the same step window, so the sample stays evenly spread
  * a half-written or corrupt file: every file is downloaded to a temp folder, checked (PNG header / loadable
    2-D .npy) and only then moved to rgb/ or depth/
  * re-runs only fetch what is missing
It prints a summary with the ids that stayed unavailable. Run scripts/make_nyc_list.py afterwards (the .sh wrapper does).
"""
import argparse
import os
import random
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from huggingface_hub import hf_hub_download, list_repo_files

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="Coaa1/DAP_data")
ap.add_argument("--out", default="data/nyc_dap")
ap.add_argument("--step", type=int, default=5)
ap.add_argument("--max_id", type=int, default=1907)
ap.add_argument("--attempts", type=int, default=6, help="tries per file for network errors")
ap.add_argument("--dead_after", type=int, default=3, help="tries before a persistent 404 counts as unavailable")
ap.add_argument("--workers", type=int, default=4)
a = ap.parse_args()

RGB = "nyc_raw_images_panorama/panorama_{}.png"
DEP = "nyc_distance_panorama_npy/erp_distance_{}.npy"
rgb_dir, dep_dir, tmp = (os.path.join(a.out, d) for d in ("rgb", "depth", "_dl"))
for d in (rgb_dir, dep_dir, tmp):
    os.makedirs(d, exist_ok=True)


def is_404(e):
    s = f"{type(e).__name__} {e}"
    return "404" in s or "EntryNotFound" in s


def valid(path, kind):
    try:
        if os.path.getsize(path) < 1000:
            return False
        if kind == "png":
            with open(path, "rb") as f:
                return f.read(8) == b"\x89PNG\r\n\x1a\n"
        arr = np.load(path, mmap_mode="r")
        return arr.ndim == 2 and arr.size > 0
    except Exception:
        return False


def fetch(src, dst, kind):
    """Returns 'ok', 'dead' (blob keeps returning 404) or 'failed' (network never recovered)."""
    if os.path.exists(dst) and valid(dst, kind):
        return "ok"
    missing_tries = 0
    for k in range(a.attempts):
        try:
            p = hf_hub_download(a.repo, src, repo_type="dataset", local_dir=tmp)
            if not valid(p, kind):
                raise OSError("downloaded file failed validation")
            os.replace(p, dst)
            return "ok"
        except Exception as e:  # noqa: BLE001
            if is_404(e):
                missing_tries += 1
                if missing_tries >= a.dead_after:
                    return "dead"
            if k == a.attempts - 1:
                break
            wait = min(60, 2 ** (k + 1)) + random.uniform(0, 2)
            time.sleep(wait)
    return "failed"


def listing():
    for k in range(6):
        try:
            return set(list_repo_files(a.repo, repo_type="dataset"))
        except Exception as e:  # noqa: BLE001
            print(f"listing failed ({type(e).__name__}), retry {k + 1}", flush=True)
            time.sleep(min(60, 2 ** (k + 1)))
    return None


files = listing()


def listed(n):
    return files is None or (RGB.format(n) in files and DEP.format(n) in files)


def pair(n):
    rgb_p = os.path.join(rgb_dir, f"panorama_{n}.png")
    had_rgb = os.path.exists(rgb_p)
    r = fetch(RGB.format(n), rgb_p, "png")
    if r != "ok":
        return r
    r = fetch(DEP.format(n), os.path.join(dep_dir, f"erp_distance_{n}.npy"), "npy")
    if r != "ok" and not had_rgb and os.path.exists(rgb_p):
        os.remove(rgb_p)  # a pair needs both files
    return r


def window(base):
    """One pair per step window: the base id first, then its neighbours inside the window."""
    for n in range(base, min(base + a.step, a.max_id + 1)):
        if not listed(n):
            continue
        r = pair(n)
        if r == "ok":
            return base, n, "ok"
    return base, None, "none"


bases = list(range(0, a.max_id + 1, a.step))
got = replaced = lost = 0
lost_ids = []
t0 = time.time()
with ThreadPoolExecutor(a.workers) as ex:
    for i, (base, n, st) in enumerate(ex.map(window, bases), 1):
        if st == "ok":
            got += 1
            replaced += n != base
        else:
            lost += 1
            lost_ids.append(base)
        if i % 25 == 0 or i == len(bases):
            print(f"{i}/{len(bases)} windows | pairs {got} | substituted {replaced} | lost {lost} | {int(time.time() - t0)} s", flush=True)
shutil.rmtree(tmp, ignore_errors=True)
print(f"done: {got} pairs ({replaced} used a neighbouring id), {lost} windows without any usable pair {lost_ids[:20]}")
sys.exit(0 if got else 1)
