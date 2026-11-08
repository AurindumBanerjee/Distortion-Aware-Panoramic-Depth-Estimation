#!/usr/bin/env bash
# ==============================================================================
# Last runs before submission, in priority order. Everything new goes to its own files; no headline result is overwritten
# except results/correction_da2m_<core>.json (DA2 under the median fit, raised from 40 to N_CORE frames).
#
#   scripts/run_submission.sh start | status | stop | run          (DRY=1 ... run  prints every command and runs nothing)
#
# Stages (env STAGES, default "da2both diag strict analysis"; add study100 and a second rule for the long version); finished files are skipped, FORCE=1 reruns:
#   da2both    DA2 under the median-fit protocol next to the existing least-squares runs (PANO_ALIGN_MODE=median, tag da2m):
#              (a) correction on the four core sets with N_CORE (100) frames, replacing the 40-frame da2m files;
#              (b) rotation and dilation sweeps (N_SWEEP, 80) on the four core sets and NYC, tags <mode>_da2m_<set>
#                  (FLIP_MEDIAN=1 adds the flip sweep).
#   diag       nadir + JPEG diagnosis (scripts/nadir_jpeg_diagnosis.py): why DAP gets no gain on NYC although the cap is detected.
#              DAP on NYC (N_DIAG_NYC, 147), Holo outdoor (71), Structured3D / PanoX / Holo indoor / Stanford2D3D (N_DIAG, 40);
#              MiDaS, DA360, DA2 (lsq) and DA2 (median, tag da2m) on NYC and Structured3D (N_DIAG_OTHER, 40).
#              -> results/diag/NADIR_JPEG_<tag>.md and .json
#   strict     stricter do-no-harm rules, end to end on Stanford2D3D (N_STRICT_STANFORD, 100) and NYC (all frames), all models,
#              policy chosen on the four core sets only. RULES (default "s5w70"; add s5w80 for the second rule) = s<min_gain %>w<min_win %>.
#              -> results/threshold_sweep/e2e_<rule>/ (separate from the headline runs)
#   study100   capture-fault study with 100 frames on the four core sets (policy-stability check: is the policy the same as from
#              the 40-frame studies?). -> results/policy_stability/study_s100_<model>_<set>.json   (slow; last)
#   analysis   CPU only: threshold_sweep.py, da2_protocol_report.py, strict_compare.py, policy_stability.py, final_summary.py,
#              external_report.py, make_figures.py.
# Env: MODELS (default "midas dap da360 da2"), N_CORE, N_SWEEP, N_DIAG, N_DIAG_NYC, N_DIAG_OTHER, N_STRICT_STANFORD, RULES, N_S100,
#      CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME. Writes results/finished_submission_<stages>.md (so that parallel shells do not overwrite each other). Nothing is committed.
# ==============================================================================
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
mkdir -p logs results
MODELS="${MODELS:-midas dap da360 da2}"
STAGES="${STAGES:-da2both diag strict analysis}"
N_CORE="${N_CORE:-100}"; N_SWEEP="${N_SWEEP:-80}"; N_DIAG="${N_DIAG:-40}"; N_DIAG_NYC="${N_DIAG_NYC:-147}"; N_DIAG_OTHER="${N_DIAG_OTHER:-40}"
N_STRICT_STANFORD="${N_STRICT_STANFORD:-100}"; RULES="${RULES:-s5w70}"; N_S100="${N_S100:-100}"
HOLO_OUT_MAX="${HOLO_OUT_MAX:-71}"
CORE="s3 panox holo_in holo_out"
FAILED=()
say() { echo "[$(date +'%F %T')] $*"; case "$*" in *❌*) FAILED+=("$*");; esac; }
py() { if [ "${DRY:-0}" = 1 ]; then echo "    DRY: python $*"; else python "$@"; fi; }
cfg_of() {
    local m="$1" d="$2"
    if [ "$m" = dap ]; then
        case "$d" in s3) echo "config_dap.yaml";; panox) echo "config_dap_panox.yaml";; holo_in) echo "config_dap_holo360d_indoor.yaml";; holo_out) echo "config_dap_holo360d_outdoor.yaml";; stanford) echo "config_dap_stanford2d3d.yaml";; nyc) echo "config_dap_nyc.yaml";; esac
    else
        case "$d" in s3) echo "config.yaml";; panox) echo "config_panox.yaml";; holo_in) echo "config_holo360d_indoor.yaml";; holo_out) echo "config_holo360d_outdoor.yaml";; stanford) echo "config_stanford2d3d.yaml";; nyc) echo "config_nyc.yaml";; esac
    fi
}
model_sets() { case "$1" in da360|da2|da2m) echo "--set model.name=${1%m}";; *) echo "";; esac; }
sweep_sets() { case "$1" in da360|da2|da2m) echo "--set model.name=${1%m} --set method1.polar_source=rotated_erp";; *) echo "";; esac; }
data_ok() { [ "${DRY:-0}" = 1 ] && return 0; case "$1" in s3) [ -f data/structured3d/test.txt ];; panox) [ -f data/panox/test.txt ];; holo_*) [ -f data/holo360d/test.txt ];;
    stanford) [ -f data/stanford2d3d/test.txt ];; nyc) [ -f data/nyc_dap/test.txt ];; esac; }
split_of() { [ "$1" = s3 ] && echo eval || echo all; }
list_len() { case "$1" in stanford) f=data/stanford2d3d/test.txt;; nyc) f=data/nyc_dap/test.txt;; *) echo 100000; return;; esac
    if [ "${DRY:-0}" = 1 ]; then echo 147; else python -c "print(sum(1 for l in open('$f') if l.strip()))"; fi; }
# frames a run can have at most: Holo outdoor has HOLO_OUT_MAX frames, the external sets their list length
cap_n() { local n="$1" d="$2"; case "$d" in holo_out) [ "$n" -gt "$HOLO_OUT_MAX" ] && n=$HOLO_OUT_MAX;; stanford|nyc) local l; l=$(list_len $d); [ "$n" -gt "$l" ] && n=$l;; esac; echo "$n"; }
# have_rows FILE MIN: the JSON exists and has at least MIN rows
have_rows() { [ "${DRY:-0}" != 1 ] && [ "${FORCE:-0}" != 1 ] && [ -f "$1" ] && python - "$1" "$2" <<'PY'
import json, sys
sys.exit(0 if len(json.load(open(sys.argv[1]))["rows"]) >= int(sys.argv[2]) else 1)
PY
}
step() {  # step LABEL cmd...   (runs, times and records success / failure)
    local label="$1"; shift; local t0; t0=$(date +%s); say ">>> $label"
    if "$@"; then say "✅ $label ($(( $(date +%s) - t0 )) s)"; else say "❌ $label FAILED"; fi
}

stage_da2both() {
    say "=============== da2both (DA2, median-fit protocol) ==============="
    export PANO_ALIGN_MODE=median
    for d in $CORE; do
        data_ok $d || { say "skip $d: no list"; continue; }
        [ -f "results/study_da2m_${d}.json" ] || [ "${DRY:-0}" = 1 ] || { say "skip da2m $d: no median-fit study"; continue; }
        n=$(cap_n "$N_CORE" $d)
        have_rows "results/correction_da2m_${d}.json" "$n" && { say "have correction da2m $d"; continue; }
        step "correction da2m $d (N=$n)" py scripts/run_correction.py --config "3_structured3d_benchmark/$(cfg_of da2 $d)" --tag "da2m_${d}" \
            --split "$(split_of $d)" --max_scenes "$n" --model_key da2m --dataset_key "$d" $(model_sets da2m)
    done
    local modes="rotation dilation"; [ "${FLIP_MEDIAN:-0}" = 1 ] && modes="$modes flip"
    for d in $CORE nyc; do
        data_ok $d || continue
        sp=all; [ "$d" = s3 ] && sp=eval
        for mode in $modes; do
            tag="${mode}_da2m_${d}_${sp}"
            [ "${DRY:-0}" != 1 ] && [ -f "results/sweep_${tag}.json" ] && [ "${FORCE:-0}" != 1 ] && { say "have sweep $tag"; continue; }
            step "sweep $tag" py scripts/distortion_sweep.py --config "3_structured3d_benchmark/$(cfg_of da2 $d)" --mode $mode --tag "$tag" \
                --split $sp --max_scenes "$N_SWEEP" $(sweep_sets da2m)
        done
    done
    unset PANO_ALIGN_MODE
}

diag_one() {  # diag_one MODEL DATASET N [median]
    local m="$1" d="$2" n; n=$(cap_n "$3" "$2"); local tag="${m}_${d}"
    [ "${4:-}" = median ] && { tag="da2m_${d}"; export PANO_ALIGN_MODE=median; }
    data_ok $d || { say "skip $d: no list"; unset PANO_ALIGN_MODE; return; }
    have_rows "results/diag/nadir_jpeg_${tag}.json" "$n" && { say "have diag $tag"; unset PANO_ALIGN_MODE; return; }
    step "diag $tag (N=$n)" py scripts/nadir_jpeg_diagnosis.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --tag "$tag" \
        --split "$(split_of $d)" --max_scenes "$n" $(model_sets $m)
    unset PANO_ALIGN_MODE
}
stage_diag() {
    say "=============== diag (nadir + JPEG, why no gain for DAP on NYC) ==============="
    case " $MODELS " in *" dap "*)
        diag_one dap nyc "$N_DIAG_NYC"
        diag_one dap holo_out 71
        for d in s3 panox holo_in stanford; do diag_one dap $d "$N_DIAG"; done ;; esac
    for m in midas da360 da2; do case " $MODELS " in *" $m "*) ;; *) continue;; esac
        for d in nyc s3; do diag_one $m $d "$N_DIAG_OTHER"; done
    done
    case " $MODELS " in *" da2 "*) diag_one da2 nyc "$N_DIAG_OTHER" median ;; esac
}

stage_strict() {
    say "=============== strict (stricter do-no-harm rules, end to end, external sets) ==============="
    for rule in $RULES; do
        g="${rule#s}"; g="${g%%w*}"; w="${rule##*w}"
        mg=$(python -c "print($g/100)"); mw=$(python -c "print($w/100)")
        out="results/threshold_sweep/e2e_${rule}"
        for d in stanford nyc; do for m in $MODELS; do
            data_ok $d || continue
            [ -f "results/study_${m}_${d}.json" ] || [ "${DRY:-0}" = 1 ] || { say "skip $m $d: no study"; continue; }
            n=$(cap_n "$N_STRICT_STANFORD" $d); [ $d = nyc ] && n=$(list_len nyc)
            have_rows "$out/correction_${m}_${d}.json" "$n" && { say "have $rule $m $d"; continue; }
            step "strict $rule $m $d (N=$n)" py scripts/run_correction.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --tag "${m}_${d}" --split all \
                --max_scenes "$n" --model_key $m --dataset_key $d --min_gain "$mg" --min_win "$mw" --out_dir "$out" $(model_sets $m)
        done; done
    done
}

stage_study100() {
    say "=============== study100 (policy stability, 100-frame studies on the core sets) ==============="
    for m in $MODELS; do for d in $CORE; do
        data_ok $d || continue
        n=$(cap_n "$N_S100" $d)
        have_rows "results/policy_stability/study_s100_${m}_${d}.json" "$n" && { say "have s100 $m $d"; continue; }
        step "study s100_${m}_${d} (N=$n)" py scripts/distortion_study.py --config "3_structured3d_benchmark/$(cfg_of $m $d)" --tag "s100_${m}_${d}" \
            --split "$(split_of $d)" --max_scenes "$n" --examples 0 --out_dir results/policy_stability $(model_sets $m)
    done; done
}

stage_analysis() {
    say "=============== analysis (CPU) ==============="
    step "threshold sweep" py scripts/threshold_sweep.py
    step "DA2 protocols" py scripts/da2_protocol_report.py
    step "strict end to end" py scripts/strict_compare.py
    step "policy stability" py scripts/policy_stability.py
    step "final summary" py scripts/final_summary.py
    step "external report" py scripts/external_report.py
    step "figures" py scripts/make_figures.py
}

do_run() {
    CONDA_SH="${CONDA_SH:-$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh}"
    if [ -f "$CONDA_SH" ]; then set +u; source "$CONDA_SH"; conda activate "${CONDA_ENV:-RL}"; set -u; fi
    export PYTHONUNBUFFERED=1 OPENCV_IO_ENABLE_OPENEXR=1 CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" MPLCONFIGDIR="/tmp/matplotlib_$$"
    export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}" HF_HUB_OFFLINE=1
    say "🚀 Submission runs | stages: $STAGES | models: $MODELS"
    for ST in $STAGES; do
        case "$ST" in
            da2both) stage_da2both ;; diag) stage_diag ;; strict) stage_strict ;; study100) stage_study100 ;; analysis) stage_analysis ;;
            *) say "❌ unknown stage $ST" ;;
        esac
    done
    { echo "# Finished: submission runs"; echo; echo "Completed $(date +'%F %T'). Stages: $STAGES. Models: $MODELS."; echo
      echo "Failed steps: ${#FAILED[@]}"; for f in ${FAILED[@]+"${FAILED[@]}"}; do echo "* $f"; done
      echo; echo "Results: results/DA2_PROTOCOLS.md, results/diag/NADIR_JPEG_*.md, results/threshold_sweep/{THRESHOLDS,E2E_STRICT}.md,"
      echo "results/policy_stability/POLICY_STABILITY.md, results/FINAL_ablations.md. Nothing was committed."; } > "results/finished_submission_${STAGES// /_}.md"
    say "🎉 Submission runs finished (results/finished_submission_${STAGES// /_}.md). Commit results/."
}
pids() { pgrep -f "$AUR/scripts/run_submission.sh run" 2>/dev/null | grep -v "^$$\$" || true; }
case "${1:-status}" in
    run) do_run ;;
    start)
        [ -n "$(pids)" ] && { say "Already running"; exit 1; }
        LOG="$AUR/logs/submission_$(date +%Y%m%d_%H%M%S).log"
        setsid nohup bash "$AUR/scripts/run_submission.sh" run > "$LOG" 2>&1 < /dev/null &
        say "Started PID $!. Log: $LOG" ;;
    status)
        [ -n "$(pids)" ] && say "RUNNING" || say "Not running."
        L="$(ls -t logs/submission_*.log 2>/dev/null | head -1)"; [ -n "$L" ] && { grep -E "✅|❌|🎉|=====" "$L" | tail -30 | sed 's/^/    /'; tail -2 "$L" | sed 's/^/    /'; } ;;
    stop)
        for p in $(pids); do kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p"; done
        pkill -f "scripts/run_correction.py" 2>/dev/null; pkill -f "scripts/distortion_study.py" 2>/dev/null
        pkill -f "scripts/distortion_sweep.py" 2>/dev/null; pkill -f "scripts/nadir_jpeg_diagnosis.py" 2>/dev/null
        say "Stopped." ;;
    *) echo "usage: $0 {start|status|stop|run}"; exit 2 ;;
esac
