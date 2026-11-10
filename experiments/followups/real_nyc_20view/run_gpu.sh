#!/usr/bin/env bash
set -euo pipefail
HERE=$(dirname "$(realpath "$0")")
ROOT_DIR=$(realpath "$HERE/../../..")
cd "$ROOT_DIR"
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=0
mkdir -p "$HERE/logs"
LOG="$HERE/logs/run_$(date +%Y%m%d_%H%M%S).log"
python "$HERE/run.py" "$@" 2>&1 | tee "$LOG"
