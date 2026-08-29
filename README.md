# ohms-razor

Never use more model than the task needs.

<!-- gen:last_solved -->
**Last solved:** 2026-08-29. **3 figure(s) past their freshness window** (run `python scripts/check_staleness.py`).
<!-- /gen:last_solved -->

Two questions, answered from dated data:

1. What do I buy for compute? (builds, sims, batch jobs)
2. What do I use for tokens? (thinking)

The short version: buy the compute, rent the tokens. An always-on box is where an agent
lives, not where thinking happens.

One rule: no static numbers. Every figure below is solved from `data/*.yaml` when the
build runs. Change an input, rerun, everything updates. If a conclusion flips, a test
fails and the flip goes in the changelog.

## Run it

```bash
pip install -r requirements.txt

python scripts/sotw.py            # the answer + what's stale
python scripts/sotw.py update     # after editing data/: re-solve docs, plots, reports, run checks
python scripts/sotw.py tokens     # write reports/latest-tokens.md
python scripts/sotw.py compute    # write reports/latest-compute.md
pytest                            # the checks on their own
```

## What you get

- The answer, below (terminal version: `python scripts/answer.py`)
- `REPORT.md`: answer, findings, freshness on one page
- `reports/latest-tokens.md` and `reports/latest-compute.md`: the deep dives
- Two plots, staleness flags, and the test suite guarding the conclusions

<!-- gen:the_answer -->
```text
THE COMPUTE QUESTION  (deterministic work: builds, simulation, batch jobs)
  own it           AMD EPYC 9965 at $2.04 per SPECrate-point-year all-in over 10 years
  renting instead  4.2x to 8.1x the cost of owning, same unit
  watts binding?   AMD EPYC 9845 is the efficiency pick at 2.96 pts per wall watt

THE TOKENS QUESTION  (thinking)
  default          glm-5.3-flash: AA 57, $0.045/task, $1,915 for the 10-yr reference workload at list ($958 on promo through 2026-09-09)
  frontier calls   grok-4.6: AA 60, $0.62/task, the cheapest costed frontier point (13.8x default per task)
  local inference  no: the best passing local config runs 3.3x cloud cost at AA 24
  the local box    hosts the agent: orchestration, sandboxes, a small resident triage model

Caveats, solved with the answer: kimi-k3, glm-5.3-max, claude-opus-5 sit at or above the frontier pick's score with no cost per task yet (TODO in data/benchmarks.yaml); the pick re-solves when they are costed. kimi-k3 is the one frontier model with API pricing here and prices the reference workload at $52,542 (27.4x default), which is why the frontier tier is for rare calls, not the loop. Every price is VOLATILE; run scripts/check_staleness.py before trusting.
```
<!-- /gen:the_answer -->

## What you can change

Every input lives in `data/*.yaml` with a date and a confidence tag. Edit, keep the old
value in `history`, run `python scripts/sotw.py update`. The knobs that matter:

<!-- gen:knobs -->
| Knob | Where | Current | Moves |
|---|---|---|---|
| Workload | `workload.yaml` | 315M out/yr, 80% cache, 10 yr | the throughput bar and every API cost |
| Electricity | `assumptions.yaml` | $0.20/kWh | Psi and local $/Mtok |
| Hold period | `assumptions.yaml` | 10 yr | Psi roughly doubles at 5 |
| DDR5 price | `assumptions.yaml` | $35.70/GB (2026-08-14) | the biggest lever on Psi; never the ranking |
| Utilization | `assumptions.yaml` | 1 | local break-evens |
| Prices and scores | `model_pricing.yaml`, `benchmarks.yaml` | dated per entry | the whole token answer |
<!-- /gen:knobs -->

## Pick your axis

The compute pick optimizes a formula, and which formula is your call:

- **Value** (the default): Psi = TCO / (work x years), dollars per SPECrate-point-year,
  lower wins. Capex, watts, cooling, and hold period all fold in.
- **Efficiency**: SPECrate points per wall watt. Pick this axis when watts are the
  constraint: a capped circuit, a thermal envelope, a UPS budget.

The two axes disagree on the winner right now (a test asserts it), which is why both are
solved and plotted instead of merged:

![Compute per watt vs Psi](analysis/assets/compute_per_watt.png)

Tokens has its own axis pair, capability vs cost per task, and the frontier is currently
a cliff: a cheap near-frontier tier, an expensive frontier tier, nothing in between.

![Capability vs cost Pareto frontier](analysis/assets/pareto_frontier.png)

## The bar

One line of arithmetic filters local hardware before cost even comes up:

<!-- gen:workload_derivation -->
```text
315,000,000 output tokens/yr / 31,557,600 s/yr = 9.98 tok/s
sustained, 24/7/365, zero downtime

over 10 years at 80% cache hit:
  3.15B output tokens
  1.26B fresh input tokens
  5.04B cached input tokens
```
<!-- /gen:workload_derivation -->

A box that can't sustain that rate can't produce the workload at any duty cycle.

## Findings

<!-- gen:findings_summary -->
| # | Finding | Solved right now | Data date |
|---|---|---|---|
| F1 | Renting beats self-hosting for the reference workload | glm-5.3-flash (list): $1,915 for 10 years at AA 57, cheapest capable path at list price | 2026-08-29 |
| F2 | There is no midrange tier | Pareto frontier runs $0.045/task (AA 57) to $0.62/task (AA 60); everything between is dominated | 2026-08-26 |
| F3 | Local hardware fails the throughput bar before it fails on cost | Bar is 9.98 tok/s sustained; 1 of 4 tested configs clears it on measured numbers | 2026-08-29 |
| F4 | Even when local passes, it loses | $0.56/M local vs $0.17/M cloud, same weights, fully saturated: 3.3x | 2026-08-29 |
| F5 | The local box is for hosting, not inference | Thesis; see README | |
| F6 | The hardware scarcity is a supply story, not a demand story | Two defensible readings; both presented in analysis 06 | 2026-08-25 |
| F7 | Owning beats renting for deterministic compute | AMD EPYC 9965 at $2.04/pt-yr; renting runs 4.2x to 8.1x owning | 2026-06-15 |
<!-- /gen:findings_summary -->

Full write-ups, including what would falsify each one: `analysis/01` through `analysis/06`.

## Known weaknesses

Up front on purpose. Details in `analysis/`.

- Local figures assume batch size 1; batching is modelled in `analysis/04` but not measured
- The 9965's 450W derate (phi 0.99) is an estimate, nobody has measured it
- 1P SPECrate is scaled from 2P; rankings survive, absolute levels inherit the error
- The 9845 has a single SPECrate submission
- The Mac Studio M5 Ultra price is a guess, tagged ESTIMATE
- Index parity is not task parity
- 10-year amortization is aggressive; numbers roughly double at 5
- The supply-vs-demand finding has a live counter-reading, presented in `analysis/06`

## Trust

<!-- gen:freshness -->
| Category | Figures | Oldest | Window | Status |
|---|---:|---|---|---|
| benchmarks | 1 | 2026-08-26 | 60d | fresh |
| dram | 1 | 2026-08-14 | 14d | **1 flagged** |
| hardware_pricing | 10 | 2026-06-15 | 30d | **2 flagged** |
| model_pricing | 5 | 2026-08-29 | 30d | fresh |

SPECrate submissions never expire and are not policed.
<!-- /gen:freshness -->

Tags: MEASURED, CONFIRMED, DERIVED, ESTIMATE, VOLATILE, EXPIRES. Estimates never get
upgraded to facts. Windows and the update loop: `CONTRIBUTING.md`.

## Layout

```text
REPORT.md      the output: answer, findings, freshness on one solved page
reports/       latest-tokens.md and latest-compute.md, per-question deep reports
data/          every figure: value, unit, date, source, confidence (the only ground truth)
models/        models 1-5 as pure functions, no I/O
scripts/       sotw, the solver, table generator, staleness gate, plots
tests/         formula checks, workbook parity, conclusions-as-relations
analysis/      one document per finding, prose around solved tables
spreadsheets/  the original interactive Psi workbook (kept in parity by test)
```

## Changelog

- **2026-08-29** Initial publication. Baseline conclusions: F1 rent the volume tier (GLM
  wins at list), F2 no midrange tier, F3 the 10 tok/s bar eliminates dense-70B local
  configs, F4 the passing local config still loses to cloud on the same weights, F5 the
  box is for hosting, F6 supply story favored over demand story (both presented), F7 own
  rather than rent for deterministic compute (9965 at 450W). Known day-one flags: DRAM
  pricing already past its 14-day window (dated 2026-08-14) and both Hetzner figures past
  30 days (dated 2026-06-15); re-pull before relying on those.
- **2026-08-29** Split the placement decision into its two questions explicitly: added the
  solved answer block (`scripts/answer.py`), and gave compute per watt its own plot and
  analysis section instead of a table column.
- **2026-08-29** Made the repo culminate in artifacts: `REPORT.md` (the one-page output),
  `reports/latest-tokens.md` and `reports/latest-compute.md` (per-question deep reports),
  and `scripts/sotw.py` with `show`, `update`, `tokens`, `compute` so the state of the
  world is one command to read and one command to refresh.
- **2026-08-29** README rewritten usage-first: run it, what you get, what you can change,
  pick your axis. The knobs table is generated so its current values can never go stale.

MIT. See `LICENSE`.
