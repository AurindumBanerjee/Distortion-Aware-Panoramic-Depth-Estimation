#!/usr/bin/env bash
# ==============================================================================
# Queue of the follow-up experiments (run AFTER the corrected suite). One command, sequential, detached.
#
#   scripts/run_next_experiments.sh start     launch detached (logs/next_experiments_<ts>.log)
#   scripts/run_next_experiments.sh status    running? + per-stage ✅/❌ + last lines
#   scripts/run_next_experiments.sh stop      stop it
#   scripts/run_next_experiments.sh run       run in the foreground (what `start` calls)
#
# Stages (env STAGES="A B C D", default all; a failing stage never blocks the next one):
#   A  DAP with the patches (gate_lat + log-scale re-anchor): series 2, series 3 Structured3D, series 3 PanoX.
#      Written to outputs_dap_gated / outputs_dap_panox_gated (+ benchmark "..._dap_gated"), so the earlier
#      un-gated DAP outputs stay available for comparison.
#   B  Holo360D, indoor + outdoor, MiDaS + DAP (needs data/holo360d; split lists are built if missing).
#   C  Möbius ablation: rotation-only / dilation-only / full  x  gate off/on  x  MiDaS/DAP  x  S3/PanoX
#      (ABL_N scenes each, default 60; Baseline + Method2 + yaw control only).
#   D  results/SUMMARY_<ts>.md with cluster-robust statistics over every outputs*/ folder.
#   E  Pared-down + self-validating Method 2 and the Method1-on-rotated-view hybrid, MiDaS only, on
#      Structured3D, PanoX and Holo360D indoor/outdoor (ESC = scenes cap, default all):
#        rotonly   mobius_tta.preset=rotation_only                      (no dilation passes)
#        rotguard  rotation_only + fit_guard {tau 0.5, a_max 4}          (label-free pass validation)
#        m1rot     Method 1 / Tangent_Spatial with method1.polar_source=rotated_erp (gradient-domain fusion of the
#                  Möbius-rotated pass instead of a tangent crop)
#        m1cos     Method 1 / Tangent_Spatial with the exact 3-term tangent alignment (method1.shift_model=cos); the
#                  earlier Method 1 numbers used the 2-term fit (shift_model=none)
#   F  scripts/diagnose_reanchor.py on the same four datasets (DIAG_N frames, default 40): intrinsic vs realised
#      gain of the rotated pass, anchor loss, and which label-free signal predicts harm.
#   Stage D should be re-run last to include E (STAGES="E F D").
#
# Other env: CONDA_ENV (RL), CONDA_SH, CUDA_VISIBLE_DEVICES, MAX_SCENES (stage A/B series 3 limit), ABL_N.
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results
PID_FILE="$AUR/logs/next_experiments.pid"
STAGES="${STAGES:-A B C D}"   # E and F are opt-in: STAGES="E F D"
ABL_N="${ABL_N:-60}"
DIAG_N="${DIAG_N:-40}"

say() { echo "[$(date +'%F %T')] $*"; }

do_run() {
    CONDA_SH="${CONDA_SH:-/DATA/Aurindum/conda/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
    export MPLCONFIGDIR="/tmp/matplotlib_$$"
    say "🚀 Follow-up experiments | stages: $STAGES | python: $(command -v python) | env: ${CONDA_DEFAULT_ENV:-none}"
    python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" || { say "❌ CUDA not available; aborting"; exit 1; }
    local have_dap=1 have_midas=1
    { [ -f weights/dap/model.pth ] && [ -d third_party/DAP/networks ]; } || { have_dap=0; say "⚠️  DAP weights/repo missing: DAP runs are skipped"; }
    [ -f weights/dpt_hybrid_384.pt ] || { have_midas=0; say "⚠️  MiDaS weights missing: MiDaS runs are skipped"; }
    local ms=""; [ -n "${MAX_SCENES:-}" ] && ms="--max_scenes $MAX_SCENES"

    ok_cfg() { case "$1" in *dap*) [ "$have_dap" = 1 ];; *) [ "$have_midas" = 1 ];; esac; }
    step() {  # step <label> <dir> <python args...>
        local label="$1" dir="$2"; shift 2
        local t0; t0=$(date +%s)
        say ">>> $label"
        if (cd "$AUR/$dir" && python run.py "$@"); then say "✅ $label ($(( $(date +%s) - t0 )) s)"; else say "❌ $label FAILED"; fi
    }

    for ST in $STAGES; do
        case "$ST" in
        A)  say "=============== Stage A: DAP with gate_lat + logscale re-anchor ==============="
            if [ "$have_dap" = 1 ]; then
                step "A1 series 2 DAP (gated)"            2_mobius_tta_ensembling  --config config_dap.yaml --tag gated
                step "A2 series 3 Structured3D DAP (gated)" 3_structured3d_benchmark --config config_dap.yaml --tag gated $ms
                [ -f data/panox/test.txt ] && step "A3 series 3 PanoX DAP (gated)" 3_structured3d_benchmark --config config_dap_panox.yaml --tag gated $ms
            else say "skip stage A (no DAP)"; fi ;;
        B)  say "=============== Stage B: Holo360D (real LiDAR-mesh GT) ==============="
            if [ -d data/holo360d ]; then
                [ -f data/holo360d/indoor.txt ] || python scripts/make_holo360d_list.py --root data/holo360d
                for KIND in indoor outdoor; do for CFG in config_holo360d_$KIND.yaml config_dap_holo360d_$KIND.yaml; do
                    ok_cfg "$CFG" && step "B Holo360D $KIND [$CFG]" 3_structured3d_benchmark --config "$CFG" $ms
                done; done
            else say "❌ data/holo360d not found (copy it to $AUR/data/holo360d); stage B skipped"; fi ;;
        C)  say "=============== Stage C: Möbius ablation ($ABL_N scenes per variant) ==============="
            if [ "$have_dap" = 1 ] && [ "$have_midas" = 1 ]; then
                # the ablation script ends with collect_results.py; failures inside it are logged by python
                bash scripts/run_mobius_ablation.sh both "$ABL_N" && say "✅ C ablation" || say "❌ C ablation FAILED"
            else say "skip stage C (needs both MiDaS and DAP weights)"; fi ;;
        E)  say "=============== Stage E: rotation-only / fit-guard / Method 1 on the rotated view (MiDaS) ==============="
            if [ "$have_midas" = 1 ]; then
                local es=""; [ -n "${ESC:-}" ] && es="--max_scenes $ESC --set data.subset=spread"
                for CFG in config.yaml config_panox.yaml config_holo360d_indoor.yaml config_holo360d_outdoor.yaml; do
                    case "$CFG" in config_panox.yaml) [ -f data/panox/test.txt ] || continue;; config_holo*) [ -f data/holo360d/test.txt ] || continue;; esac
                    step "E1 rotation-only [$CFG]" 3_structured3d_benchmark --config "$CFG" --tag rotonly $es \
                        --set "mobius_tta.preset=rotation_only" --set "evaluation.methods=[Method2_MobiusTTA,Control_YawEnsemble]"
                    step "E2 rotation-only + fit_guard [$CFG]" 3_structured3d_benchmark --config "$CFG" --tag rotguard $es \
                        --set "mobius_tta.preset=rotation_only" --set "mobius_tta.fit_guard={tau: 0.5, a_max: 4.0}" \
                        --set "evaluation.methods=[Method2_MobiusTTA]"
                    step "E4 Method 1 tangent, exact 3-term alignment [$CFG]" 3_structured3d_benchmark --config "$CFG" --tag m1cos $es \
                        --set "method1.shift_model=cos" --set "evaluation.methods=[Tangent_Spatial,Method1_GradientFusion]"
                    step "E3 Method 1 on rotated view [$CFG]" 3_structured3d_benchmark --config "$CFG" --tag m1rot $es \
                        --set "method1.polar_source=rotated_erp" --set "evaluation.methods=[Tangent_Spatial,Method1_GradientFusion]"
                done
            else say "skip stage E (no MiDaS)"; fi ;;
        F)  say "=============== Stage F: re-anchor diagnostics ==============="
            if [ "$have_midas" = 1 ]; then
                for pair in "s3:3_structured3d_benchmark/config.yaml:data/structured3d" "panox:3_structured3d_benchmark/config_panox.yaml:data/panox" \
                            "holo_indoor:3_structured3d_benchmark/config_holo360d_indoor.yaml:data/holo360d" "holo_outdoor:3_structured3d_benchmark/config_holo360d_outdoor.yaml:data/holo360d"; do
                    IFS=: read -r tag cfg dd <<< "$pair"
                    [ -d "$dd" ] || { say "skip diagnose $tag (no $dd)"; continue; }
                    python scripts/diagnose_reanchor.py --config "$cfg" --max_scenes "$DIAG_N" --tag "$tag" && say "✅ F diagnose $tag" || say "❌ F diagnose $tag FAILED"
                done
            else say "skip stage F (no MiDaS)"; fi ;;
        D)  say "=============== Stage D: cluster-robust summary ==============="
            python scripts/collect_results.py && say "✅ D summary written" || say "❌ D summary FAILED" ;;
        *)  say "unknown stage $ST" ;;
        esac
    done
    say "🎉 Follow-up experiments finished."
}

pids() { pgrep -f "$AUR/scripts/run_next_experiments.sh run" 2>/dev/null | grep -v "^$$\$" || true; }

case "${1:-status}" in
    run)    do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running (PID(s): $(pids | tr '\n' ' '))"; exit 1; }
        LOG="$AUR/logs/next_experiments_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_next_experiments.sh" run > "$LOG" 2>&1 < /dev/null &
        echo $! > "$PID_FILE"
        say "Started PID $(cat "$PID_FILE"). Log: $LOG   (status: scripts/run_next_experiments.sh status)" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING (PID(s): $(pids | tr '\n' ' '))" || say "Not running."
        L="$(ls -t logs/next_experiments_*.log 2>/dev/null | head -1)"
        if [ -n "$L" ]; then say "Log: $L"; grep -E "Stage|✅|❌|⚠️|🎉" "$L" | sed 's/^/    /'; echo "    --- last lines ---"; tail -4 "$L" | sed 's/^/    /'; fi ;;
    stop)
        P="$(pids)"; [ -z "$P" ] && { say "Not running."; exit 0; }
        for p in $P; do kill -TERM -- "-$p" 2>/dev/null || { pkill -TERM -P "$p" 2>/dev/null; kill -TERM "$p" 2>/dev/null; }; done
        say "Stopped (process group terminated)." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
