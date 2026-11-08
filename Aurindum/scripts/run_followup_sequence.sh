#!/usr/bin/env bash
# Follow-up sequence on the enlarged Holo360D (12 indoor / 3 outdoor scenes, lists built with --frames_per_scene 25).
# One detached process, one stage after another; a failing step is logged and the next one still runs.
#   1. Stage F   re-anchor diagnostics on S3, PanoX, Holo indoor, Holo outdoor   (decides what E is worth)
#   2. holo12    full MiDaS table on the enlarged Holo360D (all methods), results kept under tag holo12,
#                plus the diagnostic with 80 frames (tag holo12)
#   3. Stages E G H I D   rotation-only / fit guard / Method 1 variants, planar prior, pass sync, DA360 + DA^2 audit,
#                cluster-robust summary
#
# Usage (from Aurindum/):  setsid nohup bash scripts/run_followup_sequence.sh > logs/followup.out 2>&1 < /dev/null &
# Overrides: CONDA_ENV, CONDA_SH, ESC (scene cap for E-I), DIAG_N, STAGES_REST (default "E G H I D")
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
TS=$(date +%Y%m%d_%H%M%S)
LOG="$(pwd)/logs/followup_${TS}.log"

CONDA_SH="${CONDA_SH:-$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh}"
if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
# DA^2 loads its weights through the Hugging Face cache; the server has no internet, so use the staged local copy.
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}" HF_HUB_OFFLINE=1
export MPLCONFIGDIR="/tmp/matplotlib_followup_${TS}"

log() { local m="[$(date +'%F %T')] $1"; echo "$m"; echo "$m" >> "$LOG"; }
step() {  # step <title> <command...>
    local title="$1"; shift
    log ">>> $title"
    local t0; t0=$(date +%s)
    if "$@" >> "$LOG" 2>&1; then log "✅ $title ($(( $(date +%s) - t0 )) s)"; else log "❌ $title FAILED ($(( $(date +%s) - t0 )) s)"; fi
}

log "== follow-up sequence | python $(command -v python) | env ${CONDA_DEFAULT_ENV:-none} | log $LOG"
python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { log "❌ CUDA not available; aborting"; exit 1; }
for f in data/holo360d/indoor.txt data/holo360d/outdoor.txt weights/dpt_hybrid_384.pt; do
    [ -f "$f" ] || { log "❌ missing $f; aborting"; exit 1; }
done
log "Holo360D lists: indoor $(wc -l < data/holo360d/indoor.txt) frames, outdoor $(wc -l < data/holo360d/outdoor.txt) frames"

step "Stage F: re-anchor diagnostics" env STAGES="F" bash scripts/run_next_experiments.sh run

holo12() { ( cd 3_structured3d_benchmark && python run.py --config "$1" --tag holo12 ); }
step "holo12 MiDaS indoor (all methods)"  holo12 config_holo360d_indoor.yaml
step "holo12 MiDaS outdoor (all methods)" holo12 config_holo360d_outdoor.yaml
step "holo12 diagnostic, indoor (80 frames)" python scripts/diagnose_reanchor.py \
    --config 3_structured3d_benchmark/config_holo360d_indoor.yaml --max_scenes 80 --tag holo12

step "Stages ${STAGES_REST:-E G H I D}" env STAGES="${STAGES_REST:-E G H I D}" bash scripts/run_next_experiments.sh run
log "🎉 follow-up sequence finished."
