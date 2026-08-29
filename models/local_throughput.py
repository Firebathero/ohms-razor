"""Model 2: local inference throughput.

Token generation at batch size 1 is memory-bandwidth-bound, not compute-bound. Every
generated token requires streaming the active parameters through the memory bus once, so:

    tok/s <= BW_effective / (P_active * bytes_per_param)

This is an upper bound: it ignores KV-cache traffic, expert-routing overhead, and kernel
inefficiency. Measured throughput always takes precedence where it exists; the bound's job
is to disqualify configurations that cannot work even in principle, and to sanity-check
measurements.

The companion constraint is the sustained rate a workload demands:

    required tok/s = output_tokens_per_year / 31,557,600 s/yr

A box that cannot sustain that rate cannot produce the workload at any duty cycle.
"""

from __future__ import annotations

from . import SECONDS_PER_YEAR


def required_sustained_rate(output_tokens_per_year: float) -> float:
    """Tokens per second, 24/7/365, that the yearly output volume demands."""
    return output_tokens_per_year / SECONDS_PER_YEAR


def decode_rate_upper_bound(
    bandwidth_gb_per_s: float,
    active_params_b: float,
    bytes_per_param: float,
) -> float:
    """Best-case decode tok/s at batch 1 for a model with active_params_b billion active
    parameters. Giga and billion cancel, so the units reduce cleanly."""
    return bandwidth_gb_per_s / (active_params_b * bytes_per_param)


def fits_in_memory(
    total_params_b: float,
    bytes_per_param: float,
    memory_gb: float,
    context_overhead_fraction: float = 0.20,
) -> bool:
    """Whether the weights plus a working allowance for KV cache, activations, and the OS
    fit in unified memory. The 20 percent overhead default is an ESTIMATE; a machine that
    fails even at 0 percent overhead fails on capacity outright."""
    weights_gb = total_params_b * bytes_per_param
    return weights_gb * (1.0 + context_overhead_fraction) <= memory_gb
