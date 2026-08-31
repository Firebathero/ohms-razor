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
| GMKtec EVO-X2 (Strix Halo) | $1,499 | 256 nominal / 215 measured | 128GB | dense-70b q4 | 5 (ESTIMATE) | <= 5 | fails the bar |
| GMKtec EVO-X2 (Strix Halo) | $1,499 | 256 nominal / 215 measured | 128GB | gpt-oss-120b mxfp4 | 31 (MEASURED) | <= 80 | **passes** |
| Mac Studio M5 Ultra | $15,000 (est.) | 1200 nominal | 512GB | moe-671b q4 | 32 (ESTIMATE) |  | **passes** |

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
| Capex | $1,499 |
| Electricity (5 yr) | $1,227.24 |
| All-in | $2,726.24 |
| Lifetime output | 4.89B tokens |
| Local cost | $0.56/M output |
| Cheapest cloud, same weights | $0.17/M output |
| Local vs cloud | 3.3x |
| Break-even utilization | 3.3 (above 1.0 = impossible) |

Capability context: gpt-oss-120b scores 24 on the index. The current volume tier (glm-5.3-flash) scores 57 at $0.045/task. The local option costs more per token and delivers 42% of the capability.
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
