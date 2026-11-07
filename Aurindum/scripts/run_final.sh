#!/usr/bin/env bash
# ==============================================================================
# Final experiments: larger samples, the median-alignment protocol for DA2, and an input-resolution control.
#
#   scripts/run_final.sh start | status | stop | run
#
# Stages (env STAGES, default "full_ext median hires core_more summary"); existing results with enough frames are skipped,
# FORCE=1 reruns:
#   full_ext   correction on ALL frames of the external sets (Stanford2D3D, NYC) for every model. Replaces the 40-frame files.
#   median     DA2 scored with a median scale fit (PANO_ALIGN_MODE=median): capture-fault study on the four core sets
#              (tags da2m_<set>), then the held-out correction on all six sets with a policy learned under that protocol.
#   hires      MiDaS / DA360 / DA2 at 512x1024 (DAP's input size) on the external sets, tags <model>_hr_<set>: does the
#              weaker cap detection on blocked bottom + JPEG at 256x512 come from the resolution?
#   core_more  correction on N_CORE (default 100) frames of the four core sets, replacing the 40-frame files.
#   summary    results/FINAL_ablations.md (scripts/final_summary.py), then external_report.py and make_figures.py
# Env: MODELS (default "midas dap da360 da2"), N_STANFORD (373), N_NYC (147), N_HR (100), N_CORE (100), N_MEDIAN (40),
#      CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME. Nothing is committed.
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results
MODELS="${MODELS:-midas dap da360 da2}"
STAGES="${STAGES:-full_ext median hires core_more summary}"
N_STANFORD="${N_STANFORD:-373}"; N_NYC="${N_NYC:-147}"; N_HR="${N_HR:-100}"; N_CORE="${N_CORE:-100}"; N_MEDIAN="${N_MEDIAN:-40}"
CORE="s3 panox holo_in holo_out"
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
    stanford) [ -f data/stanford2d3d/test.txt ];; nyc) [ -f data/nyc_dap/test.txt ];; esac; }
out_dir() { case "$1" in stanford|nyc) echo results/external;; *) echo results;; esac; }
split_of() { [ "$1" = s3 ] && echo eval || echo all; }
# have_rows FILE MIN: the JSON has at least MIN frames (and before / after images, i.e. it came from this version)
have_rows() { [ "${FORCE:-0}" != 1 ] && [ -f "$1" ] && python - "$1" "$2" <<'PY'
import json, sys
j = json.load(open(sys.argv[1]))
sys.exit(0 if len(j["rows"]) >= int(sys.argv[2]) and j.get("examples") else 1)
PY
}
run_corr() {  # run_corr MODEL DATASET TAG N [extra args...]
    local m="$1" d="$2" tag="$3" n="$4"; shift 4
    local t0; t0=$(date +%s); say ">>> correction $tag (N=$n)"
    if python scripts/run_correction.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --tag "$tag" --split "$(split_of $d)" \
        --max_scenes "$n" --model_key "$KEY" --dataset_key "$d" $(model_sets $m) "$@"; then say "✅ $tag ($(( $(date +%s) - t0 )) s)"; else say "❌ $tag FAILED"; fi
}

do_run() {
    CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" MPLCONFIGDIR="/tmp/matplotlib_$$"
    export HF_HOME="${HF_HOME:-/DATA/Aurindum/hf_home}" HF_HUB_OFFLINE=1
    say "🚀 Final experiments | stages: $STAGES | models: $MODELS"
    for ST in $STAGES; do
        case "$ST" in
        full_ext)
            say "=============== full_ext ==============="
            for m in $MODELS; do for d in stanford nyc; do
                data_ok $d || { say "skip $d: no list"; continue; }
                n=$N_STANFORD; [ $d = nyc ] && n=$N_NYC
                have_rows "results/external/correction_${m}_${d}.json" "$(python -c "print(min($n, sum(1 for l in open('$( [ $d = nyc ] && echo data/nyc_dap/test.txt || echo data/stanford2d3d/test.txt)') if l.strip())))")" && { say "have $m $d"; continue; }
                KEY=$m; run_corr $m $d "${m}_${d}" $n
            done; done ;;
        median)
            say "=============== median (DA2, PANO_ALIGN_MODE=median) ==============="
            export PANO_ALIGN_MODE=median
            for d in $CORE; do
                data_ok $d || continue
                [ -f "results/study_da2m_${d}.json" ] && [ "${FORCE:-0}" != 1 ] && { say "have study da2m $d"; continue; }
                t0=$(date +%s); say ">>> study da2m $d"
                if python scripts/distortion_study.py --config "3_structured3d_benchmark/$(cfg_of da2 $d)" --tag "da2m_${d}" --split "$(split_of $d)" \
                    --max_scenes "$N_MEDIAN" --examples 3 --set model.name=da2; then say "✅ study da2m $d ($(( $(date +%s) - t0 )) s)"; else say "❌ study da2m $d FAILED"; fi
            done
            for d in $CORE stanford nyc; do
                data_ok $d || continue
                out=$(out_dir $d)
                have_rows "$out/correction_da2m_${d}.json" "$N_MEDIAN" && { say "have correction da2m $d"; continue; }
                n=$N_MEDIAN; [ $d = stanford ] && n=$N_STANFORD; [ $d = nyc ] && n=$N_NYC
                KEY=da2m; run_corr da2 $d "da2m_${d}" $n
            done
            unset PANO_ALIGN_MODE ;;
        hires)
            say "=============== hires (512x1024 input for the 256x512 models) ==============="
            for m in midas da360 da2; do case " $MODELS " in *" $m "*) ;; *) continue;; esac
                for d in nyc stanford; do
                    data_ok $d || continue
                    have_rows "results/external/correction_${m}_hr_${d}.json" "$N_HR" && { say "have $m hr $d"; continue; }
                    KEY=$m; run_corr $m $d "${m}_hr_${d}" $N_HR --set data.height=512 --set data.width=1024
                done; done ;;
        core_more)
            say "=============== core_more (N=$N_CORE) ==============="
            for m in $MODELS; do for d in $CORE; do
                data_ok $d || continue
                [ -f "results/study_${m}_${d}.json" ] || { say "skip $m $d: no study"; continue; }
                have_rows "results/correction_${m}_${d}.json" "$N_CORE" && { say "have $m $d"; continue; }
                KEY=$m; run_corr $m $d "${m}_${d}" $N_CORE
            done; done ;;
        summary)
            say "=============== summary ==============="
            python scripts/final_summary.py > /dev/null && say "✅ results/FINAL_ablations.md" || say "❌ summary FAILED"
            python scripts/external_report.py > /dev/null && say "✅ external report" || say "❌ external report FAILED"
            python scripts/make_figures.py && say "✅ figures" || say "❌ figures FAILED" ;;
        esac
    done
    say "🎉 Final experiments finished. Commit results/."
}
pids() { pgrep -f "$AUR/scripts/run_final.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    run) do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running"; exit 1; }
        LOG="$AUR/logs/final_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_final.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING" || say "Not running."
        L="$(ls -t logs/final_*.log 2>/dev/null | head -1)"; [ -n "$L" ] && { grep -E "✅|❌|🎉|=====" "$L" | tail -30 | sed 's/^/    /'; tail -2 "$L" | sed 's/^/    /'; } ;;
    stop)
        for p in $(pids); do kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p"; done
        pkill -f "scripts/run_correction.py" 2>/dev/null; pkill -f "scripts/distortion_study.py" 2>/dev/null
        say "Stopped." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
