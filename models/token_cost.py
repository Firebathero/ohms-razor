"""Model 1: API token cost.

    C_api = O * p_out + I * (1 - h) * p_in + I * h * p_cache

With peak/off-peak pricing, weight by exposure:

    C_effective = C_api * (1 + f_peak * (m_peak - 1))

where f_peak is the fraction of tokens billed at peak and m_peak the peak multiplier.
Prices are USD per million tokens; token counts are raw token counts.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import MTOK


@dataclass(frozen=True)
class Pricing:
    """Per-Mtok rates. cached_input_per_mtok of None means the provider offers no cache
    discount; cached tokens then bill at the full input rate."""

    input_per_mtok: float
    cached_input_per_mtok: float | None
    output_per_mtok: float

    def scaled(self, multiplier: float) -> "Pricing":
        """All three rates multiplied, e.g. a promo at 0.5 or a peak window at 2.0."""
        cache = self.cached_input_per_mtok
        return Pricing(
            input_per_mtok=self.input_per_mtok * multiplier,
            cached_input_per_mtok=None if cache is None else cache * multiplier,
            output_per_mtok=self.output_per_mtok * multiplier,
        )


@dataclass(frozen=True)
class Workload:
    """Token totals over whatever period is being priced."""

    output_tokens: float
    input_tokens: float
    cache_hit_rate: float

    @property
    def cached_input_tokens(self) -> float:
        return self.input_tokens * self.cache_hit_rate

    @property
    def fresh_input_tokens(self) -> float:
        return self.input_tokens - self.cached_input_tokens


def api_cost(pricing: Pricing, workload: Workload) -> float:
    """C_api in USD for the workload at the given rates."""
    cache_rate = (
        pricing.cached_input_per_mtok
        if pricing.cached_input_per_mtok is not None
        else pricing.input_per_mtok
    )
    return (
        workload.output_tokens * pricing.output_per_mtok
        + workload.fresh_input_tokens * pricing.input_per_mtok
        + workload.cached_input_tokens * cache_rate
    ) / MTOK


def peak_fraction(peak_hours_per_day: float) -> float:
    """Fraction of tokens billed at peak for a uniform 24/7 loop with no scheduling."""
    return peak_hours_per_day / 24.0


def effective_cost(base_cost: float, f_peak: float, m_peak: float) -> float:
    """C_effective = C_api * (1 + f_peak * (m_peak - 1))."""
    return base_cost * (1.0 + f_peak * (m_peak - 1.0))


def cost_at_cache_ratio(pricing: Pricing, workload: Workload, cache_hit_rate: float) -> float:
    """The same workload re-priced at a different cache hit rate. Used to test claims of
    the form 'provider A wins at every cache ratio'."""
    swapped = Workload(
        output_tokens=workload.output_tokens,
        input_tokens=workload.input_tokens,
        cache_hit_rate=cache_hit_rate,
    )
    return api_cost(pricing, swapped)
