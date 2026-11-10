#!/usr/bin/env bash
# ==============================================================================
# Setup third-party dependencies for Distortion-Aware Panoramic Depth Estimation
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p third_party weights data

# 1. Clone DAP if not present
if [ ! -d "third_party/DAP" ]; then
    echo "Cloning DAP foundation model repository..."
    git clone https://github.com/Insta360-Research-Team/DAP third_party/DAP
else
    echo "third_party/DAP already exists."
fi

# 2. Check MiDaS repo
if [ -d "third_party/midas_repo" ]; then
    echo "third_party/midas_repo is present."
fi

echo "Third-party setup complete."
