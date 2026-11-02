"""Download the parts of PanoX (OmniX, Apache-2.0) needed for depth evaluation.

PanoX is published as one zip per scene (26-75 GB each, 345 GB total):
  https://huggingface.co/datasets/KevinHuang/PanoX
The official train/val/test ids are in PanoX_filelist.json. Instead of downloading whole zips,
this script reads each zip's central directory over HTTP range requests (remotezip) and
extracts ONLY the members that (a) belong to the chosen split and (b) match the chosen
modalities (RGB + distance by default). Run it on your own machine (needs internet access
to huggingface.co):

    pip install huggingface_hub remotezip tqdm
    # 1) inspect the layout of one zip (prints the first members; nothing is downloaded)
    python scripts/download_panox.py --list --scenes Warehouse
    # 2) download test-split RGB + distance for the 6 in-domain scenes + 2 out-of-domain scenes
    python scripts/download_panox.py --split test --out data/panox
    # whole zips instead (huge):  python scripts/download_panox.py --full --scenes Warehouse

Out-of-domain scenes in the OmniX paper: the 2 scenes not listed in PanoX_filelist.json
(this script reports which scenes have no split entry and treats all of their ids as test).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = "KevinHuang/PanoX"
BASE = f"https://huggingface.co/datasets/{REPO}/resolve/main"
SCENES = ["ClothingStore", "Diner50", "FeudalJapan_Meshingun", "ModularBakeryShop", "Mountain_Environment_Set",
          "SouthOfFrance", "Warehouse", "YellowParrot"]
# keywords used to recognise modalities in member paths (case-insensitive); adjust after --list
DEFAULT_INCLUDE = ["rgb", "image", "color", "distance", "depth"]
DEFAULT_EXCLUDE = ["albedo", "normal", "rough", "metal", "mask", "semantic"]


def get_filelist(cache="data/panox/PanoX_filelist.json"):
    from huggingface_hub import hf_hub_download
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    p = hf_hub_download(REPO, "PanoX_filelist.json", repo_type="dataset", local_dir=os.path.dirname(cache))
    with open(p) as f:
        return json.load(f)


def member_id(name: str):
    """4-digit instance id found as a path component or file-name prefix."""
    m = re.findall(r"(?:^|[/_\\-])(\d{4})(?=[/_.\\-])", "/" + name)
    return m[-1] if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", nargs="*", default=SCENES)
    ap.add_argument("--split", default="test", choices=["train", "val", "test", "all"])
    ap.add_argument("--out", default="data/panox")
    ap.add_argument("--include", nargs="*", default=DEFAULT_INCLUDE)
    ap.add_argument("--exclude", nargs="*", default=DEFAULT_EXCLUDE)
    ap.add_argument("--list", action="store_true", help="only print zip members (first 60) and exit")
    ap.add_argument("--full", action="store_true", help="download the whole scene zip")
    ap.add_argument("--max-per-scene", type=int, default=None)
    a = ap.parse_args()

    if a.full:
        from huggingface_hub import hf_hub_download
        for s in a.scenes:
            print("downloading", s, "(full zip)")
            hf_hub_download(REPO, f"{s}.zip", repo_type="dataset", local_dir=a.out)
        return

    from remotezip import RemoteZip
    fl = get_filelist(os.path.join(a.out, "PanoX_filelist.json"))
    for s in a.scenes:
        url = f"{BASE}/{s}.zip"
        with RemoteZip(url) as z:
            infos = [i for i in z.infolist() if not i.is_dir()]
            if a.list:
                print(f"== {s}: {len(infos)} members")
                for i in infos[:60]:
                    print(f"  {i.filename}  ({i.file_size / 2**20:.1f} MB)")
                continue
            if s in fl:
                ids = set(fl[s][a.split]) if a.split != "all" else set(sum(fl[s].values(), []))
            else:
                print(f"[{s}] not in PanoX_filelist.json -> out-of-domain scene, taking all ids")
                ids = None
            sel = []
            for i in infos:
                n = i.filename.lower()
                if not any(k in n for k in a.include) or any(k in n for k in a.exclude):
                    continue
                mid = member_id(i.filename)
                if ids is not None and mid not in ids:
                    continue
                sel.append(i)
            if a.max_per_scene:
                keep = sorted({member_id(i.filename) for i in sel})[: a.max_per_scene]
                sel = [i for i in sel if member_id(i.filename) in keep]
            gb = sum(i.file_size for i in sel) / 2**30
            print(f"[{s}] extracting {len(sel)} files ({gb:.2f} GB) -> {a.out}/{s}")
            if not sel:
                print("   nothing matched: run with --list and adjust --include/--exclude")
            for k, i in enumerate(sel):
                z.extract(i, os.path.join(a.out, s))
                if k % 50 == 0:
                    print(f"   {k}/{len(sel)}", flush=True)
    print("done. Next: python scripts/make_panox_list.py --root", a.out)


if __name__ == "__main__":
    sys.exit(main())
