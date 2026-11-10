#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOKESH="$(cd "$HERE/../.." && pwd)"
cd "$LOKESH"
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
mkdir -p "$HERE/logs"
"${PYTHON:-python}" "$HERE/run.py" "$@" 2>&1 | tee "$HERE/logs/run_$(date +%Y%m%d_%H%M%S).log"
