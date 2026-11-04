#!/usr/bin/env bash
# ==============================================================================
# Round 3 (CHECKLIST.md): measure the distortion effect per model, then correct only where it was measured.
#
#   scripts/run_round3.sh start | status | stop | run
#
# Stages (env STAGES, default "A1 A2 B D"; a failing step never blocks the next):
#   A1  calibration: distortion sweep + latitude profile per model on the Structured3D CALIBRATION houses
#       -> results/sweep_<model>_s3_calib.json (the curve Part B uses) and profile_<model>_s3_calib.json
#   A2  description: sweep + profile per model on the evaluation data of every dataset (S3 eval houses, PanoX,
#       Holo360D indoor / outdoor). Reported in the write-up; nothing is fitted on it.
#   B   correction on the evaluation data, every model x dataset, curve from A1 (model property, measured once):
#         r3        Tangent_Spatial + Method 1 (ramp from the onset) + rotation-only M2 (onset gate, 1/ratio^2
#                   weights) + compute-matched yaw control
#         r3wonly   M2 with curve weights but no gate          r3gonly   M2 with the gate but cos^2 weights
#       A model whose curve has no onset gets its baseline back (do-no-harm; checked by tests).
#   D   results/ROUND3_ANALYSIS.md (Part A table) and results/SUMMARY_<ts>.md (Part B, cluster-robust)
#
# Env: MODELS (default "midas dap da360 da2"), N_CALIB (frames for A1, default 120), N_DESC (A2, default 80),
#      ESC (cap for B, default all), CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES.
# Models: midas = config*.yaml, dap = config_dap*.yaml, da360 / da2 = MiDaS configs with model.name overridden
#         (need third_party/DA360 + weights/da360/DA360_large.pth, third_party/DA2 + `pip install -e third_party/DA2/src`).
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results
STAGES="${STAGES:-A1 A2 B D}"
MODELS="${MODELS:-midas dap da360 da2}"
N_CALIB="${N_CALIB:-120}"; N_DESC="${N_DESC:-80}"
say() { echo "[$(date +'%F %T')] $*"; }

# config for <model> <dataset: s3|panox|holo_in|holo_out>, plus model-specific overrides
cfg_of() {
    local m="$1" d="$2" base
    case "$d" in s3) base="config";; panox) base="config_panox";; holo_in) base="config_holo360d_indoor";; holo_out) base="config_holo360d_outdoor";; esac
    if [ "$m" = dap ]; then
        case "$d" in s3) echo "config_dap.yaml";; panox) echo "config_dap_panox.yaml";; holo_in) echo "config_dap_holo360d_indoor.yaml";; holo_out) echo "config_dap_holo360d_outdoor.yaml";; esac
    else echo "$base.yaml"; fi
}
model_sets() {  # extra --set flags per model (ERP-only models need rotated-ERP polar views)
    case "$1" in
        da360|da2) echo "--set model.name=$1 --set method1.polar_source=rotated_erp";;
        *) echo "";;
    esac
}
data_ok() { case "$1" in s3) [ -f data/structured3d/test.txt ];; panox) [ -f data/panox/test.txt ];; holo_*) [ -f data/holo360d/test.txt ];; esac; }

do_run() {
    CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" MPLCONFIGDIR="/tmp/matplotlib_$$"
    # DA^2 loads its weights through the Hugging Face cache; the server is offline, so use the staged local copy.
    export HF_HOME="${HF_HOME:-/DATA/Aurindum/hf_home}" HF_HUB_OFFLINE=1
    say "🚀 Round 3 | stages: $STAGES | models: $MODELS"
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
        A1) say "=============== A1: calibration curves (Structured3D calibration houses) ==============="
            for m in $avail; do
                c="3_structured3d_benchmark/$(cfg_of $m s3)"
                run_py "A1 sweep $m" scripts/distortion_sweep.py --config "$c" --tag "${m}_s3_calib" --split calib --max_scenes "$N_CALIB" $(model_sets $m)
                run_py "A1 profile $m" scripts/latitude_profile.py --config "$c" --tag "${m}_s3_calib" --split calib --max_scenes "$N_CALIB" $(model_sets $m)
            done ;;
        A2) say "=============== A2: description on the evaluation data ==============="
            for m in $avail; do for d in s3 panox holo_in holo_out; do
                data_ok $d || continue
                c="3_structured3d_benchmark/$(cfg_of $m $d)"; sp=all; [ "$d" = s3 ] && sp=eval
                run_py "A2 sweep $m $d" scripts/distortion_sweep.py --config "$c" --tag "${m}_${d}_${sp}" --split $sp --max_scenes "$N_DESC" $(model_sets $m)
                run_py "A2 profile $m $d" scripts/latitude_profile.py --config "$c" --tag "${m}_${d}_${sp}" --split $sp --max_scenes "$N_DESC" $(model_sets $m)
            done; done ;;
        B)  say "=============== B: curve-driven correction on the evaluation data ==============="
            local es=""; [ -n "${ESC:-}" ] && es="--max_scenes $ESC --set data.subset=spread"
            for m in $avail; do
                curve="results/sweep_${m}_s3_calib.json"
                [ -f "$curve" ] || { say "❌ no calibration curve $curve (run A1): $m skipped"; continue; }
                for d in s3 panox holo_in holo_out; do
                    data_ok $d || continue
                    sp=all; [ "$d" = s3 ] && sp=eval
                    common="--set distortion_curve=$curve --set data.split=$sp --set mobius_tta.preset=rotation_only $(model_sets $m) $es"
                    bench "B r3 $m $d" --config "$(cfg_of $m $d)" --tag "r3_$m" $common \
                        --set mobius_tta.curve_gate=true --set mobius_tta.curve_weights=true --set method1.curve_gate=true \
                        --set "evaluation.methods=[Tangent_Spatial,Method1_GradientFusion,Method2_MobiusTTA,Control_YawEnsemble]"
                    bench "B r3wonly $m $d" --config "$(cfg_of $m $d)" --tag "r3wonly_$m" $common \
                        --set mobius_tta.curve_weights=true --set "evaluation.methods=[Method2_MobiusTTA]"
                    bench "B r3gonly $m $d" --config "$(cfg_of $m $d)" --tag "r3gonly_$m" $common \
                        --set mobius_tta.curve_gate=true --set "evaluation.methods=[Method2_MobiusTTA]"
                done
            done ;;
        D)  say "=============== D: reports ==============="
            run_py "D Part A table" scripts/round3_report.py
            run_py "D Part B summary" scripts/collect_results.py ;;
        *)  say "unknown stage $ST" ;;
        esac
    done
    say "🎉 Round 3 finished."
}

pids() { pgrep -f "$AUR/scripts/run_round3.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    run) do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running (PID(s): $(pids | tr '\n' ' '))"; exit 1; }
        LOG="$AUR/logs/round3_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_round3.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG   (status: scripts/run_round3.sh status)" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING (PID(s): $(pids | tr '\n' ' '))" || say "Not running."
        L="$(ls -t logs/round3_*.log 2>/dev/null | head -1)"
        if [ -n "$L" ]; then say "Log: $L"; grep -E "A1:|A2:|B:|D:|✅|❌|⚠️|🎉" "$L" | sed 's/^/    /'; echo "    --- last lines ---"; tail -3 "$L" | sed 's/^/    /'; fi ;;
    stop)
        P="$(pids)"; [ -z "$P" ] && { say "Not running."; exit 0; }
        for p in $P; do kill -TERM -- "-$p" 2>/dev/null || { pkill -TERM -P "$p" 2>/dev/null; kill -TERM "$p" 2>/dev/null; }; done
        say "Stopped." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
