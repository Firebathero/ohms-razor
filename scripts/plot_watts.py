"""Renders compute per watt as its own plot: analysis/assets/compute_per_watt.png.

The compute question has two axes that rank differently: efficiency (SPECrate points per
wall watt) and value (Psi, dollars per point-year). Plotting them against each other shows
why perf/watt alone picks the wrong part unless watts are the binding constraint.
"""

from __future__ import annotations

import sys
import textwrap
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

    cpus = {c.name: c for c in repo_data.cpu_inputs()}
    # A surveyed field is 119 dots. Colour carries the vendor, a hollow marker carries
    # "priced at list, so this dot can only move down", and only the leaders get labels.
    colors = {"AMD": "tab:red", "Intel": "tab:blue", "Ampere": "tab:green"}
    vendor_of = {c["name"]: c.get("vendor", "?") for c in spec.values()}
    labelled = {sol.winner.name, sol.best_points_per_watt.name}
    labelled |= {e.name for e in sorted(sol.evaluations, key=lambda e: e.psi)[:5]}
    # The leaders cluster in the bottom-right corner, so their labels have to be pushed
    # apart by hand or they land on top of each other.
    offsets = {}
    for i, e in enumerate(sorted(
        (e for e in sol.evaluations if e.name in labelled), key=lambda e: e.points_per_watt
    )):
        offsets[e.name] = [(10, 4), (-20, -34), (10, 14), (-24, -40)][i % 4]
    offsets[sol.winner.name] = (-42, 14)
    offsets[sol.best_points_per_watt.name] = (12, 8)

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
    seen = set()
    for e in sorted(sol.evaluations, key=lambda e: e.name in labelled):
        vendor = vendor_of.get(e.name, "?")
        color = colors.get(vendor, "tab:gray")
        is_pick = e.name in {sol.winner.name, sol.best_points_per_watt.name}
        at_list = cpus[e.name].price_is_list
        ax.scatter(
            e.points_per_watt, e.psi,
            s=110 if is_pick else 30,
            zorder=4 if is_pick else 2,
            facecolors="none" if at_list else color,
            edgecolors=color,
            linewidths=1.2,
            alpha=1.0 if e.name in labelled else 0.55,
            label=vendor if vendor not in seen and not seen.add(vendor) else None,
        )
        if e.name not in labelled:
            continue
        c = spec[e.name]
        power = c.get("run_ctdp_w") or c.get("tdp_default_w")
        label = f"{e.name.replace('AMD EPYC ', '').replace('Intel Xeon ', '')}\n{power:g}W, {c['cores']}c"
        if e.name == sol.winner.name:
            label += "\nvalue pick"
        if e.name == sol.best_points_per_watt.name:
            label += "\nefficiency pick"
        ax.annotate(
            label, (e.points_per_watt, e.psi), textcoords="offset points",
            xytext=offsets.get(e.name, (9, 5)),
            fontsize=7.5, fontweight="bold" if is_pick else "normal",
        )

    xs = [e.points_per_watt for e in sol.evaluations]
    ys = [e.psi for e in sol.evaluations]
    ax.set_xlim(min(xs) - 0.12, max(xs) + 0.55)
    top = min(max(ys), sol.winner.psi * 4)
    ax.set_ylim(min(ys) - 0.75, top + 0.10)
    # The bottom-right corner is where the winners live, so the direction-of-goodness arrow
    # goes in the empty space above them.
    ax.annotate(
        "better",
        xy=(max(xs) + 0.40, top * 0.72),
        xytext=(max(xs) - 0.45, top * 0.90),
        fontsize=9,
        color="dimgray",
        arrowprops={"arrowstyle": "->", "color": "dimgray"},
    )
    ax.legend(loc="upper left", fontsize=7.5, title="vendor", title_fontsize=7.5, frameon=False)

    op = repo_data.operating_inputs()
    a = repo_data.load("assumptions")
    ram = a["memory_pricing"]["ddr5_6400_rdimm_usd_per_gb"]
    estimated = [
        c["name"].replace("AMD EPYC ", "")
        for c in repo_data.load("cpu_specs")["candidates"]
        if c.get("phi", {}).get("confidence") == "ESTIMATE"
    ]
    caveat = f" Derate is an ESTIMATE for: {', '.join(estimated)}." if estimated else ""
    cov = repo_data.cpu_coverage()
    at_list = sum(1 for c in repo_data.cpu_inputs() if c.priceable and c.price_is_list)
    caveat += (
        f" {cov.priced} priced candidates of {cov.total} in the catalog; hollow markers "
        f"({at_list}) are priced at vendor list, an upper bound, so those dots can only "
        "move down."
    )
    cpu_survey = repo_data.load("cpu_specs").get("survey", {})
    if cpu_survey.get("last_surveyed") is None:
        caveat += f" Candidate set never surveyed: these {len(repo_data.cpu_inputs())} parts only."
    footnote = (
        f"Solved {date.today().isoformat()}: {op.years:.0f}-yr hold, "
        f"\\${op.electricity_usd_per_kwh:.2f}/kWh, DDR5 at \\${float(ram['value']):.2f}/GB "
        f"({ram['date']}).{caveat}"
    )
    fig.text(
        0.01,
        0.015,
        "\n".join(textwrap.wrap(footnote, 155)),
        fontsize=6.5,
        color="dimgray",
        va="bottom",
    )
    ax.set_xlabel("SPECrate points per wall watt (higher is better)")
    ax.set_ylabel("Psi, $ per SPECrate-point-year (lower is better)")
    ax.set_title("The compute question: efficiency and value are different answers")
    ax.grid(True, alpha=0.25)
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"wrote {OUT.relative_to(repo_data.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
