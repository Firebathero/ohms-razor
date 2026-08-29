# ohms-razor

**Never use more model than the task needs.**

<!-- gen:last_solved -->
**Last solved:** 2026-08-29. **3 figure(s) past their freshness window** (run `python scripts/check_staleness.py`).
<!-- /gen:last_solved -->

An always-on local box is where an agent lives; it is not where thinking happens. Hosting
and inference are different workloads with different economics, and conflating them is how
people buy the wrong hardware. This repo prices the placement decision (local box, cheap
volume API tier, frontier API tier) from first principles and publishes the working.

There are no static numbers here. Every figure in every table is solved from `data/` at
build time, every input carries a pull date and a confidence tag, and the conclusions are
enforced by tests that recompute them from live data. When the data moves and a conclusion
flips, the tests fail, the tables re-solve, and the reversal gets published in the
changelog below. That event is the point of the repo, not a failure of it.

## The constraint that does the most work

One line of arithmetic disqualifies most local hardware before cost is even considered.
All comparisons use one fixed reference workload (`data/workload.yaml`) so nothing can
hide in assumptions:

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

A box that cannot sustain that rate cannot produce the workload at any duty cycle.

## The two questions, answered

The modern placement decision is really two questions: what do I use for compute
(deterministic work), and what do I use for tokens for a given task. This is the repo's
current answer, solved from `data/` on every build (`python scripts/answer.py` prints the
same thing in the terminal):

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

## Known weaknesses, first

These are the strongest available rebuttals, stated before the findings they weaken:

1. **Batching favors the cloud case less than the tables imply.** The local figures assume
   batch size 1 against batched providers. `analysis/04-moe-asymmetry.md` models the
   amortization first-order instead of hiding it; measured curves are the top open question.
2. **The 9965's 450W derate (phi = 0.99) is an extrapolation**, not a measurement, and the
   9965-vs-9845 perf/watt comparison sits inside its error bar.
3. **1P SPECrate figures are scaled from 2P** by a factor calibrated on the one CPU with
   both published. It cancels out of rankings; absolute levels inherit its error.
4. **The 9845 has one SPECrate submission.** Thinnest evidence in the set.
5. **The Mac Studio M5 Ultra price is a guess** and is tagged ESTIMATE where it appears.
6. **Index parity is not task parity.** Models tied on the AA index are not interchangeable
   on a specific job.
7. **Ten-year amortization is aggressive.** Five years is the realistic economic life; the
   hold-period sensitivity table shows the numbers roughly doubling there.
8. **The supply-vs-demand finding has a live counter-reading**, presented alongside it in
   `analysis/06-supply-vs-demand.md`.

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

The tokens question, plotted (F2):

![Capability vs cost Pareto frontier](analysis/assets/pareto_frontier.png)

The compute question, plotted (F7): efficiency and value are different answers, which is
why perf/watt gets its own chart instead of a column.

![Compute per watt vs Psi](analysis/assets/compute_per_watt.png)

Each finding has a full write-up in `analysis/`, prose around solved tables: mechanism,
numbers, and what would falsify it.

## How to reproduce

```bash
git clone https://github.com/Firebathero/ohms-razor
cd ohms-razor
pip install -r requirements.txt

python scripts/answer.py              # the two questions, answered from current data
cat REPORT.md                         # the one-page report (regenerated by build_tables.py)
pytest                                # formula checks, workbook parity, live conclusions
python scripts/check_staleness.py     # what needs a re-pull before you trust it
python scripts/build_tables.py        # re-solve every table in README + analysis from data/
python scripts/build_tables.py --check  # verify the committed docs match the data layer
python scripts/plot_frontier.py       # regenerate the Pareto plot
python scripts/plot_watts.py          # regenerate the compute-per-watt plot
```

The maintenance loop (monthly or on demand) is in `CONTRIBUTING.md`: re-pull stale
figures, keep old values in `history`, re-solve, and let the conclusion tests tell you if
anything flipped.

## Data freshness

<!-- gen:freshness -->
| Category | Figures | Oldest | Window | Status |
|---|---:|---|---|---|
| benchmarks | 1 | 2026-08-26 | 60d | fresh |
| dram | 1 | 2026-08-14 | 14d | **1 flagged** |
| hardware_pricing | 10 | 2026-06-15 | 30d | **2 flagged** |
| model_pricing | 5 | 2026-08-29 | 30d | fresh |

SPECrate submissions never expire and are not policed.
<!-- /gen:freshness -->

## Repo map

```text
REPORT.md      the output: answer, findings, freshness on one solved page
data/          every figure: value, unit, date, source, confidence (the only ground truth)
models/        models 1-5 as pure functions, no I/O
scripts/       the solver, table generator, staleness gate, plot
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

## License

MIT. See `LICENSE`.
