# Compute economics: latest

The compute question (what do I buy for deterministic work), solved from `data/` by `python scripts/sotw.py compute`. Nothing here is hand-typed; git history is the archive of previous states.

**Last solved:** 2026-08-31. **3 figure(s) past their freshness window** (run `python scripts/check_staleness.py`).

## The answer

```text
THE COMPUTE QUESTION  (deterministic work: builds, simulation, batch jobs)
  own it           AMD EPYC 9965 at $2.20 per SPECrate-point-year all-in over 10 years
  renting instead  3.9x to 7.5x the cost of owning, same unit
  watts binding?   AMD EPYC 9845 is the efficiency pick at 2.68 pts per wall watt
```

## The candidates on Psi

| # | CPU | Cores | Power | phi | Mem | W (1P pts) | Wall W | TCO | Psi ($/pt-yr) | pts/W | Basis | Price |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | **AMD EPYC 9965** | 192 | 450W | 0.99 (ESTIMATE) | 384GB | 1,510 | 598 | $33,290 | 2.20 | 2.53 | 1P measured | street |
| 2 | AMD EPYC 9755 | 128 | 500W | 1 (DEFINITION) | 384GB | 1,260 | 652 | $33,743 | 2.68 | 1.93 | 1P measured | street |
| 3 | AMD EPYC 9845 | 160 | 320W | 0.98 (DERIVED) | 384GB | 1,225 | 457 | $33,497 | 2.73 | 2.68 | 1P measured | street |
| 4 | AMD EPYC 9745 | 128 | 320W | 0.98 (MEASURED) | 384GB | 1,132 | 457 | $31,013 | 2.74 | 2.48 | 1P measured | street |
| 5 | AMD EPYC 9825 | 144 | 390W stock | 1 (stock) | 384GB | 1,240 | 533 | $38,152 | 3.08 | 2.33 | 1P measured | list |
| 6 | AMD EPYC 9655P | 96 | 400W stock | 1 (stock) | 384GB | 993 | 543 | $30,683 | 3.09 | 1.83 | 1P measured | street |
| 7 | AMD EPYC 8635P | 84 | 225W stock | 1 (stock) | 192GB | 666 | 353 | $20,947 | 3.15 | 1.89 | 1P measured | list |
| 8 | AMD EPYC 8535P | 64 | 210W stock | 1 (stock) | 192GB | 614 | 337 | $20,361 | 3.32 | 1.82 | 1P measured | list |
| 9 | AMD EPYC 8435P | 48 | 200W stock | 1 (stock) | 192GB | 528 | 326 | $17,770 | 3.37 | 1.62 | 1P measured | list |
| 10 | AMD EPYC 9645 | 96 | 320W stock | 1 (stock) | 384GB | 1,004 | 457 | $34,861 | 3.47 | 2.20 | 1P measured | list |
| 11 | AMD EPYC 9654P | 96 | 360W stock | 1 (stock) | 384GB | 834 | 500 | $29,925 | 3.59 | 1.67 | 1P measured | street |
| 12 | AMD EPYC 9655 | 96 | 400W stock | 1 (stock) | 384GB | 1,030 | 543 | $37,189 | 3.61 | 1.90 | 1P measured | list |
| 13 | Intel Xeon 6980P | 128 | 500W stock | 1 (stock) | 384GB | 1,220 | 652 | $45,043 | 3.69 | 1.87 | 1P measured | list |
| 14 | Intel Xeon 6979P | 120 | 500W stock | 1 (stock) | 384GB | 1,150 | 652 | $42,993 | 3.74 | 1.76 | 1P measured | list |
| 15 | Intel Xeon 6952P | 96 | 400W stock | 1 (stock) | 384GB | 969 | 543 | $36,737 | 3.79 | 1.78 | 1P measured | list |

Top 15 of 119 priced candidates, out of 124 in the catalog. Winner: **AMD EPYC 9965** at $2.20 per SPECrate-point-year over 10 years ($22,809 capex). Best perf/watt is **AMD EPYC 9845** at 2.68 pts/W: efficiency and value rank differently, which is the point of solving for Psi instead.

**Price basis matters here.** 113 of 119 priced candidates carry only a vendor list price, which is an upper bound on what the part costs, so their Psi is an upper bound too and their true rank can only improve. Only 6 have a street price. Read a list-priced row as "no better than this", never as "this is what it costs", and see the breakeven table for the price each contender would need to reach to tie the winner.

**Mem** is memory priced into the build: one DIMM per channel, capped at the 12 the operator asked for. A six-channel SP6 part is charged for six DIMMs because it cannot hold twelve, which also means it is not the same machine as a twelve-channel one. Dollars per point has no opinion about that, so say it with a brightline: `razor.py --min-memory-gb`.

## Compute per watt, its own question

| # | CPU | pts per wall watt | Wall W | Psi rank |
|---:|---|---:|---:|---|
| 1 | AMD EPYC 9845 | 2.68 | 457 | 3 |
| 2 | AMD EPYC 9965 | 2.53 | 598 | 1 |
| 3 | AMD EPYC 9745 | 2.48 | 457 | 4 |
| 4 | Intel Xeon 6980E+ | 2.36 | 543 | unpriced |
| 5 | Intel Xeon 6990E+ | 2.35 | 598 | unpriced |
| 6 | AMD EPYC 9825 | 2.33 | 533 | 5 |
| 7 | AMD EPYC 9645 | 2.20 | 457 | 10 |
| 8 | Intel Xeon 6970E+ | 1.95 | 543 | unpriced |
| 9 | AMD EPYC 9755 | 1.93 | 652 | 2 |
| 10 | AMD EPYC 9655 | 1.90 | 543 | 12 |
| 11 | AMD EPYC 8635P | 1.89 | 353 | 7 |
| 12 | AMD EPYC 9754 | 1.88 | 500 | 18 |
| 13 | Intel Xeon 6980P | 1.87 | 652 | 13 |
| 14 | AMD EPYC 9655P | 1.83 | 543 | 6 |
| 15 | AMD EPYC 8535P | 1.82 | 337 | 8 |

Top 15 of 123 screenable candidates. Screening needs only a published work rate and a power figure, so it covers more of the field than the value ranking does. Unpriced and in the efficiency top 15: Intel Xeon 6980E+, Intel Xeon 6990E+, Intel Xeon 6970E+.

**AMD EPYC 9845** is the efficiency champion at 2.68 pts/W and **AMD EPYC 9965** wins on value at 2.53 pts/W; the value ranking holds at every electricity price in the sensitivity table, so the efficiency answer only becomes the buying answer when watts, not dollars, are the binding constraint (a power-capped circuit, a thermal envelope, a UPS budget).

![Compute per watt vs Psi](../analysis/assets/compute_per_watt.png)

## Sensitivity: electricity

| $/kWh | 9965 | 9755 | 9845 | 9745 | 9825 | 9655P | Winner (all candidates) |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0.10 | 1.86 | 2.22 | 2.41 | 2.39 | 2.70 | 2.61 | AMD EPYC 9965 |
| 0.20 | 2.20 | 2.68 | 2.73 | 2.74 | 3.08 | 3.09 | AMD EPYC 9965 |
| 0.30 | 2.55 | 3.13 | 3.06 | 3.09 | 3.45 | 3.57 | AMD EPYC 9965 |
| 0.40 | 2.90 | 3.59 | 3.39 | 3.45 | 3.83 | 4.05 | AMD EPYC 9965 |
| 0.60 | 3.59 | 4.49 | 4.04 | 4.15 | 4.58 | 5.01 | AMD EPYC 9965 |

## Sensitivity: hold period

| Hold (yr) | 9965 | 9755 | 9845 | 9745 | 9825 | 9655P | Winner (all candidates) |
|---:|---:|---:|---:|---:|---:|---:|---|
| 3 | 5.73 | 6.81 | 7.59 | 7.48 | 8.50 | 8.06 | AMD EPYC 9965 |
| 5 | 3.72 | 4.45 | 4.82 | 4.77 | 5.40 | 5.22 | AMD EPYC 9965 |
| 7 | 2.85 | 3.44 | 3.63 | 3.61 | 4.07 | 4.00 | AMD EPYC 9965 |
| 10 | 2.20 | 2.68 | 2.73 | 2.74 | 3.08 | 3.09 | AMD EPYC 9965 |
| 12 | 1.95 | 2.38 | 2.39 | 2.40 | 2.69 | 2.73 | AMD EPYC 9965 |

Shorter holds punish capex and reward efficiency; the ranking holds while the absolute numbers roughly double at five years (handoff weakness 7: ten-year amortization is aggressive).

## Tie prices

| Contender | CPU price that ties the winner | Price carried | Basis | Gap |
|---|---:|---:|---|---:|
| AMD EPYC 9755 | $540 | $6,500 | street | $5,960 too expensive |
| AMD EPYC 9845 | $3,199 | $9,684 | street | $6,485 too expensive |
| AMD EPYC 9745 | $1,146 | $7,200 | street | $6,054 too expensive |
| AMD EPYC 9825 | $2,195 | $13,006 | list | $10,811 too expensive |
| AMD EPYC 9655P | none exists | $5,346 | street | free is not enough |
| AMD EPYC 8635P | none exists | $5,799 | list | free is not enough |
| AMD EPYC 8535P | none exists | $5,499 | list | free is not enough |
| AMD EPYC 8435P | none exists | $3,099 | list | free is not enough |
| AMD EPYC 9645 | none exists | $11,048 | list | free is not enough |
| AMD EPYC 9654P | none exists | $5,350 | street | free is not enough |
| AMD EPYC 9655 | none exists | $11,852 | list | free is not enough |
| Intel Xeon 6980P | none exists | $17,800 | list | free is not enough |
| Intel Xeon 6979P | none exists | $15,750 | list | free is not enough |
| Intel Xeon 6952P | none exists | $11,400 | list | free is not enough |
| Intel Xeon 6787P | none exists | $10,400 | list | free is not enough |

Top 15 contenders of 118, ordered by Psi. 114 of them cannot reach the winner's Psi even at a CPU price of zero: memory, platform and ten years of electricity already cost more per point than the winner's whole build. For those the price basis does not matter, which is why an incomplete price survey still supports a conclusion.

## The memory lever

| DDR5 $/GB | Memory cost (384GB) | Winner Psi | Winner |
|---:|---:|---:|---|
| $8.00 (pre-shortage) | $3,072 | 1.50 | AMD EPYC 9965 |
| $15.00 | $5,760 | 1.68 | AMD EPYC 9965 |
| $25.00 | $9,600 | 1.93 | AMD EPYC 9965 |
| $35.70 (current) | $13,709 | 2.20 | AMD EPYC 9965 |
| $45.00 | $17,280 | 2.44 | AMD EPYC 9965 |

Memory is the largest single number under your control, and waiting for DRAM normalization is worth more than any CPU decision in this repo. It is no longer identical across candidates: a six-channel socket takes six DIMMs, not twelve, so cheap DRAM helps the twelve-channel parts most. The winner column solves the whole field at each price rather than assuming the ranking holds.

## Own vs rent

| Option | SPECrate 1P | $/month | Psi ($/pt-yr) | vs owning |
|---|---:|---:|---:|---:|
| **Own: AMD EPYC 9965** | 1,510 | $277.42 (amortized) | 2.20 | 1.0x |
| Hetzner AX162-1 | 523 | $722.10 | 16.57 | 7.5x |
| Hetzner AX162-1-LTD | 523 | $372.10 | 8.54 | 3.9x |

Matching the owned node takes 2.9 rented boxes, $25,014 per year: one year of equivalent rental costs most of a decade of owning ($33,290 all-in).

| Hetzner cloud instance | Old EUR/mo | New EUR/mo | Increase |
|---|---:|---:|---:|
| CCX63 | 374.49 | 853.49 | +128% |
| CPX41 | 38.99 | 120.49 | +209% |
| CPX51 | 77.99 | 237.99 | +205% |

Cloud repricing of 2026-06-15 ran +128% to +209%, computed from the raw prices (the handoff's stated 128-205% range slightly understated the top end). Renting still buys hardware replacement, redundant power, someone on call at 3am, the option to stop paying, and no DRAM-market exposure; the model does not price those, and says so.

## Reconciliation with the handoff

| Quantity | Handoff F7 | Same RAM price, handoff's work rate | Same RAM price, measured work rate | Current RAM price |
|---|---:|---:|---:|---:|
| DDR5 $/GB | implied $16.06 | $16.06 | $16.06 | $35.70 |
| Work rate (1P pts) | 1,634 | 1,634 | 1,510 | 1,510 |
| 10-yr Psi per point | $15.85 | $15.76 | $17.06 | $22.05 |
| Psi ($/pt-yr) | 1.58 | 1.58 | 1.71 | 2.20 |

The handoff's F7 figures back-solve to DDR5 near $16.06/GB, against the $35.70/GB its own data table carries (2026-08-14). Hold both its RAM price and its work rate, and this repo reproduces the reported number within 0.6%, which is rounding drift inside the handoff itself. The two columns after that are the two things that actually changed, in order: the 2026-08-31 survey replaced the scaled 2P work rate with the part's own published 1P median (1,634 points to 1,510), and DRAM went up. The published Psi is whatever the current data solves to; the old figure is kept in data/cpu_specs.yaml as SUPERSEDED.

## How wide was the search

| Candidate set | In catalog | Fully placeable | Last surveyed | Status |
|---|---:|---|---|---|
| CPU candidates for the compute node | 124 | 119 priced, 123 screenable | 2026-08-31 | current |
| hosted models for the token tiers | 97 | see report | 2026-08-31 | current |
| local machines for on-box inference | 37 | see report | 2026-08-31 | current |
| the capability axis itself | 49 | 32 costed | 2026-08-31 | current |

Every candidate set has been surveyed inside its interval.

## How much to trust this today

| Category | Figures | Oldest | Window | Status |
|---|---:|---|---|---|
| benchmarks | 1 | 2026-08-31 | 60d | fresh |
| dram | 1 | 2026-08-14 | 14d | **1 flagged** |
| hardware_pricing | 45 | 2026-06-15 | 30d | **2 flagged** |
| model_pricing | 98 | 2026-08-29 | 30d | fresh |

SPECrate submissions never expire and are not policed.
