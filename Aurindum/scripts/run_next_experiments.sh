#!/usr/bin/env bash
# ==============================================================================
# Queue of the follow-up experiments (run AFTER the corrected suite). One command, sequential, detached.
#
#   scripts/run_next_experiments.sh start     launch detached (logs/next_experiments_<ts>.log)
#   scripts/run_next_experiments.sh status    running? + per-stage ✅/❌ + last lines
#   scripts/run_next_experiments.sh stop      stop it
#   scripts/run_next_experiments.sh run       run in the foreground (what `start` calls)
#
# Stages (env STAGES="A B C D", default all; a failing stage never blocks the next one):
#   A  DAP with the patches (gate_lat + log-scale re-anchor): series 2, series 3 Structured3D, series 3 PanoX.
#      Written to outputs_dap_gated / outputs_dap_panox_gated (+ benchmark "..._dap_gated"), so the earlier
#      un-gated DAP outputs stay available for comparison.
#   B  Holo360D, indoor + outdoor, MiDaS + DAP (needs data/holo360d; split lists are built if missing).
#   C  Möbius ablation: rotation-only / dilation-only / full  x  gate off/on  x  MiDaS/DAP  x  S3/PanoX
#      (ABL_N scenes each, default 60; Baseline + Method2 + yaw control only).
#   D  results/SUMMARY_<ts>.md with cluster-robust statistics over every outputs*/ folder.
#
# Other env: CONDA_ENV (RL), CONDA_SH, CUDA_VISIBLE_DEVICES, MAX_SCENES (stage A/B series 3 limit), ABL_N.
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results
PID_FILE="$AUR/logs/next_experiments.pid"
STAGES="${STAGES:-A B C D}"
ABL_N="${ABL_N:-60}"

say() { echo "[$(date +'%F %T')] $*"; }

do_run() {
    CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
    export MPLCONFIGDIR="/tmp/matplotlib_$$"
    say "🚀 Follow-up experiments | stages: $STAGES | python: $(command -v python) | env: ${CONDA_DEFAULT_ENV:-none}"
    python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { say "❌ CUDA not available; aborting"; exit 1; }
    local have_dap=1 have_midas=1
    { [ -f weights/dap/model.pth ] && [ -d third_party/DAP/networks ]; } || { have_dap=0; say "⚠️  DAP weights/repo missing: DAP runs are skipped"; }
    [ -f weights/dpt_hybrid_384.pt ] || { have_midas=0; say "⚠️  MiDaS weights missing: MiDaS runs are skipped"; }
    local ms=""; [ -n "${MAX_SCENES:-}" ] && ms="--max_scenes $MAX_SCENES"

    ok_cfg() { case "$1" in *dap*) [ "$have_dap" = 1 ];; *) [ "$have_midas" = 1 ];; esac; }
    step() {  # step <label> <dir> <python args...>
        local label="$1" dir="$2"; shift 2
        local t0; t0=$(date +%s)
        say ">>> $label"
        if (cd "$AUR/$dir" && python run.py "$@"); then say "✅ $label ($(( $(date +%s) - t0 )) s)"; else say "❌ $label FAILED"; fi
    }

    for ST in $STAGES; do
        case "$ST" in
        A)  say "=============== Stage A: DAP with gate_lat + logscale re-anchor ==============="
            if [ "$have_dap" = 1 ]; then
                step "A1 series 2 DAP (gated)"            2_mobius_tta_ensembling  --config config_dap.yaml --tag gated
                step "A2 series 3 Structured3D DAP (gated)" 3_structured3d_benchmark --config config_dap.yaml --tag gated $ms
                [ -f data/panox/test.txt ] && step "A3 series 3 PanoX DAP (gated)" 3_structured3d_benchmark --config config_dap_panox.yaml --tag gated $ms
            else say "skip stage A (no DAP)"; fi ;;
        B)  say "=============== Stage B: Holo360D (real LiDAR-mesh GT) ==============="
            if [ -d data/holo360d ]; then
                [ -f data/holo360d/indoor.txt ] || python scripts/make_holo360d_list.py --root data/holo360d
                for KIND in indoor outdoor; do for CFG in config_holo360d_$KIND.yaml config_dap_holo360d_$KIND.yaml; do
                    ok_cfg "$CFG" && step "B Holo360D $KIND [$CFG]" 3_structured3d_benchmark --config "$CFG" $ms
                done; done
            else say "❌ data/holo360d not found (copy it to $AUR/data/holo360d); stage B skipped"; fi ;;
        C)  say "=============== Stage C: Möbius ablation ($ABL_N scenes per variant) ==============="
            if [ "$have_dap" = 1 ] && [ "$have_midas" = 1 ]; then
                # the ablation script ends with collect_results.py; failures inside it are logged by python
                bash scripts/run_mobius_ablation.sh both "$ABL_N" && say "✅ C ablation" || say "❌ C ablation FAILED"
            else say "skip stage C (needs both MiDaS and DAP weights)"; fi ;;
        D)  say "=============== Stage D: cluster-robust summary ==============="
            python scripts/collect_results.py && say "✅ D summary written" || say "❌ D summary FAILED" ;;
        *)  say "unknown stage $ST" ;;
        esac
    done
    say "🎉 Follow-up experiments finished."
}

pids() { pgrep -f "$AUR/scripts/run_next_experiments.sh run" 2>/dev/null | grep -v "^$$\$" || true; }

case "${1:-status}" in
    run)    do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running (PID(s): $(pids | tr '\n' ' '))"; exit 1; }
        LOG="$AUR/logs/next_experiments_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_next_experiments.sh" run > "$LOG" 2>&1 < /dev/null &
        echo $! > "$PID_FILE"
        say "Started PID $(cat "$PID_FILE"). Log: $LOG   (status: scripts/run_next_experiments.sh status)" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING (PID(s): $(pids | tr '\n' ' '))" || say "Not running."
        L="$(ls -t logs/next_experiments_*.log 2>/dev/null | head -1)"
        if [ -n "$L" ]; then say "Log: $L"; grep -E "Stage|✅|❌|⚠️|🎉" "$L" | sed 's/^/    /'; echo "    --- last lines ---"; tail -4 "$L" | sed 's/^/    /'; fi ;;
    stop)
        P="$(pids)"; [ -z "$P" ] && { say "Not running."; exit 0; }
        for p in $P; do kill -TERM -- "-$p" 2>/dev/null || { pkill -TERM -P "$p" 2>/dev/null; kill -TERM "$p" 2>/dev/null; }; done
        say "Stopped (process group terminated)." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
