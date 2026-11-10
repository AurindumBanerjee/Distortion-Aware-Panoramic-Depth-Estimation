#!/usr/bin/env bash
# ==============================================================================
# Last runs before submission, in priority order. Everything new goes to its own files; no headline result is overwritten
# except artifacts/results/benchmark/correction_da2m_<core>.json (DA2 under the median fit, raised from 40 to N_CORE frames).
#
#   bash scripts/run/run_submission.sh start | status | stop | run          (DRY=1 ... run  prints every command and runs nothing)
#
# Stages (env STAGES, default "da2both diag strict analysis"; add study100 and a second rule for the long version); finished files are skipped, FORCE=1 reruns:
#   da2both    DA2 under the median-fit protocol next to the existing least-squares runs (PANO_ALIGN_MODE=median, tag da2m):
#              (a) correction on the four core sets with N_CORE (100) frames, replacing the 40-frame da2m files;
#              (b) rotation and dilation sweeps (N_SWEEP, 80) on the four core sets and NYC, tags <mode>_da2m_<set>
#                  (FLIP_MEDIAN=1 adds the flip sweep).
#   diag       nadir + JPEG diagnosis (scripts/run/nadir_jpeg_diagnosis.py): why DAP gets no gain on NYC although the cap is detected.
#              DAP on NYC (N_DIAG_NYC, 147), Holo outdoor (71), Structured3D / PanoX / Holo indoor / Stanford2D3D (N_DIAG, 40);
#              MiDaS, DA360, DA2 (lsq) and DA2 (median, tag da2m) on NYC and Structured3D (N_DIAG_OTHER, 40).
#              -> artifacts/results/benchmark/diag/NADIR_JPEG_<tag>.md and .json
#   strict     stricter do-no-harm rules, end to end on Stanford2D3D (N_STRICT_STANFORD, 100) and NYC (all frames), all models,
#              policy chosen on the four core sets only. RULES (default "s5w70"; add s5w80 for the second rule) = s<min_gain %>w<min_win %>.
#              -> artifacts/results/benchmark/threshold_sweep/e2e_<rule>/ (separate from the headline runs)
#   study100   capture-fault study with 100 frames on the four core sets (policy-stability check: is the policy the same as from
#              the 40-frame studies?). -> artifacts/results/benchmark/policy_stability/study_s100_<model>_<set>.json   (slow; last)
#   analysis   CPU only: threshold_sweep.py, da2_protocol_report.py, strict_compare.py, policy_stability.py, final_summary.py,
#              external_report.py, make_figures.py.
# Env: MODELS (default "midas dap da360 da2"), N_CORE, N_SWEEP, N_DIAG, N_DIAG_NYC, N_DIAG_OTHER, N_STRICT_STANFORD, RULES, N_S100,
#      CONDA_ENV, CONDA_SH, CUDA_VISIBLE_DEVICES, HF_HOME. Nothing is committed.
# ==============================================================================
set -uo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"
mkdir -p artifacts/logs/benchmark artifacts/results/benchmark
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
step() {
    local label="$1"; shift
    say "▶ $label"
    if "$@"; then say "✔ $label"; else say "❌ $label (exit $?)"; fi
}

run_da2both() {
    say "=== STAGE da2both (DA2 under the median-fit protocol) ==="
    for d in $CORE; do
        data_ok "$d" || { say "skip $d (no data)"; continue; }
        local n; n=$(cap_n "$N_CORE" "$d")
        have_rows "artifacts/results/benchmark/correction_da2m_${d}.json" "$n" && { say "have da2m_${d} ($n frames); skip"; continue; }
        step "correction da2m $d (N=$n)" py scripts/run/run_correction.py --config "configs/benchmark/$(cfg_of da2 $d)" --tag "da2m_${d}" \
            $(model_sets da2m) --frames "$n" --split "$(split_of $d)" --save-examples 0
    done
    local modes="rotation dilation"
    [ "${FLIP_MEDIAN:-0}" = 1 ] && modes="rotation dilation flip"
    for mode in $modes; do
        for d in $CORE nyc; do
            data_ok "$d" || { say "skip $d (no data)"; continue; }
            local n; n=$(cap_n "$N_SWEEP" "$d")
            local tag="${mode}_da2m_${d}"
            have_rows "artifacts/results/benchmark/sweep_${tag}.json" "$n" && { say "have sweep $tag ($n frames); skip"; continue; }
            step "sweep $tag" py scripts/run/distortion_sweep.py --config "configs/benchmark/$(cfg_of da2 $d)" --mode $mode --tag "$tag" \
                $(sweep_sets da2m) --frames "$n" --split "$(split_of $d)" --save-examples 0
        done
    done
}

run_diag() {
    say "=== STAGE diag (nadir + JPEG diagnosis ladder) ==="
    run_one_diag() {
        local m="$1" d="$2" n="$3"
        data_ok "$d" || { say "skip $m on $d (no data)"; return 0; }
        n=$(cap_n "$n" "$d")
        local tag="${m}_${d}"
        [ -f "artifacts/results/benchmark/diag/NADIR_JPEG_${tag}.json" ] && [ "${FORCE:-0}" != 1 ] && { say "have diag $tag; skip"; return 0; }
        step "diag $tag (N=$n)" py scripts/run/nadir_jpeg_diagnosis.py --config "configs/benchmark/$(cfg_of $m $d)" --tag "$tag" \
            $(model_sets $m) --frames "$n" --split "$(split_of $d)" --save-examples 0
    }
    for m in $MODELS; do run_one_diag "$m" nyc "$N_DIAG_NYC"; done
    [[ "$MODELS" =~ dap ]] && {
        run_one_diag dap holo_out "$N_DIAG"
        for d in s3 panox holo_in stanford; do run_one_diag dap "$d" "$N_DIAG"; done
    }
    for m in midas da360 da2 da2m; do
        [[ "$MODELS" =~ ${m%m} ]] && run_one_diag "$m" s3 "$N_DIAG_OTHER"
    done
}

run_strict() {
    say "=== STAGE strict (stricter do-no-harm rules, end-to-end on external sets) ==="
    for rule in $RULES; do
        say "--- rule $rule ---"
        for m in $MODELS; do
            for d in stanford nyc; do
                data_ok "$d" || { say "skip $m on $d (no data)"; continue; }
                local n; n=$(cap_n "$N_STRICT_STANFORD" "$d")
                local out_json="artifacts/results/benchmark/threshold_sweep/e2e_${rule}/correction_${m}_${d}.json"
                have_rows "$out_json" "$n" && { say "have $out_json ($n frames); skip"; continue; }
                step "strict $rule $m $d (N=$n)" py scripts/run/run_correction.py --config "configs/benchmark/$(cfg_of $m $d)" --tag "${m}_${d}" --split all \
                    $(model_sets $m) --frames "$n" --out-dir "artifacts/results/benchmark/threshold_sweep/e2e_${rule}" \
                    --rule-name "$rule" --save-examples 0
            done
        done
    done
}

run_study100() {
    say "=== STAGE study100 (policy-stability check, 100 frames on core sets) ==="
    for m in $MODELS; do
        for d in $CORE; do
            data_ok "$d" || { say "skip $m on $d (no data)"; continue; }
            local n; n=$(cap_n "$N_S100" "$d")
            have_rows "artifacts/results/benchmark/policy_stability/study_s100_${m}_${d}.json" "$n" && { say "have study s100_${m}_${d}; skip"; continue; }
            step "study s100_${m}_${d} (N=$n)" py scripts/run/distortion_study.py --config "configs/benchmark/$(cfg_of $m $d)" --tag "s100_${m}_${d}" \
                $(model_sets $m) --frames "$n" --split "$(split_of $d)" --out-dir artifacts/results/benchmark/policy_stability --save-examples 0
        done
    done
}

run_analysis() {
    say "=== STAGE analysis (reports and submission figures) ==="
    step "threshold sweep" py scripts/analysis/threshold_sweep.py
    step "DA2 protocols" py scripts/analysis/da2_protocol_report.py
    step "strict end to end" py scripts/analysis/strict_compare.py
    step "policy stability" py scripts/analysis/policy_stability.py
    step "final summary" py scripts/analysis/final_summary.py
    step "external report" py scripts/analysis/external_report.py
    step "figures" py scripts/figures/make_figures.py
    say "all reports and figures refreshed"
}

run_all() {
    say "Starting submission run; stages: $STAGES; models: $MODELS"
    for stage in $STAGES; do
        case "$stage" in
            da2both) run_da2both;;
            diag)    run_diag;;
            strict)  run_strict;;
            study100) run_study100;;
            analysis) run_analysis;;
            *) say "❌ unknown stage: $stage";;
        esac
    done
    say "=================================================="
    if [ ${#FAILED[@]} -eq 0 ]; then
        say "ALL STAGES COMPLETED CLEANLY"
        echo "# Finished submission stages: $STAGES" > "artifacts/results/benchmark/finished_submission_${STAGES// /_}.md"
        echo "Completed at $(date)" >> "artifacts/results/benchmark/finished_submission_${STAGES// /_}.md"
    else
        say "COMPLETED WITH ${#FAILED[@]} FAILED STEPS:"
        for f in "${FAILED[@]}"; do echo "  - $f"; done
        return 1
    fi
}

pids() { pgrep -f "$ROOT_DIR/scripts/run/run_submission.sh run" 2>/dev/null | grep -v "^$$$" || true; }

case "${1:-run}" in
    run)
        run_all;;
    start)
        LOG="artifacts/logs/benchmark/submission_$(date +%Y%m%d_%H%M%S).log"
        say "Starting in background -> $LOG"
        setsid nohup bash "$ROOT_DIR/scripts/run/run_submission.sh" run > "$LOG" 2>&1 < /dev/null &
        sleep 1; ps aux | grep run_submission.sh | grep -v grep;;
    status)
        echo "PID(s): $(pids)"
        echo "Last log:"; ls -1t artifacts/logs/benchmark/submission_*.log 2>/dev/null | head -1 | xargs -r tail -n 25;;
    stop)
        say "Stopping..."
        pkill -f "run_submission.sh run" 2>/dev/null || true
        pkill -f "scripts/run/run_correction.py" 2>/dev/null; pkill -f "scripts/run/distortion_study.py" 2>/dev/null
        pkill -f "scripts/run/distortion_sweep.py" 2>/dev/null; pkill -f "scripts/run/nadir_jpeg_diagnosis.py" 2>/dev/null
        say "Stopped.";;
    *) echo "usage: $0 {run|start|status|stop}"; exit 1;;
esac
