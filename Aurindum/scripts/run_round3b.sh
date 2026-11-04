#!/usr/bin/env bash
# ==============================================================================
# Round 3b (PREREG_round3b.md): separate distortion from orientation, then the pre-registered uniform ensembles.
#
#   scripts/run_round3b.sh start | status | stop | run
#
# Stages (env STAGES, default "S B R"):
#   S  sweeps per model: dilation (X1), flip (X2), rotation re-run with the content split (X3) on the Structured3D
#      calibration houses, and the same three on the description sets (S3 eval, PanoX, Holo indoor / outdoor)
#   B  X4 uniform 3-pass rotation ensemble, X5 5 / 7-pass uniform rotation ensembles, X6 uniform dilation ensemble,
#      X7 curve-driven correction from the dilation curve (models with an X1 onset only); every run with its yaw control
#   R  results/ROUND3_ANALYSIS.md and results/SUMMARY_<ts>.md
# Env: MODELS (default "midas dap da360 da2"), N_CALIB (default 120), N_DESC (default 80), ESC (cap for B), SETS
#      (description sets, default "s3 panox holo_in holo_out"), CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME.
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results
STAGES="${STAGES:-S B R}"
MODELS="${MODELS:-midas dap da360 da2}"
SETS="${SETS:-s3 panox holo_in holo_out}"
N_CALIB="${N_CALIB:-120}"; N_DESC="${N_DESC:-80}"
say() { echo "[$(date +'%F %T')] $*"; }
cfg_of() {
    local m="$1" d="$2"
    if [ "$m" = dap ]; then
        case "$d" in s3) echo "config_dap.yaml";; panox) echo "config_dap_panox.yaml";; holo_in) echo "config_dap_holo360d_indoor.yaml";; holo_out) echo "config_dap_holo360d_outdoor.yaml";; esac
    else
        case "$d" in s3) echo "config.yaml";; panox) echo "config_panox.yaml";; holo_in) echo "config_holo360d_indoor.yaml";; holo_out) echo "config_holo360d_outdoor.yaml";; esac
    fi
}
model_sets() { case "$1" in da360|da2) echo "--set model.name=$1 --set method1.polar_source=rotated_erp";; *) echo "";; esac; }
data_ok() { case "$1" in s3) [ -f data/structured3d/test.txt ];; panox) [ -f data/panox/test.txt ];; holo_*) [ -f data/holo360d/test.txt ];; esac; }

do_run() {
    CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" MPLCONFIGDIR="/tmp/matplotlib_$$"
    export HF_HOME="${HF_HOME:-/DATA/Aurindum/hf_home}" HF_HUB_OFFLINE=1  # DA^2 weights from the staged offline cache
    say "🚀 Round 3b | stages: $STAGES | models: $MODELS | sets: $SETS"
    python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { say "❌ CUDA not available"; exit 1; }
    local avail=""
    for m in $MODELS; do
        case "$m" in
            midas) [ -f weights/dpt_hybrid_384.pt ] && avail="$avail midas" || say "⚠️  MiDaS weights missing: skipped";;
            dap)   { [ -f weights/dap/model.pth ] && [ -d third_party/DAP/networks ]; } && avail="$avail dap" || say "⚠️  DAP missing: skipped";;
            da360) { [ -f weights/da360/DA360_large.pth ] && [ -d third_party/DA360/networks ]; } && avail="$avail da360" || say "⚠️  DA360 missing: skipped";;
            da2)   { [ -f third_party/DA2/configs/infer.json ] && python -c "import sys; sys.path.insert(0,'third_party/DA2/src'); import da2.model.spherevit" 2>/dev/null; } \
                       && avail="$avail da2" || say "⚠️  DA^2 missing: skipped";;
        esac
    done
    run_py() { local label="$1"; shift; local t0; t0=$(date +%s); say ">>> $label"
        if python "$@"; then say "✅ $label ($(( $(date +%s) - t0 )) s)"; else say "❌ $label FAILED"; fi; }
    bench() { local label="$1"; shift; local t0; t0=$(date +%s); say ">>> $label"
        if (cd 3_structured3d_benchmark && python run.py "$@"); then say "✅ $label ($(( $(date +%s) - t0 )) s)"; else say "❌ $label FAILED"; fi; }

    for ST in $STAGES; do
        case "$ST" in
        S)  say "=============== S: dilation (X1), flip (X2), rotation + content split (X3) sweeps ==============="
            for m in $avail; do
                for mode in dilation flip rotation; do
                    c="3_structured3d_benchmark/$(cfg_of $m s3)"
                    run_py "S $mode $m s3 calib" scripts/distortion_sweep.py --config "$c" --mode $mode --tag "${mode}_${m}_s3_calib" \
                        --split calib --max_scenes "$N_CALIB" $(model_sets $m)
                    for d in $SETS; do
                        data_ok $d || continue
                        sp=all; [ "$d" = s3 ] && sp=eval
                        run_py "S $mode $m $d" scripts/distortion_sweep.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --mode $mode \
                            --tag "${mode}_${m}_${d}_${sp}" --split $sp --max_scenes "$N_DESC" $(model_sets $m)
                    done
                done
            done ;;
        B)  say "=============== B: pre-registered ensembles X4-X7 ==============="
            local es=""; [ -n "${ESC:-}" ] && es="--max_scenes $ESC --set data.subset=spread"
            uni="--set mobius_tta.weight_power=0 --set mobius_tta.min_weight=1.0 --set mobius_tta.gate_lat=null"
            for m in $avail; do for d in s3 panox holo_in holo_out; do
                data_ok $d || continue
                sp=all; [ "$d" = s3 ] && sp=eval
                c="$(cfg_of $m $d)"; base="--set data.split=$sp $(model_sets $m) $es $uni"
                both="--set evaluation.methods=[Method2_MobiusTTA,Control_YawEnsemble]"
                bench "X4 uniform 3-pass $m $d" --config "$c" --tag "x4_$m" $base --set mobius_tta.preset=rotation_only $both
                bench "X5 uniform 5-pass $m $d" --config "$c" --tag "x5p5_$m" $base \
                    --set "mobius_tta.passes=[{pitch: 45, scale: 1.0}, {pitch: -45, scale: 1.0}, {pitch: 90, scale: 1.0}, {pitch: -90, scale: 1.0}]" $both
                bench "X5 uniform 7-pass $m $d" --config "$c" --tag "x5p7_$m" $base \
                    --set "mobius_tta.passes=[{pitch: 30, scale: 1.0}, {pitch: -30, scale: 1.0}, {pitch: 60, scale: 1.0}, {pitch: -60, scale: 1.0}, {pitch: 90, scale: 1.0}, {pitch: -90, scale: 1.0}]" $both
                bench "X6 uniform dilation $m $d" --config "$c" --tag "x6_$m" $base \
                    --set "mobius_tta.passes=[{pitch: 0, scale: 0.5}, {pitch: 0, scale: 2.0}]" $both
                curve="results/sweep_dilation_${m}_s3_calib.json"
                rot="results/sweep_rotation_${m}_s3_calib.json"
                # PREREG: a distortion effect needs an onset in BOTH the dilation sweep and the non-planar rotation sweep
                if [ -f "$curve" ] && [ -f "$rot" ] && python -c "import json,sys; d=json.load(open('$curve'))['summary']; r=json.load(open('$rot'))['summary']; sys.exit(0 if d['onset_global'] is not None and r.get('onset_nonplanar') is not None else 1)"; then
                    bench "X7 dilation-curve correction $m $d" --config "$c" --tag "x7_$m" --set data.split=$sp $(model_sets $m) $es \
                        --set distortion_curve=$curve --set mobius_tta.preset=rotation_only --set mobius_tta.curve_gate=true \
                        --set mobius_tta.curve_weights=true --set method1.curve_gate=true \
                        --set "evaluation.methods=[Tangent_Spatial,Method1_GradientFusion,Method2_MobiusTTA,Control_YawEnsemble]"
                else say "X7 skipped for $m $d: no onset in both the dilation and the non-planar rotation sweep (PREREG)"; fi
            done; done ;;
        R)  say "=============== R: reports ==============="
            run_py "R Part A table" scripts/round3_report.py
            run_py "R summary" scripts/collect_results.py ;;
        *)  say "unknown stage $ST" ;;
        esac
    done
    say "🎉 Round 3b finished."
}

pids() { pgrep -f "$AUR/scripts/run_round3b.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    run) do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running (PID(s): $(pids | tr '\n' ' '))"; exit 1; }
        LOG="$AUR/logs/round3b_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_round3b.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG   (status: scripts/run_round3b.sh status)" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING (PID(s): $(pids | tr '\n' ' '))" || say "Not running."
        L="$(ls -t logs/round3b_*.log 2>/dev/null | head -1)"
        if [ -n "$L" ]; then say "Log: $L"; grep -E "S:|B:|R:|✅|❌|⚠️|🎉|skipped" "$L" | sed 's/^/    /'; echo "    --- last lines ---"; tail -3 "$L" | sed 's/^/    /'; fi ;;
    stop)
        P="$(pids)"; [ -z "$P" ] && { say "Not running."; exit 0; }
        for p in $P; do kill -TERM -- "-$p" 2>/dev/null || { pkill -TERM -P "$p" 2>/dev/null; kill -TERM "$p" 2>/dev/null; }; done
        say "Stopped." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
