#!/usr/bin/env bash
# ==============================================================================
# One full, self-consistent pass over every model x dataset, with all results, comparison images and plots.
#
#   scripts/run_holistic.sh start | status | stop | run
#
# Stages (env STAGES, default "study sweeps correct report"):
#   study    capture-fault study (scripts/distortion_study.py): clean vs degraded vs every fix, example images saved
#   sweeps   rotation / dilation / flip latitude sweeps on the EXTERNAL sets (the core sets have theirs from round 3b;
#            FORCE_CORE_SWEEPS=1 reruns them). Stanford is skipped (its real black caps rotate into the content and
#            confound the sweep) unless SWEEP_STANFORD=1
#   correct  learn the policy on the four core sets, then test the whole correction pipeline per model x dataset, with
#            before / after images. Stanford / NYC are external: never used to choose a fix, written to results/external/
#   report   results/EXTERNAL_stanford_nyc.md and every figure (results/figures/: heatmaps, sweep curves, image montages)
# Env: MODELS (default "midas dap da360 da2"), SETS (default "s3 panox holo_in holo_out stanford nyc"), N (frames, 40),
#      N_SWEEP (80), CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME. Datasets without a list file are skipped with a message.
# Nothing is committed: commit results/ yourself when it finishes.
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results
export MODELS="${MODELS:-midas dap da360 da2}"
export SETS="${SETS:-s3 panox holo_in holo_out stanford nyc}"
export N="${N:-40}"
STAGES="${STAGES:-study sweeps correct report}"
N_SWEEP="${N_SWEEP:-80}"
say() { echo "[$(date +'%F %T')] $*"; }
cfg_of() {
    local m="$1" d="$2"
    if [ "$m" = dap ]; then
        case "$d" in s3) echo "config_dap.yaml";; panox) echo "config_dap_panox.yaml";; holo_in) echo "config_dap_holo360d_indoor.yaml";; holo_out) echo "config_dap_holo360d_outdoor.yaml";; stanford) echo "config_dap_stanford2d3d.yaml";; nyc) echo "config_dap_nyc.yaml";; esac
    else
        case "$d" in s3) echo "config.yaml";; panox) echo "config_panox.yaml";; holo_in) echo "config_holo360d_indoor.yaml";; holo_out) echo "config_holo360d_outdoor.yaml";; stanford) echo "config_stanford2d3d.yaml";; nyc) echo "config_nyc.yaml";; esac
    fi
}
sweep_sets() { case "$1" in da360|da2) echo "--set model.name=$1 --set method1.polar_source=rotated_erp";; *) echo "";; esac; }
data_ok() { case "$1" in s3) [ -f data/structured3d/test.txt ];; panox) [ -f data/panox/test.txt ];; holo_*) [ -f data/holo360d/test.txt ];;
    stanford) [ -f data/stanford2d3d/test.txt ];; nyc) [ -f data/nyc_dap/test.txt ];; esac; }

do_run() {
    CONDA_SH="${CONDA_SH:-$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" MPLCONFIGDIR="/tmp/matplotlib_$$"
    export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}" HF_HUB_OFFLINE=1
    say "🚀 Holistic run | stages: $STAGES | models: $MODELS | sets: $SETS | N=$N"
    for d in $SETS; do data_ok $d || say "⚠️  $d: no list file, skipped everywhere"; done
    for ST in $STAGES; do
        case "$ST" in
        study)   say "=============== study (pairs that already have results are skipped; FORCE=1 reruns) ==============="
                 for m in $MODELS; do for d in $SETS; do
                     data_ok $d || continue
                     [ -f "results/study_${m}_${d}.json" ] && [ "${FORCE:-0}" != 1 ] && { say "have study $m $d"; continue; }
                     MODELS=$m SETS=$d bash scripts/run_distortion_study.sh run
                 done; done ;;
        sweeps)  say "=============== sweeps on the external sets ==============="
                 for m in $MODELS; do for d in $SETS; do
                     data_ok $d || continue
                     case "$d" in
                         stanford) [ "${SWEEP_STANFORD:-0}" = 1 ] || { say "skip sweeps stanford (real black caps confound them; SWEEP_STANFORD=1 to force)"; continue; };;
                         nyc) ;;
                         *) [ "${FORCE_CORE_SWEEPS:-0}" = 1 ] || continue;;
                     esac
                     sp=all; [ "$d" = s3 ] && sp=eval
                     for mode in rotation dilation flip; do
                         tag="${mode}_${m}_${d}_${sp}"
                         [ -f "results/sweep_${tag}.json" ] && [ "${FORCE:-0}" != 1 ] && { say "have $tag"; continue; }
                         t0=$(date +%s); say ">>> sweep $tag"
                         if python scripts/distortion_sweep.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --mode $mode --tag "$tag" \
                             --split $sp --max_scenes "$N_SWEEP" $(sweep_sets $m); then say "✅ sweep $tag ($(( $(date +%s) - t0 )) s)"; else say "❌ sweep $tag FAILED"; fi
                     done
                 done; done ;;
        correct) say "=============== correction (a result is kept only if it has before / after images, i.e. came from this version) ==============="
                 for m in $MODELS; do for d in $SETS; do
                     data_ok $d || continue
                     out=results; case "$d" in stanford|nyc) out=results/external;; esac
                     [ -f "$out/correction_${m}_${d}.json" ] && grep -q '"examples": {"' "$out/correction_${m}_${d}.json" && [ "${FORCE:-0}" != 1 ] && { say "have correction $m $d"; continue; }
                     MODELS=$m SETS=$d bash scripts/run_correction.sh run
                 done; done ;;
        report)  say "=============== report and figures ==============="
                 python scripts/external_report.py > /dev/null && say "✅ results/EXTERNAL_stanford_nyc.md" || say "❌ external report FAILED"
                 python scripts/make_figures.py && say "✅ results/figures/INDEX.md" || say "❌ figures FAILED" ;;
        esac
    done
    say "🎉 Holistic run finished. Commit results/ (figures included)."
}
pids() { pgrep -f "$AUR/scripts/run_holistic.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    run) do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running"; exit 1; }
        LOG="$AUR/logs/holistic_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_holistic.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING" || say "Not running."
        L="$(ls -t logs/holistic_*.log 2>/dev/null | head -1)"; [ -n "$L" ] && { grep -E "✅|❌|🎉|=====" "$L" | tail -30 | sed 's/^/    /'; tail -2 "$L" | sed 's/^/    /'; } ;;
    stop)
        for p in $(pids); do kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p"; done
        pkill -f "$AUR/scripts/run_distortion_study.sh run" 2>/dev/null; pkill -f "$AUR/scripts/run_correction.sh run" 2>/dev/null
        say "Stopped." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
