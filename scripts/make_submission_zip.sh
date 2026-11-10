#!/usr/bin/env bash
# ==============================================================================
# Build lightweight code-only submission archive (< 9.5 MB) via git archive
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python "$ROOT_DIR/scripts/make_submission_zip.py"
