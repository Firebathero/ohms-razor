# F3 and F4: The local inference ceiling

## The bar comes before the budget

The reference workload demands a sustained output rate (README derivation, just under 10
tok/s around the clock). A box that cannot sustain that rate cannot produce the workload
at any duty cycle, so most local hardware is disqualified before cost enters the picture.

Model 2 gives the physics: decode at batch 1 is memory-bandwidth-bound, so throughput is
capped by effective bandwidth divided by the bytes of active parameters streamed per
token. Dense 70B-class models need too many bytes per token for consumer-class bandwidth;
only an MoE with a small active set clears the bar, and only on a box with enough memory
to hold the full parameter count.

<!-- gen:local_hw -->
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
<!-- /gen:local_hw -->

Note the shape of the failures. The cheapest Mac fails on memory capacity outright. The
mid Mac holds the model and then misses the bar by half. The 128GB AMD box fails on a
dense 70B and passes with an MoE, which is Model 3's point in hardware form. The Mac mini
line cannot fit a 120B-class MoE with usable context at any price, which makes it strictly
worse than the AMD box for this job while costing more.

## F4: passing the bar still loses

Take the one measured passing configuration, saturate it 24/7 for its whole life, and
price it against the cheapest cloud host of the same weights:

<!-- gen:local_vs_cloud -->
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
<!-- /gen:local_vs_cloud -->

This is the most favorable possible framing for local (full saturation, which nobody
achieves; same weights; same quantization) and it still loses by a multiple. Real duty
cycles make it worse. The break-even utilization above 1.0 says there is no schedule at
which the box beats the API on cost.

Two caveats cut against overreading this:

- Batching is not modelled here; a local box serving several concurrent streams amortizes
  its memory cost like a provider does. `04-moe-asymmetry.md` models it first-order and
  the open-questions list asks for measurements.
- Cloud prices this low are themselves VOLATILE and spread nearly 9x across providers.
  Re-solve before quoting.

## F5: what the local box is actually for

Not inference. Hosting:

- agent orchestration running continuously
- sandbox VMs and headless browsers
- a small resident model for classification, triage, and transcription, where a 30B-class
  MoE at 70-100 tok/s is genuinely fine
- single-digit idle watts, silence, always-on
- on macOS, messaging integration, so the agent is something you text

The thinking goes to the cloud. The box is where the agent lives.
