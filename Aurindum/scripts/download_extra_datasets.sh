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

# Resumable download that survives network drops: retries with growing waits, continues where it stopped, and
# stops early only when the file is complete. Returns 1 after MAX_TRIES failures in a row without progress.
fetch_resume() {
    local url="$1" dst="$2" tries=0 last=-1 size
    while :; do
        if curl -fL --retry 5 --retry-all-errors --retry-delay 5 --connect-timeout 30 --speed-limit 100000 --speed-time 120 -C - -o "$dst" "$url"; then return 0; fi
        size=$(stat -c %s "$dst" 2>/dev/null || echo 0)
        if [ "$size" -gt "$last" ]; then tries=0; else tries=$((tries + 1)); fi   # progress resets the counter
        last=$size
        [ "$tries" -ge "${MAX_TRIES:-8}" ] && return 1
        local w=$(( 10 * (tries + 1) )); [ "$w" -gt 120 ] && w=120
        say "download interrupted at $((size / 1048576)) MB; resuming in ${w}s (failed attempts without progress: $tries)"; sleep "$w"
    done
}

stanford() {
    local out="$DATA/stanford2d3d"; mkdir -p "$out"
    for area in area_5a area_5b; do
        if [ -d "$out/$area/pano/rgb" ] && [ -n "$(ls -A "$out/$area/pano/rgb" 2>/dev/null)" ]            && [ "$(ls "$out/$area/pano/rgb" | wc -l)" = "$(ls "$out/$area/pano/depth" 2>/dev/null | wc -l)" ]; then say "$area already there"; continue; fi
        local tar="$out/${area}_no_xyz.tar" url="https://cvg-data.inf.ethz.ch/2d3ds/no_xyz/${area}_no_xyz.tar" try ok=0
        for try in 1 2 3; do
            fetch_resume "$url" "$tar" || { say "❌ $area download kept failing"; break; }
            say "extracting panorama RGB + depth of $area (attempt $try)"
            if tar -xf "$tar" -C "$out" --wildcards "*/pano/rgb/*" "*/pano/depth/*"; then ok=1; break; fi
            say "archive looks corrupt: deleting it and downloading again"; rm -f "$tar"
        done
        [ "$ok" = 1 ] || { say "❌ $area failed; rerun this script to resume"; continue; }
        [ "${KEEP_TAR:-0}" = 1 ] || rm -f "$tar"
    done
    python scripts/make_stanford_list.py --root "$out" --areas area_5a area_5b --out test.txt
}

nyc() {
    local out="$DATA/nyc_dap"; mkdir -p "$out"
    python -m pip show huggingface_hub >/dev/null 2>&1 || python -m pip install -q huggingface_hub
    # retries network errors, skips blobs the hub no longer serves (using a neighbouring id), validates every file
    HF_HUB_DISABLE_SYMLINKS_WARNING=1 python scripts/hf_fetch_retry.py --out "$out" --step "${NYC_STEP:-5}" --max_id "${NYC_MAX_ID:-1907}"
    python scripts/make_nyc_list.py --root "$out"
}

case "${1:-both}" in
    stanford) stanford ;;
    nyc) nyc ;;
    both) stanford; nyc ;;
    *) echo "usage: $0 {stanford|nyc|both}"; exit 2 ;;
esac
say "done. On the server: bash scripts/run_tasks.sh setup   (lists are already built; no STANFORD_ROOT / NYC_* needed if data/ is copied as is)"
