# Token economics: latest

The tokens question (what do I use for thinking), solved from `data/` by `python scripts/sotw.py tokens`. Nothing here is hand-typed; git history is the archive of previous states.

**Last solved:** 2026-08-31. **3 figure(s) past their freshness window** (run `python scripts/check_staleness.py`).

## The answer

```text
THE TOKENS QUESTION  (thinking)
  default          glm-5.3-flash: AA 57, $0.090/task, $1,915 for the 10-yr reference workload at list ($958 on promo through 2026-09-09)
  frontier calls   claude-opus-5: AA 63, $2.34/task, the cheapest costed frontier point (26.0x default per task)
  local inference  no: the best passing local config runs 4.1x cloud cost at AA 24
  the local box    hosts the agent: orchestration, sandboxes, a small resident triage model

Caveats, solved with the answer: The frontier tier is for rare calls, not the loop: pricing the reference workload against its 26 priced models runs from $12,348 (glm-5, 6x the default) to $756,000 (gpt-5.5-pro, 395x). Every price is VOLATILE; run scripts/check_staleness.py before trusting. And the harder caveat: 1 candidate set (CPU candidates for the compute node) has never been surveyed for entrants, so that pick is the best of an inherited list, not the best available. Run /refresh-data to re-open it.
```

## The reference workload

```text
315,000,000 output tokens/yr / 31,557,600 s/yr = 9.98 tok/s
sustained, 24/7/365, zero downtime

over 10 years at 80% cache hit:
  3.15B output tokens
  1.26B fresh input tokens
  5.04B cached input tokens
```

## Every priced path

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

## The cache objection, priced

| Cache hit rate | glm-5.3-flash | deepseek-v4-flash | gap |
|---:|---:|---:|---:|
| 0% | $2,520 | $3,465 | $945 |
| 25% | $2,331 | $3,130 | $799 |
| 50% | $2,142 | $2,794 | $652 |
| 75% | $1,953 | $2,459 | $506 |
| 80% | $1,915 | $2,391 | $476 |
| 100% | $1,764 | $2,123 | $359 |

deepseek-v4-flash has the cheapest cache rate on offer at $0.007/M against glm-5.3-flash's $0.030/M, 4.3x better. On this volume that is worth at most $145 even if every input token were cached, against a $504 output-price gap. The ranking cannot flip on cache behavior.

## The frontier is a cliff

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

![Capability vs cost Pareto frontier](../analysis/assets/pareto_frontier.png)

## The local throughput bar

| Machine | Price | Bandwidth (GB/s) | Max mem | Model | tok/s | Model 2 bound | vs 9.98 tok/s |
|---|---:|---|---:|---|---|---|---|
| Mac mini M6 | $899 | 170 nominal | 32GB | dense-70b q4 | n/a |  | **fails on capacity** |
| Mac mini M5 Pro | $1,699 | 307 nominal | 64GB | dense-70b q4 | 5.5 (ESTIMATE) |  | fails the bar |
| GMKtec EVO-X2 (Strix Halo) | $2,199 | 256 nominal / 215 measured | 128GB | dense-70b q4 | 5 (ESTIMATE) | <= 5 | fails the bar |
| GMKtec EVO-X2 (Strix Halo) | $2,199 | 256 nominal / 215 measured | 128GB | gpt-oss-120b mxfp4 | 31 (MEASURED) | <= 80 | **passes** |
| GMKtec EVO-X2 (Strix Halo) | $2,199 | 256 nominal / 215 measured | 128GB | gpt-oss-120b mxfp4 | 46.05 (MEASURED) | <= 80 | **passes** |
| GMKtec EVO-X2 (Strix Halo) | $2,199 | 256 nominal / 215 measured | 128GB | llama-3.3-70b q6 | 3.75 (MEASURED) |  | fails the bar |
| GMKtec EVO-X2 (Strix Halo) | $2,199 | 256 nominal / 215 measured | 128GB | gpt-oss-20b mxfp4 | 65.73 (MEASURED) |  | **passes** |
| GMKtec EVO-X2 (Strix Halo) | $2,199 | 256 nominal / 215 measured | 128GB | qwen3-coder-30b q8 | 50.16 (MEASURED) |  | **passes** |
| Mac Studio M5 Ultra 512GB | TODO | 1200.0 nominal | 512GB | moe-671b q4 | 32 (ESTIMATE) |  | **passes** |
| Mac Studio M5 Ultra 256GB | $18,299 | 1200.0 nominal | 256GB | dense-70b q4 | n/a |  | untested |
| Mac Studio M5 Max | $4,499 (est.) | 614.0 nominal | 128GB | dense-70b q4 | n/a |  | untested |
| Mac Studio M3 Ultra 512GB | $9,499 | 819.0 nominal | 512GB | deepseek-r1-671b q4 | 17.5 (MEASURED) |  | **passes** |
| Mac Studio M3 Ultra 512GB | $9,499 | 819.0 nominal | 512GB | deepseek-r1-0528 mlx4 | 11.15 (MEASURED) |  | **passes** |
| Mac Studio M3 Ultra 512GB | $9,499 | 819.0 nominal | 512GB | llama-3.1-405b q6 | 1.25 (MEASURED) |  | fails the bar |
| Mac Studio M3 Ultra 512GB | $9,499 | 819.0 nominal | 512GB | command-a-111b q8 | 3.24 (MEASURED) |  | fails the bar |
| Mac Studio M4 Max | $3,699 | 546.0 nominal | 128GB | llama-2-7b q4 | 69.95 (MEASURED) |  | **passes** |
| Mac mini M4 Pro | TODO | 273.0 nominal | 64GB | dense-70b q4 | n/a |  | untested |
| MacBook Pro 14 M5 | TODO | 153.0 nominal | 32GB | llama-7b q4 | 30.3 (MEASURED) |  | **passes** |
| MacBook Pro 14 M5 Pro | $3,699 (est.) | 307.0 nominal | 64GB | dense-70b q4 | n/a |  | untested |
| MacBook Pro 16 M5 Max | $10,149 | 614.0 nominal | 128GB | dense-70b q4 | n/a |  | untested |
| MacBook Pro 16 M4 Max | $4,999 | 546.0 nominal | 128GB | llama-7b q4 | 69.95 (MEASURED) |  | **passes** |
| Framework Desktop | $2,851 | 256.0 nominal / 212.0 measured | 128GB | qwen3-30b-a3b q4 | 85.11 (MEASURED) |  | **passes** |
| Framework Desktop | $2,851 | 256.0 nominal / 212.0 measured | 128GB | llama-4-scout-109b q4 | 20.23 (MEASURED) |  | **passes** |
| Framework Desktop | $2,851 | 256.0 nominal / 212.0 measured | 128GB | qwen3.5-122b-a10b q6 | 19.17 (MEASURED) |  | **passes** |
| Framework Desktop Pro 495 | TODO | 273.0 nominal | 192GB | dense-70b q4 | n/a |  | untested |
| Beelink GTR9 Pro | $1,985 | 256.0 nominal / 215.0 measured | 128GB | dense-70b q4 | n/a |  | untested |
| Minisforum MS-S1 Max | $2,299 | 256.0 nominal / 215.0 measured | 128GB | qwen3.5-35b q4 | 43.2 (MEASURED) |  | **passes** |
| Minisforum MS-S1 Max | $2,299 | 256.0 nominal / 215.0 measured | 128GB | qwen3.5-122b q4 | 19.2 (MEASURED) |  | **passes** |
| Minisforum MS-S1 Max | $2,299 | 256.0 nominal / 215.0 measured | 128GB | qwen2.5-72b q4 | 4.5 (MEASURED) |  | fails the bar |
| HP Z2 Mini G1a | $2,374 | 256.0 nominal | 128GB | gpt-oss-120b mxfp4 | 40 (MEASURED) |  | **passes** |
| Bosgame M5 | $2,999 | 256.0 nominal / 215.0 measured | 128GB | dense-70b q4 | n/a |  | untested |
| NVIDIA DGX Spark | $4,699 | 273.0 nominal | 128GB | gpt-oss-120b mxfp4 | 60.57 (MEASURED) |  | **passes** |
| NVIDIA DGX Spark | $4,699 | 273.0 nominal | 128GB | qwen3-30b-moe q4 | 89.3 (MEASURED) |  | **passes** |
| NVIDIA DGX Spark | $4,699 | 273.0 nominal | 128GB | qwen3-32b-dense q4 | 10.7 (MEASURED) |  | **passes** |
| NVIDIA DGX Spark | $4,699 | 273.0 nominal | 128GB | qwen3-coder-30b q8 | 44.26 (MEASURED) |  | **passes** |
| ASUS Ascent GX10 | $3,000 | 273.0 nominal | 128GB | dense-70b q4 | n/a |  | untested |
| Dell Pro Max with GB10 | $8,224 | 273.0 nominal | 128GB | dense-70b q4 | n/a |  | untested |
| Lenovo ThinkStation PGX | $4,100 | 273.0 nominal | 128GB | dense-70b q4 | n/a |  | untested |
| HP ZGX Nano G1n | $4,759 | 273.0 nominal | 128GB | dense-70b q4 | n/a |  | untested |
| MSI EdgeXpert MS-C931 | $5,979 | 273.0 nominal | 128GB | dense-70b q4 | n/a |  | untested |
| NVIDIA Jetson AGX Thor Dev Kit | $3,499 | 273.0 nominal | 128GB | dense-70b q4 | n/a |  | untested |
| NVIDIA RTX 5090 | $4,700 | 1792.0 nominal | 32GB | llama-2-7b q4 | 300.4 (MEASURED) |  | **passes** |
| NVIDIA RTX 4090 | $2,500 | 1008.0 nominal | 24GB | llama-2-7b q4 | 188.96 (MEASURED) |  | **passes** |
| NVIDIA RTX 5080 | $1,299 | 960.0 nominal | 16GB | llama-3.1-8b q4 | 44.9 (MEASURED) |  | **passes** |
| NVIDIA RTX 3090 | $972 | 936.0 nominal | 24GB | llama-2-7b q4 | 161.89 (MEASURED) |  | **passes** |
| NVIDIA RTX 3090 Ti | $1,240 | 1008.0 nominal | 24GB | llama-2-7b q4 | 172.26 (MEASURED) |  | **passes** |
| AMD Radeon RX 7900 XTX | $883 | 960.0 nominal | 24GB | llama-2-7b q4 | 122.5 (MEASURED) |  | **passes** |
| NVIDIA RTX 6000 Ada | $7,089 | 960.0 nominal | 48GB | llama-3-70b q4 | 18.36 (MEASURED) |  | **passes** |
| NVIDIA RTX 6000 Ada | $7,089 | 960.0 nominal | 48GB | llama-3-8b q4 | 130.99 (MEASURED) |  | **passes** |
| NVIDIA RTX PRO 6000 Blackwell | $17,000 | 1792.0 nominal | 96GB | gpt-oss-120b q4 | 134 (MEASURED) |  | **passes** |
| NVIDIA RTX PRO 6000 Blackwell | $17,000 | 1792.0 nominal | 96GB | llama-3.3-70b q4 | 32 (MEASURED) |  | **passes** |
| NVIDIA L40S | $8,500 | 864.0 nominal | 48GB | llama-3-70b q4 | 15.31 (MEASURED) |  | **passes** |
| NVIDIA A100 80GB PCIe | TODO | 1935.0 nominal | 80GB | llama-3-70b q4 | 22.11 (MEASURED) |  | **passes** |
| NVIDIA H100 80GB PCIe | $38,171 | 2000.0 nominal | 80GB | llama-3-70b q4 | 25.01 (MEASURED) |  | **passes** |

The Model 2 column is the bandwidth-bound upper bound; measured figures below their bound reflect routing and kernel overhead, and measured always wins an argument with the bound.

## The saturated local box still loses

| Quantity | Value |
|---|---:|
| Box | GMKtec EVO-X2 (Strix Halo), gpt-oss-120b, 5 yr, fully saturated |
| Capex | $2,199 |
| Electricity (5 yr) | $1,227.24 |
| All-in | $3,426.24 |
| Lifetime output | 4.89B tokens |
| Local cost | $0.70/M output |
| Cheapest cloud, same weights | $0.17/M output |
| Local vs cloud | 4.1x |
| Break-even utilization | 4.1 (above 1.0 = impossible) |

Capability context: gpt-oss-120b scores 24 on the index. The current volume tier (glm-5.3-flash) scores 57 at $0.090/task. The local option costs more per token and delivers 42% of the capability.

## Batching, modelled

gpt-oss-120b: 117B total, 5.1B active, 128 experts, top-4 routing. Sparsity ratio R = 22.9: you buy memory for 117B and get throughput from 5.1B.

| Batch | Aggregate bound (tok/s) | Per-stream bound | Resident weights per stream |
|---:|---:|---:|---:|
| 1 | 80 | 80 | 117.0B |
| 2 | 94 | 47 | 58.5B |
| 4 | 106 | 27 | 29.2B |
| 8 | 118 | 15 | 14.6B |
| 16 | 137 | 9 | 7.3B |
| 32 | 173 | 5 | 3.7B |
| 64 | 255 | 4 | 1.8B |

First-order model (uniform independent routing), measured bandwidth on GMKtec EVO-X2 (Strix Halo), ESTIMATE throughout. The measured single-stream rate is 31 tok/s against a 80 tok/s bound, a 2.6x overhead factor; scale the whole curve down accordingly. Measured batching curves are the top item on the open-questions list.

## How wide was the search

| Candidate set | In catalog | Fully placeable | Last surveyed | Status |
|---|---:|---|---|---|
| CPU candidates for the compute node | 4 | 4 priced, 4 screenable | never | **never surveyed** |
| hosted models for the token tiers | 97 | see report | 2026-08-31 | current |
| local machines for on-box inference | 37 | see report | 2026-08-31 | current |
| the capability axis itself | 49 | 32 costed | 2026-08-31 | current |

1 of 4 candidate sets were inherited from the original research and have never been re-opened. Every ranking drawn from them is "best of these", not "best available". Run `python scripts/refresh_plan.py` for the survey scope and where to look, or `/refresh-data` to have an agent do it.

## How much to trust this today

| Category | Figures | Oldest | Window | Status |
|---|---:|---|---|---|
| benchmarks | 1 | 2026-08-31 | 60d | fresh |
| dram | 1 | 2026-08-14 | 14d | **1 flagged** |
| hardware_pricing | 43 | 2026-06-15 | 30d | **2 flagged** |
| model_pricing | 98 | 2026-08-29 | 30d | fresh |

SPECrate submissions never expire and are not policed.
