# F2: There is no midrange tier — REVERSED 2026-08-31

**This finding was wrong, and how it was wrong is the most useful thing in this repo.**

The original claim: plot capability against cost per task and the Pareto frontier is a
cliff, not a slope. A cheap near-frontier tier, a small expensive frontier tier, and
nothing rational in between. The architectural conclusion was that a two-tier routing
policy falls out of the data, because there is nothing to route a "medium" call to.

That claim rested on **two costed models**. Everything else on the index carried a score
but no cost per task, so it could not be placed. A frontier drawn through two points is a
line segment by construction; calling it a cliff described the sample, not the market.

The first real survey of the model catalog (2026-08-31) costed 32 models.

<!-- gen:frontier_table -->
| Model | AA score | $/task | vs llama-4-scout | Pareto |
|---|---:|---:|---:|---|
| llama-4-scout | 10 | $0.010 | 1.0x | on frontier |
| gpt-oss-20b | 15 | $0.020 | 2.0x | on frontier |
| llama-4-maverick | 14 | $0.030 | 3.0x | dominated |
| gpt-5.6-luna | 52 | $0.050 | 5.0x | on frontier |
| gpt-oss-120b | 24 | $0.070 | 7.0x | dominated |
| mistral-large-3 | 16 | $0.080 | 8.0x | dominated |
| glm-5.3-flash | 57 | $0.090 | 9.0x | on frontier |
| gemini-3.5-flash-lite | 37 | $0.100 | 10.0x | dominated |
| mistral-small-4 | 20 | $0.100 | 10.0x | dominated |
| deepseek-v4-flash | 52 | $0.110 | 11.0x | dominated |
| ministral-3b | 7 | $0.130 | 13.0x | dominated |
| ministral-8b | 9 | $0.180 | 18.0x | dominated |
| kimi-k2.7-code | 43 | $0.220 | 22.0x | dominated |
| claude-haiku-4-5 | 30 | $0.220 | 22.0x | dominated |
| deepseek-v4-pro | 53 | $0.270 | 27.0x | dominated |
| gemini-3.1-pro-preview | 48 | $0.330 | 33.0x | dominated |
| gemini-3.6-flash | 52 | $0.340 | 34.0x | dominated |
| qwen3.5-397b-a17b | 34 | $0.360 | 36.0x | dominated |
| muse-spark-1.2 | 57 | $0.400 | 40.0x | dominated |
| gemini-3.7-flash | 56 | $0.400 | 40.0x | dominated |
| mistral-medium-3.5 | 30 | $0.410 | 41.0x | dominated |
| grok-4.5 | 56 | $0.430 | 43.0x | dominated |
| glm-5.2 | 53 | $0.440 | 44.0x | dominated |
| glm-5.3 | 60 | $0.680 | 68.0x | on frontier |
| qwen3.8-2.4t-a95b | 58 | $0.810 | 81.0x | dominated |
| kimi-k3 | 60 | $0.840 | 84.0x | dominated |
| qwen3.8-max | 58 | $0.910 | 91.0x | dominated |
| grok-4.6 | 61 | $0.940 | 94.0x | on frontier |
| gpt-5.6-sol | 61 | $0.950 | 95.0x | dominated |
| claude-sonnet-5 | 55 | $1.720 | 172.0x | dominated |
| claude-opus-5 | 63 | $2.340 | 234.0x | on frontier |
| claude-fable-5 | 62 | $3.140 | 314.0x | dominated |
| claude-opus-4-8 | 57.0 | TODO: unverified | | not placeable yet |
| gpt-5.5 | 56.0 | TODO: unverified | | not placeable yet |
| gpt-5.4 | 53.0 | TODO: unverified | | not placeable yet |
| gpt-5.3-codex | 46.0 | TODO: unverified | | not placeable yet |
| gpt-5.2 | 43.0 | TODO: unverified | | not placeable yet |
| gemini-3-flash-preview | 41.0 | TODO: unverified | | not placeable yet |
| gpt-5.1 | 38.0 | TODO: unverified | | not placeable yet |
| claude-sonnet-4-6 | 37.0 | TODO: unverified | | not placeable yet |
| gpt-5 | 35.0 | TODO: unverified | | not placeable yet |
| o3-pro | 33.0 | TODO: unverified | | not placeable yet |
| o3 | 31.0 | TODO: unverified | | not placeable yet |
| gpt-5-mini | 26.0 | TODO: unverified | | not placeable yet |
| qwen3-max | 24.0 | TODO: unverified | | not placeable yet |
| gpt-5-nano | 20.0 | TODO: unverified | | not placeable yet |
| kimi-k2 | 20.0 | TODO: unverified | | not placeable yet |
| llama-3.3-70b | 9.0 | TODO: unverified | | not placeable yet |
| llama-3.1-405b | 8.0 | TODO: unverified | | not placeable yet |

Baseline is llama-4-scout, the cheapest costed entry, solved rather than named. 7 of 32 costed models are Pareto-optimal: llama-4-scout (AA 10, $0.01), gpt-oss-20b (AA 15, $0.02), gpt-5.6-luna (AA 52, $0.05), glm-5.3-flash (AA 57, $0.09), glm-5.3 (AA 60, $0.68), grok-4.6 (AA 61, $0.94), claude-opus-5 (AA 63, $2.34).

Read as steps up the curve: 5 pts for 2.0x; then 37 pts for 2.5x; then 5 pts for 1.8x; then 3 pts for 7.6x; then 1 pts for 1.4x; then 2 pts for 2.5x. Capability is bought in increments here, not in one jump, which is what a curve means and a cliff does not.
<!-- /gen:frontier_table -->

![Capability vs cost Pareto frontier](assets/pareto_frontier.png)

## What the curve actually says

Capability is bought in increments, not in one jump. There is a real cheap tier below the
old volume pick, a real step above it, and further steps after that. A router with more
than two rungs now has somewhere to send a medium call.

Two things the two-point view hid:

- A model scoring a few points below the volume tier exists at roughly half its cost per
  task. Where the capability floor is genuinely lower, a two-tier policy leaves that on
  the table.
- Between the volume tier and the top of the index there are intermediate frontier points,
  not a void. The gap the original finding described was the gap between the only two
  models anyone had costed.

## What survives

The shape of the original advice mostly holds even though the finding is falsified. The
cheapest capable model is still dramatically cheaper than the frontier, and the frontier
tier is still priced for rare calls rather than a loop: pricing the reference workload
against the frontier models runs into five and six figures, against low four figures for
the volume tier. What does not survive is "there is nothing in between", and any
architecture justified by that sentence should be revisited.

## The methodological lesson

The finding was falsifiable, was tested against a wider candidate set, and failed. That is
the system working. But it was published as a structural claim about the market when it
was a claim about seven data points, two of them costed. Every ranking in this repo now
carries a coverage figure for exactly this reason: a frontier drawn from a hand-picked
subset is an artifact of the picking, and nothing in the plot itself tells you which one
you are looking at.

## What would falsify the reversal

A re-pull showing the intermediate points were mispriced and the gap is real after all.
These costs come from one leaderboard's published cost-per-task column read on one date;
a second independent costing would strengthen or break it. Index parity is also not task
parity: models a few points apart on the index may be far apart on a specific job, so the
curve prices capability, it does not substitute for evaluating two candidates on the
actual work.
