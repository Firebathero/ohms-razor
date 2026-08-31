"""The objective function only exists once thresholds are declared, so these test that
thresholds actually bind and that permuting them moves the answer.
"""

from __future__ import annotations

import pytest

import razor
import refresh_plan
import repo_data


def tokens(min_score=repo_data.CAPABLE_SCORE_FLOOR, budget=None, objective="cheapest",
           out_mtok=315.0, in_mtok=630.0, cache=0.8):
    return razor.solve_tokens(out_mtok, in_mtok, cache, min_score, budget, objective)


class TestThresholdsBind:
    def test_low_bar_converges_on_the_cheapest_thing(self):
        """Drop the capability line and the answer collapses to price, as it should."""
        r = tokens(min_score=0)
        assert r.winner is not None
        assert r.winner.monthly_usd == min(c.monthly_usd for c in r.candidates)

    def test_raising_the_bar_never_makes_it_cheaper(self):
        costs = []
        for bar in (0, 24, 52, 57, 60):
            r = tokens(min_score=bar)
            if r.winner:
                costs.append(r.winner.monthly_usd)
        assert costs == sorted(costs), "a stricter capability line must not lower the price"

    def test_a_high_enough_bar_excludes_everything(self):
        r = tokens(min_score=999)
        assert r.winner is None
        assert all(not c.feasible for c in r.candidates)

    def test_budget_line_excludes_by_price(self):
        loose = tokens()
        assert loose.winner is not None
        tight = tokens(budget=loose.winner.monthly_usd / 2)
        assert tight.winner is None or tight.winner.monthly_usd <= loose.winner.monthly_usd / 2
        assert any("budget" in c.excluded_by for c in tight.candidates)

    def test_objective_flips_the_pick(self):
        cheap = tokens(objective="cheapest").winner
        smart = tokens(objective="smartest").winner
        assert cheap is not None and smart is not None
        assert smart.score >= cheap.score
        assert smart.monthly_usd >= cheap.monthly_usd

    def test_rate_bar_scales_with_the_workload(self):
        small = tokens(out_mtok=31.5)
        big = tokens(out_mtok=3150.0)
        assert big.required_rate == pytest.approx(small.required_rate * 100, rel=1e-9)

    def test_local_box_fails_a_workload_it_cannot_sustain(self):
        """Ten times the reference burn puts the measured local rate under the bar."""
        r = tokens(min_score=0, out_mtok=3150.0)
        local = [c for c in r.candidates if c.kind == "local"]
        assert local and all(not c.feasible for c in local)
        assert any("tok/s" in c.excluded_by for c in local)

    def test_cost_scales_with_the_workload(self):
        base = tokens(min_score=0)
        doubled = tokens(min_score=0, out_mtok=630.0, in_mtok=1260.0)
        api_base = {c.label: c.monthly_usd for c in base.candidates if c.kind == "api"}
        api_two = {c.label: c.monthly_usd for c in doubled.candidates if c.kind == "api"}
        for label, cost in api_base.items():
            assert api_two[label] == pytest.approx(cost * 2, rel=1e-9)


class TestComputeThresholds:
    def test_watt_cap_shaves_the_thirsty_parts(self):
        loose = razor.solve_compute(0.0, None, "value")
        assert loose.winner is not None
        capped = razor.solve_compute(0.0, 500.0, "value")
        assert capped.winner is not None
        assert capped.winner.wall_w <= 500.0
        assert any("cap" in c.excluded_by for c in capped.candidates)

    def test_objective_flips_the_pick(self):
        value = razor.solve_compute(0.0, None, "value").winner
        efficiency = razor.solve_compute(0.0, None, "efficiency").winner
        assert value is not None and efficiency is not None
        assert efficiency.points_per_watt >= value.points_per_watt
        assert efficiency.psi >= value.psi

    def test_work_floor_binds(self):
        top = max(c.work_points for c in razor.solve_compute(0.0, None, "value").candidates)
        r = razor.solve_compute(top + 1, None, "value")
        assert r.winner is None

    def test_impossible_combination_returns_nothing(self):
        assert razor.solve_compute(0.0, 100.0, "value").winner is None


class TestNothingIsInvented:
    def test_unplaceable_candidates_are_named_not_guessed(self):
        r = tokens()
        for note in r.unplaceable:
            assert "no AA score in data" in note or "not in data" in note

    def test_every_excluded_candidate_says_why(self):
        r = tokens(min_score=60, budget=100.0)
        assert all(c.excluded_by for c in r.candidates if not c.feasible)


class TestRefreshPlan:
    def test_work_order_covers_stale_and_gaps(self):
        items = refresh_plan.build()
        kinds = {i.kind for i in items}
        assert "gap" in kinds
        assert all(i.file.startswith("data/") for i in items)
        assert all(i.priority in (1, 2, 3) for i in items)

    def test_uncosted_index_entries_become_work(self):
        uncosted = {
            e["model"] for e in repo_data.aa_index()["entries"] if e["cost_per_task_usd"] is None
        }
        figures = " ".join(i.figure for i in refresh_plan.build())
        for model in uncosted:
            assert model in figures

    def test_json_mode_is_serializable(self):
        import json
        from dataclasses import asdict

        json.dumps([asdict(i) for i in refresh_plan.build()])
