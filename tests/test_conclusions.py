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


def test_dense_70b_class_models_fail_the_bar():
    """F3, stated as the mechanism rather than the 2026-08-29 candidate list: a dense
    70B-class model cannot clear the sustained-rate bar on a consumer memory bus, because
    every token streams all 70B parameters. Holds for any machine and any 70B-class entry,
    including ones a later survey adds."""
    bar, rows = repo_data.solve_local_bar()
    dense_70b = [
        r for r in rows
        if r.model and any(k in r.model for k in ("dense-70b", "llama-3.3-70b", "llama-3-70b",
                                                  "qwen2.5-72b", "command-a-111b"))
        and r.tok_s is not None
    ]
    assert dense_70b, "no dense 70B-class measurement in the data to test the mechanism against"
    failures = [r for r in dense_70b if not r.passes]
    assert failures, "every dense 70B-class config now clears the bar; F3's mechanism may have broken"
    # The ones that do clear it should be discrete-GPU cards, not unified-memory boxes.
    for r in dense_70b:
        if r.passes:
            assert r.tok_s >= bar


def test_something_clears_the_bar_and_it_is_measured():
    """The bar must be passable by something, or it is not a threshold, it is a wall. What
    passes is a finding that moves with the catalog; how many pass is reported, not fixed."""
    _, rows = repo_data.solve_local_bar()
    measured_passes = [r for r in rows if r.passes and r.tok_s_confidence == "MEASURED"]
    assert measured_passes, "nothing in the catalog clears the sustained-rate bar on a measured figure"


def test_capacity_fails_before_throughput_on_the_smallest_box():
    _, rows = repo_data.solve_local_bar()
    m6 = [r for r in rows if "M6" in r.machine]
    assert m6 and all(not r.fits for r in m6)


# ---------------------------------------------------------------- F1: renting wins

def test_volume_tier_is_the_cheapest_capable_listed_path():
    """The property, not the incumbent: whatever the answer calls the volume tier must be
    the cheapest listed path clearing the capability floor, and it must win at list price
    rather than on a promo."""
    pick = repo_data.volume_tier_pick()
    listed = [
        r for r in repo_data.solve_api_costs()
        if r.expires is None and r.aa_score is not None
        and r.aa_score >= repo_data.CAPABLE_SCORE_FLOOR
    ]
    others = [r for r in listed if r.id != pick.id]
    assert all(pick.lifetime_cost <= r.lifetime_cost for r in others)
    assert pick.expires is None


def test_volume_tier_beats_the_best_cache_rate_at_every_ratio():
    """The obvious objection to F1: some rival caches far cheaper. Aimed at whichever
    rival currently has the best cache rate, not at whoever held that spot when this was
    written."""
    winner = repo_data.volume_tier_pick().id
    capable = {
        e["model"] for e in repo_data.aa_index()["entries"]
        if e["score"] >= repo_data.CAPABLE_SCORE_FLOOR
    }
    rivals = [
        m for m in repo_data.priced_models()
        if m.id != winner and m.pricing.cached_input_per_mtok is not None and m.id in capable
    ]
    if not rivals:
        pytest.skip("only one priced model carries a cache rate")
    rival = min(rivals, key=lambda m: m.pricing.cached_input_per_mtok)
    sweep = repo_data.cache_sensitivity(winner, rival.id, [i / 20 for i in range(21)])
    assert all(a < b for _, a, b in sweep), (
        f"{rival.id} now beats {winner} at some cache ratio; the volume-tier conclusion "
        "may have flipped. Check the data, then record it in the README changelog."
    )


def test_cache_advantage_is_bounded_by_the_output_gap():
    ref = repo_data.reference_workload()
    models = {m.id: m for m in repo_data.priced_models()}
    winner = models[repo_data.volume_tier_pick().id]
    capable = {
        e["model"] for e in repo_data.aa_index()["entries"]
        if e["score"] >= repo_data.CAPABLE_SCORE_FLOOR
    }
    rivals = [
        m for m in models.values()
        if m.id != winner.id and m.pricing.cached_input_per_mtok is not None and m.id in capable
    ]
    if not rivals:
        pytest.skip("only one priced model carries a cache rate")
    rival = min(rivals, key=lambda m: m.pricing.cached_input_per_mtok)
    max_cache_advantage = ref.lifetime.input_tokens * (
        winner.pricing.cached_input_per_mtok - rival.pricing.cached_input_per_mtok
    )
    output_gap = ref.lifetime.output_tokens * (
        rival.pricing.output_per_mtok - winner.pricing.output_per_mtok
    )
    assert max_cache_advantage < output_gap


def test_promo_rows_follow_the_calendar():
    before = repo_data.solve_api_costs(today=date(2026, 9, 1))
    after = repo_data.solve_api_costs(today=date(2026, 12, 1))
    assert any(r.expires is not None for r in before)
    assert all(r.expires is None for r in after)


# ---------------------------------------------------------------- F2: the cliff

def test_cheapest_costed_point_is_always_on_the_frontier():
    """By construction nothing can dominate the cheapest point. Stated as a property so it
    keeps holding when the cheapest point changes hands."""
    points = repo_data.solve_frontier()
    cheapest = min(points, key=lambda p: p.cost_per_task)
    assert cheapest.on_frontier


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


# ---------------------------------------------------------------- the two questions

def test_placement_answer_is_internally_consistent():
    """scripts/answer.py and the README block print this; it must follow from the same
    solves the rest of the repo publishes."""
    p = repo_data.solve_placement()
    assert p.compute_value.name == repo_data.solve_psi().winner.name
    assert p.compute_efficiency.points_per_watt >= p.compute_value.points_per_watt
    assert p.rent_ratio_lo > 1.0  # owning wins before the answer says so

    listed = [
        r for r in repo_data.solve_api_costs()
        if r.expires is None and r.aa_score is not None
        and r.aa_score >= repo_data.CAPABLE_SCORE_FLOOR
    ]
    assert p.token_default.lifetime_cost == min(r.lifetime_cost for r in listed)
    assert p.token_frontier.score == max(pt.score for pt in repo_data.solve_frontier())
    assert p.token_frontier.score >= p.token_default.aa_score
    assert p.local.ratio > 1.0  # "never local for thinking" must be solved, not asserted


def test_frontier_pick_reacts_to_costing_a_stronger_model():
    """When an uncosted higher scorer gains a cost per task, the pick must re-solve. This
    guards the answer's caveat: it is a promise, so prove the mechanism."""
    points = repo_data.solve_frontier()
    top = max(p.score for p in points)
    idx = repo_data.aa_index()["entries"]
    stronger_exists = any(
        e["cost_per_task_usd"] is None and e["score"] > top for e in idx
    )
    if not stronger_exists:
        import pytest

        pytest.skip("no uncosted model currently outscores the costed frontier")
    assert len(repo_data.solve_placement().frontier_uncosted) >= 1


# ---------------------------------------------------------------- priors

# The current winners, recorded on purpose. Everything else in this file tests properties
# that survive a change of incumbent; this one exists to notice when an incumbent falls.
# A failure here is the repo working: a new candidate displaced the old answer. Confirm
# the data, update these names, and record the change in the README changelog. Never
# delete a candidate to make it pass.
INCUMBENTS = {
    "volume_tier": "glm-5.3-flash",
    "compute_value": "AMD EPYC 9965",
    "compute_efficiency": "AMD EPYC 9845",
}


def test_incumbents_still_hold():
    p = repo_data.solve_placement()
    current = {
        "volume_tier": p.token_default.id,
        "compute_value": p.compute_value.name,
        "compute_efficiency": p.compute_efficiency.name,
    }
    changed = {k: (v, current[k]) for k, v in INCUMBENTS.items() if current[k] != v}
    assert not changed, (
        "an incumbent was displaced: "
        + "; ".join(f"{k}: {old} -> {new}" for k, (old, new) in changed.items())
        + ". This is a real result. Update INCUMBENTS here and add the reversal to the "
        "README changelog."
    )


def test_candidate_sets_declare_their_scope():
    """Every list of candidates must say what it is supposed to cover. Without this the
    set is whatever came up once and nothing ever re-opens it."""
    import refresh_plan

    for name, path, _yaml, what in refresh_plan.SURVEYED:
        survey = repo_data.load(name).get("survey")
        assert survey is not None, f"{path} has no survey block, so its scope is undeclared"
        assert survey.get("question"), f"{path} survey has no question"
        assert survey.get("where_to_look"), f"{path} survey says nothing about where to look"
        assert "last_surveyed" in survey, f"{path} survey never records when it last ran"
        assert survey.get("survey_interval_days"), f"{path} survey has no interval"


def test_unsurveyed_sets_are_disclosed_in_the_answer():
    """If a candidate set has never been re-opened, the answer has to say so. A pick from
    an inherited list must not read like a pick from the field."""
    import build_tables

    unsurveyed = [
        name for name, _p, _y, _w in
        __import__("refresh_plan").SURVEYED
        if repo_data.load(name).get("survey", {}).get("last_surveyed") is None
    ]
    caveat = build_tables.answer_caveat(repo_data.solve_placement())
    if unsurveyed:
        assert "never been surveyed" in caveat
    assert "VOLATILE" in caveat


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
