#!/usr/bin/env bash
# Kaggle notebook setup (Settings: Accelerator = GPU T4 x2 or P100, Internet = ON).
# In a notebook cell:  !bash scripts/kaggle_setup.sh
# Upload this repo as a Kaggle Dataset (or git clone it), then cd into it first.
set -e
pip install -q timm==0.6.13 einops safetensors remotezip huggingface_hub tabulate opencv-python-headless
# DAP (target model)
[ -d third_party/DAP ] || git clone -q https://github.com/Insta360-Research-Team/DAP third_party/DAP
python - <<'EOF'
from huggingface_hub import snapshot_download
snapshot_download("Insta360-Research/DAP-weights", local_dir="weights/dap")
EOF
# MiDaS weights (stand-in / second model)
mkdir -p weights
for f in v3/dpt_hybrid_384.pt v3_1/dpt_swin2_tiny_256.pt; do
  [ -f weights/$(basename $f) ] || wget -q -O weights/$(basename $f) https://github.com/isl-org/MiDaS/releases/download/$f
done
# PanoX test split (optional; only RGB + distance, a few GB). Enable with:  PANOX=1 bash scripts/kaggle_setup.sh
if [ "${PANOX:-0}" = "1" ]; then
  python scripts/download_panox.py --split test --out data/panox
  python scripts/make_panox_list.py --root data/panox
fi
echo "Ready:  python run_experiment.py --config configs/dap_structured3d.yaml --set dataset.root=/kaggle/input/<your-dataset>"
