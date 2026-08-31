"""State of the world.

    python scripts/sotw.py              show it: the answer plus what is stale
    python scripts/sotw.py update       re-solve everything and say what moved
    python scripts/sotw.py tokens       write reports/latest-tokens.md
    python scripts/sotw.py compute      write reports/latest-compute.md

`update` runs the whole automatable loop: staleness report, every generated block in
README/REPORT/analysis, both plots, both latest reports, then the test suite. What it
cannot do is re-pull prices from the web (sources are listed in data/SOURCES.md, several
still TODO: link), so it ends with the exact list of figures needing a manual re-pull.
If the test run fails after a data edit, a conclusion likely flipped: that goes in the
README changelog, per CONTRIBUTING.md.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_tables  # noqa: E402
import check_staleness  # noqa: E402
import repo_data  # noqa: E402

REPORTS = repo_data.ROOT / "reports"


def _section(title: str, key: str) -> str:
    return f"## {title}\n\n{build_tables.RENDERERS[key]()}\n"


def compose_tokens() -> str:
    p = repo_data.solve_placement()
    answer = "\n".join([*build_tables.tokens_question_lines(p), "", build_tables.answer_caveat(p)])
    parts = [
        "# Token economics: latest\n",
        "The tokens question (what do I use for thinking), solved from `data/` by "
        "`python scripts/sotw.py tokens`. Nothing here is hand-typed; git history is the "
        "archive of previous states.\n",
        build_tables.RENDERERS["last_solved"]() + "\n",
        f"## The answer\n\n```text\n{answer}\n```\n",
        _section("The reference workload", "workload_derivation"),
        _section("Every priced path", "api_cost_10yr"),
        _section("The cache objection, priced", "cache_sensitivity"),
        _section("The frontier is a cliff", "frontier_table"),
        "![Capability vs cost Pareto frontier](../analysis/assets/pareto_frontier.png)\n",
        _section("The local throughput bar", "local_hw"),
        _section("The saturated local box still loses", "local_vs_cloud"),
        _section("Batching, modelled", "moe_batching"),
        _section("How much to trust this today", "freshness"),
    ]
    return "\n".join(parts)


def compose_compute() -> str:
    p = repo_data.solve_placement()
    answer = "\n".join(build_tables.compute_question_lines(p))
    parts = [
        "# Compute economics: latest\n",
        "The compute question (what do I buy for deterministic work), solved from `data/` "
        "by `python scripts/sotw.py compute`. Nothing here is hand-typed; git history is "
        "the archive of previous states.\n",
        build_tables.RENDERERS["last_solved"]() + "\n",
        f"## The answer\n\n```text\n{answer}\n```\n",
        _section("The candidates on Psi", "psi_compare"),
        _section("Compute per watt, its own question", "compute_per_watt"),
        "![Compute per watt vs Psi](../analysis/assets/compute_per_watt.png)\n",
        _section("Sensitivity: electricity", "psi_sens_electricity"),
        _section("Sensitivity: hold period", "psi_sens_hold"),
        _section("Tie prices", "breakevens"),
        _section("The memory lever", "memory_lever"),
        _section("Own vs rent", "rent_compare"),
        _section("Reconciliation with the handoff", "handoff_reconciliation"),
        _section("How much to trust this today", "freshness"),
    ]
    return "\n".join(parts)


def write_report(which: str) -> Path:
    REPORTS.mkdir(exist_ok=True)
    content = compose_tokens() if which == "tokens" else compose_compute()
    out = REPORTS / f"latest-{which}.md"
    out.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(repo_data.ROOT)}")
    return out


def cmd_show() -> int:
    print("\n".join(build_tables.placement_lines()))
    flagged = [r for r in check_staleness.collect() if r.status != "fresh"]
    print()
    if flagged:
        print(f"Stale inputs ({len(flagged)}): " + "; ".join(f"{r.label} ({r.days_old}d old)" for r in flagged))
        print("Re-pull those, then: python scripts/sotw.py update")
    else:
        print("All inputs inside their freshness windows.")
    return 0


def cmd_update() -> int:
    print("== staleness ==")
    check_staleness.main()
    print("\n== re-solving docs ==")
    build_tables.apply()
    print("\n== plots ==")
    import plot_frontier
    import plot_watts

    plot_frontier.main()
    plot_watts.main()
    print("\n== latest reports ==")
    write_report("tokens")
    write_report("compute")
    print("\n== checks ==")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=repo_data.ROOT, capture_output=True, text=True
    )
    tail = (result.stdout or result.stderr).strip().splitlines()
    print("\n".join(tail[-3:]))
    if result.returncode != 0:
        print(
            "\nA check failed. If you just refreshed data, a conclusion likely flipped: do not\n"
            "weaken the test; record the reversal in the README changelog (see CONTRIBUTING.md)."
        )
        return 1
    import refresh_plan

    work = refresh_plan.build()
    if work:
        top = [i for i in work if i.priority <= 2]
        print(f"\n{len(work)} data items need pulling ({len(top)} at priority 1-2). Top of the order:")
        for i in work[:5]:
            print(f"  [P{i.priority}] {i.figure}  ({i.detail})")
        print("Full order: python scripts/refresh_plan.py    Have an agent do it: /refresh-data")
    print("\nState of the world is solved. Review the diff, then commit with a data: prefix.")
    return 0


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else "show"
    if arg == "show":
        return cmd_show()
    if arg == "update":
        return cmd_update()
    if arg in ("tokens", "compute"):
        write_report(arg)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
