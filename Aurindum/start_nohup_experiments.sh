#!/usr/bin/env bash
# ==============================================================================
# Helper Script to Launch the Full Experiment Suite via nohup on GPU Server
#
# Usage:
#   chmod +x start_nohup_experiments.sh run_all_experiments_gpu.sh
#   ./start_nohup_experiments.sh
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p "$SCRIPT_DIR/logs"
RUNNER_LOG="$SCRIPT_DIR/logs/nohup_runner.log"

echo "========================================================================"
echo " Launching Master Experiment Suite in background via nohup..."
echo "========================================================================"

nohup bash "$SCRIPT_DIR/run_all_experiments_gpu.sh" > "$RUNNER_LOG" 2>&1 &
PID=$!

echo " Process started in background with PID: $PID"
echo " Nohup log: $RUNNER_LOG"
echo ""
echo " To monitor progress in real-time:"
echo "   tail -f $RUNNER_LOG"
echo ""
echo " To check if the process is still running:"
echo "   ps aux | grep $PID"
echo "========================================================================"
