# F7: Hardware selection for deterministic compute (Psi)

A separate question from inference, kept in the same repo because the method is shared:
when the workload is deterministic compute (builds, simulation, batch jobs) rather than
token generation, what does a unit of sustained throughput cost, all in?

```text
W      = R_2P * sigma * phi      work rate (2P SPECrate scaled to 1P, derated for cTDP)
P_wall = (P_cpu + P_plat) / eta
Psi    = TCO / (W * U * Y)       dollars per SPECrate-point-year; lower wins
```

Dollars per watt picks small slow parts. Perf per watt ignores capex. Dollars per core is
meaningless across architectures. PassMark saturates past roughly 100 cores. Psi answers
the actual question, which is why the workbook ranks on it.

The two softest inputs are labeled everywhere they appear: sigma (1P scaling, DERIVED
from the one CPU with both 1P and 2P published, and it cancels out of the ranking) and
the 9965's phi at 450W (ESTIMATE; nobody has published 450 vs 500 on that part).

<!-- gen:psi_compare -->
| CPU | Cores | Run cTDP | phi | W (1P pts) | Wall W | TCO | Psi ($/pt-yr) | pts/W | Energy share | Rank |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| **AMD EPYC 9965** | 192 | 450W | 0.99 (ESTIMATE) | 1,634 | 598 | $33,290 | 2.04 | 2.73 | 31% | 1 |
| AMD EPYC 9845 | 160 | 320W | 0.98 (DERIVED) | 1,350 | 457 | $33,497 | 2.48 | 2.96 | 24% | 3 |
| AMD EPYC 9755 | 128 | 500W | 1 (DEFINITION) | 1,361 | 652 | $33,743 | 2.48 | 2.09 | 34% | 2 |
| AMD EPYC 9745 | 128 | 320W | 0.98 (MEASURED) | 1,200 | 457 | $31,013 | 2.58 | 2.63 | 26% | 4 |

Winner: **AMD EPYC 9965** at $2.04 per SPECrate-point-year over 10 years ($22,809 capex). Best perf/watt is **AMD EPYC 9845** at 2.96 pts/W: efficiency and value rank differently, which is the point of solving for Psi instead.
<!-- /gen:psi_compare -->

The interactive companion is `spreadsheets/compute-node-model.xlsx`; a parity test keeps
this pipeline and that workbook agreeing cell for cell.

## Compute per watt, as its own question

Perf/watt is not a tie-breaker column inside the value question; it is the answer to a
different question. Value (Psi) answers "what does a unit of work cost me"; efficiency
(points per wall watt) answers "what fits under a watt budget". They rank the candidates
differently, so they get their own chart.

![Compute per watt vs Psi](assets/compute_per_watt.png)

<!-- gen:compute_per_watt -->
| CPU | pts per wall watt | Efficiency rank | Psi rank |
|---|---:|---:|---:|
| AMD EPYC 9845 | 2.96 | 1 | 3 |
| AMD EPYC 9965 | 2.73 | 2 | 1 |
| AMD EPYC 9745 | 2.63 | 3 | 4 |
| AMD EPYC 9755 | 2.09 | 4 | 2 |

**AMD EPYC 9845** is the efficiency champion at 2.96 pts/W and **AMD EPYC 9965** wins on value at 2.73 pts/W; the value ranking holds at every electricity price in the sensitivity table, so the efficiency answer only becomes the buying answer when watts, not dollars, are the binding constraint (a power-capped circuit, a thermal envelope, a UPS budget).
<!-- /gen:compute_per_watt -->

The 9965-vs-9845 efficiency comparison sits inside the error bar of the 450W derate
estimate (README weakness 2); a measured 450-vs-500 run on the 9965 would firm up both
ends of this chart and is on the open-questions list.

## Sensitivity

Electricity price:

<!-- gen:psi_sens_electricity -->
| $/kWh | 9965 | 9845 | 9755 | 9745 | Winner |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.72 | 2.19 | 2.06 | 2.25 | 9965 |
| 0.20 | 2.04 | 2.48 | 2.48 | 2.58 | 9965 |
| 0.30 | 2.36 | 2.78 | 2.90 | 2.92 | 9965 |
| 0.40 | 2.68 | 3.08 | 3.32 | 3.25 | 9965 |
| 0.60 | 3.32 | 3.67 | 4.16 | 3.92 | 9965 |
<!-- /gen:psi_sens_electricity -->

Hold period:

<!-- gen:psi_sens_hold -->
| Hold (yr) | 9965 | 9845 | 9755 | 9745 | Winner |
|---:|---:|---:|---:|---:|---:|
| 3 | 5.29 | 6.89 | 6.30 | 7.06 | 9965 |
| 5 | 3.43 | 4.37 | 4.12 | 4.50 | 9965 |
| 7 | 2.64 | 3.29 | 3.18 | 3.41 | 9965 |
| 10 | 2.04 | 2.48 | 2.48 | 2.58 | 9965 |
| 12 | 1.80 | 2.17 | 2.21 | 2.26 | 9965 |

Shorter holds punish capex and reward efficiency; the ranking holds while the absolute numbers roughly double at five years (handoff weakness 7: ten-year amortization is aggressive).
<!-- /gen:psi_sens_hold -->

What each contender's CPU would have to cost to tie the winner:

<!-- gen:breakevens -->
| Contender | CPU price that ties the winner | Street price | Gap |
|---|---:|---:|---:|
| AMD EPYC 9845 | $3,684 | $9,684 | $6,000 too expensive |
| AMD EPYC 9755 | $483 | $6,500 | $6,017 too expensive |
| AMD EPYC 9745 | $640 | $7,200 | $6,560 too expensive |
<!-- /gen:breakevens -->

The perf/watt champion loses on Psi because its price never collapsed the way the
winner's did; the tie prices quantify exactly how far out of the money each part is.

## The real lever is memory

<!-- gen:memory_lever -->
| DDR5 $/GB | Memory cost (384GB) | Winner Psi |
|---:|---:|---:|
| $8.00 (pre-shortage) | $3,072 | 1.39 |
| $15.00 | $5,760 | 1.55 |
| $25.00 | $9,600 | 1.79 |
| $35.70 (current) | $13,709 | 2.04 |
| $45.00 | $17,280 | 2.26 |

Memory is identical across candidates, so it never changes the ranking. It is also the largest single number under your control; waiting for DRAM normalization is worth more than any CPU decision in this repo.
<!-- /gen:memory_lever -->

## Own vs rent, same unit

<!-- gen:rent_compare -->
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
<!-- /gen:rent_compare -->

## Reconciliation with the handoff's F7 numbers

The research handoff reported a headline Psi that this repo does not reproduce at current
data, and the difference is exactly one input:

<!-- gen:handoff_reconciliation -->
| Quantity | Handoff F7 | This repo, same RAM price | This repo, current RAM price |
|---|---:|---:|---:|
| DDR5 $/GB | implied $16.06 | $16.06 | $35.70 |
| 10-yr Psi per point | $15.85 | $15.76 | $20.37 |
| Psi ($/pt-yr) | 1.58 | 1.58 | 2.04 |

The handoff's F7 figures back-solve to DDR5 near $16.06/GB, against the $35.70/GB its own data table carries (2026-08-14). At the implied price this repo reproduces the reported number within 0.6% (the residual is rounding drift inside the handoff itself). The published Psi is whatever the current data solves to; the old figure is kept in data/cpu_specs.yaml as SUPERSEDED.
<!-- /gen:handoff_reconciliation -->
