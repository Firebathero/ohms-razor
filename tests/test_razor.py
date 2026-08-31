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

    def test_raising_the_burn_shaves_local_boxes_on_rate(self):
        """The rate bar has to actually bind on hardware. At ten times the reference burn
        the bar rises to ~100 tok/s, which the unified-memory boxes cannot sustain. A
        high-bandwidth discrete GPU may still clear it, and that is a finding, not a bug:
        what this asserts is that the constraint bites, not which machines survive it."""
        base = tokens(min_score=0)
        heavy = tokens(min_score=0, out_mtok=3150.0, in_mtok=6300.0)
        assert heavy.required_rate > base.required_rate * 9

        local_base = [c for c in base.candidates if c.kind == "local"]
        local_heavy = [c for c in heavy.candidates if c.kind == "local"]
        assert local_base and local_heavy
        shaved_base = sum(1 for c in local_base if not c.feasible)
        shaved_heavy = sum(1 for c in local_heavy if not c.feasible)
        assert shaved_heavy > shaved_base, "a 10x workload shaved no additional local box"
        assert any("tok/s" in c.excluded_by for c in local_heavy)

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


class TestBreadth:
    """A candidate that nobody has priced must stay in the running on the axis that needs
    no price. Otherwise the catalog can only ever hold fully-researched parts, which is
    what kept it at four."""

    def test_unpriced_candidates_are_screened_not_dropped(self):
        from models.hardware_psi import CpuInputs, screen

        op = repo_data.operating_inputs()
        unpriced = CpuInputs(
            name="hypothetical", specrate_2p=3000.0, sigma=0.5256, phi=1.0,
            ctdp_w=400.0, cpu_price_usd=None, non_cpu_capex_usd=15808.8,
        )
        assert unpriced.screenable
        assert not unpriced.priceable
        s = screen(unpriced, op)
        assert s.points_per_watt > 0
        with pytest.raises(ValueError):
            from models.hardware_psi import evaluate

            evaluate(unpriced, op)

    def test_efficiency_axis_competes_at_least_as_many_candidates(self):
        """Efficiency needs no price, so it can never see fewer candidates than value."""
        value = razor.solve_compute(0.0, None, "value")
        efficiency = razor.solve_compute(0.0, None, "efficiency")
        v_feasible = sum(1 for c in value.candidates if c.feasible)
        e_feasible = sum(1 for c in efficiency.candidates if c.feasible)
        assert e_feasible >= v_feasible

    def test_unpriced_candidate_is_excluded_from_value_with_a_reason(self):
        r = razor.solve_compute(0.0, None, "value")
        for c in r.candidates:
            if c.psi is None:
                assert not c.feasible
                assert "no price" in c.excluded_by

    def test_coverage_counts_are_consistent(self):
        cov = repo_data.cpu_coverage()
        assert cov.total >= cov.screenable >= cov.priced
        assert 0.0 <= cov.priced_share <= 1.0

    def test_pricing_targets_only_name_unpriced_parts_that_out_screen(self):
        op = repo_data.operating_inputs()
        targets = repo_data.pricing_targets(op)
        priced_names = {c.name for c in repo_data.cpu_inputs() if c.priceable}
        winner = repo_data.solve_psi().winner
        for t in targets:
            assert t.name not in priced_names
            assert t.points_per_watt > winner.points_per_watt
            assert t.beats_winner_by > 0


class TestImporterIsSafe:
    """Bulk import must never silently overwrite researched values, or the cheap path
    (a spreadsheet) would degrade the expensive one (a sourced figure)."""

    def test_blank_detection(self):
        import import_catalog

        for v in ("", "  ", "-", "n/a", "TODO: unverified", "todo"):
            assert import_catalog.blank(v)
        for v in ("0", "192", "AMD"):
            assert not import_catalog.blank(v)

    def test_dry_run_leaves_the_file_untouched(self, tmp_path):
        import import_catalog

        target = repo_data.DATA / "cpu_specs.yaml"
        before = target.read_bytes()
        csv_path = tmp_path / "cpus.csv"
        csv_path.write_text(
            ",".join(import_catalog.SCHEMAS["cpus"]["columns"]) + "\n"
            "test-part,Test Part,TestCo,64,TestArch,128,300,250,,1000,,,,,test,TODO\n",
            encoding="utf-8",
        )
        rows = import_catalog.read_csv(csv_path, "cpus")
        assert len(rows) == 1
        import_catalog.merge("cpus", rows, dry_run=True)
        assert target.read_bytes() == before

    def test_rows_missing_required_fields_are_skipped(self, tmp_path):
        import import_catalog

        csv_path = tmp_path / "cpus.csv"
        csv_path.write_text(
            ",".join(import_catalog.SCHEMAS["cpus"]["columns"]) + "\n"
            ",No Id,TestCo,64,,,300,,,,,,,,,\n",
            encoding="utf-8",
        )
        assert import_catalog.read_csv(csv_path, "cpus") == []


class TestNothingIsInvented:
    def test_unplaceable_candidates_are_named_not_guessed(self):
        """Every candidate the tool cannot place must say which field is missing. Silence
        would let a gap look like a judgment."""
        r = tokens()
        for note in r.unplaceable:
            assert "(" in note and note.rstrip().endswith(")"), f"no stated reason: {note}"
            reason = note[note.index("(") + 1: -1]
            assert reason.strip(), f"empty reason: {note}"
            assert "no " in reason or "not in data" in reason, f"reason is not a stated gap: {note}"

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
