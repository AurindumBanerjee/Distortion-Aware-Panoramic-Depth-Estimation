"""Experiments 3 & 4: rotation-based ensemble and hybrid tangent + rotation (reports)."""
from __future__ import annotations

import os

from .common import improvement_vs_baseline, method_table, write_markdown_table


def report(df, out_dir, method_name: str, csv_path: str, extra_methods=()):
    os.makedirs(out_dir, exist_ok=True)
    tab = method_table(df, ["baseline", method_name, *extra_methods])
    imp = improvement_vs_baseline(df, method_name)
    tab.to_csv(csv_path)
    imp.to_csv(csv_path.replace(".csv", "_improvement.csv"), index=False)
    imp_area = improvement_vs_baseline(df, method_name, weighting="area")
    imp_area.to_csv(csv_path.replace(".csv", "_improvement_area.csv"), index=False)
    write_markdown_table(imp, csv_path.replace(".csv", "_improvement.md"))
    return tab, imp


def rotation_sets_report(df, out_dir):
    """Which rotations help? Includes the yaw-only control (ensembling without moving the poles)."""
    methods = ["baseline"] + sorted(m for m in df.method.unique() if m.startswith("rotation|t45|") and
                                    ("|cosine|prior" in m or "|confidence|prior" in m))
    tab = method_table(df, methods)
    tab.to_csv(os.path.join(out_dir, "rotation_sets.csv"))
    write_markdown_table(tab[["abs_rel", "abs_rel_0-15", "abs_rel_45-60", "abs_rel_60-75", "abs_rel_75-90",
                              "abs_rel_polar_60_90", "d1", "runtime_ratio"]],
                         os.path.join(out_dir, "rotation_sets.md"))
    return tab
