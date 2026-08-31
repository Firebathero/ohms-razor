"""Flags figures past their freshness window, and anything expired outright.

Windows (CONTRIBUTING.md): model API pricing 30 days, hardware pricing 30 days, DRAM 14
days, benchmark scores 60 days. SPECrate submissions never expire. Categories outside
these four are not policed; their confidence tags carry the warning instead.

Usage:
    python scripts/check_staleness.py            report only
    python scripts/check_staleness.py --strict   exit 1 if anything is stale or expired
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repo_data  # noqa: E402

WINDOWS = {
    "model_pricing": 30,
    "hardware_pricing": 30,
    "dram": 14,
    "benchmarks": 60,
}


@dataclass(frozen=True)
class Row:
    label: str
    category: str
    dated: date
    window_days: int
    days_old: int
    status: str  # fresh | stale | expired


def collect(today: date | None = None) -> list[Row]:
    today = today or date.today()
    rows: list[Row] = []

    def add(label: str, category: str, dated: date) -> None:
        window = WINDOWS[category]
        days = (today - dated).days
        rows.append(Row(label, category, dated, window, days, "stale" if days > window else "fresh"))

    for m in repo_data.load("model_pricing")["models"]:
        add(f"pricing: {m['id']}", "model_pricing", m["date"])
        promo = m.get("promo")
        if promo is not None:
            days = (today - promo["expires"]).days
            rows.append(
                Row(
                    f"promo: {m['id']} (ends {promo['expires']})",
                    "model_pricing",
                    promo["expires"],
                    0,
                    days,
                    "expired" if days > 0 else "fresh",
                )
            )

    add("benchmarks: aa_intelligence_index", "benchmarks", repo_data.aa_index()["date"])

    for machine in repo_data.load("hardware")["machines"]:
        add(f"hardware: {machine['id']}", "hardware_pricing", machine["date"])

    spec = repo_data.load("cpu_specs")
    for c in spec["candidates"]:
        # A list price is a published figure that does not go stale the way a street price
        # does, so only street prices carry a freshness window.
        if c.get("price_date") is not None:
            add(f"cpu street price: {c['id']}", "hardware_pricing", c["price_date"])
    for offer in spec["rental_offers"]:
        add(f"rental: {offer['id']}", "hardware_pricing", offer["date"])

    dram = repo_data.load("assumptions")["memory_pricing"]["ddr5_6400_rdimm_usd_per_gb"]
    add("dram: ddr5-6400 rdimm usd/gb", "dram", dram["date"])

    return rows


def main() -> int:
    strict = "--strict" in sys.argv
    rows = collect()
    flagged = [r for r in rows if r.status != "fresh"]
    width = max(len(r.label) for r in rows)
    print(f"{'figure':{width}}  {'category':16} {'dated':10}  {'age':>4}  window  status")
    for r in sorted(rows, key=lambda r: (r.status == "fresh", r.category, r.label)):
        window = "-" if r.window_days == 0 else f"{r.window_days}d"
        print(
            f"{r.label:{width}}  {r.category:16} {r.dated}  {r.days_old:>3}d  {window:>6}  {r.status.upper() if r.status != 'fresh' else 'fresh'}"
        )
    print()
    if flagged:
        print(f"{len(flagged)} figure(s) need a re-pull. Update data/, keep the old value in history,")
        print("then run scripts/build_tables.py and pytest. A flipped conclusion goes in the README changelog.")
    else:
        print("All figures inside their freshness windows.")
    return 1 if (strict and flagged) else 0


if __name__ == "__main__":
    raise SystemExit(main())
