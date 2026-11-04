#!/usr/bin/env bash
# Sequential runner. Fine-tuning is opt-in because it is the longest stage.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOKESH="$(cd "$HERE/.." && pwd)"
cd "$LOKESH"
EXP="${EXP:-all}"
export PYTHON="${PYTHON:-python}"
FAILED=0
run_one() {
  local id="$1"; shift
  local script="$HERE/$id/run_gpu.sh"
  echo "================================================================"
  echo "Starting $id at $(date)"
  if bash "$script" "$@"; then
    echo "Completed $id at $(date)"
  else
    echo "FAILED $id (continuing to next experiment)"
    FAILED=$((FAILED + 1))
  fi
}
case "$EXP" in
  01) run_one 01_scale_only_protocol "$@" ;;
  02) run_one 02_domain_conditioned_gate "$@" ;;
  03) CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1}" bash "$HERE/03_panda_style_finetuning/run_gpu.sh" "$@" || FAILED=$((FAILED+1)) ;;
  04) run_one 04_mono360_20view "$@" ;;
  05) run_one 05_fov_resolution_sweep "$@" ;;
  all)
    run_one 01_scale_only_protocol "$@"
    run_one 02_domain_conditioned_gate "$@"
    run_one 04_mono360_20view "$@"
    run_one 05_fov_resolution_sweep "$@"
    if [ "${RUN_FINETUNE:-0}" = 1 ]; then
      echo "Starting optional two-GPU student training"
      CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1}" bash "$HERE/03_panda_style_finetuning/run_gpu.sh" || FAILED=$((FAILED+1))
      CKPT="$(find "$HERE/03_panda_style_finetuning/outputs" -type f -name best.pt 2>/dev/null | sort | tail -1)"
      if [ -n "$CKPT" ]; then
        CUDA_VISIBLE_DEVICES=0 bash "$HERE/03_panda_style_finetuning/evaluate_gpu.sh" "$CKPT" || FAILED=$((FAILED+1))
      else
        echo "No best.pt found after student training."
        FAILED=$((FAILED+1))
      fi
    fi
    ;;
  *) echo "EXP must be one of: all, 01, 02, 03, 04, 05"; exit 2 ;;
esac
echo "Finished at $(date); failed stages: $FAILED"
[ "$FAILED" -eq 0 ]