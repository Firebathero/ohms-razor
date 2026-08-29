"""Model 5: hardware selection for deterministic compute, ranked on Psi.

    W      = R_2P * sigma * phi         work rate (sigma = 1P scaling, phi = cTDP derate)
    P_wall = (P_cpu + P_plat) / eta
    P_eff  = U * P_wall + (1 - U) * P_idle
    kWh/yr = P_eff * k * 8766 / 1000
    E      = kWh/yr * r * year_factor(Y, e)
    TCO    = C_cpu + C_rest + E - S
    Work   = W * U * Y                  point-years actually delivered
    Psi    = TCO / Work                 dollars per SPECrate-point-year; lower wins

Why this metric: dollars per watt picks small slow parts, perf per watt ignores capex,
dollars per core is meaningless across architectures, and PassMark saturates past roughly
100 cores. Psi answers the actual question: what a unit of sustained throughput costs per
year, all in.

Renting prices in the same unit: Psi_rent = 12 * monthly / R_1P, directly comparable.

This module reproduces spreadsheets/compute-node-model.xlsx cell for cell; a parity test
holds the two together.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import HOURS_PER_YEAR


@dataclass(frozen=True)
class OperatingInputs:
    years: float
    utilization: float
    electricity_usd_per_kwh: float
    electricity_escalation: float
    discount_rate: float
    platform_draw_w: float
    psu_efficiency: float
    cooling_overhead: float
    idle_draw_w: float
    residual_value_usd: float


@dataclass(frozen=True)
class CpuInputs:
    name: str
    specrate_2p: float
    sigma: float
    phi: float
    ctdp_w: float
    cpu_price_usd: float
    non_cpu_capex_usd: float


@dataclass(frozen=True)
class Evaluation:
    name: str
    work_rate: float          # W, scaled 1P SPECrate points
    wall_power_w: float       # P_wall under load
    duty_power_w: float       # P_eff
    annual_kwh: float
    capex_usd: float
    energy_usd: float
    tco_usd: float
    work_point_years: float
    psi: float                # USD per SPECrate-point-year
    points_per_watt: float    # epsilon
    energy_share: float       # theta


def work_rate(specrate_2p: float, sigma: float, phi: float) -> float:
    return specrate_2p * sigma * phi


def wall_power(ctdp_w: float, platform_draw_w: float, psu_efficiency: float) -> float:
    return (ctdp_w + platform_draw_w) / psu_efficiency


def duty_weighted_power(p_wall_w: float, idle_draw_w: float, utilization: float) -> float:
    return utilization * p_wall_w + (1.0 - utilization) * idle_draw_w


def annual_kwh(duty_power_w: float, cooling_overhead: float) -> float:
    return duty_power_w * cooling_overhead * HOURS_PER_YEAR / 1000.0


def year_factor(years: float, escalation: float) -> float:
    """Sum of (1+e)^t over the hold; equals Y when escalation is zero."""
    if escalation == 0.0:
        return years
    return ((1.0 + escalation) ** years - 1.0) / escalation


def npv_year_factor(years: float, escalation: float, discount: float) -> float:
    """The same series discounted at d; equals year_factor when d equals e."""
    if abs(escalation - discount) < 1e-7:
        return years
    ratio = (1.0 + escalation) / (1.0 + discount)
    return (1.0 - ratio**years) / (1.0 - ratio)


def evaluate(cpu: CpuInputs, op: OperatingInputs) -> Evaluation:
    w = work_rate(cpu.specrate_2p, cpu.sigma, cpu.phi)
    p_wall = wall_power(cpu.ctdp_w, op.platform_draw_w, op.psu_efficiency)
    p_eff = duty_weighted_power(p_wall, op.idle_draw_w, op.utilization)
    kwh = annual_kwh(p_eff, op.cooling_overhead)
    energy = kwh * op.electricity_usd_per_kwh * year_factor(op.years, op.electricity_escalation)
    capex = cpu.cpu_price_usd + cpu.non_cpu_capex_usd
    tco = capex + energy - op.residual_value_usd
    work_py = w * op.utilization * op.years
    return Evaluation(
        name=cpu.name,
        work_rate=w,
        wall_power_w=p_wall,
        duty_power_w=p_eff,
        annual_kwh=kwh,
        capex_usd=capex,
        energy_usd=energy,
        tco_usd=tco,
        work_point_years=work_py,
        psi=tco / work_py,
        points_per_watt=w / p_wall,
        energy_share=energy / tco,
    )


def rent_psi(monthly_usd: float, specrate_1p: float) -> float:
    """Psi_rent = 12 * monthly / R_1P, dollars per SPECrate-point-year."""
    return monthly_usd * 12.0 / specrate_1p


def cpu_price_to_match_psi(target_psi: float, contender: CpuInputs, op: OperatingInputs) -> float:
    """The CPU price at which the contender's Psi equals target_psi, holding everything
    else fixed. Solved from Psi * Work = C_cpu + C_rest + E - S. Negative means it cannot
    get there at any price."""
    ev = evaluate(contender, op)
    return (
        target_psi * ev.work_point_years
        - contender.non_cpu_capex_usd
        - ev.energy_usd
        + op.residual_value_usd
    )
