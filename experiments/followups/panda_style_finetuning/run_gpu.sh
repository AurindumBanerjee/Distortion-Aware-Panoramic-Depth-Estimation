#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$HERE/../../.." && pwd)"
cd "$ROOT_DIR"
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1}"
mkdir -p "$HERE/logs"
"${PYTHON:-python}" "$HERE/train.py" "$@" 2>&1 | tee "$HERE/logs/train_$(date +%Y%m%d_%H%M%S).log"
