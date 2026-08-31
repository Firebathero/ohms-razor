# Token economics: latest

The tokens question (what do I use for thinking), solved from `data/` by `python scripts/sotw.py tokens`. Nothing here is hand-typed; git history is the archive of previous states.

**Last solved:** 2026-08-31. **3 figure(s) past their freshness window** (run `python scripts/check_staleness.py`).

## The answer

```text
THE TOKENS QUESTION  (thinking)
  default          glm-5.3-flash: AA 57, $0.045/task, $1,915 for the 10-yr reference workload at list ($958 on promo through 2026-09-09)
  frontier calls   grok-4.6: AA 60, $0.62/task, the cheapest costed frontier point (13.8x default per task)
  local inference  no: the best passing local config runs 4.1x cloud cost at AA 24
  the local box    hosts the agent: orchestration, sandboxes, a small resident triage model

Caveats, solved with the answer: kimi-k3, glm-5.3-max, claude-opus-5 sit at or above the frontier pick's score with no cost per task yet (TODO in data/benchmarks.yaml); the pick re-solves when they are costed. kimi-k3 is the one frontier model with API pricing here and prices the reference workload at $52,542 (27.4x default), which is why the frontier tier is for rare calls, not the loop. Every price is VOLATILE; run scripts/check_staleness.py before trusting. And the harder caveat: 2 candidate sets (CPU candidates for the compute node, hosted models for the token tiers) have never been surveyed for entrants, so these picks are the best of an inherited list, not the best available. Run /refresh-data to re-open them.
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
| gpt-oss-120b-cloud (list) | $724 | 24 | 2026-08-29 | VOLATILE |
| glm-5.3-flash (promo) | $958 | 57 | 2026-08-29 | EXPIRES, ends 2026-09-09 |
| glm-5.3-flash (list) | $1,915 | 57 | 2026-08-29 | VOLATILE |
| deepseek-v4-flash (off-peak only) | $2,391 | 52 | 2026-08-29 | VOLATILE |
| deepseek-v4-flash (24/7, 29% peak) | $3,089 | 52 | 2026-08-29 | VOLATILE |
| kimi-k3 (list) | $52,542 | 60 | 2026-08-29 | VOLATILE |

Scores: AA Intelligence Index v4.1.1 (2026-08-26). Index parity is not task parity.

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

| Model | AA score | $/task | vs glm-5.3-flash | Pareto |
|---|---:|---:|---:|---|
| glm-5.3-flash | 57 | $0.045 | 1.0x | on frontier |
| grok-4.6 | 60 | $0.620 | 13.8x | on frontier |
| deepseek-v4-flash | 52 | TODO: unverified | | not placeable yet |
| kimi-k3 | 60 | TODO: unverified | | not placeable yet |
| glm-5.3-max | 60 | TODO: unverified | | not placeable yet |
| claude-opus-5 | 63 | TODO: unverified | | not placeable yet |
| gpt-oss-120b | 24 | TODO: unverified | | not placeable yet |

Baseline is glm-5.3-flash, the cheapest costed entry, solved rather than named. Models the handoff placed between the tiers, scoring at or below the volume tier while costing a multiple of it (individual figures pending re-pull): gpt-5.6-luna, deepseek-v4-pro, glm-5.2, qwen3.8-27b, gemini-3.7-flash, grok-4.5, muse-spark.

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

Capability context: gpt-oss-120b scores 24 on the index. The current volume tier (glm-5.3-flash) scores 57 at $0.045/task. The local option costs more per token and delivers 42% of the capability.

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
| hosted models for the token tiers | 4 | see report | never | **never surveyed** |
| local machines for on-box inference | 37 | see report | 2026-08-31 | current |
| the capability axis itself | 7 | 2 costed | 2026-08-26 | current |

2 of 4 candidate sets were inherited from the original research and have never been re-opened. Every ranking drawn from them is "best of these", not "best available". Run `python scripts/refresh_plan.py` for the survey scope and where to look, or `/refresh-data` to have an agent do it.

## How much to trust this today

| Category | Figures | Oldest | Window | Status |
|---|---:|---|---|---|
| benchmarks | 1 | 2026-08-26 | 60d | fresh |
| dram | 1 | 2026-08-14 | 14d | **1 flagged** |
| hardware_pricing | 43 | 2026-06-15 | 30d | **2 flagged** |
| model_pricing | 5 | 2026-08-29 | 30d | fresh |

SPECrate submissions never expire and are not policed.
