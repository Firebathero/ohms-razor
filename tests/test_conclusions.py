"""The published conclusions, asserted as relations over whatever data/ currently holds.

None of these pin a dollar figure. When a data refresh makes one fail, the world changed
and a conclusion genuinely flipped: do not weaken the test, update the data, re-solve the
docs, and record the reversal in the README changelog. That event is the most valuable
thing this repo can publish.
"""

from __future__ import annotations

from datetime import date

import pytest

import repo_data


# ---------------------------------------------------------------- the throughput bar

def test_reference_rate_is_the_headline_constraint():
    ref = repo_data.reference_workload()
    assert 5 < ref.required_tok_s < 50  # sanity: the bar is set by workload.yaml, not code


def test_dense_70b_fails_everywhere_and_one_moe_config_passes():
    """F3: the bar disqualifies every dense-70B configuration in the data; the only
    measured pass is an MoE on the high-memory box."""
    _, rows = repo_data.solve_local_bar()
    dense = [r for r in rows if r.model and r.model.startswith("dense-70b")]
    assert dense and all(not r.passes for r in dense)
    measured_passes = [r for r in rows if r.passes and r.tok_s_confidence == "MEASURED"]
    assert len(measured_passes) >= 1
    assert all("gpt-oss-120b" in r.model for r in measured_passes)


def test_capacity_fails_before_throughput_on_the_smallest_box():
    _, rows = repo_data.solve_local_bar()
    m6 = [r for r in rows if "M6" in r.machine]
    assert m6 and all(not r.fits for r in m6)


# ---------------------------------------------------------------- F1: renting wins

def test_glm_is_the_cheapest_capable_volume_path_at_list():
    """Cheapest path among capable models (score >= 50) at list price, promos excluded.
    Winning at list is what makes the conclusion robust to the promo expiring."""
    rows = [r for r in repo_data.solve_api_costs() if r.aa_score is not None and r.aa_score >= 50]
    listed = [r for r in rows if r.expires is None]
    cheapest = min(listed, key=lambda r: r.lifetime_cost)
    assert cheapest.id == "glm-5.3-flash"
    others = [r for r in listed if r.id != cheapest.id]
    assert all(cheapest.lifetime_cost < r.lifetime_cost for r in others)
    top_score = max(r.aa_score for r in listed)
    assert cheapest.aa_score >= top_score - 3  # and it is near the top on capability


def test_glm_beats_deepseek_at_every_cache_ratio():
    """The obvious objection to F1: DeepSeek's 4x cheaper cache. It never adds up."""
    sweep = repo_data.cache_sensitivity(
        "glm-5.3-flash", "deepseek-v4-flash", [i / 20 for i in range(21)]
    )
    assert all(glm < ds for _, glm, ds in sweep)


def test_cache_advantage_is_bounded_by_the_output_gap():
    ref = repo_data.reference_workload()
    models = {m.id: m for m in repo_data.priced_models()}
    glm, ds = models["glm-5.3-flash"], models["deepseek-v4-flash"]
    max_cache_advantage = ref.lifetime.input_tokens * (
        glm.pricing.cached_input_per_mtok - ds.pricing.cached_input_per_mtok
    )
    output_gap = ref.lifetime.output_tokens * (ds.pricing.output_per_mtok - glm.pricing.output_per_mtok)
    assert max_cache_advantage < output_gap


def test_promo_rows_follow_the_calendar():
    before = repo_data.solve_api_costs(today=date(2026, 9, 1))
    after = repo_data.solve_api_costs(today=date(2026, 12, 1))
    assert any(r.expires is not None for r in before)
    assert all(r.expires is None for r in after)


# ---------------------------------------------------------------- F2: the cliff

def test_frontier_holds_glm_and_nothing_dominates_it():
    points = repo_data.solve_frontier()
    glm = next(p for p in points if p.model == "glm-5.3-flash")
    assert glm.on_frontier
    assert all(p.on_frontier for p in points if p.cost_per_task == min(q.cost_per_task for q in points))


# ---------------------------------------------------------------- F4: local loses anyway

def test_local_loses_even_fully_saturated():
    lc = repo_data.solve_local_vs_cloud()
    assert lc.ratio > 1.0
    assert lc.breakeven_utilization > 1.0  # cannot break even at any duty cycle
    assert lc.local_score is not None and lc.volume_tier_score is not None
    assert lc.local_score < lc.volume_tier_score  # more expensive and less capable


# ---------------------------------------------------------------- Model 3 consequences

def test_sparsity_ratio_is_large_and_batching_amortizes():
    R, curve = repo_data.solve_moe_batching()
    assert R > 10
    aggregates = [r.aggregate_bound_tok_s for r in curve]
    assert aggregates == sorted(aggregates)
    assert curve[0].resident_params_b_per_stream > 10 * curve[-1].resident_params_b_per_stream


# ---------------------------------------------------------------- F7: Psi

def test_winner_by_psi_and_winner_by_watts_differ():
    """Efficiency and value are different questions; if this ever fails, that talking
    point comes out of the docs."""
    sol = repo_data.solve_psi()
    assert sol.winner.psi == min(e.psi for e in sol.evaluations)
    assert sol.best_points_per_watt.name != sol.winner.name


def test_ranking_survives_sigma():
    """sigma is applied identically to every candidate, so the ranking must not move when
    it does."""
    base = [e.name for e in sorted(repo_data.solve_psi().evaluations, key=lambda e: e.psi)]
    for sigma in (0.40, 0.60):
        cpus = repo_data.cpu_inputs()
        op = repo_data.operating_inputs()
        from models.hardware_psi import evaluate

        evs = [evaluate(c.__class__(**{**c.__dict__, "sigma": sigma}), op) for c in cpus]
        assert [e.name for e in sorted(evs, key=lambda e: e.psi)] == base


def test_ranking_survives_electricity_and_hold():
    base = [e.name for e in sorted(repo_data.solve_psi().evaluations, key=lambda e: e.psi)]
    for r in (0.10, 0.40, 0.60):
        sol = repo_data.solve_psi(repo_data.operating_inputs(electricity_usd_per_kwh=r))
        assert sorted(sol.evaluations, key=lambda e: e.psi)[0].name == base[0]
    for y in (3, 5, 12):
        sol = repo_data.solve_psi(repo_data.operating_inputs(years=float(y)))
        assert sorted(sol.evaluations, key=lambda e: e.psi)[0].name == base[0]


def test_memory_moves_the_level_not_the_ranking():
    lever = repo_data.solve_memory_lever([8.0, 15.0, 25.0, 35.7, 45.0])
    psis = [p for _, _, p in lever]
    assert psis == sorted(psis)  # monotone in RAM price
    for g in (8.0, 45.0):
        assert repo_data.solve_psi(usd_per_gb=g).winner.name == repo_data.solve_psi().winner.name


def test_owning_beats_renting_on_every_offer():
    _, rent_rows, boxes, fleet = repo_data.solve_rent()
    assert all(r.times_owning > 1.0 for r in rent_rows)
    assert boxes > 1.0
    own = repo_data.solve_psi().winner
    assert fleet > own.tco_usd / repo_data.operating_inputs().years  # renting costs more per year


def test_handoff_reconciliation_closes():
    """The F7 discrepancy is explained, not mysterious: at the implied RAM price the model
    lands within the handoff's own rounding drift of the reported figure."""
    rec = repo_data.solve_handoff_reconciliation()
    assert rec["implied_usd_per_gb"] < rec["current_usd_per_gb"]
    drift = abs(rec["psi_per_point_at_implied_ram"] - rec["reported_psi_per_point"])
    assert drift / rec["reported_psi_per_point"] < 0.01


# ---------------------------------------------------------------- data hygiene

def test_every_dated_figure_carries_confidence():
    for m in repo_data.priced_models():
        assert m.confidence
        assert m.date is not None
    for c in repo_data.load("cpu_specs")["candidates"]:
        assert c["specrate_2p"]["confidence"]
        assert c["phi"]["confidence"]
        assert c["price_confidence"]
    for machine in repo_data.load("hardware")["machines"]:
        assert machine["price_confidence"]


def test_estimates_stay_estimates():
    """The two most important non-measured numbers keep their tags (agent prompt rule:
    never upgrade an estimate to a fact)."""
    spec = repo_data.load("cpu_specs")
    assert spec["calibration"]["sigma_1p_scaling"]["confidence"] == "DERIVED"
    phi_9965 = next(c for c in spec["candidates"] if c["id"] == "epyc-9965")["phi"]
    assert phi_9965["confidence"] == "ESTIMATE"
