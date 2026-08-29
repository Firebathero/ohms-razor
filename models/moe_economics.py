"""Model 3: the MoE memory-vs-compute asymmetry, plus a first-order batching model.

The sparsity ratio is the core of it:

    R = P_total / P_active

You buy memory capacity for P_total and receive throughput from P_active. A provider
batches many concurrent requests, so different requests activate different experts and the
memory cost of holding P_total amortizes across the batch. A solo local user runs at batch
size 1 and eats the full memory cost for one request's worth of compute. R grows with
model size, so the local-vs-cloud gap widens structurally as models get larger.

The handoff names unmodelled batching as its strongest available rebuttal (weakness 1), so
this module models it rather than waiting to be told. First order, decode phase, uniform
independent routing:

    E[distinct experts touched by a batch of B] = n * (1 - (1 - k/n)^B)

Weights streamed per decode step are the shared parameters plus the distinct experts, so
aggregate throughput is

    tok/s(B) <= B * BW / (bytes_per_param * (P_shared + per_expert * E[distinct]))

At B = 1 this reduces exactly to Model 2 (the bound over P_active). As B grows the reads
amortize and aggregate throughput approaches B * BW / (bytes * P_total-ish), which is the
provider's economics. Everything here is an upper bound and is labeled ESTIMATE wherever
it lands in a table; real routing is not uniform and real batches contend for KV bandwidth.
"""

from __future__ import annotations

from dataclasses import dataclass


def sparsity_ratio(total_params_b: float, active_params_b: float) -> float:
    """R = P_total / P_active."""
    return total_params_b / active_params_b


@dataclass(frozen=True)
class MoeGeometry:
    """Weight geometry. Shared/per-expert split is derived, not stored, so the only inputs
    are the four published numbers."""

    total_params_b: float
    active_params_b: float
    n_experts: int
    experts_per_token: int

    @property
    def per_expert_params_b(self) -> float:
        """Solve the split: active = shared + k * per_expert and
        total = shared + n * per_expert."""
        n, k = self.n_experts, self.experts_per_token
        return (self.total_params_b - self.active_params_b) / (n - k)

    @property
    def shared_params_b(self) -> float:
        return self.active_params_b - self.experts_per_token * self.per_expert_params_b


def expected_distinct_experts(n_experts: int, experts_per_token: int, batch: int) -> float:
    """E[distinct] = n * (1 - (1 - k/n)^B) under independent uniform top-k routing."""
    n, k = float(n_experts), float(experts_per_token)
    return n * (1.0 - (1.0 - k / n) ** batch)


def batched_decode_rate_upper_bound(
    geometry: MoeGeometry,
    bandwidth_gb_per_s: float,
    bytes_per_param: float,
    batch: int,
) -> float:
    """Aggregate tok/s upper bound for a batch of B concurrent decode streams."""
    distinct = expected_distinct_experts(geometry.n_experts, geometry.experts_per_token, batch)
    streamed_b = geometry.shared_params_b + geometry.per_expert_params_b * distinct
    return batch * bandwidth_gb_per_s / (streamed_b * bytes_per_param)


def memory_cost_per_stream_b(geometry: MoeGeometry, batch: int) -> float:
    """Billions of resident weight parameters carried per concurrent stream. The solo user
    carries all of P_total for one stream; a provider divides it by the batch."""
    return geometry.total_params_b / batch
