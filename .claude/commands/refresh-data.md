---
description: Pull the latest figures for every stale or missing input, then re-solve
allowed-tools: Bash, Read, Edit, WebSearch, WebFetch, Glob, Grep
---

Refresh this repo's data layer. This is the only job here that needs judgment; everything
downstream is arithmetic that re-solves itself.

## What to do

1. Run `python scripts/refresh_plan.py --json` and treat that list as the work order.
   Priority 1 first (expired), then 2, then 3. Do not invent work that is not on it.

2. For each item, find the current figure. `data/SOURCES.md` says what each source is;
   many notes are marked `TODO: link` because no URL was captured, so search for the
   primary source rather than guessing a URL. Prefer, in order:
   - the vendor's own pricing or spec page for prices and specs
   - spec.org for SPECrate submissions
   - the benchmark's own site, with its version, for index scores
   - a retailer listing for street prices, naming the retailer

3. Edit the YAML. Every changed figure:
   - new `value` and a `date` of the day you pulled it
   - old value moved into a `history` entry with `superseded:` and a note
   - `confidence` per CONTRIBUTING.md; never upgrade an ESTIMATE to a fact because a
     newer number appeared
   - add or fix the matching note in `data/SOURCES.md`, replacing `TODO: link` with the
     real URL when you have one

4. If you cannot verify a figure, leave it alone and say so. Write `TODO: unverified`
   rather than a plausible value. Never invent a price, a score, a DOI, or a URL.

5. Run `python scripts/sotw.py update`. It re-solves every doc, both plots, both latest
   reports, and runs the checks.

6. If a check fails, a conclusion probably flipped. Do not weaken the test. Confirm the
   new data is right, then record the reversal in the README changelog. A reversal is the
   most valuable thing this repo publishes.

7. Commit with a `data:` prefix, naming what moved and by how much. One logical change per
   commit. Report at the end: what moved, what flipped, what you could not verify.

## Rules

- Every number carries a pull date and a confidence tag. No exceptions.
- Prices are VOLATILE by default. SPECrate submissions never expire.
- Do not touch `models/`, `scripts/`, or the analysis prose. Data only.
- If the work order is empty, say so and stop.
