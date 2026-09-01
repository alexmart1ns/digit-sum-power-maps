"""Orbit-length miner for Problem 10.3.

For n with D base-b digits, f(n) ≤ k(b−1)D, so after one or two iterates the
value is already O(k D log b) or smaller. L(k,b,N) is therefore expected to
be 2 + max tail depth on [1, M] once N is large; the maximizer should sit at
moderate n, not at the far end of the window.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Any

from dspm.core import f_kb, num_digits
from dspm.dynamics import FiniteSystem

__all__ = ["max_orbit_in_window", "orbit_length", "sample_orbit_by_digits"]

_GUARD = 10_000


def orbit_length(n: int, system: FiniteSystem) -> int:
    """Steps from n to its attractor, including the tail inside [1, M]."""
    if n < 1:
        raise ValueError("n must be >= 1")
    steps = 0
    k, b, M = system.k, system.b, system.M
    while n > M:
        n = f_kb(n, k, b)
        steps += 1
        if steps >= _GUARD:
            return steps
    return steps + int(system.tail_depth[n])


def max_orbit_in_window(system: FiniteSystem, N: int | None = None) -> dict[str, Any]:
    """Exhaustive max orbit length among n ≤ min(N, M), plus the witness."""
    limit = system.M if N is None else min(N, system.M)
    best = -1
    witness = 1
    for n in range(1, limit + 1):
        length = int(system.tail_depth[n])
        if length > best:
            best = length
            witness = n
    return {
        "N": limit,
        "L": best,
        "witness": witness,
        "witness_digits": num_digits(witness, system.b),
        "max_tail_on_M": max(int(system.tail_depth[n]) for n in range(1, system.M + 1)),
    }


def sample_orbit_by_digits(
    system: FiniteSystem,
    digit_lengths: Sequence[int],
    samples_per_band: int = 200,
    seed: int = 0,
) -> dict[str, Any]:
    """Monte-Carlo L(k,b,N) on digit bands, to test the O(log N) claim."""
    rng = random.Random(seed)
    k, b = system.k, system.b
    bands = []
    global_max = 0
    global_witness = 1
    for D in digit_lengths:
        lo, hi = b ** (D - 1), b**D - 1
        if hi < lo:
            continue
        best = 0
        witness = lo
        total = 0
        for _ in range(samples_per_band):
            n = rng.randint(lo, hi)
            length = orbit_length(n, system)
            total += length
            if length > best:
                best = length
                witness = n
        bands.append(
            {
                "D": D,
                "N": hi,
                "logb_N": D,
                "L_max": best,
                "L_mean": round(total / samples_per_band, 4),
                "witness": witness,
            }
        )
        if best > global_max:
            global_max = best
            global_witness = witness
    max_tail = max((int(system.tail_depth[n]) for n in range(1, system.M + 1)), default=0)
    return {
        "k": k,
        "b": b,
        "max_tail_on_M": max_tail,
        "bands": bands,
        "L_global_max": global_max,
        "witness": global_witness,
        "bounded_by_two_plus_tail": all(
            row["L_max"] <= 2 + max_tail for row in bands
        ),
    }
