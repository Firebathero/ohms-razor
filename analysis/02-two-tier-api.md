# F2: There is no midrange tier

Plot capability against cost per task and the Pareto frontier is a cliff, not a slope: a
cheap near-frontier tier, a small expensive frontier tier, and nothing rational in
between. Every midrange model observed so far scores at or below the volume tier's best
while costing a multiple of it.

The consequence is architectural. A two-tier routing policy (volume tier by default,
frontier tier for the calls that provably need it) is not a simplification imposed on the
data; it falls out of the data. There is currently nothing to route a "medium" call to.

![Capability vs cost Pareto frontier](assets/pareto_frontier.png)

<!-- gen:frontier_table -->
| Model | AA score | $/task | vs glm-5.3-flash | Pareto |
|---|---:|---:|---:|---|
| glm-5.3-flash | 57 | $0.045 | 1.0x | on frontier |
| grok-4.6 | 60 | $0.620 | 13.8x | on frontier |
| deepseek-v4-flash | 52 | TODO: unverified | | not placeable yet |
| kimi-k3 | 60 | TODO: unverified | | not placeable yet |
| glm-5.3-max | 60 | TODO: unverified | | not placeable yet |
| claude-opus-5 | 63 | TODO: unverified | | not placeable yet |
| gpt-oss-120b | 24 | TODO: unverified | | not placeable yet |

Midrange models the handoff places at 2x to 14x glm-5.3-flash per task while scoring at or below it (individual figures pending re-pull): gpt-5.6-luna, deepseek-v4-pro, glm-5.2, qwen3.8-27b, gemini-3.7-flash, grok-4.5, muse-spark.
<!-- /gen:frontier_table -->

At the top of the index, capability parity does not mean price parity: several models tie
on score while spreading widely on cost, so within the frontier tier the selection
criterion is price and task fit, not the index. And index parity is not task parity
(handoff weakness 6): two models tied at 60 are not interchangeable on a specific job.

## Honest gaps

Most index entries above are missing a cost per task (`TODO: unverified` in
`data/benchmarks.yaml`). The cliff claim rests on the handoff's reading of the full index
plus the two fully costed endpoints; filling in the missing costs is the fastest way for a
contributor to strengthen or break this finding.

## What would falsify this

A genuine midrange point: capability meaningfully above the volume tier at a fraction of
frontier cost. New model launches are the watch item. If it appears, the conclusion test
fails, the frontier re-solves, and the reversal goes in the changelog. That outcome would
be a more useful publication than the original finding.
