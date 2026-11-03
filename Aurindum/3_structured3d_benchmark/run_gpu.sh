#!/usr/bin/env bash
# ==============================================================================
# Method 3 GPU Runner: Structured3D Real-World Foundation Benchmark
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
export MPLCONFIGDIR=/tmp/matplotlib_$$

echo "========================================================================"
echo " Starting Method 3 Benchmark on GPU (Device: $CUDA_VISIBLE_DEVICES)"
echo " Timestamp: $(date)"
echo "========================================================================"

mkdir -p logs outputs data/curated_scenes

# Run benchmark across real indoor scenes
python run.py \
    --config "${CONFIG:-config.yaml}" \
    --max_scenes 20

echo "========================================================================"
echo " Method 3 GPU execution finished at $(date)"
echo " Results stored in $SCRIPT_DIR/outputs/"
echo "========================================================================"
