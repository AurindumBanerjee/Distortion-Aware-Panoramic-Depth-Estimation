#!/usr/bin/env bash
# ==============================================================================
# Master GPU Experiment Suite: Sequential Execution
#
# Runs all 3 experiment series in order:
#   Series 1: Gradient-Domain Polar Fusion & Shift-Decoupled Alignment
#   Series 2: Test-Time Möbius Augmentation Ensembling
#   Series 3: Real Structured3D Comparative Foundation Benchmark
#
# Automatically updates 'best_model/' after each run.
# ==============================================================================
set -uo pipefail

AURINDUM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$AURINDUM_DIR"

mkdir -p "$AURINDUM_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MASTER_LOG="$AURINDUM_DIR/logs/master_experiment_${TIMESTAMP}.log"

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
log "Log File: $MASTER_LOG"
log "=========================================================================="

# --- Preflight: fail fast instead of producing meaningless results ---
log "Python: $(command -v python) | env: ${CONDA_DEFAULT_ENV:-none}"
PREFLIGHT_OK=1
[ -f "$AURINDUM_DIR/weights/dpt_hybrid_384.pt" ] || { log "❌ Missing weights/dpt_hybrid_384.pt"; PREFLIGHT_OK=0; }
[ -d "$AURINDUM_DIR/data/structured3d/rgb" ] || { log "❌ Missing data/structured3d/rgb"; PREFLIGHT_OK=0; }
python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { log "❌ CUDA not available to torch"; PREFLIGHT_OK=0; }
if [ "$PREFLIGHT_OK" != 1 ]; then log "Preflight failed; aborting."; exit 1; fi
log "Preflight OK."

START_TOTAL=$(date +%s)

# --- SERIES 1 ---
log ">>> [1/3] Running Experiment Series 1: Gradient-Domain Polar Fusion..."
START_S1=$(date +%s)
if (cd "$AURINDUM_DIR/1_gradient_polar_fusion" && bash run_gpu.sh >> "$MASTER_LOG" 2>&1); then
    END_S1=$(date +%s)
    log "✅ [1/3] Series 1 completed successfully in $((END_S1 - START_S1)) seconds."
else
    log "❌ [1/3] Series 1 failed! Check $MASTER_LOG for details."
fi

# --- SERIES 2 ---
log ">>> [2/3] Running Experiment Series 2: Test-Time Möbius Ensembling..."
START_S2=$(date +%s)
if (cd "$AURINDUM_DIR/2_mobius_tta_ensembling" && bash run_gpu.sh >> "$MASTER_LOG" 2>&1); then
    END_S2=$(date +%s)
    log "✅ [2/3] Series 2 completed successfully in $((END_S2 - START_S2)) seconds."
else
    log "❌ [2/3] Series 2 failed! Check $MASTER_LOG for details."
fi

# --- SERIES 3 ---
log ">>> [3/3] Running Experiment Series 3: Real Structured3D Benchmark..."
START_S3=$(date +%s)
if (cd "$AURINDUM_DIR/3_structured3d_benchmark" && bash run_gpu.sh >> "$MASTER_LOG" 2>&1); then
    END_S3=$(date +%s)
    log "✅ [3/3] Series 3 completed successfully in $((END_S3 - START_S3)) seconds."
else
    log "❌ [3/3] Series 3 failed! Check $MASTER_LOG for details."
fi

END_TOTAL=$(date +%s)
log "=========================================================================="
log "🎉 Master Experiment Suite Finished!"
log "Total Runtime: $((END_TOTAL - START_TOTAL)) seconds."
log "Current Best Model Status:"
if [ -f "$AURINDUM_DIR/best_model/BEST_MODEL.md" ]; then
    head -n 12 "$AURINDUM_DIR/best_model/BEST_MODEL.md" | while read -r line; do log "  $line"; done
fi
log "Detailed report available at: $AURINDUM_DIR/best_model/BEST_MODEL.md"
log "=========================================================================="
