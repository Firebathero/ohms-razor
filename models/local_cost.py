"""Model 4: local cost per token, and the break-even against cloud.

    C_local_per_Mtok = (capex + P_wall * k * 8766 * Y * r / 1000)
                       / (tok_s * 31.5576e6 * Y * U / 1e6)

As specified in the handoff, the box draws P_wall around the clock (it is an always-on
machine) while useful output scales with utilization U. That is deliberately conservative
toward the local side only when U = 1; at any U < 1 it charges idle hours at full draw,
which is what an always-on box actually does absent aggressive power management.

Break-even utilization against a cloud price:

    U_breakeven = C_local_total / (C_cloud_per_Mtok * tok_s * 31.5576e6 * Y / 1e6)

A U_breakeven above 1.0 means the box cannot beat the cloud price at any duty cycle.
"""

from __future__ import annotations

from . import HOURS_PER_YEAR, MTOK, SECONDS_PER_YEAR


def lifetime_energy_cost(
    wall_draw_w: float,
    cooling_overhead: float,
    electricity_usd_per_kwh: float,
    years: float,
) -> float:
    """USD of electricity for an always-on box over the hold, cooling included."""
    return wall_draw_w * cooling_overhead * HOURS_PER_YEAR * years * electricity_usd_per_kwh / 1000.0


def lifetime_output_tokens(tok_s: float, years: float, utilization: float) -> float:
    return tok_s * SECONDS_PER_YEAR * years * utilization


def local_cost_per_mtok(
    capex_usd: float,
    wall_draw_w: float,
    cooling_overhead: float,
    electricity_usd_per_kwh: float,
    years: float,
    tok_s: float,
    utilization: float,
) -> float:
    """All-in USD per million output tokens for the always-on box."""
    total = capex_usd + lifetime_energy_cost(
        wall_draw_w, cooling_overhead, electricity_usd_per_kwh, years
    )
    return total / (lifetime_output_tokens(tok_s, years, utilization) / MTOK)


def breakeven_utilization(
    local_total_cost_usd: float,
    cloud_usd_per_mtok: float,
    tok_s: float,
    years: float,
) -> float:
    """Utilization at which the box's cost per token equals the cloud price."""
    return local_total_cost_usd / (cloud_usd_per_mtok * tok_s * SECONDS_PER_YEAR * years / MTOK)
