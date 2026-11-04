#!/usr/bin/env bash
# Download the two extra real datasets for the distortion study. Needs internet (run it on a machine that has it,
# e.g. the laptop, and copy data/ to the server if the server is offline).
#
#   bash scripts/download_extra_datasets.sh stanford     # Stanford2D3D area 5a + 5b, panorama RGB + depth only
#   bash scripts/download_extra_datasets.sh nyc          # DAP NYC street panoramas, every NYC_STEP-th frame
#   bash scripts/download_extra_datasets.sh both
#
# Sources
#   Stanford2D3D: ETH Zurich mirror used by NVIDIA torch-harmonics, https://cvg-data.inf.ethz.ch/2d3ds/no_xyz/
#                 (official access: form on the 2D-3D-S page; the mirror serves the same 'no_xyz' archives)
#   NYC:          Hugging Face dataset Coaa1/DAP_data, folders nyc_raw_images_panorama (PNG, ~3 MB each) and
#                 nyc_distance_panorama_npy (float64 range in metres, 16.8 MB each; 32 GB for all of them)
# Env: DATA (default data), NYC_STEP (default 5 -> ~380 frames, ~7.6 GB), NYC_MAX_ID (default 1907),
#      KEEP_TAR=1 keeps the Stanford archives.
set -euo pipefail
cd "$(dirname "$0")/.."
DATA="${DATA:-data}"
say() { echo "[$(date +'%F %T')] $*"; }

stanford() {
    local out="$DATA/stanford2d3d"; mkdir -p "$out"
    for area in area_5a area_5b; do
        if [ -d "$out/$area/pano/rgb" ] && [ -n "$(ls -A "$out/$area/pano/rgb" 2>/dev/null)" ]; then say "$area already there"; continue; fi
        local tar="$out/${area}_no_xyz.tar"
        say "downloading $area (resumable; several GB)"
        curl -fL --retry 5 -C - -o "$tar" "https://cvg-data.inf.ethz.ch/2d3ds/no_xyz/${area}_no_xyz.tar"
        say "extracting panorama RGB + depth of $area"
        tar -xf "$tar" -C "$out" --wildcards "*/pano/rgb/*" "*/pano/depth/*"
        [ "${KEEP_TAR:-0}" = 1 ] || rm -f "$tar"
    done
    python scripts/make_stanford_list.py --root "$out" --areas area_5a area_5b --out test.txt
}

nyc() {
    local out="$DATA/nyc_dap"; mkdir -p "$out"
    python -m pip show huggingface_hub >/dev/null 2>&1 || python -m pip install -q huggingface_hub
    python - "$out" "${NYC_STEP:-5}" "${NYC_MAX_ID:-1907}" <<'PY'
import os, shutil, sys
from huggingface_hub import hf_hub_download
out, step, max_id = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
os.makedirs(f"{out}/rgb", exist_ok=True); os.makedirs(f"{out}/depth", exist_ok=True)
ok = miss = 0
for n in range(0, max_id + 1, step):
    pairs = ((f"nyc_raw_images_panorama/panorama_{n}.png", f"{out}/rgb/panorama_{n}.png"),
             (f"nyc_distance_panorama_npy/erp_distance_{n}.npy", f"{out}/depth/erp_distance_{n}.npy"))
    try:
        for src, dst in pairs:
            if not os.path.exists(dst):
                # download straight into a staging folder (no second copy in the HF cache), then move into place
                p = hf_hub_download("Coaa1/DAP_data", src, repo_type="dataset", local_dir=f"{out}/_hf")
                shutil.move(p, dst)
        ok += 1
    except Exception as e:  # an id may not exist; skip it
        miss += 1
        print(f"skip {n}: {type(e).__name__}")
    if ok % 25 == 0 and ok:
        print(f"{ok} pairs", flush=True)
shutil.rmtree(f"{out}/_hf", ignore_errors=True)
print(f"done: {ok} pairs, {miss} skipped")
PY
    python scripts/make_nyc_list.py --root "$out"
}

case "${1:-both}" in
    stanford) stanford ;;
    nyc) nyc ;;
    both) stanford; nyc ;;
    *) echo "usage: $0 {stanford|nyc|both}"; exit 2 ;;
esac
say "done. On the server: bash scripts/run_tasks.sh setup   (lists are already built; no STANFORD_ROOT / NYC_* needed if data/ is copied as is)"
