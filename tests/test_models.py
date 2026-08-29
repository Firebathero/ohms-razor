"""Model math. Three kinds of assertions, none of which enshrine a market price as truth:

1. Formula checks: given a dated input snapshot spelled out inline, the model must produce
   the arithmetic result. These verify the implementation, not the world.
2. Properties and identities: things that must hold for any input (inversions, limits,
   cancellation, monotonicity).
3. Workbook parity (test_workbook_parity): the pipeline must reproduce
   spreadsheets/compute-node-model.xlsx cell for cell from the workbook's own inputs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from models import SECONDS_PER_YEAR
from models.token_cost import Pricing, Workload, api_cost, cost_at_cache_ratio, effective_cost, peak_fraction
from models.local_throughput import decode_rate_upper_bound, fits_in_memory, required_sustained_rate
from models.moe_economics import (
    MoeGeometry,
    batched_decode_rate_upper_bound,
    expected_distinct_experts,
    memory_cost_per_stream_b,
    sparsity_ratio,
)
from models.local_cost import breakeven_utilization, lifetime_energy_cost, local_cost_per_mtok
from models.hardware_psi import (
    CpuInputs,
    OperatingInputs,
    cpu_price_to_match_psi,
    evaluate,
    npv_year_factor,
    rent_psi,
    year_factor,
)

ROOT = Path(__file__).resolve().parents[1]

# The reference workload over ten years (handoff definition, 2026-08-29).
LIFETIME = Workload(output_tokens=3.15e9, input_tokens=6.30e9, cache_hit_rate=0.80)

# Pricing snapshots, all dated 2026-08-29, used here as fixed inputs to check arithmetic.
GLM = Pricing(input_per_mtok=0.15, cached_input_per_mtok=0.03, output_per_mtok=0.50)
DEEPSEEK_OFFPEAK = Pricing(input_per_mtok=0.22, cached_input_per_mtok=0.007, output_per_mtok=0.66)
KIMI = Pricing(input_per_mtok=3.00, cached_input_per_mtok=0.30, output_per_mtok=15.00)


class TestModel1TokenCost:
    def test_glm_snapshot(self):
        # 3,150 Mtok x 0.50 + 1,260 x 0.15 + 5,040 x 0.03
        assert api_cost(GLM, LIFETIME) == pytest.approx(1915.20, abs=1e-9)

    def test_glm_promo_is_half(self):
        assert api_cost(GLM.scaled(0.5), LIFETIME) == pytest.approx(957.60, abs=1e-9)

    def test_deepseek_offpeak_snapshot(self):
        assert api_cost(DEEPSEEK_OFFPEAK, LIFETIME) == pytest.approx(2391.48, abs=1e-9)

    def test_deepseek_peak_exposure(self):
        # 7 of 24 hours at 2x. The handoff rounded f_peak to 0.29 and reported $3,084;
        # the exact fraction gives $3,089. Both are the same formula.
        base = api_cost(DEEPSEEK_OFFPEAK, LIFETIME)
        exact = effective_cost(base, peak_fraction(7.0), 2.0)
        assert exact == pytest.approx(base * 31 / 24, rel=1e-12)
        assert exact == pytest.approx(3089.0, abs=0.5)
        assert effective_cost(base, 0.29, 2.0) == pytest.approx(3084, rel=1e-3)

    def test_kimi_snapshot(self):
        assert api_cost(KIMI, LIFETIME) == pytest.approx(52542.00, abs=1e-9)

    def test_no_cache_discount_bills_input_rate(self):
        flat = Pricing(input_per_mtok=0.10, cached_input_per_mtok=None, output_per_mtok=1.0)
        with_rate = Pricing(input_per_mtok=0.10, cached_input_per_mtok=0.10, output_per_mtok=1.0)
        assert api_cost(flat, LIFETIME) == pytest.approx(api_cost(with_rate, LIFETIME))

    def test_peak_multiplier_one_is_identity(self):
        base = api_cost(GLM, LIFETIME)
        assert effective_cost(base, 0.5, 1.0) == base

    def test_cache_ratio_sweep_is_linear(self):
        lo = cost_at_cache_ratio(GLM, LIFETIME, 0.0)
        hi = cost_at_cache_ratio(GLM, LIFETIME, 1.0)
        mid = cost_at_cache_ratio(GLM, LIFETIME, 0.5)
        assert mid == pytest.approx((lo + hi) / 2, rel=1e-12)


class TestModel2Throughput:
    def test_reference_rate_just_under_ten(self):
        assert required_sustained_rate(315e6) == pytest.approx(9.98, abs=0.01)

    def test_bound_arithmetic(self):
        # 215 GB/s over 5.1B active at 0.53 B/param
        assert decode_rate_upper_bound(215, 5.1, 0.53) == pytest.approx(79.54, abs=0.01)

    def test_capacity_gate(self):
        assert not fits_in_memory(70, 0.60, 32)   # dense 70B q4 vs 32GB: fails outright
        assert fits_in_memory(117, 0.53, 128)     # gpt-oss-120b vs 128GB: fits
        assert not fits_in_memory(70, 0.60, 42, context_overhead_fraction=0.20)


class TestModel3Moe:
    GEO = MoeGeometry(total_params_b=117, active_params_b=5.1, n_experts=128, experts_per_token=4)

    def test_sparsity_ratio(self):
        assert sparsity_ratio(117, 5.1) == pytest.approx(22.94, abs=0.01)

    def test_geometry_split_solves_both_totals(self):
        g = self.GEO
        assert g.shared_params_b + g.experts_per_token * g.per_expert_params_b == pytest.approx(g.active_params_b)
        assert g.shared_params_b + g.n_experts * g.per_expert_params_b == pytest.approx(g.total_params_b)

    def test_batch_one_reduces_to_model_2(self):
        assert expected_distinct_experts(128, 4, 1) == pytest.approx(4.0)
        assert batched_decode_rate_upper_bound(self.GEO, 215, 0.53, 1) == pytest.approx(
            decode_rate_upper_bound(215, 5.1, 0.53), rel=1e-9
        )

    def test_distinct_experts_monotone_and_bounded(self):
        prev = 0.0
        for b in (1, 2, 4, 8, 32, 128):
            d = expected_distinct_experts(128, 4, b)
            assert d > prev
            assert d <= 128  # saturates at n; float underflow reaches it exactly for huge B
            prev = d
        assert expected_distinct_experts(128, 4, 100_000) == pytest.approx(128, rel=1e-6)

    def test_aggregate_throughput_monotone_in_batch(self):
        rates = [batched_decode_rate_upper_bound(self.GEO, 215, 0.53, b) for b in (1, 2, 4, 8, 16)]
        assert rates == sorted(rates)

    def test_memory_amortization(self):
        assert memory_cost_per_stream_b(self.GEO, 1) == pytest.approx(117)
        assert memory_cost_per_stream_b(self.GEO, 16) == pytest.approx(117 / 16)


class TestModel4LocalCost:
    # Strix Halo scenario snapshot (2026-08-29): $1,499 box, 140W wall, $0.20/kWh, 5 yr,
    # 31 tok/s measured, fully saturated.
    def test_energy_snapshot(self):
        assert lifetime_energy_cost(140, 1.0, 0.20, 5) == pytest.approx(1227.24, abs=1e-9)

    def test_cost_per_mtok_snapshot(self):
        got = local_cost_per_mtok(1499, 140, 1.0, 0.20, 5, 31, 1.0)
        assert got == pytest.approx(0.5574, abs=5e-4)

    def test_breakeven_inverts_cost(self):
        # At exactly the break-even utilization, local cost per Mtok equals the cloud price.
        total = 1499 + lifetime_energy_cost(140, 1.0, 0.20, 5)
        u = breakeven_utilization(total, 0.17, 31, 5)
        assert local_cost_per_mtok(1499, 140, 1.0, 0.20, 5, 31, u) == pytest.approx(0.17, rel=1e-12)


OP = OperatingInputs(
    years=10, utilization=1.0, electricity_usd_per_kwh=0.20, electricity_escalation=0.0,
    discount_rate=0.0, platform_draw_w=100, psu_efficiency=0.92, cooling_overhead=1.0,
    idle_draw_w=120, residual_value_usd=0.0,
)


def cpu(name: str, spec: float, phi: float, ctdp: float, price: float, rest: float = 15808.8) -> CpuInputs:
    return CpuInputs(name=name, specrate_2p=spec, sigma=0.5256, phi=phi, ctdp_w=ctdp,
                     cpu_price_usd=price, non_cpu_capex_usd=rest)


class TestModel5Psi:
    def test_year_factor_identities(self):
        assert year_factor(10, 0.0) == 10
        assert year_factor(10, 1e-9) == pytest.approx(10, rel=1e-6)
        assert npv_year_factor(10, 0.03, 0.03) == 10

    def test_evaluation_internal_consistency(self):
        ev = evaluate(cpu("x", 3140, 0.99, 450, 7000), OP)
        assert ev.psi * ev.work_point_years == pytest.approx(ev.tco_usd, rel=1e-12)
        assert ev.tco_usd == pytest.approx(ev.capex_usd + ev.energy_usd, rel=1e-12)
        assert 0 < ev.energy_share < 1

    def test_sigma_cancels_from_ranking(self):
        candidates = [
            ("a", 3140, 0.99, 450, 7000),
            ("b", 2620, 0.98, 320, 9684),
            ("c", 2589, 1.00, 500, 6500),
            ("d", 2330, 0.98, 320, 7200),
        ]
        orders = []
        for sigma in (0.40, 0.5256, 0.60):
            evs = [
                evaluate(CpuInputs(n, s, sigma, p, t, pr, 15808.8), OP)
                for n, s, p, t, pr in candidates
            ]
            orders.append([e.name for e in sorted(evs, key=lambda e: e.psi)])
        assert orders[0] == orders[1] == orders[2]

    def test_tie_price_inverts(self):
        winner = evaluate(cpu("w", 3140, 0.99, 450, 7000), OP)
        contender = cpu("c", 2620, 0.98, 320, 9684)
        tie = cpu_price_to_match_psi(winner.psi, contender, OP)
        tied = evaluate(cpu("c", 2620, 0.98, 320, tie), OP)
        assert tied.psi == pytest.approx(winner.psi, rel=1e-12)

    def test_rent_psi_arithmetic(self):
        assert rent_psi(722.10, 523) == pytest.approx(722.10 * 12 / 523, rel=1e-12)


class TestWorkbookParity:
    """The pipeline must reproduce the workbook from the workbook's own inputs, and the
    YAML transcription must match those inputs. No tolerance for drift beyond float noise."""

    @pytest.fixture(scope="class")
    def wb(self):
        openpyxl = pytest.importorskip("openpyxl")
        path = ROOT / "spreadsheets" / "compute-node-model.xlsx"
        if not path.exists():
            pytest.skip("workbook not present")
        return openpyxl.load_workbook(path, data_only=True)

    @pytest.fixture(scope="class")
    def pipeline(self, wb):
        inputs = wb["Inputs"]
        compare = wb["Compare"]
        parts = wb["Parts List"]
        op = OperatingInputs(
            years=inputs["C7"].value,
            utilization=inputs["C8"].value,
            electricity_usd_per_kwh=inputs["C10"].value,
            electricity_escalation=inputs["C11"].value,
            discount_rate=inputs["C12"].value,
            platform_draw_w=inputs["C15"].value,
            psu_efficiency=inputs["C16"].value,
            cooling_overhead=inputs["C17"].value,
            idle_draw_w=inputs["C18"].value,
            residual_value_usd=inputs["C19"].value,
        )
        sigma = inputs["C29"].value
        memory = inputs["C22"].value * inputs["C23"].value * inputs["C24"].value
        statics = sum(parts[f"E{row}"].value for row in (6, 9, 10, 11, 12, 13, 14))
        rest = statics + memory
        evaluations = {}
        for col in "CDEF":
            name = str(compare[f"{col}3"].value)
            evaluations[col] = evaluate(
                CpuInputs(
                    name=name,
                    specrate_2p=compare[f"{col}18"].value,
                    sigma=sigma,
                    phi=compare[f"{col}14"].value,
                    ctdp_w=compare[f"{col}13"].value,
                    cpu_price_usd=compare[f"{col}28"].value,
                    non_cpu_capex_usd=rest,
                ),
                op,
            )
        return op, rest, evaluations

    def test_non_cpu_subtotal(self, wb, pipeline):
        _, rest, _ = pipeline
        assert rest == pytest.approx(wb["Parts List"]["F15"].value, rel=1e-9)

    @pytest.mark.parametrize("row,field", [
        (20, "work_rate"), (23, "wall_power_w"), (25, "annual_kwh"), (31, "energy_usd"),
        (33, "tco_usd"), (36, "work_point_years"), (37, "psi"), (38, "points_per_watt"),
        (39, "energy_share"),
    ])
    def test_compare_tab_rows(self, wb, pipeline, row, field):
        _, _, evaluations = pipeline
        compare = wb["Compare"]
        for col, ev in evaluations.items():
            assert getattr(ev, field) == pytest.approx(compare[f"{col}{row}"].value, rel=1e-9), (
                f"cell {col}{row} ({field}) for {ev.name}"
            )

    def test_rent_tab(self, wb, pipeline):
        _, _, evaluations = pipeline
        rent = wb["Rent Compare"]
        for row in (7, 8):
            got = rent_psi(rent[f"D{row}"].value, rent[f"C{row}"].value)
            assert got == pytest.approx(rent[f"E{row}"].value, rel=1e-9)
        winner = min(evaluations.values(), key=lambda e: e.psi)
        boxes = winner.work_rate / rent["C7"].value
        assert boxes == pytest.approx(rent["C10"].value, rel=1e-9)
        assert boxes * rent["D7"].value * 12 == pytest.approx(rent["C11"].value, rel=1e-9)

    def test_sensitivity_tie_prices(self, wb, pipeline):
        op, rest, evaluations = pipeline
        sens = wb["Sensitivity"]
        winner = min(evaluations.values(), key=lambda e: e.psi)
        compare = wb["Compare"]
        expected = {"D": sens["C23"].value, "F": sens["C24"].value, "E": sens["C25"].value}
        for col, cell_value in expected.items():
            contender = CpuInputs(
                name=str(compare[f"{col}3"].value),
                specrate_2p=compare[f"{col}18"].value,
                sigma=wb["Inputs"]["C29"].value,
                phi=compare[f"{col}14"].value,
                ctdp_w=compare[f"{col}13"].value,
                cpu_price_usd=compare[f"{col}28"].value,
                non_cpu_capex_usd=rest,
            )
            assert cpu_price_to_match_psi(winner.psi, contender, op) == pytest.approx(cell_value, rel=1e-9)

    def test_yaml_matches_workbook_inputs(self, wb):
        """The transcription proof: data/assumptions.yaml and data/cpu_specs.yaml carry
        exactly the workbook's blue cells."""
        import repo_data

        inputs = wb["Inputs"]
        op = repo_data.operating_inputs()
        assert op.years == inputs["C7"].value
        assert op.utilization == inputs["C8"].value
        assert op.electricity_usd_per_kwh == inputs["C10"].value
        assert op.platform_draw_w == inputs["C15"].value
        assert op.psu_efficiency == inputs["C16"].value
        assert op.cooling_overhead == inputs["C17"].value
        assert op.idle_draw_w == inputs["C18"].value
        assert repo_data.non_cpu_capex() == pytest.approx(wb["Parts List"]["F15"].value, rel=1e-9)

        compare = wb["Compare"]
        by_suffix = {c.name.replace("AMD EPYC ", ""): c for c in repo_data.cpu_inputs()}
        for col in "CDEF":
            name = str(compare[f"{col}3"].value)
            c = by_suffix[name]
            assert c.specrate_2p == compare[f"{col}18"].value
            assert c.phi == compare[f"{col}14"].value
            assert c.ctdp_w == compare[f"{col}13"].value
            assert c.cpu_price_usd == compare[f"{col}28"].value
            assert c.sigma == inputs["C29"].value
