#!/usr/bin/env bash
# ==============================================================================
# Policy experiments, kept apart from every headline result (all outputs under results/policy_comparison/):
#
#   scripts/run_policies.sh start | status | stop | run
#
# Stages (env STAGES, default "e2e_allloo same_domain analysis"); finished files are skipped, FORCE=1 reruns:
#   e2e_allloo   the combined correction pipeline with the ALL-SETS leave-one-out policy (fixes chosen on every other set incl.
#                Stanford2D3D and NYC) on the same frames as the headline runs: core sets N_E2E_CORE (100), external sets in full.
#                -> results/policy_comparison/e2e_allloo/correction_<model>_<set>.json
#   same_domain  full capture-fault study on Stanford2D3D (N_SD_STANFORD, 150) and NYC (N_SD_NYC, 147), own tag sd_<model>_<set>,
#                -> results/policy_comparison/same_domain/study_sd_<model>_<set>.json  (the 40-frame headline studies are untouched)
#   analysis     scripts/same_domain_analysis.py (room / block split, in-domain vs core policy) and scripts/policy_e2e_compare.py
#                (headline vs all_loo, frames matched by id); writes results/policy_comparison/finished_runs.md
# Env: MODELS (default "midas dap da360 da2"), CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME. Nothing is committed.
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results/policy_comparison
MODELS="${MODELS:-midas dap da360 da2}"
STAGES="${STAGES:-e2e_allloo same_domain analysis}"
N_E2E_CORE="${N_E2E_CORE:-100}"; N_SD_STANFORD="${N_SD_STANFORD:-150}"; N_SD_NYC="${N_SD_NYC:-147}"
E2E=results/policy_comparison/e2e_allloo
SD=results/policy_comparison/same_domain
FAILED=()
say() { echo "[$(date +'%F %T')] $*"; case "$*" in *❌*) FAILED+=("$*");; esac; }
cfg_of() {
    local m="$1" d="$2"
    if [ "$m" = dap ]; then
        case "$d" in s3) echo "config_dap.yaml";; panox) echo "config_dap_panox.yaml";; holo_in) echo "config_dap_holo360d_indoor.yaml";; holo_out) echo "config_dap_holo360d_outdoor.yaml";; stanford) echo "config_dap_stanford2d3d.yaml";; nyc) echo "config_dap_nyc.yaml";; esac
    else
        case "$d" in s3) echo "config.yaml";; panox) echo "config_panox.yaml";; holo_in) echo "config_holo360d_indoor.yaml";; holo_out) echo "config_holo360d_outdoor.yaml";; stanford) echo "config_stanford2d3d.yaml";; nyc) echo "config_nyc.yaml";; esac
    fi
}
model_sets() { case "$1" in da360|da2) echo "--set model.name=$1";; *) echo "";; esac; }
data_ok() { case "$1" in s3) [ -f data/structured3d/test.txt ];; panox) [ -f data/panox/test.txt ];; holo_*) [ -f data/holo360d/test.txt ];;
    stanford) [ -f data/stanford2d3d/test.txt ];; nyc) [ -f data/nyc_dap/test.txt ];; esac; }
list_len() { case "$1" in stanford) f=data/stanford2d3d/test.txt;; nyc) f=data/nyc_dap/test.txt;; *) echo 100000; return;; esac
    python -c "print(sum(1 for l in open('$f') if l.strip()))"; }
# have_rows FILE MIN: the JSON exists and has at least MIN rows
have_rows() { [ "${FORCE:-0}" != 1 ] && [ -f "$1" ] && python - "$1" "$2" <<'PY'
import json, sys
sys.exit(0 if len(json.load(open(sys.argv[1]))["rows"]) >= int(sys.argv[2]) else 1)
PY
}
do_run() {
    CONDA_SH="${CONDA_SH:-$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" MPLCONFIGDIR="/tmp/matplotlib_$$"
    export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}" HF_HUB_OFFLINE=1
    say "🚀 Policy experiments | stages: $STAGES | models: $MODELS"
    for ST in $STAGES; do
        case "$ST" in
        e2e_allloo)
            say "=============== e2e_allloo ==============="
            for m in $MODELS; do for d in s3 panox holo_in holo_out stanford nyc; do
                data_ok $d || { say "skip $d: no list"; continue; }
                [ -f "results/study_${m}_${d}.json" ] || { say "skip $m $d: no study"; continue; }
                n=$N_E2E_CORE; case $d in stanford|nyc) n=$(list_len $d);; esac
                have_rows "$E2E/correction_${m}_${d}.json" "$n" && { say "have $m $d"; continue; }
                sp=all; [ $d = s3 ] && sp=eval
                t0=$(date +%s); say ">>> e2e all_loo $m $d (N=$n)"
                if python scripts/run_correction.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --tag "${m}_${d}" --split $sp \
                    --max_scenes "$n" --model_key $m --dataset_key $d --policy_mode all_loo --out_dir "$E2E" $(model_sets $m); then
                    say "✅ e2e $m $d ($(( $(date +%s) - t0 )) s)"; else say "❌ e2e $m $d FAILED"; fi
            done; done ;;
        same_domain)
            say "=============== same_domain ==============="
            for m in $MODELS; do for d in stanford nyc; do
                data_ok $d || { say "skip $d: no list"; continue; }
                n=$N_SD_STANFORD; [ $d = nyc ] && n=$N_SD_NYC
                have_rows "$SD/study_sd_${m}_${d}.json" "$(python -c "print(min($n, $(list_len $d)))")" && { say "have sd $m $d"; continue; }
                t0=$(date +%s); say ">>> study sd_${m}_${d} (N=$n)"
                if python scripts/distortion_study.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --tag "sd_${m}_${d}" --split all \
                    --max_scenes "$n" --examples 0 --out_dir "$SD" $(model_sets $m); then
                    say "✅ sd $m $d ($(( $(date +%s) - t0 )) s)"; else say "❌ sd $m $d FAILED"; fi
            done; done ;;
        analysis)
            say "=============== analysis ==============="
            python scripts/same_domain_analysis.py > /dev/null && say "✅ same-domain analysis" || say "❌ same-domain analysis FAILED"
            python scripts/policy_e2e_compare.py > /dev/null && say "✅ e2e comparison" || say "❌ e2e comparison FAILED" ;;
        esac
    done
    { echo "# Finished: policy experiments"; echo; echo "Completed $(date +'%F %T'). Stages: $STAGES. Models: $MODELS."; echo
      echo "Failed steps: ${#FAILED[@]}"; for f in ${FAILED[@]+"${FAILED[@]}"}; do echo "* $f"; done
      echo; echo "Results: results/policy_comparison/{E2E_ALLLOO.md,same_domain/SAME_DOMAIN.md}. Headline results untouched. Nothing was committed."; } > results/policy_comparison/finished_runs.md
    say "🎉 Policy experiments finished (results/policy_comparison/finished_runs.md)."
}
pids() { pgrep -f "$AUR/scripts/run_policies.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    run) do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running"; exit 1; }
        LOG="$AUR/logs/policies_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_policies.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING" || say "Not running."
        L="$(ls -t logs/policies_*.log 2>/dev/null | head -1)"; [ -n "$L" ] && { grep -E "✅|❌|🎉|=====" "$L" | tail -30 | sed 's/^/    /'; tail -2 "$L" | sed 's/^/    /'; } ;;
    stop)
        for p in $(pids); do kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p"; done
        pkill -f "scripts/run_correction.py" 2>/dev/null; pkill -f "scripts/distortion_study.py" 2>/dev/null
        say "Stopped." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
