"""Cross-domain microbenchmark.

Times ``N`` ``fork + abort`` cycles in four of the V-domains. The point
is *not* absolute throughput — these are pure-Python dataclasses — but
the **relative** cost across domains, which should be roughly constant
because they all share the same :class:`VLayer` / :class:`VVersion`
primitives.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from v_universal.bio import VBio
from v_universal.consciousness import VConsciousness
from v_universal.economy import InsufficientFunds, VEconomy
from v_universal.hardware import VHardware


def _bench_hardware(n: int) -> float:
    hw = VHardware()
    t0 = time.perf_counter()
    for i in range(n):
        hw.begin_tx()
        hw.write_reg(0, i)
        hw.abort_tx()
    return time.perf_counter() - t0


def _bench_bio(n: int) -> float:
    bio = VBio(genome_size=64, seed=42)
    t0 = time.perf_counter()
    for _ in range(n):
        v = bio.genome.fork()
        bio.mutate(v, rate=0.01)
        v.abort()
    return time.perf_counter() - t0


def _bench_economy(n: int) -> float:
    eco = VEconomy()
    t0 = time.perf_counter()
    for _ in range(n):
        v = eco.ledger.fork()
        try:
            eco.transfer(v, "alice", "bob", 1)
        except InsufficientFunds:
            pass
        v.abort()
    return time.perf_counter() - t0


def _bench_consciousness(n: int) -> float:
    m = VConsciousness()
    t0 = time.perf_counter()
    for i in range(n):
        v = m.mind.fork()
        m.think(v, f"thought {i}")
        v.abort()
    return time.perf_counter() - t0


_BENCHMARKS: dict[str, Callable[[int], float]] = {
    "V-HARDWARE": _bench_hardware,
    "V-BIO": _bench_bio,
    "V-ECONOMY": _bench_economy,
    "V-CONSCIOUSNESS": _bench_consciousness,
}


def bench_universal(n: int = 10000) -> dict[str, float]:
    """Run ``n`` fork/abort cycles in each V-domain.

    Returns
    -------
    dict
        Mapping ``{domain_name: seconds_elapsed}``.
    """

    if n <= 0:
        raise ValueError("n must be positive")
    return {name: fn(n) for name, fn in _BENCHMARKS.items()}


def format_results(results: dict[str, float], n: int) -> str:
    """Render ``results`` as a human-readable table."""

    lines = [f"{'domain':<20} {'seconds':>10} {'µs/op':>10}"]
    for name, t in results.items():
        us_per_op = t / n * 1e6
        lines.append(f"{name:<20} {t:>10.4f} {us_per_op:>10.2f}")
    return "\n".join(lines)
