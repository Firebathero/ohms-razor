# F1: Renting beats self-hosting for the reference workload

Model 1 prices the reference workload (see the README derivation) against every API path
in `data/model_pricing.yaml`:

```text
C_api       = O * p_out + I * (1 - h) * p_in + I * h * p_cache
C_effective = C_api * (1 + f_peak * (m_peak - 1))
```

Peak exposure matters for a 24/7 agent loop because it cannot schedule around a vendor's
peak windows without giving up the always-on property. DeepSeek's windows cover 7 of 24
hours at 2x, so an unscheduled loop pays the blended rate.

<!-- gen:api_cost_10yr -->
| Path | 10-yr cost | AA score | Priced | Confidence |
|---|---:|---:|---|---|
| gpt-oss-120b-cloud (list) | $724 | 24 | 2026-08-29 | VOLATILE |
| glm-5.3-flash (promo) | $958 | 57 | 2026-08-29 | EXPIRES, ends 2026-09-09 |
| glm-5.3-flash (list) | $1,915 | 57 | 2026-08-29 | VOLATILE |
| deepseek-v4-flash (off-peak only) | $2,391 | 52 | 2026-08-29 | VOLATILE |
| deepseek-v4-flash (24/7, 29% peak) | $3,089 | 52 | 2026-08-29 | VOLATILE |
| kimi-k3 (list) | $52,542 | 60 | 2026-08-29 | VOLATILE |

Scores: AA Intelligence Index v4.1.1 (2026-08-26). Index parity is not task parity.
<!-- /gen:api_cost_10yr -->

The cheapest capable path wins on cost and capability at the same time, and it wins at
full list price. That is what makes the conclusion robust to the promo expiring: the
discount is a bonus, not the argument.

## The cache objection

The obvious rebuttal is the cache-rate gap: DeepSeek's cached input is roughly 4x cheaper
per token than GLM's. The sweep below re-prices the whole workload at cache hit rates from
0 to 100 percent.

<!-- gen:cache_sensitivity -->
| Cache hit rate | glm-5.3-flash | deepseek-v4-flash | gap |
|---:|---:|---:|---:|
| 0% | $2,520 | $3,465 | $945 |
| 25% | $2,331 | $3,130 | $799 |
| 50% | $2,142 | $2,794 | $652 |
| 75% | $1,953 | $2,459 | $506 |
| 80% | $1,915 | $2,391 | $476 |
| 100% | $1,764 | $2,123 | $359 |

deepseek-v4-flash has the cheapest cache rate on offer at $0.007/M against glm-5.3-flash's $0.030/M, 4.3x better. On this volume that is worth at most $145 even if every input token were cached, against a $504 output-price gap. The ranking cannot flip on cache behavior.
<!-- /gen:cache_sensitivity -->

## What would falsify this

- A capable model (index within a few points of the frontier) landing below the current
  winner's cost per task. The conclusion tests would fail on the next data refresh.
- A pricing change: DeepSeek moved output pricing 371 percent in one week (2026-08-16),
  so treat every figure here as VOLATILE and re-solve before quoting.
- The frontier tier is a different question: nothing in this file argues Kimi K3 or its
  peers into or out of a workflow that needs top-of-index capability rarely. The two-tier
  argument is in `02-two-tier-api.md`.
