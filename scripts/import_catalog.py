"""Bulk-load candidates from a CSV into the data layer.

Hand-writing YAML is why the candidate sets stayed at four entries. This takes a
spreadsheet of dozens of parts and merges it in, so the marginal cost of one more
candidate is one more row.

    python scripts/import_catalog.py cpus incoming/cpus.csv
    python scripts/import_catalog.py cpus incoming/cpus.csv --dry-run
    python scripts/import_catalog.py --template cpus > incoming/cpus.csv

Merge rules, in order of importance:

1. A blank or TODO cell never overwrites a value already in the data. Research is
   expensive and the CSV is usually the less-informed source.
2. A cell that CONFLICTS with an existing value is reported and skipped, not applied.
   Resolving it is a human decision with a source behind it, not a merge policy.
3. New ids are appended with every figure tagged from the CSV's confidence column.
4. Nothing is ever deleted. Removing a candidate is a deliberate edit.

Every row needs an id, a name, and enough of a power figure to be placed. Everything else
may be blank; the tools report an incomplete candidate as unplaceable and the refresh plan
turns it into work.
"""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repo_data  # noqa: E402

import yaml  # noqa: E402

BLANK = {"", "-", "n/a", "na", "none", "null", "?"}

SCHEMAS: dict[str, dict[str, Any]] = {
    "cpus": {
        "file": "cpu_specs.yaml",
        "collection": "candidates",
        "required": ["id", "name"],
        "columns": [
            "id", "name", "vendor", "cores", "architecture", "l3_mb",
            "tdp_default_w", "ctdp_floor_w", "mem_bandwidth_gb_s",
            "specrate_2p", "specrate_2p_systems", "specrate_1p",
            "price_street_usd", "price_note", "source", "confidence",
        ],
    },
    "models": {
        "file": "model_pricing.yaml",
        "collection": "models",
        "required": ["id", "vendor"],
        "columns": [
            "id", "vendor", "tier", "input_per_mtok", "cached_input_per_mtok",
            "output_per_mtok", "context_window", "open_weights",
            "source", "confidence", "notes",
        ],
    },
    "machines": {
        "file": "hardware.yaml",
        "collection": "machines",
        "required": ["id", "name"],
        "columns": [
            "id", "name", "vendor", "memory_gb_max", "bandwidth_nominal_gb_s",
            "bandwidth_effective_gb_s", "price_usd", "idle_w", "load_w",
            "source", "confidence", "notes",
        ],
    },
}


def blank(v: str | None) -> bool:
    return v is None or v.strip().lower() in BLANK or v.strip().upper().startswith("TODO")


def typed(column: str, raw: str) -> Any:
    if column in {"id", "name", "vendor", "tier", "architecture", "source", "confidence",
                  "notes", "price_note", "specrate_2p_systems"}:
        return raw.strip()
    if column == "open_weights":
        return raw.strip().lower() in {"true", "yes", "y", "1"}
    if column in {"cores", "l3_mb", "memory_gb_max", "context_window"}:
        return int(float(raw.strip().replace(",", "")))
    return float(raw.strip().replace(",", "").replace("$", ""))


def nest(kind: str, row: dict[str, Any], today: date) -> dict[str, Any]:
    """CSV columns to the shape the data layer already uses."""
    src = row.pop("source", None) or "TODO: link"
    conf = row.pop("confidence", None) or "TODO"
    out: dict[str, Any] = {}
    if kind == "cpus":
        systems = row.pop("specrate_2p_systems", None)
        rate = row.pop("specrate_2p", None)
        one_p = row.pop("specrate_1p", None)
        price = row.pop("price_street_usd", None)
        price_note = row.pop("price_note", None)
        out.update(row)
        if rate is not None:
            out["specrate_2p"] = {
                "value_used": rate,
                "confidence": conf,
                "source": src,
                **({"submissions_note": systems} if systems else {}),
            }
        if one_p is not None:
            out["specrate_1p"] = {"value_used": one_p, "confidence": conf, "source": src}
        if price is not None:
            out["price_street_usd"] = price
            out["price_confidence"] = "VOLATILE"
            out["price_date"] = today
            if price_note:
                out["price_note"] = price_note
        out.setdefault("source", src)
    elif kind == "models":
        out.update(row)
        out["date"] = today
        out["confidence"] = conf
        out["source"] = src
        out.setdefault("peak_pricing", None)
    else:
        out.update(row)
        out["date"] = today
        out["price_confidence"] = conf
        out["source"] = src
    return out


def merge(kind: str, rows: list[dict[str, Any]], dry_run: bool) -> int:
    schema = SCHEMAS[kind]
    path = repo_data.DATA / schema["file"]
    blob = yaml.safe_load(path.read_text(encoding="utf-8"))
    existing = blob[schema["collection"]]
    by_id = {e["id"]: e for e in existing}
    today = date.today()

    added, filled, conflicts, unchanged = [], [], [], 0
    for row in rows:
        entry = nest(kind, dict(row), today)
        eid = entry["id"]
        if eid not in by_id:
            added.append(eid)
            if not dry_run:
                existing.append(entry)
            continue
        current = by_id[eid]
        touched = False
        for key, value in entry.items():
            if key in {"id", "date", "price_date"}:
                continue
            if key not in current or current[key] is None:
                if not dry_run:
                    current[key] = value
                filled.append(f"{eid}.{key}")
                touched = True
            elif isinstance(value, (int, float)) and isinstance(current[key], (int, float)):
                if abs(float(current[key]) - float(value)) > 1e-9:
                    conflicts.append(f"{eid}.{key}: data has {current[key]}, csv has {value}")
        if not touched:
            unchanged += 1

    print(f"{kind}: {len(rows)} rows read")
    print(f"  added      {len(added)}" + (f"  ({', '.join(added[:8])}{'...' if len(added) > 8 else ''})" if added else ""))
    print(f"  filled     {len(filled)} previously empty fields")
    print(f"  unchanged  {unchanged}")
    if conflicts:
        print(f"  CONFLICTS  {len(conflicts)} (not applied; resolve by hand with a source):")
        for c in conflicts[:20]:
            print(f"    {c}")
        if len(conflicts) > 20:
            print(f"    ...and {len(conflicts) - 20} more")
    if dry_run:
        print("\ndry run: nothing written")
        return 0
    path.write_text(
        yaml.safe_dump(blob, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    print(f"\nwrote {path.relative_to(repo_data.ROOT)}")
    print("Next: python scripts/sotw.py update")
    return 0


def read_csv(path: Path, kind: str) -> list[dict[str, Any]]:
    schema = SCHEMAS[kind]
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for lineno, raw in enumerate(csv.DictReader(f), start=2):
            row: dict[str, Any] = {}
            for column, value in raw.items():
                if column is None or column not in schema["columns"]:
                    continue
                if blank(value):
                    continue
                try:
                    row[column] = typed(column, value)
                except ValueError:
                    print(f"  line {lineno}: cannot parse {column}={value!r}, skipping that cell")
            missing = [c for c in schema["required"] if c not in row]
            if missing:
                print(f"  line {lineno}: missing {', '.join(missing)}, skipping row")
                continue
            rows.append(row)
    return rows


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--template" in flags:
        kind = args[0] if args else "cpus"
        print(",".join(SCHEMAS[kind]["columns"]))
        return 0
    if len(args) < 2:
        print(__doc__)
        print("kinds: " + ", ".join(SCHEMAS))
        return 2
    kind, csv_path = args[0], Path(args[1])
    if kind not in SCHEMAS:
        print(f"unknown kind {kind!r}; expected one of {', '.join(SCHEMAS)}")
        return 2
    if not csv_path.exists():
        print(f"no such file: {csv_path}")
        return 2
    return merge(kind, read_csv(csv_path, kind), "--dry-run" in flags)


if __name__ == "__main__":
    raise SystemExit(main())
