#!/usr/bin/env bash
# ==============================================================================
# Method 2 GPU Runner: Test-Time Möbius Augmentation Ensembling
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
export MPLCONFIGDIR=/tmp/matplotlib_$$

echo "========================================================================"
echo " Starting Method 2 on GPU (Device: $CUDA_VISIBLE_DEVICES)"
echo " Timestamp: $(date)"
echo "========================================================================"

mkdir -p logs outputs

# Run full evaluation series
python run.py \
    --config config.yaml \
    --num_scenes 24 \
    --fusion_mode distortion_weighted

echo "========================================================================"
echo " Method 2 GPU execution finished at $(date)"
echo " Results stored in $SCRIPT_DIR/outputs/"
echo "========================================================================"
