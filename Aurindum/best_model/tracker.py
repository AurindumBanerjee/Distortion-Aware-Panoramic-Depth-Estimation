"""Best Model and Method Tracker.

Automatically tracks and saves the best-performing model/method across all runs.
Monitors Polar AbsRel (|phi| >= 60 deg) and Global AbsRel, automatically saving:
- best_metrics.json
- best_config.yaml
- BEST_MODEL.md (structured markdown report)
- sample_predictions/ (RGB, GT, Pred, Error map)
"""
from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import matplotlib.pyplot as plt
import numpy as np
import yaml

logger = logging.getLogger("BestModelTracker")


class BestModelTracker:
    def __init__(self, tracker_dir: Optional[str] = None, benchmark: Optional[str] = None):
        """benchmark: results on different datasets / protocols are not comparable, so each
        benchmark (e.g. 'synthetic', 'structured3d') keeps its own registry in
        <tracker_dir>/<benchmark>/. Without it the legacy top-level registry is used."""
        if tracker_dir is None:
            self.tracker_dir = Path(__file__).resolve().parent
        else:
            self.tracker_dir = Path(tracker_dir)
        self.benchmark = benchmark
        if benchmark:
            self.tracker_dir = self.tracker_dir / benchmark

        self.tracker_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.tracker_dir / "best_metrics.json"
        self.config_file = self.tracker_dir / "best_config.yaml"
        self.report_file = self.tracker_dir / "BEST_MODEL.md"
        self.samples_dir = self.tracker_dir / "sample_predictions"
        self.samples_dir.mkdir(parents=True, exist_ok=True)

        self.best_record = self._load_current_best()

    def _load_current_best(self) -> Optional[Dict[str, Any]]:
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not read existing best_metrics.json: {e}")
        return None

    def is_better(self, new_metrics: Dict[str, Any]) -> bool:
        """Determines if new metrics outperform the current best.
        
        Priority:
        1. Polar AbsRel (|phi| >= 60 deg or '60-75'/'75-90')
        2. Global AbsRel ('all' -> 'abs_rel')
        """
        if self.best_record is None:
            return True

        curr_polar = self._extract_polar_absrel(self.best_record.get("metrics", {}))
        new_polar = self._extract_polar_absrel(new_metrics)

        curr_global = self._extract_global_absrel(self.best_record.get("metrics", {}))
        new_global = self._extract_global_absrel(new_metrics)

        logger.info(f"Evaluation check: New Polar AbsRel={new_polar:.4f} (Best={curr_polar:.4f}), "
                    f"New Global AbsRel={new_global:.4f} (Best={curr_global:.4f})")

        if not np.isfinite(curr_polar):  # stored record is NaN (e.g. empty polar band): replace it
            return bool(np.isfinite(new_polar))
        if not np.isfinite(new_polar):
            return False

        # Significant improvement in polar region with non-degraded global
        if new_polar < curr_polar - 1e-4:
            return True
        elif abs(new_polar - curr_polar) <= 1e-4 and new_global < curr_global:
            return True

        return False

    def _extract_polar_absrel(self, metrics: Dict[str, Any]) -> float:
        """Extracts polar AbsRel from either hierarchical or flat metrics dict."""
        if "severe" in metrics and "abs_rel" in metrics["severe"]:
            return float(metrics["severe"]["abs_rel"])
        if "75-90" in metrics and "abs_rel" in metrics["75-90"]:
            # Average 60-75 and 75-90 if both exist
            val_75_90 = metrics["75-90"]["abs_rel"]
            val_60_75 = metrics.get("60-75", {}).get("abs_rel", val_75_90)
            return float(0.5 * (val_75_90 + val_60_75))
        if "polar" in metrics and isinstance(metrics["polar"], dict):
            return float(metrics["polar"].get("abs_rel", 999.0))
        if "all" in metrics and "abs_rel" in metrics["all"]:
            return float(metrics["all"]["abs_rel"])
        return float(metrics.get("abs_rel", 999.0))

    def _extract_global_absrel(self, metrics: Dict[str, Any]) -> float:
        if "all" in metrics and "abs_rel" in metrics["all"]:
            return float(metrics["all"]["abs_rel"])
        return float(metrics.get("abs_rel", 999.0))

    def update_if_best(
        self,
        method_name: str,
        config: Dict[str, Any],
        metrics: Dict[str, Any],
        rgb: Optional[np.ndarray] = None,
        gt_depth: Optional[np.ndarray] = None,
        pred_depth: Optional[np.ndarray] = None,
        notes: str = ""
    ) -> bool:
        """Checks and updates the best model directory if this run is superior."""
        if not self.is_better(metrics):
            logger.info(f"Run for '{method_name}' did not surpass current best.")
            return False

        logger.info(f"🏆 NEW BEST METHOD RECORDED: '{method_name}'!")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "timestamp": timestamp,
            "method_name": method_name,
            "benchmark": self.benchmark,
            "notes": notes,
            "polar_absrel": self._extract_polar_absrel(metrics),
            "global_absrel": self._extract_global_absrel(metrics),
            "metrics": metrics,
        }

        with open(self.metrics_file, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False)

        if pred_depth is not None and gt_depth is not None:
            self._save_visualizations(rgb, gt_depth, pred_depth, method_name)

        self._generate_report(record, config)

        self.best_record = record
        return True

    def _save_visualizations(
        self,
        rgb: Optional[np.ndarray],
        gt_depth: np.ndarray,
        pred_depth: np.ndarray,
        method_name: str
    ):
        """Renders qualitative comparison figures."""
        valid_mask = np.isfinite(gt_depth) & (gt_depth > 0) & np.isfinite(pred_depth) & (pred_depth > 0)
        
        # Colorize depth using spectral colormap
        def colorize(d, vmin=None, vmax=None):
            d_valid = d[valid_mask]
            if len(d_valid) == 0:
                return np.zeros((*d.shape, 3), dtype=np.uint8)
            vmin = vmin or np.percentile(d_valid, 2)
            vmax = vmax or np.percentile(d_valid, 98)
            norm = np.clip((d - vmin) / max(vmax - vmin, 1e-4), 0, 1)
            cm = plt.get_cmap("Spectral_r")
            colored = (cm(norm)[:, :, :3] * 255).astype(np.uint8)
            return colored

        gt_colored = colorize(gt_depth)
        pred_colored = colorize(pred_depth)

        # Absolute relative error heatmap
        abs_rel_map = np.zeros_like(gt_depth)
        abs_rel_map[valid_mask] = np.abs(pred_depth[valid_mask] - gt_depth[valid_mask]) / gt_depth[valid_mask]
        norm_err = np.clip(abs_rel_map / 0.5, 0, 1)
        err_colored = (plt.get_cmap("turbo")(norm_err)[:, :, :3] * 255).astype(np.uint8)

        # Save individual images
        if rgb is not None:
            rgb_u8 = (rgb * 255).astype(np.uint8) if rgb.max() <= 1.0 else rgb.astype(np.uint8)
            cv2.imwrite(str(self.samples_dir / "sample_rgb.png"), cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(self.samples_dir / "sample_gt_depth.png"), cv2.cvtColor(gt_colored, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(self.samples_dir / "sample_best_pred.png"), cv2.cvtColor(pred_colored, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(self.samples_dir / "sample_error_heatmap.png"), cv2.cvtColor(err_colored, cv2.COLOR_RGB2BGR))

        # Composite Figure
        fig, axes = plt.subplots(4, 1, figsize=(12, 10))
        if rgb is not None:
            axes[0].imshow(rgb_u8)
            axes[0].set_title("Input Panoramic RGB (ERP)")
        axes[0].axis("off")

        axes[1].imshow(gt_colored)
        axes[1].set_title("Ground Truth Depth")
        axes[1].axis("off")

        axes[2].imshow(pred_colored)
        axes[2].set_title(f"Best Prediction: {method_name}")
        axes[2].axis("off")

        axes[3].imshow(err_colored)
        axes[3].set_title("AbsRel Error Map (turbo: dark blue = 0%, bright red >= 50%)")
        axes[3].axis("off")

        plt.tight_layout()
        plt.savefig(str(self.samples_dir / "comparison_overview.png"), dpi=150)
        plt.close()

    def _generate_report(self, record: Dict[str, Any], config: Dict[str, Any]):
        """Generates BEST_MODEL.md with summary tables."""
        m = record["metrics"]
        lines = [
            "# 🏆 Best Model & Method Registry",
            "",
            f"> **Last Updated:** `{record['timestamp']}`  ",
            f"> **Winning Method:** **{record['method_name']}**  ",
            f"> **Key Highlights:** Polar AbsRel = **{record['polar_absrel']:.4f}**, Global AbsRel = **{record['global_absrel']:.4f}**",
            "",
            "---",
            "",
            "## 1. Quantitative Performance",
            "",
        ]

        if "all" in m:
            g = m["all"]
            lines.extend([
                "### Global Metrics (Full Sphere)",
                "| Metric | AbsRel ↓ | SqRel ↓ | RMSE ↓ | RMSElog ↓ | δ < 1.25 ↑ | δ < 1.25² ↑ | δ < 1.25³ ↑ |",
                "|:--- |:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
                f"| **Score** | **{g.get('abs_rel', 0):.4f}** | {g.get('sq_rel', 0):.4f} | {g.get('rmse', 0):.4f} | {g.get('rmse_log', 0):.4f} | {g.get('d1', 0)*100:.2f}% | {g.get('d2', 0)*100:.2f}% | {g.get('d3', 0)*100:.2f}% |",
                ""
            ])

        lines.extend([
            "### Per-Latitude Band Breakdown (|φ|)",
            "| Band | Latitude Range | AbsRel ↓ | RMSE ↓ | δ < 1.25 ↑ | Status |",
            "|:--- |:---:|:---:|:---:|:---:|:---:|"
        ])

        bands = [
            ("Equatorial", "0-15", m.get("0-15", {})),
            ("Low Latitude", "15-30", m.get("15-30", {})),
            ("Mid Latitude", "30-45", m.get("30-45", {})),
            ("High Latitude", "45-60", m.get("45-60", {})),
            ("Severe Polar", "60-75", m.get("60-75", {})),
            ("Extreme Polar", "75-90", m.get("75-90", {})),
        ]

        for name, key, data in bands:
            if data:
                ar = f"**{data.get('abs_rel', 0):.4f}**" if "75" in key else f"{data.get('abs_rel', 0):.4f}"
                rmse = f"{data.get('rmse', 0):.4f}"
                d1 = f"{data.get('d1', 0)*100:.1f}%"
                status = "🎯 Target Corrected" if "60" in key or "75" in key else "Stable"
                lines.append(f"| {name} | {key}° | {ar} | {rmse} | {d1} | {status} |")

        lines.extend([
            "",
            "---",
            "",
            "## 2. Configuration",
            "```yaml",
            yaml.dump(config, default_flow_style=False).strip(),
            "```",
            "",
            "## 3. Qualitative Predictions",
            "Sample output files saved in `sample_predictions/`:",
            "- `sample_rgb.png`: Input equirectangular panorama",
            "- `sample_gt_depth.png`: Ground truth Euclidean depth",
            "- `sample_best_pred.png`: Colorized prediction from current best model",
            "- `sample_error_heatmap.png`: Pixel-wise absolute relative error heatmap",
            "- `comparison_overview.png`: Side-by-side composite visual overview",
            ""
        ])

        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info(f"Updated {self.report_file}")
