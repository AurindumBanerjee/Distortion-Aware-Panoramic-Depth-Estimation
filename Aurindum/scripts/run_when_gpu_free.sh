#!/usr/bin/env bash
# Run a command only after the shared GPU has had no compute processes for IDLE_MIN consecutive minutes.
#
#   setsid nohup bash scripts/run_when_gpu_free.sh <command ...> > logs/when_free.out 2>&1 < /dev/null &
#
# Example (planar-prior re-run, then the summary):
#   setsid nohup bash scripts/run_when_gpu_free.sh bash -c 'STAGES="G" bash scripts/run_next_experiments.sh run; python scripts/collect_results.py' ...
#
# Env: IDLE_MIN (default 3), POLL_S (default 30), MAX_WAIT_H (default 24: give up and exit 2 afterwards)
set -uo pipefail
cd "$(dirname "$0")/.."
IDLE_MIN="${IDLE_MIN:-3}"; POLL_S="${POLL_S:-30}"; MAX_WAIT_H="${MAX_WAIT_H:-24}"
say() { echo "[$(date +'%F %T')] $*"; }
[ "$#" -gt 0 ] || { echo "usage: $0 <command ...>"; exit 1; }
command -v nvidia-smi >/dev/null || { say "nvidia-smi not found"; exit 1; }

need=$(( IDLE_MIN * 60 / POLL_S )); free=0; t0=$(date +%s)
say "waiting for the GPU to be idle for ${IDLE_MIN} min, then running: $*"
while [ "$free" -lt "$need" ]; do
    if [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null)" ]; then free=$((free + 1)); else free=0; fi
    if [ $(( $(date +%s) - t0 )) -gt $(( MAX_WAIT_H * 3600 )) ]; then say "gave up after ${MAX_WAIT_H} h"; exit 2; fi
    [ "$free" -lt "$need" ] && sleep "$POLL_S"
done
say "GPU idle: starting"
"$@"
rc=$?
say "finished (exit $rc)"
exit $rc
