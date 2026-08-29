"""Renders the cost-vs-capability Pareto plot to analysis/assets/pareto_frontier.png.

Only fully costed index entries are plotted; models with a score but no cost per task are
listed in the footnote rather than invented. The visual claim is F2: the frontier is a
cliff, not a slope, and the space between the volume tier and the frontier tier is empty.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repo_data  # noqa: E402

OUT = repo_data.ROOT / "analysis" / "assets" / "pareto_frontier.png"


def main() -> int:
    idx = repo_data.aa_index()
    points = repo_data.solve_frontier()
    frontier = [p for p in points if p.on_frontier]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.set_xscale("log")

    xs = [p.cost_per_task for p in points]
    ys = [p.score for p in points]
    ax.scatter(xs, ys, zorder=3, s=60)
    ax.set_xlim(min(xs) * 0.5, max(xs) * 3.0)
    ax.set_ylim(min(ys) - 0.6, max(ys) + 0.6)
    for p in points:
        ax.annotate(
            f"{p.model}\n${p.cost_per_task:g}/task",
            (p.cost_per_task, p.score),
            textcoords="offset points",
            xytext=(10, -4),
            fontsize=8,
        )

    fx = [p.cost_per_task for p in frontier]
    fy = [p.score for p in frontier]
    ax.step(fx, fy, where="post", linestyle="--", linewidth=1, zorder=2)

    if len(frontier) >= 2:
        lo, hi = frontier[0], frontier[-1]
        mid_x = (lo.cost_per_task * hi.cost_per_task) ** 0.5
        ax.annotate(
            f"no midrange: nothing beats {lo.score} pts\nfor less than {hi.model}'s price",
            (mid_x, (lo.score + hi.score) / 2),
            ha="center",
            fontsize=8,
            color="dimgray",
        )

    uncosted = [f"{e['model']} ({e['score']})" for e in idx["entries"] if e["cost_per_task_usd"] is None]
    footnote = (
        f"AA Intelligence Index {idx['version']}, {idx['date']}. "
        "Scored but not yet costed (TODO in data/benchmarks.yaml): " + ", ".join(uncosted)
    )
    fig.text(0.01, 0.01, footnote, fontsize=6.5, color="dimgray", wrap=True)

    ax.set_xlabel("Cost per task, USD (log scale)")
    ax.set_ylabel("AA Intelligence Index")
    ax.set_title("Capability vs cost: the frontier is a cliff, not a slope")
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"wrote {OUT.relative_to(repo_data.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
