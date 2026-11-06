#!/usr/bin/env bash
# Exploratory distortion study (distortions/catalogue.py, scripts/distortion_study.py) for every model x dataset.
#   scripts/run_distortion_study.sh start | status | stop | run
# Env: MODELS (default "midas dap da360 da2"), SETS (default "s3 panox holo_in holo_out"; optional stanford, nyc), N (frames, default 40),
#      ONLY (comma list of distortion keys), TAG_PREFIX (prepended to every output name, e.g. smoke_), CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME.
# Writes results/STUDY_<model>_<set>.md, study_<model>_<set>.json and example images in study_<model>_<set>_img/.
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results
MODELS="${MODELS:-midas dap da360 da2}"
SETS="${SETS:-s3 panox holo_in holo_out}"   # opt-in: add stanford / nyc (scripts/download_extra_datasets.sh)
N="${N:-40}"
say() { echo "[$(date +'%F %T')] $*"; }
cfg_of() {
    local m="$1" d="$2"
    if [ "$m" = dap ]; then
        case "$d" in s3) echo "config_dap.yaml";; panox) echo "config_dap_panox.yaml";; holo_in) echo "config_dap_holo360d_indoor.yaml";; holo_out) echo "config_dap_holo360d_outdoor.yaml";; stanford) echo "config_dap_stanford2d3d.yaml";; nyc) echo "config_dap_nyc.yaml";; esac
    else
        case "$d" in s3) echo "config.yaml";; panox) echo "config_panox.yaml";; holo_in) echo "config_holo360d_indoor.yaml";; holo_out) echo "config_holo360d_outdoor.yaml";; stanford) echo "config_stanford2d3d.yaml";; nyc) echo "config_nyc.yaml";; esac
    fi
}
model_sets() { case "$1" in da360|da2) echo "--set model.name=$1";; *) echo "";; esac; }
data_ok() { case "$1" in s3) [ -f data/structured3d/test.txt ];; panox) [ -f data/panox/test.txt ];; holo_*) [ -f data/holo360d/test.txt ];;
    stanford) [ -f data/stanford2d3d/test.txt ] || { say "skip stanford: build data/stanford2d3d/test.txt (scripts/make_stanford_list.py --out test.txt)"; false; };;
    nyc) [ -f data/nyc_dap/test.txt ] || { say "skip nyc: build data/nyc_dap/test.txt (scripts/make_nyc_list.py, or scripts/run_tasks.sh setup with NYC_RGB / NYC_DEPTH)"; false; };; esac; }
do_run() {
    CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" MPLCONFIGDIR="/tmp/matplotlib_$$"
    export HF_HOME="${HF_HOME:-/DATA/Aurindum/hf_home}" HF_HUB_OFFLINE=1
    say "🚀 Distortion study | models: $MODELS | sets: $SETS | N=$N"
    local only=""; [ -n "${ONLY:-}" ] && only="--only $ONLY"
    for m in $MODELS; do for d in $SETS; do
        data_ok $d || continue
        sp=all; [ "$d" = s3 ] && sp=eval   # S3 calibration houses stay untouched
        local t0; t0=$(date +%s); say ">>> $m $d"
        if python scripts/distortion_study.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --tag "${TAG_PREFIX:-}${m}_${d}" --split $sp \
            --max_scenes "$N" --examples 3 $only $(model_sets $m); then say "✅ $m $d ($(( $(date +%s) - t0 )) s)"; else say "❌ $m $d FAILED"; fi
    done; done
    say "🎉 Distortion study finished."
}
pids() { pgrep -f "$AUR/scripts/run_distortion_study.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    run) do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running"; exit 1; }
        LOG="$AUR/logs/distortion_study_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_distortion_study.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING" || say "Not running."
        L="$(ls -t logs/distortion_study_*.log 2>/dev/null | head -1)"; [ -n "$L" ] && { grep -E "✅|❌|🎉" "$L" | sed 's/^/    /'; tail -2 "$L" | sed 's/^/    /'; } ;;
    stop)
        for p in $(pids); do kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p"; done; say "Stopped." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
