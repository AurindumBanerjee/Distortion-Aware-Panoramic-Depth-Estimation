#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
LOKESH="$(cd "$HERE/../.." && pwd)"
cd "$LOKESH"
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES="\${CUDA_VISIBLE_DEVICES:-0}"
if [ "$#" -lt 1 ]; then echo "usage: bash evaluate_gpu.sh /path/to/best.pt [other args]"; exit 2; fi
CKPT="$1"; shift
mkdir -p "$HERE/logs"
python "$HERE/evaluate.py" --checkpoint "$CKPT" "$@" 2>&1 | tee "$HERE/logs/evaluate_$(date +%Y%m%d_%H%M%S).log"
