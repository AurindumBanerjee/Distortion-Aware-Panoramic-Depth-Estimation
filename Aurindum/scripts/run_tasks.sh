#!/usr/bin/env bash
# ==============================================================================
# One driver for the current task checklist (run from Aurindum/ on the GPU server).
#
#   scripts/run_tasks.sh setup        checks + data lists (foreground, minutes)
#   scripts/run_tasks.sh smoke        2 frames per model x dataset through the distortion study (foreground)
#   scripts/run_tasks.sh start        detached: distortion study, then round 3b, then the summaries
#   scripts/run_tasks.sh status       progress of the detached run
#   scripts/run_tasks.sh stop         stop it
#   scripts/run_tasks.sh run          what `start` runs, in the foreground
#
# Env (all optional):
#   STANFORD_ROOT  default data/stanford2d3d   (needs area_5a/pano/{rgb,depth} ...)
#   NYC_RGB, NYC_DEPTH  source folders nyc_raw_images_panorama / nyc_distance_panorama_npy; linked into data/nyc_dap
#   MODELS (default "midas dap da360 da2"), SETS (default "s3 panox holo_in holo_out"; stanford / nyc are opt-in), N (default 40)
#   SKIP_ROUND3B=1 to run only the distortion study. CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME as usual.
# Nothing is committed: when it finishes, commit results/ yourself.
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results data
say() { echo "[$(date +'%F %T')] $*"; }
env_up() {
    CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" MPLCONFIGDIR="/tmp/matplotlib_$$"
    export HF_HOME="${HF_HOME:-/DATA/Aurindum/hf_home}" HF_HUB_OFFLINE=1
}

do_setup() {
    env_up
    local ok=1
    say "== 1. tests"
    local tlog; tlog=$(mktemp)
    if python -m pytest tests -q -p no:cacheprovider > "$tlog" 2>&1; then tail -1 "$tlog"; else tail -15 "$tlog"; say "❌ tests failed: fix before running anything"; ok=0; fi
    rm -f "$tlog"
    say "== 2. GPU and models"
    python -c "import torch,sys; print('CUDA:', torch.cuda.is_available()); sys.exit(0 if torch.cuda.is_available() else 1)" || { say "❌ no CUDA"; ok=0; }
    [ -f weights/dpt_hybrid_384.pt ] && say "✅ MiDaS" || say "⚠️  MiDaS weights missing (weights/dpt_hybrid_384.pt)"
    { [ -f weights/dap/model.pth ] && [ -d third_party/DAP/networks ]; } && say "✅ DAP" || say "⚠️  DAP missing (skipped later)"
    { [ -f weights/da360/DA360_large.pth ] && [ -d third_party/DA360/networks ]; } && say "✅ DA360" || say "⚠️  DA360 missing (skipped later)"
    python -c "import sys; sys.path.insert(0,'third_party/DA2/src'); import da2.model.spherevit" 2>/dev/null && [ -f third_party/DA2/configs/infer.json ] \
        && say "✅ DA^2 code (weights come from \$HF_HOME offline cache)" || say "⚠️  DA^2 missing (skipped later)"
    say "== 3. datasets"
    for d in structured3d panox holo360d; do [ -f data/$d/test.txt ] && say "✅ $d ($(wc -l < data/$d/test.txt) frames)" || say "⚠️  data/$d/test.txt missing"; done
    local SR="${STANFORD_ROOT:-data/stanford2d3d}"
    if [ -d "$SR/area_5a" ] || [ -d "$SR/area_5b" ]; then
        [ "$SR" != data/stanford2d3d ] && [ ! -e data/stanford2d3d ] && ln -s "$(cd "$SR" && pwd)" data/stanford2d3d
        python scripts/make_stanford_list.py --root data/stanford2d3d --areas area_5a area_5b --out test.txt && say "✅ stanford2d3d list"
    else say "·  Stanford2D3D not present (optional, not in the default sets)"; fi
    if [ -n "${NYC_RGB:-}" ] && [ -n "${NYC_DEPTH:-}" ]; then
        mkdir -p data/nyc_dap
        [ -e data/nyc_dap/rgb ] || ln -s "$(cd "$NYC_RGB" && pwd)" data/nyc_dap/rgb
        [ -e data/nyc_dap/depth ] || ln -s "$(cd "$NYC_DEPTH" && pwd)" data/nyc_dap/depth
    fi
    if [ -d data/nyc_dap/rgb ] && [ -d data/nyc_dap/depth ]; then
        python scripts/make_nyc_list.py --root data/nyc_dap && say "✅ nyc_dap list"
    else say "·  NYC not present (optional, not in the default sets)"; fi
    [ "$ok" = 1 ] && say "🎉 setup OK" || { say "❌ setup has blocking problems (above)"; return 1; }
}

do_smoke() {
    env_up
    say "== smoke: 2 frames per model x dataset, all faults"
    N=2 TAG_PREFIX=smoke_ bash scripts/run_distortion_study.sh run 2>&1 | grep -E "✅|❌|skip|🎉"
    say "removing smoke outputs (only results/*smoke_*; real results are never touched)"
    rm -rf results/STUDY_smoke_* results/study_smoke_*
}

do_run() {
    env_up
    say "🚀 tasks: distortion study$([ "${SKIP_ROUND3B:-0}" = 1 ] || echo ', round 3b'), summaries"
    do_setup || { say "❌ setup failed, nothing run"; exit 1; }
    local t0; t0=$(date +%s)
    bash scripts/run_distortion_study.sh run && say "✅ distortion study ($(( ($(date +%s) - t0) / 60 )) min)" || say "❌ distortion study had failures (see above)"
    if [ "${SKIP_ROUND3B:-0}" != 1 ]; then
        t0=$(date +%s)
        bash scripts/run_round3b.sh run && say "✅ round 3b ($(( ($(date +%s) - t0) / 60 )) min)" || say "❌ round 3b had failures (see above)"
    fi
    python scripts/round3_report.py && python scripts/collect_results.py && say "✅ summaries"
    say "files to commit:"; git status --short results | head -40
    say "🎉 all tasks finished — commit results/ and tell Claude"
}

pids() { pgrep -f "$AUR/scripts/run_tasks.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    setup) do_setup ;;
    smoke) do_smoke ;;
    run)   do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running"; exit 1; }
        LOG="$AUR/logs/tasks_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_tasks.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG   (scripts/run_tasks.sh status)" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING" || say "Not running."
        L="$(ls -t logs/tasks_*.log 2>/dev/null | head -1)"
        [ -n "$L" ] && { say "Log: $L"; grep -E "✅|❌|⚠️|🎉|>>>" "$L" | tail -25 | sed 's/^/    /'; } ;;
    stop)
        for p in $(pids); do kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p"; done
        pkill -f "scripts/run_distortion_study.sh run" 2>/dev/null; pkill -f "scripts/run_round3b.sh run" 2>/dev/null
        say "Stopped." ;;
    *) echo "usage: $0 {setup|smoke|start|status|stop|run}"; exit 2 ;;
esac
