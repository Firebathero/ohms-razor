# Contributing

This repo has one governing rule: **there are no static numbers.** Every figure in every
table is solved from `data/` at build time. If you find a number in prose or a table that a
script could have produced, that is a bug. PRs that hand-type numbers into markdown will be
asked to move them into the data layer.

## The loop

Steps 2 through 5 are one command: `python scripts/sotw.py update` (it also rewrites
`reports/latest-tokens.md` and `reports/latest-compute.md`, and ends with the list of
figures still needing a manual re-pull). The steps individually:

1. Edit or add figures in `data/*.yaml`. Every figure carries `value`, `date`, `source`, and
   `confidence`. When you update a value, move the old one into a `history` list rather than
   deleting it.
2. `python scripts/check_staleness.py` to see what is past its freshness window.
3. `python scripts/build_tables.py` to re-solve every generated block in the README and the
   analysis docs. `--check` verifies the committed docs match the data without writing.
4. `python scripts/plot_frontier.py` and `python scripts/plot_watts.py` to regenerate the
   plots. `python scripts/answer.py` prints the currently solved answer to both placement
   questions; sanity-check it after any data change.
5. `pytest` runs three kinds of tests:
   - math checks: the model formulas against dated input snapshots
   - workbook parity: the pipeline must reproduce `spreadsheets/compute-node-model.xlsx`
     from that workbook's own inputs
   - conclusion tests: the published claims, recomputed as relations over live data
6. If a conclusion test fails after a data refresh, the world changed. Do not weaken the
   test to make it pass. Update the data, let the tables re-solve, and record the reversal in
   the README changelog. A reversal is the most valuable thing this repo can publish.

## Confidence tags

| Tag | Meaning |
|---|---|
| MEASURED | Someone ran the benchmark or read the meter |
| CONFIRMED | Vendor-published spec or price, checked on the date given |
| DERIVED | Computed from measured figures; derivation stated in the source note |
| ESTIMATE | Someone's judgment; labeled as such everywhere it propagates |
| VOLATILE | Correct on the pull date, expected to move; re-verify before relying on it |
| EXPIRES | Carries an explicit end date |
| DEFINITION | A chosen unit of account, not a fact about the world |

Never upgrade an estimate to a fact. If a number is missing, write `TODO: unverified`
rather than a plausible value. Do not invent citations or URLs; `data/SOURCES.md` marks
uncaptured links with `TODO: link`.

## Freshness windows

| Category | Window |
|---|---|
| Model API pricing | 30 days |
| Hardware pricing | 30 days |
| DRAM pricing | 14 days |
| Benchmark scores | 60 days |
| SPECrate submissions | never expire |

## Commits

Conventional prefixes: `data:`, `models:`, `analysis:`, `docs:`, `fix:`. One logical change
per commit. Never force-push `main`. Tag a release whenever a conclusion changes, with the
reversal in the release notes. No secrets, no API keys, no personal information.

## Watch list

Each of these will move, and each one changes a conclusion:

- GLM-5.3-Flash promo ends 2026-09-09. The list-price conclusion should survive; confirm it.
- DeepSeek moved output pricing 371% in one week (2026-08-16). Assume more volatility.
- DDR5 shortage forecast into mid-2027. Every hardware conclusion is sensitive to $/GB.
- New model launches may create the midrange tier that finding F2 says does not exist.
  Reporting that reversal is worth more than having been right the first time.
- Kimi K2.5 and moonshot-v1 retirement. Model deprecation is a live risk for the frontier tier.

## Open questions worth a contributor's time

- Measured batching curves on Strix Halo: aggregate tok/s vs concurrent requests for a
  120B-class MoE. This is the strongest rebuttal to the local-vs-cloud finding and the repo
  wants the measurement, whichever way it points.
- Actual 450W vs 500W performance on an EPYC 9965. The phi = 0.99 derate is an estimate.
- Whether the two-tier structure holds as new models land.
- Effective vs nominal bandwidth across unified-memory platforms.
- Cost per unit of capability rather than per token: dollars per (index point x Mtok).
