# F6: The hardware scarcity is a supply story, not a demand story

High-memory local-AI-capable machines are scarce and getting more expensive, and this is
widely read as evidence of a local-AI movement: demand pulling the market. The
counter-reading is that it is a components story: DRAM supply pushing the market. The two
readings predict different futures, so the repo presents both.

<!-- gen:apple_lineup -->
| Machine | Price | Max unified memory | Bandwidth |
|---|---:|---:|---:|
| Mac mini M6 | $899 | 32GB | 170 GB/s |
| Mac mini M5 Pro | $1,699 | 64GB | 307 GB/s |
| Mac Studio M5 Ultra | $15,000 (ESTIMATE) | 512GB | 1200 GB/s |
<!-- /gen:apple_lineup -->

## The supply reading

Apple's own product behavior is the evidence. The M6 mini caps at 32GB. The M4 Pro mini's
memory ceiling was cut from 64GB to 48GB mid-cycle. Base prices rose $100 across the
line. Cook described "a hundred-year flood on the memory pricing." DDR5 street pricing
sits at multiples of its pre-shortage level with the squeeze forecast into mid-2027, and
Hetzner passed a triple-digit-percent repricing through its cloud tiers driven by the
same components market (solved percentages in `05-hardware-selection.md`).

Nobody caps memory ceilings when high-memory buyers are showing up. You cap them when you
cannot get parts. Restricting your best-selling configurations is not a demand response;
it is an allocation response.

## The demand reading

On a later earnings call, Cook described customers deploying "clusters of Mac Studio
systems to run frontier-class models locally" and tied Mac mini and Studio demand to the
OpenClaw agent platform. If accurate at volume, that is genuine demand for exactly the
high-memory boxes in question, and some of the scarcity is being bought, not withheld.

## Which reading is stronger

The supply reading, on current evidence. It explains the specific shape of the facts (the
ceilings came down, which demand cannot cause), it has an identified physical mechanism
(HBM capacity diversion), and the demand quote is a vendor characterizing its own demand
during a shortage, which is what a vendor would say in either world. But the demand
reading is not dismissible: cluster deployments are concrete and the agent-platform pull
is real. Both are recorded; the disagreement is over weights, not facts.

## What would settle it

- Memory ceilings recovering as DRAM normalizes (supply reading confirmed) versus staying
  capped while prices fall (demand for segmentation, a third reading).
- Sustained availability data for the 128GB unified-memory boxes.
- Whether "clusters of Mac Studios" shows up in any independent channel data rather than
  a single earnings-call anecdote.
