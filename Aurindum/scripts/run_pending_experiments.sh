#!/usr/bin/env bash
# Sequential driver for the follow-up experiments on the GPU server (run detached, see usage).
#   1. DAP re-run with the gate_lat / log-scale re-anchor patches (series 2 + series 3 on Structured3D and PanoX);
#      the pre-patch DAP outputs are moved to results/archive/<ts>_dap_prepatch first (nothing is deleted)
#   2. Möbius ablation (scripts/run_mobius_ablation.sh both 60) and Holo360D (indoor + outdoor, MiDaS + DAP):
#      Holo360D goes first if data/holo360d/.transfer_done exists when step 1 ends, otherwise the ablation does
#   3. scripts/collect_results.py (cluster-robust summary of everything)
# A failing step is logged and the next one still runs.
#
# Usage (from Aurindum/):  setsid nohup bash scripts/run_pending_experiments.sh > logs/pending_tasks.out 2>&1 < /dev/null &
# Overrides: CONDA_ENV, CONDA_SH, ABL_SCENES (default 60), HOLO_WAIT_MIN (default 240)
set -uo pipefail
cd "$(dirname "$0")/.."
AURINDUM_DIR="$(pwd)"
mkdir -p logs
TS=$(date +%Y%m%d_%H%M%S)
LOG="$AURINDUM_DIR/logs/pending_tasks_${TS}.log"

CONDA_SH="${CONDA_SH:-$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh}"
if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
export PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0} OPENCV_IO_ENABLE_OPENEXR=1
export MPLCONFIGDIR="/tmp/matplotlib_pending_${TS}"

log() { local m="[$(date +'%Y-%m-%d %H:%M:%S')] $1"; echo "$m"; echo "$m" >> "$LOG"; }
step() {  # step <title> <command...>
    local title="$1"; shift
    log ">>> $title"
    local t0; t0=$(date +%s)
    if "$@" >> "$LOG" 2>&1; then log "✅ $title ($(( $(date +%s) - t0 )) s)"; else log "❌ $title FAILED ($(( $(date +%s) - t0 )) s)"; fi
}
series3() { ( cd "$AURINDUM_DIR/3_structured3d_benchmark" && CONFIG="$1" bash run_gpu.sh ); }
series2() { ( cd "$AURINDUM_DIR/2_mobius_tta_ensembling" && CONFIG="$1" bash run_gpu.sh ); }

log "== pending experiments | python $(command -v python) | env ${CONDA_DEFAULT_ENV:-none} | log $LOG"
python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { log "❌ CUDA not available; aborting"; exit 1; }

archive_prepatch_dap() {
    local dst="$AURINDUM_DIR/results/archive/${TS}_dap_prepatch" moved=0 d
    mkdir -p "$dst"
    for d in 2_mobius_tta_ensembling/outputs_dap 2_mobius_tta_ensembling/logs_dap \
             3_structured3d_benchmark/outputs_dap 3_structured3d_benchmark/logs_dap \
             3_structured3d_benchmark/outputs_dap_panox 3_structured3d_benchmark/logs_dap_panox; do
        [ -e "$d" ] || continue
        mkdir -p "$dst/$(dirname "$d")"; mv "$d" "$dst/$d" && moved=1
    done
    [ "$moved" = 1 ] && echo "archived to ${dst#$AURINDUM_DIR/}" || { rmdir "$dst" 2>/dev/null; echo "nothing to archive"; }
}

run_dap_rerun() {
    step "DAP re-run: archive pre-patch outputs" archive_prepatch_dap
    step "DAP re-run: series 2 (synthetic, config_dap.yaml)" series2 config_dap.yaml
    step "DAP re-run: Structured3D (config_dap.yaml)" series3 config_dap.yaml
    step "DAP re-run: PanoX (config_dap_panox.yaml)" series3 config_dap_panox.yaml
}

run_ablation() { step "Möbius ablation (both datasets, ${ABL_SCENES:-60} scenes)" bash scripts/run_mobius_ablation.sh both "${ABL_SCENES:-60}"; }

run_holo() {
    local marker="data/holo360d/.transfer_done" waited=0
    while [ ! -f "$marker" ] && [ "$waited" -lt "${HOLO_WAIT_MIN:-240}" ]; do sleep 60; waited=$((waited + 1)); done
    if [ ! -f "$marker" ]; then log "❌ Holo360D data not transferred after ${waited} min; skipping Holo360D"; return; fi
    step "Holo360D: build split lists" python scripts/make_holo360d_list.py --root data/holo360d
    log "Holo360D lists: indoor $(wc -l < data/holo360d/indoor.txt) | outdoor $(wc -l < data/holo360d/outdoor.txt)"
    for cfg in config_holo360d_indoor config_holo360d_outdoor config_dap_holo360d_indoor config_dap_holo360d_outdoor; do
        step "Holo360D: $cfg" series3 "$cfg.yaml"
    done
}

run_dap_rerun
if [ -f data/holo360d/.transfer_done ]; then
    log "Holo360D data is ready: running it before the ablation"
    run_holo; run_ablation
else
    log "Holo360D data not ready yet: running the ablation first"
    run_ablation; run_holo
fi
step "Collect results (cluster-robust summary)" python scripts/collect_results.py
log "🎉 All pending experiments finished."
