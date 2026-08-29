# Model 3: The MoE memory-vs-compute asymmetry

This is the most important and least understood mechanism in the repo.

```text
R = P_total / P_active
```

A mixture-of-experts model makes you buy memory for all of its parameters while giving
you throughput from the small active set each token touches. That asymmetry prices
differently depending on who you are:

- A provider batches many concurrent requests. Different requests activate different
  experts, so the cost of holding the full parameter set amortizes across the batch.
- A solo local user runs at batch size 1 and carries the entire memory bill for one
  request's worth of compute.

R grows as models scale, so the local-vs-cloud gap widens structurally with model size.
This is not a pricing observation that a cheaper GPU fixes; it is a property of the
workload shape.

## Batching, modelled instead of hand-waved

The handoff names unmodelled batching as the strongest available rebuttal to F4 (weakness
1), so the repo models it rather than waiting to be told. First order, uniform independent
routing: a batch of B decode streams touches an expected `n * (1 - (1 - k/n)^B)` distinct
experts per step, and the streamed bytes amortize accordingly.

<!-- gen:moe_batching -->
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

First-order model (uniform independent routing), measured Strix Halo bandwidth, ESTIMATE throughout. The measured single-stream rate is 31 tok/s against a 80 tok/s bound, a 2.6x overhead factor; scale the whole curve down accordingly. Measured batching curves are the top item on the open-questions list.
<!-- /gen:moe_batching -->

Read the two right-hand columns together: aggregate throughput climbs while resident
weights per stream collapse. That pair is the provider's entire cost structure, and it is
why the cloud price of open weights sits so far below a solo box's cost for the same
weights. A local box that actually serves several concurrent streams starts to claw the
gap back; how much, on real hardware, is the top open question in CONTRIBUTING.md.

## Caveats

- The routing model is uniform and independent, which overstates amortization for real
  routers with hot experts, and everything inherits the Model 2 bound's optimism: the one
  measured point sits well below its bound. The table says ESTIMATE because it is one.
- KV-cache traffic and scheduling overhead are not modelled and both grow with B.
- None of this changes the batch-1 story a solo user lives in; it bounds how far the
  story bends when they stop being solo.
