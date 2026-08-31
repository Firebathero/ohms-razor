"""What needs pulling, as a work order for whoever (or whatever) does the pulling.

This is the only job in the repo that needs intelligence: knowing whether the data is
current, and going and getting it when it is not. Everything downstream is arithmetic.

    python scripts/refresh_plan.py            human-readable work order
    python scripts/refresh_plan.py --json     same thing for an agent to consume

Three kinds of work, and the third matters most:

  stale     a figure we have, past its freshness window
  gap       a figure we know is missing, so a candidate cannot be placed
  survey    the candidate set itself is due to be re-opened

Refreshing prices for a fixed list of candidates keeps last quarter's answer accurate to
four decimal places while the actual answer moved to a part that is not on the list. Each
data file carries a `survey` block declaring what its list is supposed to cover and where
to look for entrants; this emits an item whenever that question is overdue, and treats a
list that has never been surveyed as overdue by definition.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_staleness  # noqa: E402
import repo_data  # noqa: E402


@dataclass
class Item:
    kind: str        # stale | expired | gap | survey
    figure: str
    file: str
    yaml_path: str
    source: str
    detail: str
    priority: int    # 1 highest


# Each data file that carries a candidate list, and where its survey block lives.
SURVEYED = [
    ("cpu_specs", "data/cpu_specs.yaml", "candidates[]", "CPU candidates for the compute node"),
    ("model_pricing", "data/model_pricing.yaml", "models[]", "hosted models for the token tiers"),
    ("hardware", "data/hardware.yaml", "machines[]", "local machines for on-box inference"),
    ("benchmarks", "data/benchmarks.yaml", "aa_intelligence_index", "the capability axis itself"),
]


def survey_items(today: date) -> list[Item]:
    """Is the candidate set itself due to be re-opened? A list that has never been
    surveyed is overdue by definition: it is whatever came up once, not a considered set."""
    items: list[Item] = []
    for name, path, yaml_path, what in SURVEYED:
        blob = repo_data.load(name)
        s = blob.get("survey")
        if s is None:
            items.append(
                Item("survey", f"survey scope undeclared: {what}", path, "survey",
                     "data/SOURCES.md",
                     "no survey block, so there is no record of what this list should cover", 1)
            )
            continue
        last = s.get("last_surveyed")
        interval = int(s.get("survey_interval_days", 90))
        n = _count_candidates(blob, name)
        if last is None:
            items.append(
                Item("survey", f"never surveyed: {what}", path, yaml_path,
                     "; ".join(s.get("where_to_look", [])) or "data/SOURCES.md",
                     f"{n} candidates inherited, never re-opened. {s.get('question', '').strip()}",
                     1)
            )
        else:
            age = (today - last).days
            if age > interval:
                items.append(
                    Item("survey", f"survey overdue: {what}", path, yaml_path,
                         "; ".join(s.get("where_to_look", [])) or "data/SOURCES.md",
                         f"last surveyed {age}d ago against a {interval}d interval, {n} candidates",
                         2)
                )
    return items


def _count_candidates(blob: dict, name: str) -> int:
    for key in ("candidates", "models", "machines"):
        if key in blob:
            return len(blob[key])
    idx = blob.get("aa_intelligence_index")
    return len(idx["entries"]) if idx else 0


def build(today: date | None = None) -> list[Item]:
    today = today or date.today()
    items: list[Item] = survey_items(today)

    for r in check_staleness.collect():
        if r.status == "fresh":
            continue
        if r.label.startswith("pricing:") or r.label.startswith("promo:"):
            file, path, src = "data/model_pricing.yaml", f"models[id={r.label.split(': ')[1]}]", "vendor pricing page"
        elif r.label.startswith("dram:"):
            file, path, src = "data/assumptions.yaml", "memory_pricing.ddr5_6400_rdimm_usd_per_gb", "sources#dram"
        elif r.label.startswith("cpu street price:"):
            file, path, src = "data/cpu_specs.yaml", f"candidates[id={r.label.split(': ')[1]}].price_street_usd", "sources#cpu-prices"
        elif r.label.startswith("rental:"):
            file, path, src = "data/cpu_specs.yaml", f"rental_offers[id={r.label.split(': ')[1]}]", "sources#hetzner"
        elif r.label.startswith("hardware:"):
            file, path, src = "data/hardware.yaml", f"machines[id={r.label.split(': ')[1]}]", "sources#strix-halo / sources#apple-lineup"
        elif r.label.startswith("benchmarks:"):
            file, path, src = "data/benchmarks.yaml", "aa_intelligence_index", "sources#aa-intelligence-index"
        else:
            file, path, src = "data/", r.label, "data/SOURCES.md"
        items.append(
            Item(
                kind=r.status,
                figure=r.label,
                file=file,
                yaml_path=path,
                source=src,
                detail=f"{r.days_old}d old against a {r.window_days}d window"
                if r.window_days
                else f"expired {r.days_old}d ago",
                priority=1 if r.status == "expired" else 2,
            )
        )

    idx = repo_data.aa_index()
    priced = {m.id for m in repo_data.priced_models()}
    for e in idx["entries"]:
        if e["cost_per_task_usd"] is None:
            items.append(
                Item("gap", f"cost per task: {e['model']}", "data/benchmarks.yaml",
                     f"aa_intelligence_index.entries[model={e['model']}].cost_per_task_usd",
                     "sources#aa-intelligence-index",
                     f"scores {e['score']} but cannot be placed on the tokens graph without a cost",
                     2 if e["score"] >= 57 else 3)
            )
        if e["model"] not in priced and not any(e["model"] in p for p in priced):
            items.append(
                Item("gap", f"per-Mtok pricing: {e['model']}", "data/model_pricing.yaml",
                     f"models[] (add id={e['model']})", "vendor pricing page",
                     "on the index but has no token pricing, so the workload cannot be priced against it",
                     2 if e["score"] >= 57 else 3)
            )

    for name in ("midrange_noted",):
        for model in idx.get(name, []):
            items.append(
                Item("gap", f"midrange datapoint: {model}", "data/benchmarks.yaml",
                     "aa_intelligence_index.entries[] (add)", "sources#aa-intelligence-index",
                     "named in the handoff as midrange but carries no score or cost; the no-midrange finding rests on these",
                     3)
            )

    # Unpriced parts that out-screen the current value winner. These are the highest-value
    # research in the repo: the only unpriced candidates whose price could move the answer.
    try:
        for t in repo_data.pricing_targets():
            items.append(
                Item("gap", f"price this contender: {t.name}", "data/cpu_specs.yaml",
                     f"candidates[name={t.name}].price_street_usd", "sources#cpu-prices",
                     f"out-screens the value winner by {t.beats_winner_by:.0%} on perf/watt "
                     f"({t.points_per_watt:.2f} pts/W) but has no price, so it cannot be ranked",
                     1)
            )
    except (ValueError, KeyError):
        pass  # no priced baseline yet; the survey items already cover that

    cov = repo_data.cpu_coverage()
    for name in cov.unplaceable:
        items.append(
            Item("gap", f"unplaceable candidate: {name}", "data/cpu_specs.yaml",
                 f"candidates[name={name}]", "sources#specrate",
                 "in the catalog but missing a work rate or a power figure, so it appears on "
                 "no graph", 3)
        )

    src = (repo_data.ROOT / "data" / "SOURCES.md").read_text(encoding="utf-8")
    todo_links = src.count("TODO: link")
    if todo_links:
        items.append(
            Item("gap", "unlinked sources", "data/SOURCES.md", "TODO: link markers",
                 "data/SOURCES.md", f"{todo_links} source notes have no URL, so refreshes cannot be automated yet", 2)
        )

    return sorted(items, key=lambda i: (i.priority, i.kind, i.figure))


def main() -> int:
    items = build()
    if "--json" in sys.argv:
        print(json.dumps([asdict(i) for i in items], indent=2))
        return 0
    if not items:
        print("Nothing to pull. All figures fresh, no gaps.")
        return 0
    surveys = [i for i in items if i.kind == "survey"]
    print(f"REFRESH WORK ORDER  ({len(items)} items, {len(surveys)} of them surveys)\n")
    if surveys:
        print("Surveys come first. Refreshing prices for a fixed candidate list keeps the old")
        print("answer accurate while the real answer moves to something not on the list.\n")
    for i in items:
        print(f"[P{i.priority}] {i.kind.upper():8} {i.figure}")
        print(f"         {i.detail}")
        print(f"         edit {i.file} :: {i.yaml_path}")
        print(f"         source: {i.source}\n")
    print("Rules: keep the old value in a history list, set the new date, never invent a")
    print("figure or a URL (write 'TODO: unverified'), never upgrade an estimate to a fact.")
    print("On a survey: add what you find, record what you rejected and why in")
    print("considered_and_excluded, and set last_surveyed even when nothing changed.")
    print("Then: python scripts/sotw.py update")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
