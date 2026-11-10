"""Canonical repository paths, configurable via environment variables."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path(os.environ.get("PANO_ARTIFACTS", ROOT / "artifacts"))
RESULTS = ARTIFACTS / "results"
LOGS = ARTIFACTS / "logs"
FIGURES = ARTIFACTS / "figures"
NOTEBOOKS = ARTIFACTS / "notebooks"
ARCHIVES = ARTIFACTS / "archives"
DATA = Path(os.environ.get("PANO_DATA", ROOT / "data"))
WEIGHTS = Path(os.environ.get("PANO_WEIGHTS", ROOT / "weights"))
THIRD_PARTY = Path(os.environ.get("PANO_THIRD_PARTY", ROOT / "third_party"))
CONFIGS = ROOT / "configs"
REPORT = ROOT / "report"

# Sub-areas under artifacts/results/
BENCHMARK_RESULTS = RESULTS / "benchmark"
PROJECTION_RESULTS = RESULTS / "projection"
NYC_RESULTS = RESULTS / "nyc"
FOLLOWUP_RESULTS = RESULTS / "followups"
