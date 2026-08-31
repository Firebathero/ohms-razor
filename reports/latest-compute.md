# Compute economics: latest

The compute question (what do I buy for deterministic work), solved from `data/` by `python scripts/sotw.py compute`. Nothing here is hand-typed; git history is the archive of previous states.

**Last solved:** 2026-08-31. **3 figure(s) past their freshness window** (run `python scripts/check_staleness.py`).

## The answer

```text
THE COMPUTE QUESTION  (deterministic work: builds, simulation, batch jobs)
  own it           AMD EPYC 9965 at $2.04 per SPECrate-point-year all-in over 10 years
  renting instead  4.2x to 8.1x the cost of owning, same unit
  watts binding?   AMD EPYC 9845 is the efficiency pick at 2.96 pts per wall watt
```

## The candidates on Psi

| CPU | Cores | Run cTDP | phi | W (1P pts) | Wall W | TCO | Psi ($/pt-yr) | pts/W | Energy share | Rank |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| **AMD EPYC 9965** | 192 | 450W | 0.99 (ESTIMATE) | 1,634 | 598 | $33,290 | 2.04 | 2.73 | 31% | 1 |
| AMD EPYC 9845 | 160 | 320W | 0.98 (DERIVED) | 1,350 | 457 | $33,497 | 2.48 | 2.96 | 24% | 3 |
| AMD EPYC 9755 | 128 | 500W | 1 (DEFINITION) | 1,361 | 652 | $33,743 | 2.48 | 2.09 | 34% | 2 |
| AMD EPYC 9745 | 128 | 320W | 0.98 (MEASURED) | 1,200 | 457 | $31,013 | 2.58 | 2.63 | 26% | 4 |

Winner: **AMD EPYC 9965** at $2.04 per SPECrate-point-year over 10 years ($22,809 capex). Best perf/watt is **AMD EPYC 9845** at 2.96 pts/W: efficiency and value rank differently, which is the point of solving for Psi instead.

## Compute per watt, its own question

| CPU | pts per wall watt | Efficiency rank | Psi rank |
|---|---:|---:|---:|
| AMD EPYC 9845 | 2.96 | 1 | 3 |
| AMD EPYC 9965 | 2.73 | 2 | 1 |
| AMD EPYC 9745 | 2.63 | 3 | 4 |
| AMD EPYC 9755 | 2.09 | 4 | 2 |

**AMD EPYC 9845** is the efficiency champion at 2.96 pts/W and **AMD EPYC 9965** wins on value at 2.73 pts/W; the value ranking holds at every electricity price in the sensitivity table, so the efficiency answer only becomes the buying answer when watts, not dollars, are the binding constraint (a power-capped circuit, a thermal envelope, a UPS budget).

![Compute per watt vs Psi](../analysis/assets/compute_per_watt.png)

## Sensitivity: electricity

| $/kWh | 9965 | 9845 | 9755 | 9745 | Winner |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.72 | 2.19 | 2.06 | 2.25 | 9965 |
| 0.20 | 2.04 | 2.48 | 2.48 | 2.58 | 9965 |
| 0.30 | 2.36 | 2.78 | 2.90 | 2.92 | 9965 |
| 0.40 | 2.68 | 3.08 | 3.32 | 3.25 | 9965 |
| 0.60 | 3.32 | 3.67 | 4.16 | 3.92 | 9965 |

## Sensitivity: hold period

| Hold (yr) | 9965 | 9845 | 9755 | 9745 | Winner |
|---:|---:|---:|---:|---:|---:|
| 3 | 5.29 | 6.89 | 6.30 | 7.06 | 9965 |
| 5 | 3.43 | 4.37 | 4.12 | 4.50 | 9965 |
| 7 | 2.64 | 3.29 | 3.18 | 3.41 | 9965 |
| 10 | 2.04 | 2.48 | 2.48 | 2.58 | 9965 |
| 12 | 1.80 | 2.17 | 2.21 | 2.26 | 9965 |

Shorter holds punish capex and reward efficiency; the ranking holds while the absolute numbers roughly double at five years (handoff weakness 7: ten-year amortization is aggressive).

## Tie prices

| Contender | CPU price that ties the winner | Street price | Gap |
|---|---:|---:|---:|
| AMD EPYC 9845 | $3,684 | $9,684 | $6,000 too expensive |
| AMD EPYC 9755 | $483 | $6,500 | $6,017 too expensive |
| AMD EPYC 9745 | $640 | $7,200 | $6,560 too expensive |

## The memory lever

| DDR5 $/GB | Memory cost (384GB) | Winner Psi |
|---:|---:|---:|
| $8.00 (pre-shortage) | $3,072 | 1.39 |
| $15.00 | $5,760 | 1.55 |
| $25.00 | $9,600 | 1.79 |
| $35.70 (current) | $13,709 | 2.04 |
| $45.00 | $17,280 | 2.26 |

Memory is identical across candidates, so it never changes the ranking. It is also the largest single number under your control; waiting for DRAM normalization is worth more than any CPU decision in this repo.

## Own vs rent

| Option | SPECrate 1P | $/month | Psi ($/pt-yr) | vs owning |
|---|---:|---:|---:|---:|
| **Own: AMD EPYC 9965** | 1,634 | $277.42 (amortized) | 2.04 | 1.0x |
| Hetzner AX162-1 | 523 | $722.10 | 16.57 | 8.1x |
| Hetzner AX162-1-LTD | 523 | $372.10 | 8.54 | 4.2x |

Matching the owned node takes 3.1 rented boxes, $27,071 per year: one year of equivalent rental costs most of a decade of owning ($33,290 all-in).

| Hetzner cloud instance | Old EUR/mo | New EUR/mo | Increase |
|---|---:|---:|---:|
| CCX63 | 374.49 | 853.49 | +128% |
| CPX41 | 38.99 | 120.49 | +209% |
| CPX51 | 77.99 | 237.99 | +205% |

Cloud repricing of 2026-06-15 ran +128% to +209%, computed from the raw prices (the handoff's stated 128-205% range slightly understated the top end). Renting still buys hardware replacement, redundant power, someone on call at 3am, the option to stop paying, and no DRAM-market exposure; the model does not price those, and says so.

## Reconciliation with the handoff

| Quantity | Handoff F7 | This repo, same RAM price | This repo, current RAM price |
|---|---:|---:|---:|
| DDR5 $/GB | implied $16.06 | $16.06 | $35.70 |
| 10-yr Psi per point | $15.85 | $15.76 | $20.37 |
| Psi ($/pt-yr) | 1.58 | 1.58 | 2.04 |

The handoff's F7 figures back-solve to DDR5 near $16.06/GB, against the $35.70/GB its own data table carries (2026-08-14). At the implied price this repo reproduces the reported number within 0.6% (the residual is rounding drift inside the handoff itself). The published Psi is whatever the current data solves to; the old figure is kept in data/cpu_specs.yaml as SUPERSEDED.

## How wide was the search

| Candidate set | Candidates | Last surveyed | Interval | Status |
|---|---:|---|---:|---|
| CPU candidates for the compute node | 4 | never | 90d | **never surveyed** |
| hosted models for the token tiers | 4 | never | 30d | **never surveyed** |
| local machines for on-box inference | 4 | never | 90d | **never surveyed** |
| the capability axis itself | 7 | 2026-08-26 | 60d | current |

3 of 4 candidate sets were inherited from the original research and have never been re-opened. Every ranking drawn from them is "best of these", not "best available". Run `python scripts/refresh_plan.py` for the survey scope and where to look, or `/refresh-data` to have an agent do it.

## How much to trust this today

| Category | Figures | Oldest | Window | Status |
|---|---:|---|---|---|
| benchmarks | 1 | 2026-08-26 | 60d | fresh |
| dram | 1 | 2026-08-14 | 14d | **1 flagged** |
| hardware_pricing | 10 | 2026-06-15 | 30d | **2 flagged** |
| model_pricing | 5 | 2026-08-29 | 30d | fresh |

SPECrate submissions never expire and are not policed.
