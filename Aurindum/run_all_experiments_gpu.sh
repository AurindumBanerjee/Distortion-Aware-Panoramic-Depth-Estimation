#!/usr/bin/env bash
# ==============================================================================
# Master GPU Experiment Suite: Sequential Execution
#
# For each config in CONFIGS (default: the normal MiDaS config, then the DAP config)
# runs the 3 experiment series in order:
#   Series 1: Gradient-Domain Polar Fusion & Shift-Decoupled Alignment
#   Series 2: Test-Time Möbius Augmentation Ensembling
#   Series 3: Real Structured3D Comparative Foundation Benchmark
#
# Each config writes to its own outputs/logs folders (outputs/ + logs/ for config.yaml,
# outputs_dap/ + logs_dap/ for config_dap.yaml) and its own best_model/ registry
# ("synthetic", "structured3d" vs "synthetic_dap", "structured3d_dap").
# A failing series or config does not stop the rest.
#
# Overrides:
#   CONFIGS="config.yaml"                  only the normal run
#   CONFIGS="config_dap.yaml"              only the DAP run
#   CONDA_ENV=RL  CONDA_SH=<conda.sh>      environment
# ==============================================================================
set -uo pipefail

AURINDUM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$AURINDUM_DIR"

mkdir -p "$AURINDUM_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MASTER_LOG="$AURINDUM_DIR/logs/master_experiment_${TIMESTAMP}.log"
CONFIGS="${CONFIGS:-config.yaml config_dap.yaml}"

export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
export MPLCONFIGDIR="/tmp/matplotlib_${TIMESTAMP}"

log() {
    local msg="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$MASTER_LOG"
}

# Conda env (override with CONDA_ENV / CONDA_SH). Done here so a detached run needs no active shell env.
CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
if [ -f "$CONDA_SH" ]; then
    set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u
fi

log "=========================================================================="
log "🚀 Starting Master GPU Experiment Suite"
log "Host: $(hostname) | CUDA Device: $CUDA_VISIBLE_DEVICES"
log "Configs (in order): $CONFIGS"
log "Log File: $MASTER_LOG"
log "=========================================================================="

# --- Preflight: fail fast instead of producing meaningless results ---
log "Python: $(command -v python) | env: ${CONDA_DEFAULT_ENV:-none}"
PREFLIGHT_OK=1
[ -d "$AURINDUM_DIR/data/structured3d/rgb" ] || { log "❌ Missing data/structured3d/rgb"; PREFLIGHT_OK=0; }
python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { log "❌ CUDA not available to torch"; PREFLIGHT_OK=0; }
if [ "$PREFLIGHT_OK" != 1 ]; then log "Preflight failed; aborting."; exit 1; fi
log "Preflight OK."

# Per-config requirements (a config that cannot run is skipped, the others continue)
config_ready() {
    case "$1" in
        *dap*)
            [ -f "$AURINDUM_DIR/weights/dap/model.pth" ] || { log "❌ Missing weights/dap/model.pth"; return 1; }
            [ -d "$AURINDUM_DIR/third_party/DAP/networks" ] || { log "❌ Missing third_party/DAP"; return 1; } ;;
        *)
            [ -f "$AURINDUM_DIR/weights/dpt_hybrid_384.pt" ] || { log "❌ Missing weights/dpt_hybrid_384.pt"; return 1; } ;;
    esac
    return 0
}

run_series() {  # run_series <index> <dir> <title> <config>
    local idx="$1" dir="$2" title="$3" cfg="$4" t0 t1
    log ">>> [$idx/3][$cfg] Running Series $idx: $title..."
    t0=$(date +%s)
    if (cd "$AURINDUM_DIR/$dir" && CONFIG="$cfg" bash run_gpu.sh >> "$MASTER_LOG" 2>&1); then
        t1=$(date +%s)
        log "✅ [$idx/3][$cfg] Series $idx completed successfully in $((t1 - t0)) seconds."
    else
        log "❌ [$idx/3][$cfg] Series $idx failed! Check $MASTER_LOG for details."
    fi
}

START_TOTAL=$(date +%s)

for CFG in $CONFIGS; do
    log "=========================== CONFIG: $CFG ==========================="
    if [ ! -f "$AURINDUM_DIR/1_gradient_polar_fusion/$CFG" ]; then
        log "❌ $CFG not found; skipping."
        continue
    fi
    if ! config_ready "$CFG"; then
        log "Skipping $CFG (requirements missing)."
        continue
    fi
    run_series 1 1_gradient_polar_fusion "Gradient-Domain Polar Fusion" "$CFG"
    run_series 2 2_mobius_tta_ensembling "Test-Time Möbius Ensembling" "$CFG"
    run_series 3 3_structured3d_benchmark "Real Structured3D Benchmark" "$CFG"
done

END_TOTAL=$(date +%s)
log "=========================================================================="
log "🎉 Master Experiment Suite Finished!"
log "Total Runtime: $((END_TOTAL - START_TOTAL)) seconds."
log "Summary: ✅/❌ lines above show each series per config."
for R in best_model/*/BEST_MODEL.md; do
    [ -f "$AURINDUM_DIR/$R" ] && log "Best-model report: $AURINDUM_DIR/$R"
done
log "=========================================================================="
