"""Loads data/*.yaml into model inputs and solves every published figure.

This is the only place numbers leave the data layer. build_tables.py renders what these
solvers return; the conclusion tests assert relations over the same returns. Nothing here
hard-codes a result; if it is not in data/, it is computed.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import MTOK, SECONDS_PER_YEAR  # noqa: E402
from models.token_cost import Pricing, Workload, api_cost, cost_at_cache_ratio, effective_cost, peak_fraction  # noqa: E402
from models.local_throughput import decode_rate_upper_bound, fits_in_memory, required_sustained_rate  # noqa: E402
from models.moe_economics import MoeGeometry, batched_decode_rate_upper_bound, sparsity_ratio  # noqa: E402
from models.local_cost import breakeven_utilization, lifetime_energy_cost, local_cost_per_mtok  # noqa: E402
from models.hardware_psi import (  # noqa: E402
    CpuInputs,
    Evaluation,
    OperatingInputs,
    cpu_price_to_match_psi,
    evaluate,
    rent_psi,
)

DATA = ROOT / "data"


def load(name: str) -> dict[str, Any]:
    with open(DATA / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------- workload

@dataclass(frozen=True)
class ReferenceWorkload:
    per_year: Workload
    lifetime: Workload
    years: float
    required_tok_s: float


def reference_workload() -> ReferenceWorkload:
    w = load("workload")["reference_workload"]
    years = float(w["years"])
    per_year = Workload(
        output_tokens=float(w["output_tokens_per_year"]),
        input_tokens=float(w["input_tokens_per_year"]),
        cache_hit_rate=float(w["cache_hit_rate"]),
    )
    lifetime = Workload(
        output_tokens=per_year.output_tokens * years,
        input_tokens=per_year.input_tokens * years,
        cache_hit_rate=per_year.cache_hit_rate,
    )
    return ReferenceWorkload(
        per_year=per_year,
        lifetime=lifetime,
        years=years,
        required_tok_s=required_sustained_rate(per_year.output_tokens),
    )


# ---------------------------------------------------------------- api pricing

@dataclass(frozen=True)
class PricedModel:
    id: str
    vendor: str
    tier: str
    pricing: Pricing
    date: date
    confidence: str
    promo: dict[str, Any] | None
    peak: dict[str, Any] | None
    notes: str | None


def priced_models() -> list[PricedModel]:
    out = []
    for m in load("model_pricing")["models"]:
        out.append(
            PricedModel(
                id=m["id"],
                vendor=m["vendor"],
                tier=m["tier"],
                pricing=Pricing(
                    input_per_mtok=float(m["input_per_mtok"]),
                    cached_input_per_mtok=(
                        None if m["cached_input_per_mtok"] is None else float(m["cached_input_per_mtok"])
                    ),
                    output_per_mtok=float(m["output_per_mtok"]),
                ),
                date=m["date"],
                confidence=m["confidence"],
                promo=m.get("promo"),
                peak=m.get("peak_pricing"),
                notes=m.get("notes"),
            )
        )
    return out


@dataclass(frozen=True)
class ApiCostRow:
    id: str
    label: str
    lifetime_cost: float
    aa_score: int | None
    date: date
    confidence: str
    expires: date | None


def peak_exposure(peak: dict[str, Any]) -> tuple[float, float]:
    """(f_peak, m_peak) for a 24/7 loop against the model's peak windows."""
    hours = 0.0
    for window in peak["windows_utc"]:
        start, end = window.split("-")
        h0 = int(start.split(":")[0]) + int(start.split(":")[1]) / 60.0
        h1 = int(end.split(":")[0]) + int(end.split(":")[1]) / 60.0
        hours += h1 - h0
    return peak_fraction(hours), float(peak["multiplier"])


def solve_api_costs(today: date | None = None) -> list[ApiCostRow]:
    """Ten-year (hold-period) API cost of the reference workload for every priced path:
    list price, active promo, off-peak-only, and unscheduled 24/7 peak exposure."""
    ref = reference_workload()
    scores = {e["model"]: e["score"] for e in aa_index()["entries"]}
    today = today or date.today()
    rows: list[ApiCostRow] = []
    for m in priced_models():
        score = scores.get(m.id, scores.get(m.id.removesuffix("-cloud")))
        base = api_cost(m.pricing, ref.lifetime)
        if m.peak is None:
            rows.append(ApiCostRow(m.id, f"{m.id} (list)", base, score, m.date, m.confidence, None))
        else:
            f_peak, mult = peak_exposure(m.peak)
            rows.append(
                ApiCostRow(m.id, f"{m.id} (off-peak only)", base, score, m.date, m.confidence, None)
            )
            rows.append(
                ApiCostRow(
                    m.id,
                    f"{m.id} (24/7, {f_peak:.0%} peak)",
                    effective_cost(base, f_peak, mult),
                    score,
                    m.date,
                    m.confidence,
                    None,
                )
            )
        if m.promo is not None and today <= m.promo["expires"]:
            promo_cost = api_cost(m.pricing.scaled(float(m.promo["multiplier"])), ref.lifetime)
            rows.append(
                ApiCostRow(
                    m.id,
                    f"{m.id} (promo)",
                    promo_cost,
                    score,
                    m.date,
                    "EXPIRES",
                    m.promo["expires"],
                )
            )
    return sorted(rows, key=lambda r: r.lifetime_cost)


def cache_sensitivity(id_a: str, id_b: str, ratios: list[float]) -> list[tuple[float, float, float]]:
    """Lifetime cost of both models across cache hit ratios. Answers 'does the cheaper
    cache rate ever flip the ranking'."""
    ref = reference_workload()
    models = {m.id: m for m in priced_models()}
    a, b = models[id_a], models[id_b]
    return [
        (
            h,
            cost_at_cache_ratio(a.pricing, ref.lifetime, h),
            cost_at_cache_ratio(b.pricing, ref.lifetime, h),
        )
        for h in ratios
    ]


# ---------------------------------------------------------------- benchmarks

def aa_index() -> dict[str, Any]:
    return load("benchmarks")["aa_intelligence_index"]


@dataclass(frozen=True)
class FrontierPoint:
    model: str
    score: int
    cost_per_task: float
    on_frontier: bool


def solve_frontier() -> list[FrontierPoint]:
    """Pareto frontier over the fully costed index entries: a point is on the frontier if
    nothing scores at least as high for less money."""
    costed = [
        (e["model"], int(e["score"]), float(e["cost_per_task_usd"]))
        for e in aa_index()["entries"]
        if e["cost_per_task_usd"] is not None
    ]
    points = []
    for model, score, cost in costed:
        dominated = any(
            other_score >= score and other_cost < cost
            or (other_score > score and other_cost <= cost)
            for _, other_score, other_cost in costed
            if _ != model
        )
        points.append(FrontierPoint(model, score, cost, not dominated))
    return sorted(points, key=lambda p: p.cost_per_task)


# ---------------------------------------------------------------- local hardware

@dataclass(frozen=True)
class LocalBarRow:
    machine: str
    price_usd: float | None
    price_confidence: str
    bandwidth_label: str
    memory_gb: int
    model: str | None
    tok_s: float | None
    tok_s_confidence: str | None
    bound_tok_s: float | None
    fits: bool
    passes: bool
    verdict: str


def _quant_bytes() -> dict[str, float]:
    return {q["quant"]: float(q["bytes"]) for q in load("hardware")["quant_bytes_per_param"]}


def _model_params() -> dict[str, dict[str, Any]]:
    return {m["id"]: m for m in load("hardware")["model_params"]}


def solve_local_bar() -> tuple[float, list[LocalBarRow]]:
    """The sustained-rate constraint against every machine/model pairing in the data."""
    ref = reference_workload()
    bar = ref.required_tok_s
    hw = load("hardware")
    qb = _quant_bytes()
    params = _model_params()
    rows: list[LocalBarRow] = []
    for machine in hw["machines"]:
        bw_eff = machine.get("bandwidth_effective_gb_s")
        bw_label = f"{machine['bandwidth_nominal_gb_s']} nominal"
        if bw_eff:
            bw_label += f" / {bw_eff} measured"
        entries = machine.get("throughput") or [None]
        for t in entries:
            if t is None:
                # No throughput entry: the machine is judged on capacity alone against the
                # dense-70b reference model.
                p = params["dense-70b"]
                fits = fits_in_memory(float(p["total_params_b"]), qb["q4"], machine["memory_gb_max"])
                rows.append(
                    LocalBarRow(
                        machine=machine["name"],
                        price_usd=machine.get("price_usd"),
                        price_confidence=machine.get("price_confidence", ""),
                        bandwidth_label=bw_label,
                        memory_gb=machine["memory_gb_max"],
                        model="dense-70b q4",
                        tok_s=None,
                        tok_s_confidence=None,
                        bound_tok_s=None,
                        fits=fits,
                        passes=False,
                        verdict="fails on capacity" if not fits else "untested",
                    )
                )
                continue
            p = params[t["model"]]
            bytes_pp = qb[t["quant"]]
            fits = fits_in_memory(float(p["total_params_b"]), bytes_pp, machine["memory_gb_max"])
            bound = (
                decode_rate_upper_bound(float(bw_eff), float(p["active_params_b"]), bytes_pp)
                if bw_eff
                else None
            )
            tok_s = float(t["tok_s"])
            passes = fits and tok_s >= bar
            if not fits:
                verdict = "fails on capacity"
            elif passes:
                verdict = "passes"
            else:
                verdict = "fails the bar"
            rows.append(
                LocalBarRow(
                    machine=machine["name"],
                    price_usd=machine.get("price_usd"),
                    price_confidence=machine.get("price_confidence", ""),
                    bandwidth_label=bw_label,
                    memory_gb=machine["memory_gb_max"],
                    model=f"{t['model']} {t['quant']}",
                    tok_s=tok_s,
                    tok_s_confidence=t.get("confidence"),
                    bound_tok_s=bound,
                    fits=fits,
                    passes=passes,
                    verdict=verdict,
                )
            )
    return bar, rows


@dataclass(frozen=True)
class LocalVsCloud:
    machine: str
    model: str
    years: float
    capex_usd: float
    energy_usd: float
    total_usd: float
    lifetime_mtok: float
    local_per_mtok: float
    cloud_per_mtok: float
    ratio: float
    breakeven_utilization: float
    local_score: int | None
    volume_tier: str
    volume_tier_score: int | None
    volume_tier_cost_per_task: float | None


def volume_tier_pick(today: date | None = None) -> ApiCostRow:
    """Whichever listed path is cheapest while clearing the capability floor. Solved, never
    named: if a new model undercuts the incumbent, this returns the new model and every
    table and narrative that references "the volume tier" follows it."""
    listed = [
        r for r in solve_api_costs(today=today)
        if r.expires is None and r.aa_score is not None and r.aa_score >= CAPABLE_SCORE_FLOOR
    ]
    if not listed:
        raise ValueError(
            f"no listed model clears the capability floor of {CAPABLE_SCORE_FLOOR}; "
            "either the floor is wrong or data/model_pricing.yaml needs a survey"
        )
    return min(listed, key=lambda r: r.lifetime_cost)


def solve_local_vs_cloud() -> LocalVsCloud:
    """F4: the saturated best-case local box against the cheapest cloud host of the same
    weights, plus the capability comparison against the volume API tier."""
    hw = load("hardware")
    sc = hw["local_box_scenario"]
    machine = next(m for m in hw["machines"] if m["id"] == sc["machine"])
    tok = next(t for t in machine["throughput"] if t["model"] == sc["model"])
    op = load("assumptions")["operating"]
    r = float(op["electricity_usd_per_kwh"]["value"])
    cooling = float(op["cooling_overhead"]["value"])
    years = float(sc["years"])
    u = float(sc["utilization"])
    capex = float(machine["price_usd"])
    wall = float(sc["wall_draw_w"])
    tok_s = float(tok["tok_s"])
    energy = lifetime_energy_cost(wall, cooling, r, years)
    per_mtok = local_cost_per_mtok(capex, wall, cooling, r, years, tok_s, u)
    cloud = next(m for m in priced_models() if m.id == f"{sc['model']}-cloud")
    scores = {e["model"]: e["score"] for e in aa_index()["entries"]}
    costs = {e["model"]: e["cost_per_task_usd"] for e in aa_index()["entries"]}
    volume = volume_tier_pick()
    return LocalVsCloud(
        machine=machine["name"],
        model=sc["model"],
        years=years,
        capex_usd=capex,
        energy_usd=energy,
        total_usd=capex + energy,
        lifetime_mtok=tok_s * SECONDS_PER_YEAR * years * u / MTOK,
        local_per_mtok=per_mtok,
        cloud_per_mtok=cloud.pricing.output_per_mtok,
        ratio=per_mtok / cloud.pricing.output_per_mtok,
        breakeven_utilization=breakeven_utilization(
            capex + energy, cloud.pricing.output_per_mtok, tok_s, years
        ),
        local_score=scores.get(sc["model"]),
        volume_tier=volume.id,
        volume_tier_score=volume.aa_score,
        volume_tier_cost_per_task=costs.get(volume.id),
    )


# ---------------------------------------------------------------- moe

def moe_geometry(model_id: str) -> MoeGeometry:
    p = _model_params()[model_id]
    return MoeGeometry(
        total_params_b=float(p["total_params_b"]),
        active_params_b=float(p["active_params_b"]),
        n_experts=int(p["n_experts"]),
        experts_per_token=int(p["experts_per_token"]),
    )


@dataclass(frozen=True)
class BatchingRow:
    batch: int
    aggregate_bound_tok_s: float
    per_stream_bound_tok_s: float
    resident_params_b_per_stream: float


def solve_moe_batching(model_id: str | None = None, batches: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64)) -> tuple[float, list[BatchingRow]]:
    """R and the first-order batching curve for whichever model the local box scenario
    actually runs, on that machine's measured bandwidth. Not pinned to a model name: swap
    the scenario in data/hardware.yaml and this follows."""
    hw = load("hardware")
    model_id = model_id or hw["local_box_scenario"]["model"]
    geo = moe_geometry(model_id)
    machine = next(m for m in hw["machines"] if m["id"] == hw["local_box_scenario"]["machine"])
    bw = float(machine["bandwidth_effective_gb_s"])
    quant = next(t["quant"] for t in machine["throughput"] if t["model"] == model_id)
    bytes_pp = _quant_bytes()[quant]
    rows = []
    for b in batches:
        agg = batched_decode_rate_upper_bound(geo, bw, bytes_pp, b)
        rows.append(
            BatchingRow(
                batch=b,
                aggregate_bound_tok_s=agg,
                per_stream_bound_tok_s=agg / b,
                resident_params_b_per_stream=geo.total_params_b / b,
            )
        )
    return sparsity_ratio(geo.total_params_b, geo.active_params_b), rows


# ---------------------------------------------------------------- psi

def operating_inputs(**overrides: float) -> OperatingInputs:
    op = load("assumptions")["operating"]
    values = dict(
        years=float(op["hold_years"]["value"]),
        utilization=float(op["utilization"]["value"]),
        electricity_usd_per_kwh=float(op["electricity_usd_per_kwh"]["value"]),
        electricity_escalation=float(op["electricity_escalation"]["value"]),
        discount_rate=float(op["discount_rate"]["value"]),
        platform_draw_w=float(op["platform_draw_w"]["value"]),
        psu_efficiency=float(op["psu_efficiency"]["value"]),
        cooling_overhead=float(op["cooling_overhead"]["value"]),
        idle_draw_w=float(op["idle_draw_w"]["value"]),
        residual_value_usd=float(op["residual_value_usd"]["value"]),
    )
    values.update(overrides)
    return OperatingInputs(**values)


def memory_cost_usd(usd_per_gb: float | None = None) -> float:
    a = load("assumptions")
    slots = float(a["memory_config"]["dimm_slots_populated"]["value"])
    gb = float(a["memory_config"]["gb_per_dimm"]["value"])
    price = (
        float(a["memory_pricing"]["ddr5_6400_rdimm_usd_per_gb"]["value"])
        if usd_per_gb is None
        else usd_per_gb
    )
    return slots * gb * price


def non_cpu_capex(usd_per_gb: float | None = None) -> float:
    bom = sum(float(item["unit_usd"]) for item in load("assumptions")["server_bom"])
    return bom + memory_cost_usd(usd_per_gb)


def cpu_inputs(usd_per_gb: float | None = None) -> list[CpuInputs]:
    spec = load("cpu_specs")
    sigma = float(spec["calibration"]["sigma_1p_scaling"]["value"])
    rest = non_cpu_capex(usd_per_gb)
    return [
        CpuInputs(
            name=c["name"],
            specrate_2p=float(c["specrate_2p"]["value_used"]),
            sigma=sigma,
            phi=float(c["phi"]["value"]),
            ctdp_w=float(c["run_ctdp_w"]),
            cpu_price_usd=float(c["price_street_usd"]),
            non_cpu_capex_usd=rest,
        )
        for c in spec["candidates"]
    ]


@dataclass(frozen=True)
class PsiSolution:
    evaluations: list[Evaluation]
    winner: Evaluation
    best_points_per_watt: Evaluation


def solve_psi(op: OperatingInputs | None = None, usd_per_gb: float | None = None) -> PsiSolution:
    op = op or operating_inputs()
    evs = [evaluate(c, op) for c in cpu_inputs(usd_per_gb)]
    return PsiSolution(
        evaluations=evs,
        winner=min(evs, key=lambda e: e.psi),
        best_points_per_watt=max(evs, key=lambda e: e.points_per_watt),
    )


@dataclass(frozen=True)
class RentRow:
    name: str
    specrate_1p: float
    monthly_usd: float
    psi: float
    times_owning: float
    note: str


def solve_rent() -> tuple[Evaluation, list[RentRow], float, float]:
    """Owning vs Hetzner in the same unit, plus the fleet math."""
    sol = solve_psi()
    spec = load("cpu_specs")
    ref = {c["id"]: c for c in spec["reference_cpus"]}
    rows = []
    for offer in spec["rental_offers"]:
        r1p = float(ref[offer["cpu"]]["specrate_1p"]["value_used"])
        psi_r = rent_psi(float(offer["monthly_usd"]), r1p)
        rows.append(
            RentRow(
                name=offer["name"],
                specrate_1p=r1p,
                monthly_usd=float(offer["monthly_usd"]),
                psi=psi_r,
                times_owning=psi_r / sol.winner.psi,
                note=offer.get("note", ""),
            )
        )
    standard = rows[0]
    boxes_needed = sol.winner.work_rate / standard.specrate_1p
    fleet_per_year = boxes_needed * standard.monthly_usd * 12.0
    return sol.winner, rows, boxes_needed, fleet_per_year


def solve_tie_prices() -> list[tuple[str, float, float]]:
    """CPU price at which each loser ties the winner: (name, tie price, street price)."""
    op = operating_inputs()
    cpus = cpu_inputs()
    evs = {c.name: evaluate(c, op) for c in cpus}
    winner = min(evs.values(), key=lambda e: e.psi)
    out = []
    for c in cpus:
        if c.name == winner.name:
            continue
        out.append((c.name, cpu_price_to_match_psi(winner.psi, c, op), c.cpu_price_usd))
    return out


def solve_memory_lever(prices_per_gb: list[float]) -> list[tuple[float, float, float]]:
    """(usd_per_gb, memory cost, winner Psi) across RAM prices. Memory is identical across
    candidates so the ranking never moves; the level does."""
    out = []
    for g in prices_per_gb:
        sol = solve_psi(usd_per_gb=g)
        out.append((g, memory_cost_usd(g), sol.winner.psi))
    return out


def solve_handoff_reconciliation() -> dict[str, float]:
    """Back-solve the RAM price implied by the handoff's F7 figures and re-solve Psi at
    that price. Shows exactly why the published number moved."""
    spec = load("cpu_specs")
    reported = spec["handoff_reported"]["psi_per_point_10yr_epyc_9965"]
    tco_reported = float(reported["tco_10yr_usd"])
    op = operating_inputs()
    winner_name = solve_psi().winner.name
    cpu = next(c for c in cpu_inputs() if c.name == winner_name)
    ev = evaluate(cpu, op)
    bom = sum(float(item["unit_usd"]) for item in load("assumptions")["server_bom"])
    a = load("assumptions")
    total_gb = float(a["memory_config"]["dimm_slots_populated"]["value"]) * float(
        a["memory_config"]["gb_per_dimm"]["value"]
    )
    implied_memory = tco_reported - ev.energy_usd - cpu.cpu_price_usd - bom
    implied_per_gb = implied_memory / total_gb
    resolved = solve_psi(usd_per_gb=implied_per_gb).winner
    current = load("assumptions")["memory_pricing"]["ddr5_6400_rdimm_usd_per_gb"]
    return {
        "reported_psi_per_point": float(reported["value"]),
        "reported_tco": tco_reported,
        "implied_usd_per_gb": implied_per_gb,
        "current_usd_per_gb": float(current["value"]),
        "psi_at_implied_ram": resolved.psi,
        "psi_per_point_at_implied_ram": resolved.psi * op.years,
        "psi_at_current_ram": ev.psi,
        "psi_per_point_at_current_ram": ev.psi * op.years,
    }


# ---------------------------------------------------------------- the two questions

@dataclass(frozen=True)
class Placement:
    """The repo's current answer to the two modern questions, solved from data/."""

    compute_value: Evaluation            # what to buy for deterministic work
    compute_efficiency: Evaluation       # what to buy when watts are the binding constraint
    rent_ratio_lo: float
    rent_ratio_hi: float
    token_default: ApiCostRow            # cheapest capable listed path
    token_default_cost_per_task: float | None
    token_default_promo: ApiCostRow | None
    token_frontier: FrontierPoint        # highest-score costed point, cheapest on ties
    frontier_multiple_per_task: float | None
    frontier_uncosted: list[str]         # scored at or above the pick, no cost per task yet
    frontier_priced_workload: list[tuple[str, float, float]]  # (id, workload cost, x default)
    local: LocalVsCloud


CAPABLE_SCORE_FLOOR = 50  # DEFINITION: a volume-tier model must be near-frontier to count


def solve_placement(today: date | None = None) -> Placement:
    psi_sol = solve_psi()
    _, rent_rows, _, _ = solve_rent()
    ratios = sorted(r.times_owning for r in rent_rows)

    api = solve_api_costs(today=today)
    default = volume_tier_pick(today=today)
    promo = next((r for r in api if r.id == default.id and r.expires is not None), None)
    costs = {e["model"]: e["cost_per_task_usd"] for e in aa_index()["entries"]}

    points = solve_frontier()
    frontier = max(points, key=lambda p: (p.score, -p.cost_per_task))
    default_task = costs.get(default.id)
    multiple = frontier.cost_per_task / default_task if default_task else None
    uncosted = [
        e["model"]
        for e in aa_index()["entries"]
        if e["cost_per_task_usd"] is None and e["score"] >= frontier.score
    ]
    priced_frontier = [
        (m.id, row.lifetime_cost, row.lifetime_cost / default.lifetime_cost)
        for m in priced_models()
        if m.tier == "frontier"
        for row in api
        if row.id == m.id and row.expires is None
    ]
    return Placement(
        compute_value=psi_sol.winner,
        compute_efficiency=psi_sol.best_points_per_watt,
        rent_ratio_lo=ratios[0],
        rent_ratio_hi=ratios[-1],
        token_default=default,
        token_default_cost_per_task=default_task,
        token_default_promo=promo,
        token_frontier=frontier,
        frontier_multiple_per_task=multiple,
        frontier_uncosted=uncosted,
        frontier_priced_workload=priced_frontier,
        local=solve_local_vs_cloud(),
    )


def solve_hetzner_cloud_moves() -> list[tuple[str, float, float, float]]:
    """(instance, old EUR, new EUR, percent increase) computed from raw prices."""
    rep = load("cpu_specs")["hetzner_cloud_repricing"]
    return [
        (i["id"], float(i["old_eur"]), float(i["new_eur"]), (float(i["new_eur"]) / float(i["old_eur"]) - 1.0) * 100.0)
        for i in rep["instances"]
    ]
