"""The razor: feed it your brightlines, get two graphs and a pick.

There is no objective function until the operator declares one. A threshold is what makes
"efficiency" mean anything: minimum capability, minimum sustained rate, a watts cap, a
budget. This script takes those as parameters, shaves away every candidate that fails
them, optimizes the axis you chose over what survives, and writes one graph per question
with your brightlines drawn on it.

    python scripts/razor.py                                   # good defaults
    python scripts/razor.py --min-score 20                    # allow weak models; watch it converge on cheap
    python scripts/razor.py --min-score 60                    # demand frontier capability; watch the price
    python scripts/razor.py --out-mtok-yr 900                 # heavier token burn; the rate bar moves with it
    python scripts/razor.py --max-watts 500                   # power brightline; the compute pick flips
    python scripts/razor.py --compute-objective efficiency    # optimize pts/W instead of $/work

Outputs: out/tokens.png, out/compute.png, and the picks on stdout. Candidates that cannot
be placed (missing score, price, or wall draw in data/) are listed, never invented.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repo_data  # noqa: E402
from models import MTOK, SECONDS_PER_YEAR  # noqa: E402
from models.local_cost import lifetime_energy_cost  # noqa: E402
from models.token_cost import Workload, api_cost  # noqa: E402
from models.token_cost import effective_cost as peak_effective  # noqa: E402


# ---------------------------------------------------------------- tokens

@dataclass(frozen=True)
class TokenCandidate:
    label: str
    kind: str                 # api | local
    monthly_usd: float
    score: int
    rate_tok_s: float | None  # None = not rate-limited (API)
    feasible: bool
    excluded_by: str          # "" when feasible


@dataclass(frozen=True)
class TokenResult:
    candidates: list[TokenCandidate]
    unplaceable: list[str]
    required_rate: float
    winner: TokenCandidate | None
    objective: str
    min_score: int
    budget_monthly: float | None


def solve_tokens(
    out_mtok_yr: float,
    in_mtok_yr: float,
    cache_hit: float,
    min_score: int,
    budget_monthly: float | None,
    objective: str,
) -> TokenResult:
    year = Workload(out_mtok_yr * MTOK, in_mtok_yr * MTOK, cache_hit)
    required = year.output_tokens / SECONDS_PER_YEAR
    scores = {e["model"]: e["score"] for e in repo_data.aa_index()["entries"]}
    candidates: list[TokenCandidate] = []
    unplaceable: list[str] = []

    for m in repo_data.priced_models():
        score = scores.get(m.id, scores.get(m.id.removesuffix("-cloud")))
        if score is None:
            unplaceable.append(f"{m.id} (no AA score in data)")
            continue
        monthly = api_cost(m.pricing, year) / 12.0
        label = m.id
        if m.peak is not None:
            f_peak, mult = repo_data.peak_exposure(m.peak)
            monthly = peak_effective(monthly, f_peak, mult)
            label += " (24/7)"
        if m.id.endswith("-cloud"):
            label = m.id.removesuffix("-cloud") + " (cloud)"
        candidates.append(_judge(label, "api", monthly, score, None, required, min_score, budget_monthly))

    for e in repo_data.aa_index()["entries"]:
        if e["cost_per_task_usd"] is not None and e["model"] not in {m.id for m in repo_data.priced_models()}:
            unplaceable.append(f"{e['model']} (cost/task known, per-Mtok pricing not in data)")

    hw = repo_data.load("hardware")
    sc = hw["local_box_scenario"]
    op = repo_data.load("assumptions")["operating"]
    for machine in hw["machines"]:
        for t in machine.get("throughput") or []:
            score = scores.get(t["model"])
            if score is None:
                unplaceable.append(f"{machine['name']} + {t['model']} (no AA score in data)")
                continue
            if not (machine["id"] == sc["machine"] and t["model"] == sc["model"]):
                unplaceable.append(f"{machine['name']} + {t['model']} (no measured wall draw in data)")
                continue
            years = float(sc["years"])
            total = float(machine["price_usd"]) + lifetime_energy_cost(
                float(sc["wall_draw_w"]),
                float(op["cooling_overhead"]["value"]),
                float(op["electricity_usd_per_kwh"]["value"]),
                years,
            )
            candidates.append(
                _judge(
                    f"{machine['name']} + {t['model']} (local)",
                    "local",
                    total / (years * 12.0),
                    score,
                    float(t["tok_s"]),
                    required,
                    min_score,
                    budget_monthly,
                )
            )

    feasible = [c for c in candidates if c.feasible]
    winner = None
    if feasible:
        if objective == "smartest":
            winner = max(feasible, key=lambda c: (c.score, -c.monthly_usd))
        else:
            winner = min(feasible, key=lambda c: (c.monthly_usd, -c.score))
    return TokenResult(candidates, unplaceable, required, winner, objective, min_score, budget_monthly)


def _judge(
    label: str,
    kind: str,
    monthly: float,
    score: int,
    rate: float | None,
    required: float,
    min_score: int,
    budget: float | None,
) -> TokenCandidate:
    reasons = []
    if score < min_score:
        reasons.append(f"score {score} < {min_score}")
    if rate is not None and rate < required:
        reasons.append(f"{rate:g} tok/s < {required:.1f} bar")
    if budget is not None and monthly > budget:
        reasons.append(f"${monthly:,.0f}/mo > ${budget:,.0f} budget")
    return TokenCandidate(label, kind, monthly, score, rate, not reasons, "; ".join(reasons))


# ---------------------------------------------------------------- compute

@dataclass(frozen=True)
class ComputeCandidate:
    label: str
    wall_w: float
    psi: float
    points_per_watt: float
    work_points: float
    feasible: bool
    excluded_by: str


@dataclass(frozen=True)
class ComputeResult:
    candidates: list[ComputeCandidate]
    winner: ComputeCandidate | None
    objective: str
    min_points: float
    max_watts: float | None


def solve_compute(min_points: float, max_watts: float | None, objective: str) -> ComputeResult:
    sol = repo_data.solve_psi()
    candidates = []
    for e in sol.evaluations:
        reasons = []
        if e.work_rate < min_points:
            reasons.append(f"{e.work_rate:,.0f} pts < {min_points:,.0f} floor")
        if max_watts is not None and e.wall_power_w > max_watts:
            reasons.append(f"{e.wall_power_w:,.0f}W wall > {max_watts:,.0f}W cap")
        candidates.append(
            ComputeCandidate(
                e.name, e.wall_power_w, e.psi, e.points_per_watt, e.work_rate,
                not reasons, "; ".join(reasons),
            )
        )
    feasible = [c for c in candidates if c.feasible]
    winner = None
    if feasible:
        if objective == "efficiency":
            winner = max(feasible, key=lambda c: c.points_per_watt)
        else:
            winner = min(feasible, key=lambda c: c.psi)
    return ComputeResult(candidates, winner, objective, min_points, max_watts)


# ---------------------------------------------------------------- plots

def plot_tokens(r: TokenResult, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.set_xscale("log")
    for c in r.candidates:
        color = "tab:blue" if c.feasible else "silver"
        ax.scatter(c.monthly_usd, c.score, s=70, color=color, zorder=3)
        note = f"{c.label}\n${c.monthly_usd:,.0f}/mo"
        if not c.feasible:
            note += f"\nout: {c.excluded_by}"
        ax.annotate(note, (c.monthly_usd, c.score), textcoords="offset points",
                    xytext=(8, 5), fontsize=7.5, color="black" if c.feasible else "gray")
    xs = [c.monthly_usd for c in r.candidates]
    ys = [c.score for c in r.candidates] + [r.min_score]
    ax.set_xlim(min(xs) * 0.55, max(xs) * 4.0)
    ax.set_ylim(min(ys) - 4, max(ys) + 4)
    ax.axhline(r.min_score, linestyle="--", linewidth=1, color="peru")
    ax.annotate(f"brightline: score >= {r.min_score}", (ax.get_xlim()[0], r.min_score),
                xytext=(6, -12), textcoords="offset points", fontsize=8, color="peru")
    if r.budget_monthly is not None:
        ax.axvline(r.budget_monthly, linestyle="--", linewidth=1, color="peru")
    feasible = sorted([c for c in r.candidates if c.feasible], key=lambda c: c.monthly_usd)
    frontier = []
    best = -1
    for c in feasible:
        if c.score > best:
            frontier.append(c)
            best = c.score
    if len(frontier) > 1:
        ax.step([c.monthly_usd for c in frontier], [c.score for c in frontier],
                where="post", linestyle=":", linewidth=1, color="tab:blue")
    if r.winner:
        ax.scatter(r.winner.monthly_usd, r.winner.score, s=240, facecolors="none",
                   edgecolors="tab:red", linewidths=1.6, zorder=4)
    ax.set_xlabel("Your workload, $ per month (log)")
    ax.set_ylabel("AA Intelligence Index")
    ax.set_title(f"Tokens: {r.objective} above your lines (rate bar {r.required_rate:.1f} tok/s)")
    ax.grid(True, which="both", alpha=0.25)
    if r.unplaceable:
        fig.text(0.01, 0.01, "Not placeable (missing data, never invented): " + "; ".join(r.unplaceable),
                 fontsize=6, color="dimgray", wrap=True)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def plot_compute(r: ComputeResult, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    efficiency = r.objective == "efficiency"
    for c in r.candidates:
        y = c.points_per_watt if efficiency else c.psi
        color = "tab:blue" if c.feasible else "silver"
        ax.scatter(c.wall_w, y, s=70, color=color, zorder=3)
        note = f"{c.label.replace('AMD EPYC ', '')}\n{c.work_points:,.0f} pts"
        if not c.feasible:
            note += f"\nout: {c.excluded_by}"
        ax.annotate(note, (c.wall_w, y), textcoords="offset points", xytext=(8, 5),
                    fontsize=7.5, color="black" if c.feasible else "gray")
    xs = [c.wall_w for c in r.candidates] + ([r.max_watts] if r.max_watts else [])
    ys = [c.points_per_watt if efficiency else c.psi for c in r.candidates]
    xpad, ypad = (max(xs) - min(xs)) or 50, (max(ys) - min(ys)) or 1
    ax.set_xlim(min(xs) - xpad * 0.12, max(xs) + xpad * 0.45)
    ax.set_ylim(min(ys) - ypad * 0.15, max(ys) + ypad * 0.22)
    if r.max_watts is not None:
        ax.axvline(r.max_watts, linestyle="--", linewidth=1, color="peru")
        ax.annotate(f"brightline: wall <= {r.max_watts:,.0f}W", (r.max_watts, ax.get_ylim()[0]),
                    xytext=(-6, 8), textcoords="offset points", fontsize=8,
                    color="peru", ha="right")
    if r.winner:
        y = r.winner.points_per_watt if efficiency else r.winner.psi
        ax.scatter(r.winner.wall_w, y, s=240, facecolors="none", edgecolors="tab:red",
                   linewidths=1.6, zorder=4)
    ax.set_xlabel("Wall watts under load")
    if efficiency:
        ax.set_ylabel("SPECrate points per wall watt (higher wins)")
    else:
        ax.set_ylabel("Psi, $ per SPECrate-point-year (lower wins)")
    floor = f", work >= {r.min_points:,.0f} pts" if r.min_points else ""
    ax.set_title(f"Compute: {r.objective} above your lines{floor}")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------- cli

def main() -> int:
    w = repo_data.load("workload")["reference_workload"]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-mtok-yr", type=float, default=float(w["output_tokens_per_year"]) / MTOK,
                    help="output Mtok per year (default: reference workload)")
    ap.add_argument("--in-mtok-yr", type=float, default=float(w["input_tokens_per_year"]) / MTOK)
    ap.add_argument("--cache", type=float, default=float(w["cache_hit_rate"]))
    ap.add_argument("--min-score", type=int, default=repo_data.CAPABLE_SCORE_FLOOR,
                    help="capability brightline (default: the repo's capable floor)")
    ap.add_argument("--budget-monthly", type=float, default=None, help="token budget brightline, $/mo")
    ap.add_argument("--tokens-objective", choices=["cheapest", "smartest"], default="cheapest")
    ap.add_argument("--min-points", type=float, default=0.0, help="compute work floor, 1P SPECrate points")
    ap.add_argument("--max-watts", type=float, default=None, help="compute power brightline, wall watts")
    ap.add_argument("--compute-objective", choices=["value", "efficiency"], default="value")
    ap.add_argument("--outdir", type=Path, default=repo_data.ROOT / "out")
    args = ap.parse_args()

    tokens = solve_tokens(args.out_mtok_yr, args.in_mtok_yr, args.cache,
                          args.min_score, args.budget_monthly, args.tokens_objective)
    compute = solve_compute(args.min_points, args.max_watts, args.compute_objective)

    args.outdir.mkdir(exist_ok=True)
    plot_tokens(tokens, args.outdir / "tokens.png")
    plot_compute(compute, args.outdir / "compute.png")

    print(f"TOKENS  objective={tokens.objective}  score>={tokens.min_score}  "
          f"rate bar={tokens.required_rate:.1f} tok/s"
          + (f"  budget=${tokens.budget_monthly:,.0f}/mo" if tokens.budget_monthly else ""))
    for c in sorted(tokens.candidates, key=lambda c: c.monthly_usd):
        mark = "->" if tokens.winner and c.label == tokens.winner.label else ("  " if c.feasible else " x")
        why = f"  [{c.excluded_by}]" if c.excluded_by else ""
        print(f"  {mark} {c.label:38s} ${c.monthly_usd:>9,.2f}/mo  AA {c.score}{why}")
    if tokens.winner is None:
        print("  no feasible candidate above your lines; loosen a threshold or add data")
    if tokens.unplaceable:
        print("  not placeable: " + "; ".join(tokens.unplaceable))

    print(f"\nCOMPUTE objective={compute.objective}"
          + (f"  work>={compute.min_points:,.0f} pts" if compute.min_points else "")
          + (f"  wall<={compute.max_watts:,.0f}W" if compute.max_watts else ""))
    for c in sorted(compute.candidates, key=lambda c: c.psi):
        mark = "->" if compute.winner and c.label == compute.winner.label else ("  " if c.feasible else " x")
        why = f"  [{c.excluded_by}]" if c.excluded_by else ""
        print(f"  {mark} {c.label:16s} Psi ${c.psi:.2f}/pt-yr  {c.points_per_watt:.2f} pts/W  "
              f"{c.wall_w:,.0f}W wall{why}")
    if compute.winner is None:
        print("  no feasible candidate above your lines; loosen a threshold")

    print(f"\nwrote {args.outdir / 'tokens.png'}")
    print(f"wrote {args.outdir / 'compute.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
