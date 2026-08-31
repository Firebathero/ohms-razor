---
description: Pull the latest figures for every stale or missing input, then re-solve
allowed-tools: Bash, Read, Edit, WebSearch, WebFetch, Glob, Grep
---

Refresh this repo's data layer. This is the only job here that needs judgment; everything
downstream is arithmetic that re-solves itself.

## What to do

1. Run `python scripts/refresh_plan.py --json` and treat that list as the work order.
   Priority 1 first, then 2, then 3. Do not invent work that is not on it.

2. **Do the `survey` items before anything else.** These are the ones that matter. A
   survey item means a candidate list has not been re-opened inside its interval, or ever.
   Refreshing prices for a stale list of candidates produces a precisely wrong answer: the
   incumbent's price to the cent, while the actual winner is a part nobody added.

   For each survey item, read the `survey` block in that YAML file. It carries the
   question to answer, the inclusion criteria, what is out of scope, and where to look.
   Then:
   - Search for candidates that meet the inclusion criteria and are not already listed.
     Look for things released or repriced since `last_surveyed`, and for whole categories
     the list is missing (a vendor, an architecture, a form factor nobody considered).
   - Add every candidate that plausibly competes, with the same field structure as the
     existing entries, each figure dated and tagged. A candidate you cannot fully populate
     still goes in, with `TODO: unverified` on the missing fields; the tools report it as
     unplaceable rather than silently ignoring it.
   - Record what you looked at and rejected in `considered_and_excluded`, with the reason.
     That list is how the next survey avoids re-litigating settled questions, and how a
     reader checks your judgment.
   - Set `last_surveyed` to today and `confidence` appropriately, **even if you added
     nothing**. "We looked and there was nothing new" is a finding worth recording, and it
     is different from "nobody has looked."
   - If the survey block's own scope looks wrong (criteria too narrow, a source that no
     longer exists), say so rather than working inside a bad frame.

3. Then the `stale` and `gap` items. For each, find the current figure. `data/SOURCES.md`
   says what each source is; many notes are marked `TODO: link` because no URL was
   captured, so search for the primary source rather than guessing a URL. Prefer, in order:
   - the vendor's own pricing or spec page for prices and specs
   - spec.org for SPECrate submissions
   - the benchmark's own site, with its version, for index scores
   - a retailer listing for street prices, naming the retailer

4. Edit the YAML. Every changed figure:
   - new `value` and a `date` of the day you pulled it
   - old value moved into a `history` entry with `superseded:` and a note
   - `confidence` per CONTRIBUTING.md; never upgrade an ESTIMATE to a fact because a
     newer number appeared
   - add or fix the matching note in `data/SOURCES.md`, replacing `TODO: link` with the
     real URL when you have one

5. If you cannot verify a figure, leave it alone and say so. Write `TODO: unverified`
   rather than a plausible value. Never invent a price, a score, a DOI, or a URL.

6. Run `python scripts/sotw.py update`. It re-solves every doc, both plots, both latest
   reports, and runs the checks.

7. If a check fails, a conclusion probably flipped. Do not weaken the test, and never drop
   a candidate to make a test pass. Confirm the new data is right, then record the
   reversal in the README changelog. `tests/test_conclusions.py` carries an `INCUMBENTS`
   map naming the current winners; if a survey displaced one, update it there and say so
   in the changelog. A displaced incumbent is the most valuable thing this repo publishes.

8. Commit with a `data:` prefix, naming what moved and by how much. Keep surveys and
   refreshes in separate commits. Report at the end: what you added, what you rejected and
   why, what moved, what flipped, and what you could not verify.

## Rules

- Every number carries a pull date and a confidence tag. No exceptions.
- Prices are VOLATILE by default. SPECrate submissions never expire.
- Adding a candidate is cheap and reversible; leaving one out is invisible. When unsure
  whether something belongs in scope, add it and note the doubt.
- Do not touch `models/`, `scripts/`, or the analysis prose. Data only.
- If the work order is empty, say so and stop.
