#!/usr/bin/env bash
# Ablation for the Möbius-TTA failures on DAP (metric) and outdoor PanoX.
# Runs only Baseline + Method2 + Control_YawEnsemble (no Poisson / tangent work) for every variant:
#   rot_only   : two pitch +/-90 passes, no dilation       dil_only : two dilation passes, no rotation
#   full       : the default passes                         each with gate_lat off / on (30-55)
# Output folders: 3_structured3d_benchmark/outputs*_abl_<variant>; results/ABLATION_<ts>.md is built at the end.
# Usage: scripts/run_mobius_ablation.sh [s3|panox|both] [MAX_SCENES]   (default both, 60 scenes)
set -euo pipefail
cd "$(dirname "$0")/../3_structured3d_benchmark"
WHICH="${1:-both}"; N="${2:-60}"
declare -A PASSES=(
  [rot]='[{pitch: 90, scale: 1.0}, {pitch: -90, scale: 1.0}]'
  [dil]='[{pitch: 0, scale: 1.6}, {pitch: 0, scale: 0.625}]'
  [full]='[{pitch: 90, scale: 1.0}, {pitch: -90, scale: 1.0}, {pitch: 0, scale: 1.6}, {pitch: 0, scale: 0.625}]'
)
declare -A GATES=([off]='null' [on]='[30, 55]')
run() {  # config tag
  local cfg="$1" name="$2"
  for p in rot dil full; do for g in off on; do
    python run.py --config "$cfg" --max_scenes "$N" --tag "abl_${name}_${p}_${g}" \
      --set "evaluation.methods=[Method2_MobiusTTA,Control_YawEnsemble]" \
      --set "mobius_tta.passes=${PASSES[$p]}" --set "mobius_tta.gate_lat=${GATES[$g]}"
  done; done
}
if [[ "$WHICH" == s3 || "$WHICH" == both ]]; then run config.yaml midas_s3; run config_dap.yaml dap_s3; fi
if [[ "$WHICH" == panox || "$WHICH" == both ]]; then run config_panox.yaml midas_panox; run config_dap_panox.yaml dap_panox; fi
cd ..
python scripts/collect_results.py --out "results/ABLATION_$(date +%Y%m%d_%H%M%S).md"
