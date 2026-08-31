"""What needs pulling, as a work order for whoever (or whatever) does the pulling.

This is the only job in the repo that needs intelligence: knowing whether the data is
current, and going and getting it when it is not. Everything downstream is arithmetic.

    python scripts/refresh_plan.py            human-readable work order
    python scripts/refresh_plan.py --json     same thing for an agent to consume

Emits one item per stale or missing figure: the YAML path to edit, what to look for, and
which source note in data/SOURCES.md covers it. Gaps count as work too, because a missing
price is why a candidate cannot be placed on the graphs.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_staleness  # noqa: E402
import repo_data  # noqa: E402


@dataclass
class Item:
    kind: str        # stale | expired | gap
    figure: str
    file: str
    yaml_path: str
    source: str
    detail: str
    priority: int    # 1 highest


def build() -> list[Item]:
    items: list[Item] = []

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
    print(f"REFRESH WORK ORDER  ({len(items)} items)\n")
    for i in items:
        print(f"[P{i.priority}] {i.kind.upper():8} {i.figure}")
        print(f"         {i.detail}")
        print(f"         edit {i.file} :: {i.yaml_path}")
        print(f"         source: {i.source}\n")
    print("Rules: keep the old value in a history list, set the new date, never invent a")
    print("figure or a URL (write 'TODO: unverified'), never upgrade an estimate to a fact.")
    print("Then: python scripts/sotw.py update")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
