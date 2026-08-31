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
| llama-3.1-8b-deepinfra (list) | $252 | n/a | 2026-08-31 | VOLATILE |
| gpt-oss-20b-deepinfra (list) | $630 | n/a | 2026-08-31 | VOLATILE |
| gpt-oss-120b-cloud (list) | $724 | 24 | 2026-08-29 | VOLATILE |
| deepseek-v4-flash-deepinfra (list) | $760 | n/a | 2026-08-31 | VOLATILE |
| muse-spark-1.2-contributor (list) | $766 | n/a | 2026-08-31 | CONFIRMED |
| gpt-oss-120b-deepinfra (list) | $769 | n/a | 2026-08-31 | VOLATILE |
| ministral-3b (list) | $945 | 7.0 | 2026-08-31 | CONFIRMED |
| glm-5.3-flash (promo) | $958 | 57 | 2026-08-29 | EXPIRES, ends 2026-09-09 |
| deepseek-v4-flash-together (list) | $1,210 | n/a | 2026-08-31 | VOLATILE |
| gpt-5-nano (list) | $1,348 | 20.0 | 2026-08-31 | CONFIRMED |
| ministral-8b (list) | $1,418 | 9.0 | 2026-08-31 | CONFIRMED |
| gpt-oss-20b-groq (list) | $1,418 | n/a | 2026-08-31 | VOLATILE |
| gemini-2.5-flash-lite (list) | $1,436 | n/a | 2026-08-31 | CONFIRMED |
| gpt-4.1-nano (list) | $1,512 | n/a | 2026-08-31 | CONFIRMED |
| llama-4-scout-deepinfra (list) | $1,575 | n/a | 2026-08-31 | VOLATILE |
| llama-3.3-70b-deepinfra (list) | $1,638 | n/a | 2026-08-31 | VOLATILE |
| glm-4.7-flashx (list) | $1,701 | n/a | 2026-08-31 | CONFIRMED |
| ministral-14b (list) | $1,890 | n/a | 2026-08-31 | CONFIRMED |
| glm-5.3-flash (list) | $1,915 | 57 | 2026-08-29 | VOLATILE |
| gpt-oss-120b-fireworks (list) | $2,155 | n/a | 2026-08-31 | VOLATILE |
| qwen3-235b-a22b-deepinfra (list) | $2,300 | n/a | 2026-08-31 | VOLATILE |
| deepseek-v4-flash (off-peak only) | $2,391 | 52 | 2026-08-29 | VOLATILE |
| qwen3.8-flash (list) | $2,426 | n/a | 2026-08-31 | CONFIRMED |
| gpt-4o-mini (list) | $2,457 | n/a | 2026-08-31 | CONFIRMED |
| mistral-small-4 (list) | $2,835 | 20.0 | 2026-08-31 | CONFIRMED |
| gpt-oss-120b-together (list) | $2,835 | n/a | 2026-08-31 | VOLATILE |
| gpt-oss-120b-groq (list) | $2,835 | n/a | 2026-08-31 | VOLATILE |
| deepseek-v4-flash (24/7, 21% peak) | $2,890 | 52 | 2026-08-29 | VOLATILE |
| llama-4-maverick-deepinfra (list) | $3,780 | n/a | 2026-08-31 | VOLATILE |
| glm-4.5-air (list) | $3,868 | n/a | 2026-08-31 | CONFIRMED |
| qwen3-coder-480b-deepinfra (list) | $4,032 | n/a | 2026-08-31 | VOLATILE |
| gpt-5.6-luna (list) | $4,133 | 52.0 | 2026-08-31 | CONFIRMED |
| gpt-5.4-nano (list) | $4,290 | n/a | 2026-08-31 | CONFIRMED |
| codestral (list) | $4,725 | n/a | 2026-08-31 | CONFIRMED |
| gemini-3.1-flash-lite (list) | $5,166 | n/a | 2026-08-31 | CONFIRMED |
| gpt-4.1-mini (list) | $6,048 | n/a | 2026-08-31 | CONFIRMED |
| gpt-5-mini (list) | $6,741 | 26.0 | 2026-08-31 | CONFIRMED |
| deepseek-v4-pro (off-peak only) | $7,179 | 53.0 | 2026-08-31 | CONFIRMED |
| mistral-large-3 (list) | $7,875 | 16.0 | 2026-08-31 | CONFIRMED |
| glm-4.7 (list) | $8,240 | n/a | 2026-08-31 | CONFIRMED |
| glm-4.6 (list) | $8,240 | n/a | 2026-08-31 | CONFIRMED |
| glm-4.5 (list) | $8,240 | n/a | 2026-08-31 | CONFIRMED |
| gemini-2.5-flash (list) | $8,404 | n/a | 2026-08-31 | CONFIRMED |
| gemini-3.5-flash-lite (list) | $8,404 | 37.0 | 2026-08-31 | CONFIRMED |
| grok-build-0.1 (list) | $8,568 | n/a | 2026-08-31 | CONFIRMED |
| deepseek-v4-pro (24/7, 21% peak) | $8,675 | 53.0 | 2026-08-31 | CONFIRMED |
| deepseek-r1-0528-deepinfra (list) | $9,166 | n/a | 2026-08-31 | VOLATILE |
| gemini-3-flash-preview (list) | $10,332 | 41.0 | 2026-08-31 | CONFIRMED |
| deepseek-v4-pro-deepinfra (list) | $10,332 | n/a | 2026-08-31 | VOLATILE |
| grok-4.3 (list) | $10,458 | n/a | 2026-08-31 | CONFIRMED |
| glm-5 (list) | $12,348 | n/a | 2026-08-31 | CONFIRMED |
| qwen3.6-plus (list) | $12,600 | n/a | 2026-08-31 | CONFIRMED |
| qwq-plus (list) | $12,600 | n/a | 2026-08-31 | CONFIRMED |
| gemini-3.7-flash (list) | $13,136 | 56.0 | 2026-08-31 | EXPIRES |
| gemini-3.6-flash (list) | $13,136 | 52.0 | 2026-08-31 | EXPIRES |
| qwen3.6-27b-groq (list) | $13,230 | n/a | 2026-08-31 | VOLATILE |
| kimi-k2.6 (list) | $14,603 | n/a | 2026-08-31 | CONFIRMED |
| kimi-k2.7-code (list) | $14,755 | 43.0 | 2026-08-31 | CONFIRMED |
| qwen3.5-397b-a17b (list) | $15,120 | 34.0 | 2026-08-31 | CONFIRMED |
| gpt-5.4-mini (list) | $15,498 | n/a | 2026-08-31 | CONFIRMED |
| muse-spark-1.2 (list) | $15,718 | 57.0 | 2026-08-31 | CONFIRMED |
| o4-mini (list) | $16,632 | n/a | 2026-08-31 | CONFIRMED |
| glm-5.3 (list) | $16,934 | 60.0 | 2026-08-31 | CONFIRMED |
| glm-5.2 (list) | $16,934 | 53.0 | 2026-08-31 | CONFIRMED |
| claude-haiku-4-5 (list) | $17,514 | 30.0 | 2026-08-31 | CONFIRMED |
| qwen3.8-27b-groq (list) | $17,640 | n/a | 2026-08-31 | VOLATILE |
| glm-5.1 (list) | $22,680 | n/a | 2026-08-31 | CONFIRMED |
| grok-4.5 (list) | $22,932 | 56.0 | 2026-08-31 | CONFIRMED |
| grok-4.6 (list) | $23,940 | 61 | 2026-08-31 | CONFIRMED |
| gpt-4.1 (list) | $30,240 | n/a | 2026-08-31 | CONFIRMED |
| o3 (list) | $30,240 | 31.0 | 2026-08-31 | CONFIRMED |
| qwen-max (list) | $30,240 | n/a | 2026-08-31 | CONFIRMED |
| gemini-3.5-flash (list) | $30,996 | n/a | 2026-08-31 | CONFIRMED |
| qwen3.8-max (list) | $31,500 | 58.0 | 2026-08-31 | CONFIRMED |
| qwen3.8-2.4t-a95b (list) | $31,500 | 58.0 | 2026-08-31 | CONFIRMED |
| mistral-medium-3.5 (list) | $33,075 | 30.0 | 2026-08-31 | CONFIRMED |
| gpt-5.1 (list) | $33,705 | 38.0 | 2026-08-31 | CONFIRMED |
| gpt-5 (list) | $33,705 | 35.0 | 2026-08-31 | CONFIRMED |
| gemini-2.5-pro (list) | $33,705 | n/a | 2026-08-31 | CONFIRMED |
| claude-sonnet-5 (list) | $35,028 | 55.0 | 2026-08-31 | CONFIRMED |
| qwen3.7-max (list) | $39,375 | n/a | 2026-08-31 | VOLATILE |
| gpt-4o (list) | $40,950 | n/a | 2026-08-31 | CONFIRMED |
| gpt-5.6-terra (list) | $41,328 | n/a | 2026-08-31 | CONFIRMED |
| gemini-3.1-pro-preview (list) | $41,328 | 48.0 | 2026-08-31 | CONFIRMED |
| gpt-5.3-codex (list) | $47,187 | 46.0 | 2026-08-31 | CONFIRMED |
| gpt-5.2 (list) | $47,187 | 43.0 | 2026-08-31 | CONFIRMED |
| gpt-5.4 (list) | $51,660 | 53.0 | 2026-08-31 | CONFIRMED |
| kimi-k3 (list) | $52,542 | 60 | 2026-08-29 | VOLATILE |
| claude-sonnet-4-6 (list) | $52,542 | 37.0 | 2026-08-31 | CONFIRMED |
| gpt-5.6-sol (list) | $70,056 | 61.0 | 2026-08-31 | CONFIRMED |
| claude-opus-5 (list) | $87,570 | 63 | 2026-08-31 | CONFIRMED |
| claude-opus-4-8 (list) | $87,570 | 57.0 | 2026-08-31 | CONFIRMED |
| claude-opus-4-7 (list) | $87,570 | n/a | 2026-08-31 | CONFIRMED |
| claude-opus-4-6 (list) | $87,570 | n/a | 2026-08-31 | CONFIRMED |
| claude-opus-4-5 (list) | $87,570 | n/a | 2026-08-31 | CONFIRMED |
| gpt-5.5 (list) | $103,320 | 56.0 | 2026-08-31 | CONFIRMED |
| claude-fable-5 (list) | $175,140 | 62.0 | 2026-08-31 | CONFIRMED |
| o3-pro (list) | $378,000 | 33.0 | 2026-08-31 | CONFIRMED |
| gpt-5-pro (list) | $472,500 | n/a | 2026-08-31 | CONFIRMED |
| gpt-5.5-pro (list) | $756,000 | n/a | 2026-08-31 | CONFIRMED |

Scores: AA Intelligence Index v4.1.1 (2026-08-31). Index parity is not task parity.
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
