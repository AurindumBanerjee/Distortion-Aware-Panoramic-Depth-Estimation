#!/usr/bin/env bash
# ==============================================================================
# One entry point for the corrected (v2.1) experiment suite on the GPU server.
#
#   ./run_corrected_suite.sh start     stop anything still running, archive old results,
#                                      preflight (tests, data, weights), launch detached
#   ./run_corrected_suite.sh stop      stop a running suite (this one or start_nohup_experiments.sh)
#   ./run_corrected_suite.sh status    running? + per-series ✅/❌ + tail of the master log
#   ./run_corrected_suite.sh collect   (re)build results/SUMMARY_<ts>.md from the result JSONs
#
# What `start` runs, in order (one config after the other, each series after the other):
#   CONFIGS="config.yaml config_dap.yaml"   (MiDaS DPT-Hybrid, then DAP)
#     series 1  gradient polar fusion        synthetic, 24 scenes
#     series 2  Möbius TTA + yaw control     synthetic, 24 scenes
#     series 3  Structured3D benchmark       all panoramas in the split list (300)
#     series 3  PanoX benchmark              200 frames (RUN_PANOX=0 to skip)
#   then scripts/collect_results.py -> results/SUMMARY_<ts>.md
#
# Overrides (environment): CONFIGS, RUN_PANOX, MAX_SCENES (series 3 limit), CONDA_ENV, CONDA_SH,
#                          CUDA_VISIBLE_DEVICES, SKIP_TESTS=1, NO_ARCHIVE=1
# A config whose weights are missing (e.g. DAP) is skipped by the master script; the rest still run.
# ==============================================================================
set -uo pipefail
AURINDUM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$AURINDUM_DIR"
mkdir -p logs results
PID_FILE="$AURINDUM_DIR/logs/suite.pid"
RUNNER_LOG="$AURINDUM_DIR/logs/nohup_runner.log"
export CONFIGS="${CONFIGS:-config.yaml config_dap.yaml}"
export RUN_PANOX="${RUN_PANOX:-1}"

say() { echo "[$(date +'%H:%M:%S')] $*"; }

suite_pids() {  # PIDs of a suite started from THIS folder (full path match; other folders/users untouched)
    { [ -f "$PID_FILE" ] && cat "$PID_FILE"; \
      pgrep -f "$AURINDUM_DIR/run_all_experiments_gpu.sh"; } 2>/dev/null | sort -u | while read -r p; do
        [ -n "$p" ] && [ "$p" != "$$" ] && kill -0 "$p" 2>/dev/null && echo "$p"; done
}

do_stop() {
    local pids; pids="$(suite_pids)"
    if [ -z "$pids" ]; then say "No running suite found."; rm -f "$PID_FILE"; return 0; fi
    for p in $pids; do
        local pg own; pg="$(ps -o pgid= -p "$p" 2>/dev/null | tr -d ' ')"; own="$(ps -o pgid= -p $$ | tr -d ' ')"
        say "Stopping suite PID $p (process group ${pg:-?}) ..."
        if [ -n "$pg" ] && [ "$pg" != "$own" ]; then kill -TERM -- "-$pg" 2>/dev/null; else kill -TERM "$p" 2>/dev/null; fi
    done
    for _ in $(seq 1 20); do [ -z "$(suite_pids)" ] && break; sleep 1; done
    for p in $(suite_pids); do
        local pg; pg="$(ps -o pgid= -p "$p" 2>/dev/null | tr -d ' ')"
        say "Force-killing $p"; kill -KILL "$p" 2>/dev/null; [ -n "$pg" ] && [ "$pg" != "$(ps -o pgid= -p $$ | tr -d ' ')" ] && kill -KILL -- "-$pg" 2>/dev/null
    done
    # stray series processes: only `run.py` whose working directory is inside this Aurindum folder
    for p in $(pgrep -f "run.py --config" 2>/dev/null); do
        case "$(readlink "/proc/$p/cwd" 2>/dev/null)" in "$AURINDUM_DIR"/*) say "Killing series process $p"; kill -TERM "$p" 2>/dev/null ;; esac
    done
    rm -f "$PID_FILE"
    say "Stopped. GPU:"; command -v nvidia-smi >/dev/null && nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader
    return 0
}

do_archive() {
    [ "${NO_ARCHIVE:-0}" = 1 ] && { say "NO_ARCHIVE=1: keeping previous outputs in place."; return; }
    local dst="$AURINDUM_DIR/results/archive/$(date +%Y%m%d_%H%M%S)_before_v2.1_run"
    local moved=0
    mkdir -p "$dst"
    for d in [123]_*/outputs* [123]_*/logs* logs/master_experiment_*.log logs/nohup_runner.log \
             best_model/synthetic* best_model/structured3d* best_model/panox* best_model/BEST_MODEL.md \
             best_model/best_metrics.json best_model/best_config.yaml best_model/sample_predictions; do
        [ -e "$d" ] || continue
        mkdir -p "$dst/$(dirname "$d")"; mv "$d" "$dst/$d" && moved=1
    done
    if [ "$moved" = 1 ]; then say "Archived previous results to ${dst#$AURINDUM_DIR/}"; else rmdir "$dst" 2>/dev/null; fi
}

do_preflight() {
    local ok=1
    CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    say "Code: $(git -C "$AURINDUM_DIR" log -1 --format='%h %s' 2>/dev/null)"
    [ -n "$(git -C "$AURINDUM_DIR" status --porcelain -- '*.py' '*.yaml' '*.sh' 2>/dev/null)" ] && \
        say "⚠️  Uncommitted code/config changes present (results will not match a commit)."
    if [ "${SKIP_TESTS:-0}" != 1 ]; then
        if python -m pytest -q tests/test_methods.py >"logs/preflight_tests.log" 2>&1; then
            say "✅ Regression tests passed ($(tail -1 logs/preflight_tests.log))"
        else
            say "❌ Regression tests failed, see logs/preflight_tests.log"; ok=0
        fi
    fi
    python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { say "❌ CUDA not available"; ok=0; }
    [ -f weights/dpt_hybrid_384.pt ] || say "⚠️  weights/dpt_hybrid_384.pt missing: MiDaS config will be skipped"
    if [[ " $CONFIGS " == *dap* ]]; then
        { [ -f weights/dap/model.pth ] && [ -d third_party/DAP/networks ]; } || say "⚠️  DAP weights/repo missing: DAP config will be skipped"
    fi
    local n_s3d; n_s3d=$(ls data/structured3d/rgb 2>/dev/null | wc -l)
    [ "$n_s3d" -gt 0 ] || { say "❌ data/structured3d/rgb is empty"; ok=0; }
    say "Structured3D: $n_s3d panoramas; split list: $([ -f data/structured3d/test.txt ] && wc -l < data/structured3d/test.txt || echo 'none (folder discovery)')"
    if [ "$RUN_PANOX" = 1 ]; then
        if [ -f data/panox/test.txt ]; then
            say "PanoX: $(wc -l < data/panox/test.txt) frames"
            # actually read one EXR + RGB with the same loader the benchmark uses (cv2, then OpenEXR fallback)
            python - <<'PYEOF' || say "⚠️  PanoX EXR cannot be read (pip install openexr, or RUN_PANOX=0): PanoX series will fail"
import os, sys
os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
import cv2, numpy as np
sys.path.insert(0, ".")
from datasets.panorama import PanoramaDataset
s = PanoramaDataset("data/panox", "test.txt", height=64, width=128, name="panox")[0]
assert np.isfinite(s.depth).any(), "no valid depth pixels in first PanoX frame"
print("PanoX loader OK (first frame: %.1f-%.1f m)" % (np.nanmin(s.depth), np.nanmax(s.depth)))
PYEOF
        else
            say "⚠️  data/panox/test.txt missing: PanoX runs will fail (RUN_PANOX=0 to skip)"
        fi
    fi
    [ "$ok" = 1 ]
}

do_start() {
    do_stop
    do_preflight || { say "Preflight failed; not starting."; exit 1; }
    do_archive
    say "Launching: CONFIGS=\"$CONFIGS\" RUN_PANOX=$RUN_PANOX ${MAX_SCENES:+MAX_SCENES=$MAX_SCENES}"
    setsid nohup bash -c "bash '$AURINDUM_DIR/run_all_experiments_gpu.sh'; \
        cd '$AURINDUM_DIR' && python scripts/collect_results.py" \
        > "$RUNNER_LOG" 2>&1 < /dev/null &
    echo $! > "$PID_FILE"
    say "Started (PID $(cat "$PID_FILE")). Monitor: ./run_corrected_suite.sh status   or   tail -f logs/nohup_runner.log"
}

do_status() {
    local pids; pids="$(suite_pids)"
    if [ -n "$pids" ]; then say "RUNNING (PID(s): $(echo $pids))"; else say "Not running."; fi
    local ml; ml="$(ls -t logs/master_experiment_*.log 2>/dev/null | head -1)"
    if [ -n "$ml" ]; then
        say "Master log: $ml"
        grep -E "CONFIG:|✅|❌|Skipping" "$ml" | sed 's/^/    /'
        echo "    --- last lines ---"; tail -5 "$ml" | sed 's/^/    /'
    fi
    ls -t results/SUMMARY_*.md 2>/dev/null | head -1 | sed 's/^/    Latest summary: /'
}

case "${1:-status}" in
    start)   do_start ;;
    stop)    do_stop ;;
    status)  do_status ;;
    collect) do_preflight >/dev/null 2>&1; python scripts/collect_results.py ;;
    *) echo "usage: $0 {start|stop|status|collect}"; exit 2 ;;
esac
