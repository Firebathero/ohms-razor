# Sources

Every figure in `data/*.yaml` points here. Figures the handoff dated only "2026-08" were
verified current at the 2026-08-29 pull; that is the date they carry. URLs the handoff did
not capture are marked `TODO: link`; do not invent them, chase them.

Confidence tag normalization from the workbook: `Current` maps to VOLATILE, `Assumption`
and `Est` map to ESTIMATE, `Calibrated` maps to DERIVED, `Confirm` maps to CONFIRMED.

## handoff

`HANDOFF.md`, internal research document, last data pull 2026-08-29. Defines the reference
work unit and findings F1-F7. Not published; this repo is its public form.

## glm-53-flash-pricing

Zhipu list pricing for GLM-5.3-Flash: $0.15 input / $0.03 cached / $0.50 output per Mtok.
Promo: 50 percent off, ends 2026-09-09 24:00 UTC+8. Accessed 2026-08-29. TODO: link
(vendor pricing page).

## deepseek-v4-flash-pricing

DeepSeek V4-Flash off-peak pricing: $0.22 / $0.007 / $0.66 per Mtok, peak windows
01:00-04:00 and 06:00-10:00 UTC at 2x. Output moved $0.28 to $0.66/$1.32 on 2026-08-16
(confirmed against the vendor's change announcement). Accessed 2026-08-29. TODO: link
(vendor pricing page and change notice).

## kimi-k3-pricing

Moonshot Kimi K3: $3.00 / $0.30 / $15.00 per Mtok; 2.8T total parameters. Accessed
2026-08-29. TODO: link.

## gpt-oss-120b-cloud-pricing

Cheapest observed hosted pricing for gpt-oss-120b: $0.03 input / $0.17 output per Mtok at
CoreWeave and DeepInfra; spread up to 8.9x across the 18 providers tracked. Accessed
2026-08-29. TODO: link (provider price tracker snapshot).

## gpt-oss-120b-params

OpenAI gpt-oss-120b model card: 117B total parameters, 5.1B active per token, 128 experts
per MoE layer, top-4 routing. TODO: link (model card).

## moe-671b-params

DeepSeek V3/R1-class geometry: 671B total, 37B active. Used only for the Mac Studio
estimate. TODO: link (technical report).

## aa-intelligence-index

AA Intelligence Index v4.1.1, read 2026-08-26. Scores: GLM-5.3-Flash 57, DeepSeek V4-Flash
52, Kimi K3 60, GLM-5.3-max 60, Grok 4.6 60, Claude Opus 5 63, gpt-oss-120b 24. Cost per
task: GLM-5.3-Flash $0.045, Grok 4.6 $0.62; other entries not carried in the handoff and
marked TODO: unverified in `benchmarks.yaml`. TODO: link (index page, pin the version).

## apple-lineup

Apple published specs and US prices, read 2026-08-25: Mac mini M6 $899, 32GB max,
170 GB/s. Mac mini M5 Pro $1,699 base, 64GB max, 307 GB/s, about $2,700 at 64GB. Mac
Studio M5 Ultra 512GB at 1.2 TB/s; price not confirmed, carried as ESTIMATE. Context for
the supply story: the M4 Pro mini's ceiling was cut from 64GB to 48GB and base prices rose
$100. Tim Cook's "hundred-year flood on the memory pricing" remark and, on a later call,
"clusters of Mac Studio systems to run frontier-class models locally" tied to the OpenClaw
agent platform. TODO: link (spec pages, earnings call transcripts).

## strix-halo

GMKtec EVO-X2 (AMD Strix Halo), 128GB, $1,499 street. Bandwidth 256 GB/s nominal,
about 215 GB/s measured. gpt-oss-120b decode measured at about 31 tok/s. Accessed
2026-08-29. TODO: link (retail listing, bench thread with the measured figures).

## specrate

SPECrate 2017 int_base vendor submissions, spec.org. These do not expire.

**2026-08-31 survey pull.** Every published CPU2017 integer-rate result, 13,179 of them,
newest published 2026-08-10. Two indexes were needed:

- <https://www.spec.org/cpu2017/results/rint2017.html>, "All Published SPEC CPU2017
  Results", which covers everything through 2025q1 and then stops: the page itself says
  "Last update: 2025-02-11". Anyone who pulls only this page silently misses eighteen
  months of submissions.
- <https://www.spec.org/cpu2017/results/res2025q2/> through `res2026q3/`, the quarterly
  indexes, section "CPU2017 Integer Rates", which carry the rest.

Of those, 2,876 report one enabled chip. Virtual-machine submissions are excluded: HPE
published eight EPYC 9965 results at 153-163 points from a ProLiant DL345 Gen12 VM whose
disclosure still names 192 cores, against a real single-socket 1,525. Each candidate's
`specrate_1p.value_used` is the median of its single-chip submissions, with the count and
the observed range recorded on the entry.

Cross-check on the four inherited candidates: scaling their 2P medians by sigma = 0.5256
predicts 1,634 / 1,349 / 1,361 / 1,200 for the 9965 / 9845 / 9755 / 9745; the measured 1P
medians are 1,525 / 1,250 / 1,260 / 1,155. The scaled numbers run 5 to 8 percent high, all
in the same direction, which is what a sigma calibrated on one part does. The catalog now
uses the measured figures.

Pre-survey transcription, accessed 2026-08-29, kept for the workbook trail:
9965 2P: 3,100-3,230 across four submissions, median 3,140 used. 9845 2P: 2,620, single
Dell M7725 result, Mar-2025. 9745 2P: 2,290-2,400 across four, workbook used 2,330 (strict
median 2,320; flagged in the YAML). 9745 1P: 1,170-1,270 across three. 9755 2P: no
submission found; 2,589 back-solved from the Phoronix 9745-to-9755 geomean ratio, tagged
DERIVED. EPYC 9454P 1P: 523, Dell R6615, Nov-2023. TODO: link (individual result pages).

## phi-derate

Phoronix, Mar-2026, Gigabyte MZ33-AR1: EPYC 9745 at 320W cTDP delivered about 98 percent
of its 400W performance across a 555-benchmark geomean; peak CPU draw 379W at the 400W
rating. The 0.99 figure for the 9965 at 450W is an extrapolation from this measurement,
tagged ESTIMATE; nobody has published 450 vs 500 on the 9965. TODO: link (article).

## cpu-prices

Street prices, US channel, accessed 2026-08-29, all VOLATILE. 9965: about $7,000 (eBay new
about $6,995; TechRadar tracked sub-$6,000 new in Jun-2026; AMD 1kU cut $14,813 to
$11,988). 9845: $9,684 (IT Creations, new unlocked tray; 1kU $11,411; never discounted the
way the 9965 was). 9755: about $6,500 (Phoronix noted about $7,200 Mar-2026; eBay dealer
$6,169). 9745: about $7,200 (Phoronix Mar-2026; IT Creations $7,950-8,340; 1kU cut $12,141
to $10,588). cTDP ranges and 614 GB/s 12-channel bandwidth from AMD product pages,
CONFIRMED. TODO: link (retail listings, AMD product pages).

Added by the 2026-08-31 survey, US channel, VOLATILE: EPYC 9655P $5,346 and EPYC 9654P
$5,350 new tray, both IT Creations (<https://www.itcreations.com/>; a second 9654P listing
of the same part sat at $5,450). Those two plus the four above are the only street prices
in the catalog. Every other candidate carries a vendor list price instead, which is an
upper bound on what the part costs, flagged as such in `price_list_note` and shown as
"list" in every table. The refresh plan names the ones where a real street price could
still change the ranking.

## amd-epyc-specs

AMD EPYC model specifications: cores, architecture, L3, socket, socket count, memory
channels and speed, TDP, launch date, and list price at launch. Accessed 2026-08-31 from
the maintained EPYC spec tables at
<https://en.wikipedia.org/wiki/Template:AMD_Epyc_9005_series> (Turin, Turin Dense, Sorano,
Grado) and <https://en.wikipedia.org/wiki/Template:AMD_Epyc_9004_Genoa> (Genoa, Genoa-X,
Bergamo, Siena), each cell of which cites AMD's own product pages. AMD's combined table at
<https://www.amd.com/en/products/specifications/server-processor.html> renders client-side
and could not be pulled as data. EPYC 8005 "Sorano" launched 2026-05-09 per
<https://www.amd.com/en/products/processors/server/epyc/8005-series.html>; its list prices
were confirmed against ServeTheHome's launch coverage (8535P $5,499, 8635P $5,799).

## intel-xeon6-specs

Intel Xeon 6 model specifications, accessed 2026-08-31 from
<https://en.wikipedia.org/wiki/Granite_Rapids> (6900P and 6700P/6500P tables) and
<https://en.wikipedia.org/wiki/Sierra_Forest> (6700E), each row linking the matching
ark.intel.com SKU page. Memory channels are 12 for the 6900 platform (LGA7529) and 8 for
the 6700/6500 platform (LGA4710).

Clearwater Forest, the Xeon 6+ 6900E+ parts, launched 2026-06-01 and has no SKU table yet:
6990E+ 288 cores 450W, 6980E+ 264 cores 400W, 6970E+ 192 cores 400W, all 12-channel
DDR5-8000, from launch coverage at
<https://www.tomshardware.com/pc-components/cpus/intel-xeon-6-clearwater-forest-puts-18a-in-the-data-center-with-up-to-288-cores-576-mb-of-l3-cache-new-xeon-6990e-is-30-percent-faster-per-thread-than-192-core-amd-epyc-9965-says-intel>
and <https://www.servethehome.com/intel-xeon-6-clearwater-forest-is-out/>. Intel also ships
a 330W 6990E+ and a 300W 6980E+; the SPEC submissions do not say which variant was run, so
the catalog carries the higher figure and says so. No list price has been published, so
these three sit in the catalog unpriced and compete on the efficiency axis only. ARK
returns HTTP 403 to scripted fetches; transcribe by hand.

## ampere-specs

Ampere AmpereOne A192-32X: 192 cores at 3.2 GHz, 12-channel DDR5, socket FCLGA5964, $5,555
at launch. Accessed 2026-08-31 via ServeTheHome's review and Phoronix's benchmark coverage.
Ampere quotes 400W as "usage power" measured on a SPEC integer workload rather than a
conventional TDP; one retailer lists the same part at 276W. The catalog carries 400W and
records the conflict rather than picking silently.

## motherboard

Gigabyte MZ33-AR1, about $900. Phoronix put it near $700; eBay and Newegg run
$1,000-1,250. Single socket SP5, cTDP to 500W, 24 DIMM slots. TODO: link.

## dram

DDR5-6400 ECC RDIMM street pricing, DatacenterDisk live tracker, read 2026-08-14: observed
band $29.56-39.06/GB, median $35.70. Driven by HBM capacity diversion; shortage forecast
into mid-2027. Pre-shortage reference of about $8/GB is an ESTIMATE. TODO: link.

## electricity

BGE price-to-compare 14.609c/kWh generation-only through 30-Sep-2026; Maryland residential
all-in averages 16-22c depending on source. The $0.20/kWh input is an assumption on top of
these. TODO: link (BGE tariff page).

## hetzner

Hetzner price-adjustment document effective 2026-06-15: AX162-1 $722.10/mo (launched
EUR 199/mo Feb-2024), AX162-1-LTD $372.10/mo, both excl. IPv4 and VAT plus $359 setup.
Cloud repricing old-vs-new: CCX63 EUR 374.49 to 853.49, CPX41 EUR 38.99 to 120.49, CPX51
EUR 77.99 to 237.99. Percentage moves are computed at solve time from these raw prices.
TODO: link (the adjustment doc).
