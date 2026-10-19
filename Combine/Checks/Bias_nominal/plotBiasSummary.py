#!/usr/bin/env python3
"""
Make summary plots of the bias pull median per category.

Reads summary/bias_results_final.csv (produced by merge_bias_results.py) and
produces one plot for the ggH categories and one for the VBF categories.

For every category, one point per toy function is drawn:
    y    = bias_pull_median
    yerr = bias_pull_err

Horizontal dashed lines are drawn at +-0.2, the y range is fixed to [-1, 1].

Usage:
    python3 plotBiasSummary.py
    python3 plotBiasSummary.py -i summary/bias_results_final.csv -o summary/plots
"""

import argparse
import csv
import os
import re

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as hep


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
DEFAULT_INPUT = os.path.join("summary", "bias_results_final.csv")
DEFAULT_OUTPUT = os.path.join("summary", "plots")

# order in which the toy functions appear in the legend / on the x axis
TOY_FUNCTION_ORDER = [
    "bwzgam2",
    "2exp6",
    "mBW3",
    "bwzexp1",
    "bwzexp2",
    "bwzexp3",
    "dytFcheb1",
    "dytFcheb2",
    "dytFcheb3",
]

MARKERS = ["o", "s", "^", "v", "D", "P", "X", "<", ">", "*"]
COLORS = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
          "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]


def natural_key(text):
    """Sort 'ggHcat10' after 'ggHcat2'."""
    return [int(part) if part.isdigit() else part
            for part in re.split(r"(\d+)", text)]


def base_name(toy_function):
    """Strip the trailing order digits, e.g. bwzexp2 -> bwzexp."""
    return re.sub(r"\d+$", "", toy_function) or toy_function


def read_csv(path):
    """Read the summary CSV (quoted fields contain commas)."""
    rows = []
    with open(path, newline="") as csvfile:
        for row in csv.DictReader(csvfile):
            cat = row["category"].strip()
            if not cat:
                continue
            rows.append({
                "category": cat,
                "toy_function": row["toy_function"].strip(),
                "bias_pull_median": float(row["bias_pull_median"]),
                "bias_pull_err": float(row["bias_pull_err"]),
                "fit_valid": row.get("fit_valid", "1").strip() in ("1", "True", "true"),
            })
    return rows


def ordered_toy_functions(rows):
    """Toy functions present in the data, in the preferred order."""
    present = {r["toy_function"] for r in rows}
    order = [f for f in TOY_FUNCTION_ORDER if f in present]
    order += sorted(present - set(order))
    return order


def make_plot(rows, prefix, output_dir):
    """Plot all categories belonging to one group (ggH or VBF)."""
    categories = sorted({r["category"] for r in rows}, key=natural_key)
    toy_functions = ordered_toy_functions(rows)

    # the legend does not distinguish the order, only the function family
    families = []
    for func in toy_functions:
        family = base_name(func)
        if family not in families:
            families.append(family)

    def family_style(func):
        """Same colour/marker for all orders of the same function family."""
        idx = families.index(base_name(func))
        return COLORS[idx % len(COLORS)], MARKERS[idx % len(MARKERS)]

    fig, ax = plt.subplots(figsize=(10, 6))

    # acceptance band and reference lines
    ax.axhspan(-0.2, 0.2, color="gray", alpha=0.12, zorder=0)
    ax.axhline(0.0, color="black", linewidth=1.0, zorder=1)
    ax.axhline(0.2, color="black", linestyle="--", linewidth=1.2, zorder=1)
    ax.axhline(-0.2, color="black", linestyle="--", linewidth=1.2, zorder=1)

    # horizontal offsets so the different toy functions do not overlap.
    # A constant spacing is used and the cluster is centred in each category;
    # this keeps the spacing identical even when a category is missing some
    # of the toy functions (which is why the old version looked uneven).
    point_spacing = 0.18

    # x position of every (category, toy function) pair
    positions = {}
    for icat, cat in enumerate(categories):
        funcs_here = [f for f in toy_functions
                      if any(r["category"] == cat and r["toy_function"] == f
                             for r in rows)]
        n_here = len(funcs_here)
        for i, func in enumerate(funcs_here):
            offset = (i - (n_here - 1) / 2.0) * point_spacing
            positions[(cat, func)] = icat + offset

    # vertical dashed separators between neighbouring categories
    for icat in range(len(categories) - 1):
        ax.axvline(icat + 0.5, color="gray", linestyle="--",
                   linewidth=0.9, alpha=0.7, zorder=0.5)

    labelled_families = set()
    for idx, func in enumerate(toy_functions):
        color, marker = family_style(func)
        family = base_name(func)
        xs, ys, yerrs = [], [], []
        for icat, cat in enumerate(categories):
            match = [r for r in rows
                     if r["category"] == cat and r["toy_function"] == func]
            if not match:
                continue
            entry = match[0]
            xs.append(positions[(cat, func)])
            ys.append(entry["bias_pull_median"])
            yerrs.append(entry["bias_pull_err"])

        # only one legend entry per function family
        label = family if family not in labelled_families else None
        labelled_families.add(family)

        ax.errorbar(
            xs, ys, yerr=yerrs,
            marker=marker,
            color=color,
            linestyle="none",
            markersize=4,
            capsize=2,
            elinewidth=1.0,
            label=label,
            zorder=3,
        )

    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, fontsize=13)
    ax.set_xlim(-0.6, len(categories) - 0.4)
    ax.set_ylim(-1.0, 1.0)
    ax.set_ylabel(r"Bias pull median", fontsize=15)
    ax.set_xlabel("Category", fontsize=15)

    hep.cms.label(
        data=False,
        loc=0,
        label="",
        com="13.6",
        lumi="307.54",
        ax=ax,
    )

    ax.legend(
        loc="upper right",
        ncol=2,
        fontsize=11,
        frameon=True,
        title="Toy function",
    )

    plt.tight_layout()

    for ext in ("pdf", "png"):
        outfile = os.path.join(output_dir, f"{prefix}_bias_pull_median.{ext}")
        fig.savefig(outfile)
        print(f"[INFO] saved {outfile}")

    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", default=DEFAULT_INPUT,
                        help=f"input CSV (default: {DEFAULT_INPUT})")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT,
                        help=f"output directory (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()

    rows = read_csv(args.input)
    if not rows:
        raise RuntimeError(f"No entries found in {args.input}")

    os.makedirs(args.output, exist_ok=True)

    groups = {
        "ggH": [r for r in rows if r["category"].startswith("ggH")],
        "VBF": [r for r in rows if r["category"].startswith("VBF")],
    }

    for prefix, group_rows in groups.items():
        if not group_rows:
            print(f"[WARNING] no entries for {prefix} categories, skipping")
            continue
        make_plot(group_rows, prefix, args.output)


if __name__ == "__main__":
    main()
