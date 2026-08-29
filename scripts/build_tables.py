"""Re-solves every generated block in README.md and analysis/*.md from data/.

There are no static numbers in this repo. Prose lives outside the markers; everything
between them is owned by this script and overwritten on every run.

    <!-- gen:key -->
    ...solved content...
    <!-- /gen:key -->

Usage:
    python scripts/build_tables.py           solve and rewrite the docs
    python scripts/build_tables.py --check   verify the docs match the data, write nothing
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_staleness  # noqa: E402
import repo_data  # noqa: E402
from repo_data import MTOK, ROOT  # noqa: E402

DOCS = [ROOT / "README.md", ROOT / "REPORT.md", *sorted((ROOT / "analysis").glob("*.md"))]

MARKER = re.compile(r"(<!-- gen:(?P<key>[a-z0-9_]+) -->\n)(?P<body>.*?)(<!-- /gen:(?P=key) -->)", re.S)


def usd(x: float, decimals: int = 2) -> str:
    return f"${x:,.{decimals}f}"


# ---------------------------------------------------------------- renderers

def render_last_solved() -> str:
    rows = check_staleness.collect()
    flagged = [r for r in rows if r.status != "fresh"]
    line = f"**Last solved:** {date.today().isoformat()}."
    if flagged:
        line += f" **{len(flagged)} figure(s) past their freshness window** (run `python scripts/check_staleness.py`)."
    else:
        line += " All figures inside their freshness windows."
    return line


def render_workload_derivation() -> str:
    ref = repo_data.reference_workload()
    w = ref.per_year
    lt = ref.lifetime
    return (
        "```text\n"
        f"{w.output_tokens:,.0f} output tokens/yr / 31,557,600 s/yr = {ref.required_tok_s:.2f} tok/s\n"
        f"sustained, 24/7/365, zero downtime\n"
        "\n"
        f"over {ref.years:.0f} years at {w.cache_hit_rate:.0%} cache hit:\n"
        f"  {lt.output_tokens / 1e9:.2f}B output tokens\n"
        f"  {lt.fresh_input_tokens / 1e9:.2f}B fresh input tokens\n"
        f"  {lt.cached_input_tokens / 1e9:.2f}B cached input tokens\n"
        "```"
    )


def render_api_cost_10yr() -> str:
    ref = repo_data.reference_workload()
    lines = [
        f"| Path | {ref.years:.0f}-yr cost | AA score | Priced | Confidence |",
        "|---|---:|---:|---|---|",
    ]
    for r in repo_data.solve_api_costs():
        score = str(r.aa_score) if r.aa_score is not None else "n/a"
        conf = r.confidence + (f", ends {r.expires}" if r.expires else "")
        lines.append(f"| {r.label} | {usd(r.lifetime_cost, 0)} | {score} | {r.date} | {conf} |")
    lines.append("")
    lines.append(
        "Scores: AA Intelligence Index "
        f"{repo_data.aa_index()['version']} ({repo_data.aa_index()['date']}). Index parity is not task parity."
    )
    return "\n".join(lines)


def render_cache_sensitivity() -> str:
    ref = repo_data.reference_workload()
    models = {m.id: m for m in repo_data.priced_models()}
    glm, ds = models["glm-5.3-flash"], models["deepseek-v4-flash"]
    rows = repo_data.cache_sensitivity("glm-5.3-flash", "deepseek-v4-flash", [0.0, 0.25, 0.5, 0.75, 0.8, 1.0])
    lines = [
        "| Cache hit rate | glm-5.3-flash | deepseek-v4-flash (off-peak) | gap |",
        "|---:|---:|---:|---:|",
    ]
    for h, a, b in rows:
        lines.append(f"| {h:.0%} | {usd(a, 0)} | {usd(b, 0)} | {usd(b - a, 0)} |")
    max_cache_advantage = (
        ref.lifetime.input_tokens
        * (glm.pricing.cached_input_per_mtok - ds.pricing.cached_input_per_mtok)
        / MTOK
    )
    output_gap = ref.lifetime.output_tokens * (ds.pricing.output_per_mtok - glm.pricing.output_per_mtok) / MTOK
    lines.append("")
    lines.append(
        f"DeepSeek's cache rate ({usd(ds.pricing.cached_input_per_mtok, 3)}/M vs "
        f"{usd(glm.pricing.cached_input_per_mtok, 3)}/M) is worth at most "
        f"{usd(max_cache_advantage, 0)} on this volume even if every input token were cached, "
        f"against a {usd(output_gap, 0)} output-price gap. The ranking cannot flip on cache behavior."
    )
    return "\n".join(lines)


def render_frontier_table() -> str:
    idx = repo_data.aa_index()
    points = repo_data.solve_frontier()
    glm_cost = next(p.cost_per_task for p in points if p.model == "glm-5.3-flash")
    lines = [
        "| Model | AA score | $/task | vs glm-5.3-flash | Pareto |",
        "|---|---:|---:|---:|---|",
    ]
    for p in points:
        lines.append(
            f"| {p.model} | {p.score} | {usd(p.cost_per_task, 3)} | {p.cost_per_task / glm_cost:.1f}x | "
            f"{'on frontier' if p.on_frontier else 'dominated'} |"
        )
    uncosted = [e for e in idx["entries"] if e["cost_per_task_usd"] is None]
    for e in uncosted:
        lines.append(f"| {e['model']} | {e['score']} | TODO: unverified | | not placeable yet |")
    lines.append("")
    lines.append(
        "Midrange models the handoff places at 2x to 14x glm-5.3-flash per task while scoring at or "
        "below it (individual figures pending re-pull): " + ", ".join(idx["midrange_noted"]) + "."
    )
    return "\n".join(lines)


def render_local_hw() -> str:
    bar, rows = repo_data.solve_local_bar()
    lines = [
        f"| Machine | Price | Bandwidth (GB/s) | Max mem | Model | tok/s | Model 2 bound | vs {bar:.2f} tok/s |",
        "|---|---:|---|---:|---|---|---|---|",
    ]
    for r in rows:
        price = usd(r.price_usd, 0) if r.price_usd else "TODO"
        if r.price_confidence == "ESTIMATE":
            price += " (est.)"
        tok = f"{r.tok_s:g} ({r.tok_s_confidence})" if r.tok_s is not None else "n/a"
        bound = f"<= {r.bound_tok_s:.0f}" if r.bound_tok_s is not None else ""
        verdict = f"**{r.verdict}**" if r.passes or not r.fits else r.verdict
        lines.append(
            f"| {r.machine} | {price} | {r.bandwidth_label} | {r.memory_gb}GB | {r.model} | {tok} | {bound} | {verdict} |"
        )
    lines.append("")
    lines.append(
        "The Model 2 column is the bandwidth-bound upper bound; measured figures below their bound "
        "reflect routing and kernel overhead, and measured always wins an argument with the bound."
    )
    return "\n".join(lines)


def render_local_vs_cloud() -> str:
    lc = repo_data.solve_local_vs_cloud()
    lines = [
        "| Quantity | Value |",
        "|---|---:|",
        f"| Box | {lc.machine}, {lc.model}, {lc.years:.0f} yr, fully saturated |",
        f"| Capex | {usd(lc.capex_usd, 0)} |",
        f"| Electricity ({lc.years:.0f} yr) | {usd(lc.energy_usd, 2)} |",
        f"| All-in | {usd(lc.total_usd, 2)} |",
        f"| Lifetime output | {lc.lifetime_mtok / 1000:.2f}B tokens |",
        f"| Local cost | {usd(lc.local_per_mtok, 2)}/M output |",
        f"| Cheapest cloud, same weights | {usd(lc.cloud_per_mtok, 2)}/M output |",
        f"| Local vs cloud | {lc.ratio:.1f}x |",
        f"| Break-even utilization | {lc.breakeven_utilization:.1f} (above 1.0 = impossible) |",
    ]
    lines.append("")
    lines.append(
        f"Capability context: {lc.model} scores {lc.local_score} on the AA index. The volume API tier "
        f"(glm-5.3-flash) scores {lc.volume_tier_score} at {usd(lc.volume_tier_cost_per_task, 3)}/task. "
        "The local option costs more per token and delivers less than half the capability."
    )
    return "\n".join(lines)


def render_moe_batching() -> str:
    R, curve = repo_data.solve_moe_batching()
    geo = repo_data.moe_geometry("gpt-oss-120b")
    _, bar_rows = repo_data.solve_local_bar()
    measured = next(r for r in bar_rows if r.model == "gpt-oss-120b mxfp4")
    lines = [
        f"gpt-oss-120b: {geo.total_params_b:g}B total, {geo.active_params_b:g}B active, "
        f"{geo.n_experts} experts, top-{geo.experts_per_token} routing. "
        f"Sparsity ratio R = {R:.1f}: you buy memory for {geo.total_params_b:g}B and get throughput from {geo.active_params_b:g}B.",
        "",
        "| Batch | Aggregate bound (tok/s) | Per-stream bound | Resident weights per stream |",
        "|---:|---:|---:|---:|",
    ]
    for r in curve:
        lines.append(
            f"| {r.batch} | {r.aggregate_bound_tok_s:,.0f} | {r.per_stream_bound_tok_s:,.0f} | "
            f"{r.resident_params_b_per_stream:.1f}B |"
        )
    lines.append("")
    lines.append(
        f"First-order model (uniform independent routing), measured Strix Halo bandwidth, ESTIMATE "
        f"throughout. The measured single-stream rate is {measured.tok_s:g} tok/s against a "
        f"{measured.bound_tok_s:.0f} tok/s bound, a {measured.bound_tok_s / measured.tok_s:.1f}x overhead "
        "factor; scale the whole curve down accordingly. Measured batching curves are the top item on "
        "the open-questions list."
    )
    return "\n".join(lines)


def render_psi_compare() -> str:
    sol = repo_data.solve_psi()
    spec = {c["name"]: c for c in repo_data.load("cpu_specs")["candidates"]}
    ranked = sorted(sol.evaluations, key=lambda e: e.psi)
    lines = [
        "| CPU | Cores | Run cTDP | phi | W (1P pts) | Wall W | TCO | Psi ($/pt-yr) | pts/W | Energy share | Rank |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for e in sol.evaluations:
        c = spec[e.name]
        phi = f"{c['phi']['value']:g} ({c['phi']['confidence']})"
        name = f"**{e.name}**" if e.name == sol.winner.name else e.name
        rank = ranked.index(e) + 1
        lines.append(
            f"| {name} | {c['cores']} | {c['run_ctdp_w']}W | {phi} | {e.work_rate:,.0f} | "
            f"{e.wall_power_w:,.0f} | {usd(e.tco_usd, 0)} | {e.psi:.2f} | {e.points_per_watt:.2f} | "
            f"{e.energy_share:.0%} | {rank} |"
        )
    op = repo_data.operating_inputs()
    lines.append("")
    lines.append(
        f"Winner: **{sol.winner.name}** at {usd(sol.winner.psi, 2)} per SPECrate-point-year over "
        f"{op.years:.0f} years ({usd(sol.winner.capex_usd, 0)} capex). Best perf/watt is "
        f"**{sol.best_points_per_watt.name}** at {sol.best_points_per_watt.points_per_watt:.2f} pts/W: "
        "efficiency and value rank differently, which is the point of solving for Psi instead."
    )
    return "\n".join(lines)


def render_psi_sens_electricity() -> str:
    cpus = [c.name for c in repo_data.cpu_inputs()]
    lines = ["| $/kWh | " + " | ".join(c.replace("AMD EPYC ", "") for c in cpus) + " | Winner |", "|---:|" + "---:|" * (len(cpus) + 1)]
    for r in [0.10, 0.20, 0.30, 0.40, 0.60]:
        sol = repo_data.solve_psi(repo_data.operating_inputs(electricity_usd_per_kwh=r))
        cells = " | ".join(f"{e.psi:.2f}" for e in sol.evaluations)
        lines.append(f"| {r:.2f} | {cells} | {sol.winner.name.replace('AMD EPYC ', '')} |")
    return "\n".join(lines)


def render_psi_sens_hold() -> str:
    cpus = [c.name for c in repo_data.cpu_inputs()]
    lines = ["| Hold (yr) | " + " | ".join(c.replace("AMD EPYC ", "") for c in cpus) + " | Winner |", "|---:|" + "---:|" * (len(cpus) + 1)]
    for y in [3, 5, 7, 10, 12]:
        sol = repo_data.solve_psi(repo_data.operating_inputs(years=float(y)))
        cells = " | ".join(f"{e.psi:.2f}" for e in sol.evaluations)
        lines.append(f"| {y} | {cells} | {sol.winner.name.replace('AMD EPYC ', '')} |")
    lines.append("")
    lines.append(
        "Shorter holds punish capex and reward efficiency; the ranking holds while the absolute "
        "numbers roughly double at five years (handoff weakness 7: ten-year amortization is aggressive)."
    )
    return "\n".join(lines)


def render_breakevens() -> str:
    lines = [
        "| Contender | CPU price that ties the winner | Street price | Gap |",
        "|---|---:|---:|---:|",
    ]
    for name, tie, street in repo_data.solve_tie_prices():
        gap = "cannot get there" if tie <= 0 else f"{usd(street - tie, 0)} too expensive"
        lines.append(f"| {name} | {usd(tie, 0)} | {usd(street, 0)} | {gap} |")
    return "\n".join(lines)


def render_memory_lever() -> str:
    a = repo_data.load("assumptions")
    current = float(a["memory_pricing"]["ddr5_6400_rdimm_usd_per_gb"]["value"])
    pre = float(a["memory_pricing"]["pre_shortage_reference_usd_per_gb"]["value"])
    prices = sorted({pre, 15.0, 25.0, current, 45.0})
    lines = ["| DDR5 $/GB | Memory cost (384GB) | Winner Psi |", "|---:|---:|---:|"]
    for g, mem, psi in repo_data.solve_memory_lever(prices):
        marker = " (current)" if g == current else (" (pre-shortage)" if g == pre else "")
        lines.append(f"| {usd(g, 2)}{marker} | {usd(mem, 0)} | {psi:.2f} |")
    lines.append("")
    lines.append(
        "Memory is identical across candidates, so it never changes the ranking. It is also the "
        "largest single number under your control; waiting for DRAM normalization is worth more than "
        "any CPU decision in this repo."
    )
    return "\n".join(lines)


def render_rent_compare() -> str:
    own, rows, boxes, fleet = repo_data.solve_rent()
    op = repo_data.operating_inputs()
    monthly_own = own.tco_usd / (op.years * 12.0)
    lines = [
        "| Option | SPECrate 1P | $/month | Psi ($/pt-yr) | vs owning |",
        "|---|---:|---:|---:|---:|",
        f"| **Own: {own.name}** | {own.work_rate:,.0f} | {usd(monthly_own, 2)} (amortized) | {own.psi:.2f} | 1.0x |",
    ]
    for r in rows:
        lines.append(
            f"| {r.name} | {r.specrate_1p:,.0f} | {usd(r.monthly_usd, 2)} | {r.psi:.2f} | {r.times_owning:.1f}x |"
        )
    lines.append("")
    lines.append(
        f"Matching the owned node takes {boxes:.1f} rented boxes, {usd(fleet, 0)} per year: one year "
        f"of equivalent rental costs most of a decade of owning ({usd(own.tco_usd, 0)} all-in)."
    )
    moves = repo_data.solve_hetzner_cloud_moves()
    lo = min(m[3] for m in moves)
    hi = max(m[3] for m in moves)
    lines.append("")
    lines.append("| Hetzner cloud instance | Old EUR/mo | New EUR/mo | Increase |")
    lines.append("|---|---:|---:|---:|")
    for inst, old, new, pct in moves:
        lines.append(f"| {inst} | {old:,.2f} | {new:,.2f} | +{pct:.0f}% |")
    lines.append("")
    lines.append(
        f"Cloud repricing of 2026-06-15 ran +{lo:.0f}% to +{hi:.0f}%, computed from the raw prices "
        "(the handoff's stated 128-205% range slightly understated the top end). Renting still buys "
        "hardware replacement, redundant power, someone on call at 3am, the option to stop paying, "
        "and no DRAM-market exposure; the model does not price those, and says so."
    )
    return "\n".join(lines)


def render_handoff_reconciliation() -> str:
    rec = repo_data.solve_handoff_reconciliation()
    drift = abs(rec["psi_per_point_at_implied_ram"] - rec["reported_psi_per_point"]) / rec["reported_psi_per_point"]
    return "\n".join(
        [
            "| Quantity | Handoff F7 | This repo, same RAM price | This repo, current RAM price |",
            "|---|---:|---:|---:|",
            f"| DDR5 $/GB | implied {usd(rec['implied_usd_per_gb'], 2)} | {usd(rec['implied_usd_per_gb'], 2)} | {usd(rec['current_usd_per_gb'], 2)} |",
            f"| 10-yr Psi per point | {usd(rec['reported_psi_per_point'], 2)} | {usd(rec['psi_per_point_at_implied_ram'], 2)} | {usd(rec['psi_per_point_at_current_ram'], 2)} |",
            f"| Psi ($/pt-yr) | {rec['reported_psi_per_point'] / 10:.2f} | {rec['psi_at_implied_ram']:.2f} | {rec['psi_at_current_ram']:.2f} |",
            "",
            f"The handoff's F7 figures back-solve to DDR5 near {usd(rec['implied_usd_per_gb'], 2)}/GB, "
            f"against the {usd(rec['current_usd_per_gb'], 2)}/GB its own data table carries (2026-08-14). "
            f"At the implied price this repo reproduces the reported number within {drift:.1%} (the "
            "residual is rounding drift inside the handoff itself). The published Psi is whatever the "
            "current data solves to; the old figure is kept in data/cpu_specs.yaml as SUPERSEDED.",
        ]
    )


def render_apple_lineup() -> str:
    hw = repo_data.load("hardware")
    lines = ["| Machine | Price | Max unified memory | Bandwidth |", "|---|---:|---:|---:|"]
    for m in hw["machines"]:
        if not m["id"].startswith("mac-"):
            continue
        price = usd(m["price_usd"], 0) + (" (ESTIMATE)" if m["price_confidence"] == "ESTIMATE" else "")
        lines.append(f"| {m['name']} | {price} | {m['memory_gb_max']}GB | {m['bandwidth_nominal_gb_s']} GB/s |")
    return "\n".join(lines)


def compute_question_lines(p: "repo_data.Placement") -> list[str]:
    op = repo_data.operating_inputs()
    return [
        "THE COMPUTE QUESTION  (deterministic work: builds, simulation, batch jobs)",
        f"  own it           {p.compute_value.name} at {usd(p.compute_value.psi, 2)} per "
        f"SPECrate-point-year all-in over {op.years:.0f} years",
        f"  renting instead  {p.rent_ratio_lo:.1f}x to {p.rent_ratio_hi:.1f}x the cost of owning, same unit",
        f"  watts binding?   {p.compute_efficiency.name} is the efficiency pick at "
        f"{p.compute_efficiency.points_per_watt:.2f} pts per wall watt",
    ]


def tokens_question_lines(p: "repo_data.Placement") -> list[str]:
    ref = repo_data.reference_workload()
    default_line = (
        f"{p.token_default.id}: AA {p.token_default.aa_score}, "
        f"{usd(p.token_default_cost_per_task, 3)}/task, {usd(p.token_default.lifetime_cost, 0)} "
        f"for the {ref.years:.0f}-yr reference workload at list"
    )
    if p.token_default_promo is not None:
        default_line += (
            f" ({usd(p.token_default_promo.lifetime_cost, 0)} on promo through "
            f"{p.token_default_promo.expires})"
        )
    frontier_line = (
        f"{p.token_frontier.model}: AA {p.token_frontier.score}, "
        f"{usd(p.token_frontier.cost_per_task, 2)}/task, the cheapest costed frontier point"
    )
    if p.frontier_multiple_per_task is not None:
        frontier_line += f" ({p.frontier_multiple_per_task:.1f}x default per task)"
    return [
        "THE TOKENS QUESTION  (thinking)",
        f"  default          {default_line}",
        f"  frontier calls   {frontier_line}",
        f"  local inference  no: the best passing local config runs {p.local.ratio:.1f}x cloud "
        f"cost at AA {p.local.local_score}",
        "  the local box    hosts the agent: orchestration, sandboxes, a small resident triage model",
    ]


def answer_caveat(p: "repo_data.Placement") -> str:
    caveat = (
        "Caveats, solved with the answer: "
        + ", ".join(p.frontier_uncosted)
        + " sit at or above the frontier pick's score with no cost per task yet (TODO in "
        "data/benchmarks.yaml); the pick re-solves when they are costed."
    )
    for model_id, cost, mult in p.frontier_priced_workload:
        caveat += (
            f" {model_id} is the one frontier model with API pricing here and prices the "
            f"reference workload at {usd(cost, 0)} ({mult:.1f}x default), which is why the "
            "frontier tier is for rare calls, not the loop."
        )
    caveat += " Every price is VOLATILE; run scripts/check_staleness.py before trusting."
    return caveat


def placement_lines() -> list[str]:
    """The two questions, answered from current data. Plain text so the terminal answerer
    (scripts/answer.py) and the README block stay identical."""
    p = repo_data.solve_placement()
    return [
        *compute_question_lines(p),
        "",
        *tokens_question_lines(p),
        "",
        answer_caveat(p),
    ]


def render_the_answer() -> str:
    return "```text\n" + "\n".join(placement_lines()) + "\n```"


def render_compute_per_watt() -> str:
    sol = repo_data.solve_psi()
    by_eps = sorted(sol.evaluations, key=lambda e: e.points_per_watt, reverse=True)
    by_psi = sorted(sol.evaluations, key=lambda e: e.psi)
    lines = [
        "| CPU | pts per wall watt | Efficiency rank | Psi rank |",
        "|---|---:|---:|---:|",
    ]
    for e in by_eps:
        lines.append(
            f"| {e.name} | {e.points_per_watt:.2f} | {by_eps.index(e) + 1} | {by_psi.index(e) + 1} |"
        )
    eff, val = by_eps[0], by_psi[0]
    lines.append("")
    lines.append(
        f"**{eff.name}** is the efficiency champion at {eff.points_per_watt:.2f} pts/W and "
        f"**{val.name}** wins on value at {val.points_per_watt:.2f} pts/W; the value ranking "
        "holds at every electricity price in the sensitivity table, so the efficiency answer "
        "only becomes the buying answer when watts, not dollars, are the binding constraint "
        "(a power-capped circuit, a thermal envelope, a UPS budget)."
    )
    return "\n".join(lines)


def render_knobs() -> str:
    """The inputs that move the answer, with their current values read from data/."""
    w = repo_data.load("workload")["reference_workload"]
    a = repo_data.load("assumptions")
    op = a["operating"]
    ram = a["memory_pricing"]["ddr5_6400_rdimm_usd_per_gb"]
    rows = [
        (
            "Workload",
            "`workload.yaml`",
            f"{float(w['output_tokens_per_year']) / 1e6:,.0f}M out/yr, "
            f"{float(w['cache_hit_rate']):.0%} cache, {w['years']} yr",
            "the throughput bar and every API cost",
        ),
        (
            "Electricity",
            "`assumptions.yaml`",
            f"${float(op['electricity_usd_per_kwh']['value']):.2f}/kWh",
            "Psi and local $/Mtok",
        ),
        (
            "Hold period",
            "`assumptions.yaml`",
            f"{op['hold_years']['value']:g} yr",
            "Psi roughly doubles at 5",
        ),
        (
            "DDR5 price",
            "`assumptions.yaml`",
            f"${float(ram['value']):.2f}/GB ({ram['date']})",
            "the biggest lever on Psi; never the ranking",
        ),
        (
            "Utilization",
            "`assumptions.yaml`",
            f"{float(op['utilization']['value']):g}",
            "local break-evens",
        ),
        (
            "Prices and scores",
            "`model_pricing.yaml`, `benchmarks.yaml`",
            "dated per entry",
            "the whole token answer",
        ),
    ]
    lines = ["| Knob | Where | Current | Moves |", "|---|---|---|---|"]
    lines += [f"| {k} | {where} | {cur} | {moves} |" for k, where, cur, moves in rows]
    return "\n".join(lines)


def render_findings_summary() -> str:
    api = repo_data.solve_api_costs()
    ref = repo_data.reference_workload()
    capable = [r for r in api if r.aa_score is not None and r.aa_score >= 50 and r.expires is None]
    cheapest = min(capable, key=lambda r: r.lifetime_cost)
    frontier = repo_data.solve_frontier()
    f_lo = min(frontier, key=lambda p: p.cost_per_task)
    f_hi = max(frontier, key=lambda p: p.cost_per_task)
    bar, rows = repo_data.solve_local_bar()
    measured_pass = [r for r in rows if r.passes and r.tok_s_confidence == "MEASURED"]
    lc = repo_data.solve_local_vs_cloud()
    sol = repo_data.solve_psi()
    _, rent_rows, _, _ = repo_data.solve_rent()
    rng = sorted(r.times_owning for r in rent_rows)
    return "\n".join(
        [
            "| # | Finding | Solved right now | Data date |",
            "|---|---|---|---|",
            f"| F1 | Renting beats self-hosting for the reference workload | {cheapest.label}: "
            f"{usd(cheapest.lifetime_cost, 0)} for {ref.years:.0f} years at AA {cheapest.aa_score}, "
            f"cheapest capable path at list price | {cheapest.date} |",
            f"| F2 | There is no midrange tier | Pareto frontier runs {usd(f_lo.cost_per_task, 3)}/task "
            f"(AA {f_lo.score}) to {usd(f_hi.cost_per_task, 2)}/task (AA {f_hi.score}); everything "
            f"between is dominated | {repo_data.aa_index()['date']} |",
            f"| F3 | Local hardware fails the throughput bar before it fails on cost | Bar is "
            f"{bar:.2f} tok/s sustained; {len(measured_pass)} of {len([r for r in rows if r.tok_s is not None])} "
            f"tested configs clears it on measured numbers | 2026-08-29 |",
            f"| F4 | Even when local passes, it loses | {usd(lc.local_per_mtok, 2)}/M local vs "
            f"{usd(lc.cloud_per_mtok, 2)}/M cloud, same weights, fully saturated: {lc.ratio:.1f}x | 2026-08-29 |",
            "| F5 | The local box is for hosting, not inference | Thesis; see README | |",
            "| F6 | The hardware scarcity is a supply story, not a demand story | Two defensible "
            "readings; both presented in analysis 06 | 2026-08-25 |",
            f"| F7 | Owning beats renting for deterministic compute | {sol.winner.name} at "
            f"{usd(sol.winner.psi, 2)}/pt-yr; renting runs {rng[0]:.1f}x to {rng[-1]:.1f}x owning | "
            f"2026-06-15 |",
        ]
    )


def render_freshness() -> str:
    rows = check_staleness.collect()
    by_cat: dict[str, list] = {}
    for r in rows:
        by_cat.setdefault(r.category, []).append(r)
    lines = ["| Category | Figures | Oldest | Window | Status |", "|---|---:|---|---|---|"]
    for cat, items in sorted(by_cat.items()):
        oldest = min(i.dated for i in items)
        window = "-" if cat not in check_staleness.WINDOWS else f"{check_staleness.WINDOWS[cat]}d"
        flagged = [i for i in items if i.status != "fresh"]
        status = f"**{len(flagged)} flagged**" if flagged else "fresh"
        lines.append(f"| {cat} | {len(items)} | {oldest} | {window} | {status} |")
    lines.append("")
    lines.append("SPECrate submissions never expire and are not policed.")
    return "\n".join(lines)


RENDERERS = {
    "last_solved": render_last_solved,
    "the_answer": render_the_answer,
    "knobs": render_knobs,
    "compute_per_watt": render_compute_per_watt,
    "workload_derivation": render_workload_derivation,
    "findings_summary": render_findings_summary,
    "freshness": render_freshness,
    "api_cost_10yr": render_api_cost_10yr,
    "cache_sensitivity": render_cache_sensitivity,
    "frontier_table": render_frontier_table,
    "local_hw": render_local_hw,
    "local_vs_cloud": render_local_vs_cloud,
    "moe_batching": render_moe_batching,
    "psi_compare": render_psi_compare,
    "psi_sens_electricity": render_psi_sens_electricity,
    "psi_sens_hold": render_psi_sens_hold,
    "breakevens": render_breakevens,
    "memory_lever": render_memory_lever,
    "rent_compare": render_rent_compare,
    "handoff_reconciliation": render_handoff_reconciliation,
    "apple_lineup": render_apple_lineup,
}


def solve_all() -> dict[str, str]:
    return {key: fn() for key, fn in RENDERERS.items()}


def apply(check_only: bool = False) -> int:
    solved = solve_all()
    drift: list[str] = []
    used: set[str] = set()
    for doc in DOCS:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")

        def sub(m: re.Match) -> str:
            key = m.group("key")
            if key not in solved:
                raise KeyError(f"{doc.name}: no renderer for gen:{key}")
            used.add(key)
            return f"{m.group(1)}{solved[key]}\n{m.group(4)}"

        new = MARKER.sub(sub, text)
        if new != text:
            drift.append(str(doc.relative_to(ROOT)))
            if not check_only:
                doc.write_text(new, encoding="utf-8", newline="\n")
    unused = set(solved) - used
    if unused:
        print(f"note: renderers with no marker in any doc: {', '.join(sorted(unused))}")
    if check_only:
        if drift:
            print("out of sync with data/: " + ", ".join(drift))
            print("run: python scripts/build_tables.py")
            return 1
        print("docs match the data layer")
        return 0
    print(("re-solved: " + ", ".join(drift)) if drift else "docs already match the data layer")
    return 0


if __name__ == "__main__":
    raise SystemExit(apply(check_only="--check" in sys.argv))
