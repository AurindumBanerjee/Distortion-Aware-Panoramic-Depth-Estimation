#!/usr/bin/env bash
# Capture-aware correction (distortions/correction.py): learn the policy from the study results, then test it end to end,
# held out per dataset (scripts/calibrate_correction.py, scripts/run_correction.py). Needs results/study_<model>_<set>.json.
#   scripts/run_correction.sh start | status | stop | run
# Env: MODELS (default "midas dap da360 da2"), SETS (default "s3 panox holo_in holo_out"), N (frames, default 40),
#      TAG_PREFIX (e.g. smoke_), CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME.
# Writes results/correction_policy.json, CORRECTION_POLICY.md, CORRECTION_<model>_<set>.md, correction_<model>_<set>.json.
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
    say "🚀 Capture-aware correction | models: $MODELS | sets: $SETS | N=$N"
    if python scripts/calibrate_correction.py > /dev/null; then say "✅ policy -> results/CORRECTION_POLICY.md"; else say "❌ calibration FAILED"; exit 1; fi
    for m in $MODELS; do for d in $SETS; do
        data_ok $d || continue
        [ -f "results/study_${m}_${d}.json" ] || { say "skip $m $d: no results/study_${m}_${d}.json"; continue; }
        sp=all; [ "$d" = s3 ] && sp=eval   # same frames as the study; the policy never saw this dataset
        local t0; t0=$(date +%s); say ">>> $m $d"
        if python scripts/run_correction.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --tag "${TAG_PREFIX:-}${m}_${d}" --split $sp \
            --max_scenes "$N" --model_key $m --dataset_key $d $(model_sets $m); then say "✅ $m $d ($(( $(date +%s) - t0 )) s)"; else say "❌ $m $d FAILED"; fi
    done; done
    say "🎉 Correction runs finished."
}
pids() { pgrep -f "$AUR/scripts/run_correction.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    run) do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running"; exit 1; }
        LOG="$AUR/logs/correction_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_correction.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING" || say "Not running."
        L="$(ls -t logs/correction_*.log 2>/dev/null | head -1)"; [ -n "$L" ] && { grep -E "✅|❌|🎉" "$L" | sed 's/^/    /'; tail -2 "$L" | sed 's/^/    /'; } ;;
    stop)
        for p in $(pids); do kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p"; done; say "Stopped." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
