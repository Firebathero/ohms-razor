"""Renders compute per watt as its own plot: analysis/assets/compute_per_watt.png.

The compute question has two axes that rank differently: efficiency (SPECrate points per
wall watt) and value (Psi, dollars per point-year). Plotting them against each other shows
why perf/watt alone picks the wrong part unless watts are the binding constraint.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repo_data  # noqa: E402

OUT = repo_data.ROOT / "analysis" / "assets" / "compute_per_watt.png"


def main() -> int:
    sol = repo_data.solve_psi()
    spec = {c["name"]: c for c in repo_data.load("cpu_specs")["candidates"]}

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    for e in sol.evaluations:
        is_value = e.name == sol.winner.name
        is_eff = e.name == sol.best_points_per_watt.name
        ax.scatter(e.points_per_watt, e.psi, s=90, zorder=3)
        c = spec[e.name]
        label = f"{e.name.replace('AMD EPYC ', '')}\n{c['run_ctdp_w']}W, {c['cores']}c"
        if is_value:
            label += "\nvalue pick"
        if is_eff:
            label += "\nefficiency pick"
        ax.annotate(
            label,
            (e.points_per_watt, e.psi),
            textcoords="offset points",
            xytext=(10, 6),
            fontsize=8,
            fontweight="bold" if (is_value or is_eff) else "normal",
        )

    xs = [e.points_per_watt for e in sol.evaluations]
    ys = [e.psi for e in sol.evaluations]
    ax.set_xlim(min(xs) - 0.12, max(xs) + 0.22)
    ax.set_ylim(min(ys) - 0.08, max(ys) + 0.10)
    ax.annotate(
        "better",
        xy=(max(xs) + 0.14, min(ys) - 0.02),
        xytext=(max(xs) - 0.10, min(ys) + 0.16),
        fontsize=9,
        color="dimgray",
        arrowprops={"arrowstyle": "->", "color": "dimgray"},
    )

    op = repo_data.operating_inputs()
    a = repo_data.load("assumptions")
    ram = a["memory_pricing"]["ddr5_6400_rdimm_usd_per_gb"]
    fig.text(
        0.01,
        0.01,
        f"Solved {date.today().isoformat()}: {op.years:.0f}-yr hold, "
        f"\\${op.electricity_usd_per_kwh:.2f}/kWh, DDR5 at \\${float(ram['value']):.2f}/GB "
        f"({ram['date']}). The 9965's derate at 450W is an ESTIMATE.",
        fontsize=6.5,
        color="dimgray",
    )
    ax.set_xlabel("SPECrate points per wall watt (higher is better)")
    ax.set_ylabel("Psi, $ per SPECrate-point-year (lower is better)")
    ax.set_title("The compute question: efficiency and value are different answers")
    ax.grid(True, alpha=0.25)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"wrote {OUT.relative_to(repo_data.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
