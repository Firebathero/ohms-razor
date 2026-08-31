# ohms-razor: the report

This file is the repo's output. One page, entirely solved from `data/` by
`python scripts/build_tables.py`; nothing here is hand-typed. For the terminal version of
the answer alone, run `python scripts/answer.py`. For mechanisms, sensitivities, and what
would falsify each finding, see `analysis/`.

<!-- gen:last_solved -->
**Last solved:** 2026-08-31. **3 figure(s) past their freshness window** (run `python scripts/check_staleness.py`).
<!-- /gen:last_solved -->

## The answer

<!-- gen:the_answer -->
```text
THE COMPUTE QUESTION  (deterministic work: builds, simulation, batch jobs)
  own it           AMD EPYC 9965 at $2.20 per SPECrate-point-year all-in over 10 years
  renting instead  3.9x to 7.5x the cost of owning, same unit
  watts binding?   AMD EPYC 9845 is the efficiency pick at 2.68 pts per wall watt

THE TOKENS QUESTION  (thinking)
  default          glm-5.3-flash: AA 57, $0.090/task, $1,915 for the 10-yr reference workload at list ($958 on promo through 2026-09-09)
  frontier calls   claude-opus-5: AA 63, $2.34/task, the cheapest costed frontier point (26.0x default per task)
  local inference  no: the best passing local config runs 4.1x cloud cost at AA 24
  the local box    hosts the agent: orchestration, sandboxes, a small resident triage model

Caveats, solved with the answer: The frontier tier is for rare calls, not the loop: pricing the reference workload against its 26 priced models runs from $12,348 (glm-5, 6x the default) to $756,000 (gpt-5.5-pro, 395x). Every price is VOLATILE; run scripts/check_staleness.py before trusting.
```
<!-- /gen:the_answer -->

## The findings behind it

<!-- gen:findings_summary -->
| # | Finding | Solved right now | Data date |
|---|---|---|---|
| F1 | Renting beats self-hosting for the reference workload | glm-5.3-flash (list): $1,915 for 10 years at AA 57, cheapest capable path at list price | 2026-08-29 |
| F2 | ~~There is no midrange tier~~ **Reversed 2026-08-31**: the frontier is a curve, not a cliff | 7 of 32 costed models are Pareto-optimal, spanning $0.01/task (AA 10) to $2.34/task (AA 63) | 2026-08-31 |
| F3 | Local hardware fails the throughput bar before it fails on cost | Bar is 9.98 tok/s sustained; 32 of 39 tested configs clears it on measured numbers | 2026-08-29 |
| F4 | Even when local passes, it loses | $0.70/M local vs $0.17/M cloud, same weights, fully saturated: 4.1x | 2026-08-29 |
| F5 | The local box is for hosting, not inference | Thesis; see README | |
| F6 | The hardware scarcity is a supply story, not a demand story | Two defensible readings; both presented in analysis 06 | 2026-08-25 |
| F7 | Owning beats renting for deterministic compute | AMD EPYC 9965 at $2.20/pt-yr; renting runs 3.9x to 7.5x owning | 2026-06-15 |
<!-- /gen:findings_summary -->

![Capability vs cost Pareto frontier](analysis/assets/pareto_frontier.png)

![Compute per watt vs Psi](analysis/assets/compute_per_watt.png)

## How wide was the search?

<!-- gen:survey_status -->
| Candidate set | In catalog | Fully placeable | Last surveyed | Status |
|---|---:|---|---|---|
| CPU candidates for the compute node | 124 | 119 priced, 123 screenable | 2026-08-31 | current |
| hosted models for the token tiers | 97 | see report | 2026-08-31 | current |
| local machines for on-box inference | 37 | see report | 2026-08-31 | current |
| the capability axis itself | 49 | 32 costed | 2026-08-31 | current |

Every candidate set has been surveyed inside its interval.
<!-- /gen:survey_status -->

## How much to trust it today

<!-- gen:freshness -->
| Category | Figures | Oldest | Window | Status |
|---|---:|---|---|---|
| benchmarks | 1 | 2026-08-31 | 60d | fresh |
| dram | 1 | 2026-08-14 | 14d | **1 flagged** |
| hardware_pricing | 45 | 2026-06-15 | 30d | **2 flagged** |
| model_pricing | 98 | 2026-08-29 | 30d | fresh |

SPECrate submissions never expire and are not policed.
<!-- /gen:freshness -->

Confidence tags and freshness windows are defined in `CONTRIBUTING.md`. If the tables
above disagree with `python scripts/answer.py`, run `python scripts/build_tables.py`;
the docs are stale, the solver is not.
