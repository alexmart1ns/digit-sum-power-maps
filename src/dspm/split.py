"""Measuring the intra-signature basin split (section 7).

Theorem 5.3 pins the aggregate mass of each residue signature to p_i exactly.
It says nothing about how that mass divides among several attractors sharing
the signature. This module measures the division, restricted to integers with
exactly D base-b digits, which is the scale at which the phenomenon is visible.

The headline finding is that the split does not converge: competing attractors
exchange mass quasi-periodically in D while always summing to p_i.

A warning that cost the original analysis a wrong conclusion: do *not* judge
convergence from the drift over a single step of D. An oscillation has long
flat stretches, and sampling noise inside one of them looks exactly like
convergence. `split_curves` therefore reports the whole curve, and
`oscillation_report` summarises amplitude and monotonicity over the full range.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field

from .dynamics import FiniteSystem, build_system

__all__ = ["SplitCurves", "split_curves", "oscillation_report"]


@dataclass
class SplitCurves:
    """Per-attractor mass as a function of digit length D."""

    k: int
    b: int
    digit_lengths: list[int]
    samples_per_band: int
    labels: list[str]
    signatures: list[frozenset[int]]
    curves: dict[int, list[float]] = field(default_factory=dict)

    def signature_sums(self) -> dict[frozenset[int], list[float]]:
        """Aggregate mass per signature at each D. Theorem 5.3 forces p_i."""
        groups: dict[frozenset[int], list[int]] = {}
        for i, sig in enumerate(self.signatures):
            groups.setdefault(sig, []).append(i)
        return {
            sig: [sum(self.curves[i][j] for i in idx) for j in range(len(self.digit_lengths))]
            for sig, idx in groups.items()
        }

    def amplitude(self, index: int) -> float:
        values = self.curves[index]
        return max(values) - min(values)


def split_curves(
    k: int,
    b: int,
    digit_lengths: Sequence[int],
    samples_per_band: int = 20_000,
    seed: int = 0,
    system: FiniteSystem | None = None,
) -> SplitCurves:
    """Monte-Carlo the attractor split band by band.

    For each D, sample integers uniformly from [b^(D-1), b^D - 1] and record
    which attractor each one reaches. Cost per sample is a handful of digit-sum
    iterations, so large D is cheap.

    The sampling standard error on each entry is about 0.5 / sqrt(samples).
    """
    system = system or build_system(k, b)
    rng = random.Random(seed)
    lengths = list(digit_lengths)

    out = SplitCurves(
        k=k,
        b=b,
        digit_lengths=lengths,
        samples_per_band=samples_per_band,
        labels=[str(list(a)) for a in system.attractors],
        signatures=[system.signature(i) for i in range(system.count)],
        curves={i: [] for i in range(system.count)},
    )

    for D in lengths:
        lo, hi = b ** (D - 1), b**D - 1
        counts = [0] * system.count
        for _ in range(samples_per_band):
            counts[system.attractor_of(rng.randint(lo, hi))] += 1
        for i in range(system.count):
            out.curves[i].append(counts[i] / samples_per_band)

    return out


def oscillation_report(curves: SplitCurves, noise: float | None = None) -> list[dict]:
    """Per-attractor summary: range, amplitude, and whether the curve is monotone.

    ``noise`` is the tolerance used when calling a curve monotone; it defaults
    to three sampling standard errors.
    """
    if noise is None:
        noise = 3 * 0.5 / (curves.samples_per_band**0.5)

    report = []
    for i in range(len(curves.labels)):
        values = curves.curves[i]
        decreasing = all(values[j] >= values[j + 1] - noise for j in range(len(values) - 1))
        increasing = all(values[j] <= values[j + 1] + noise for j in range(len(values) - 1))
        half = len(values) // 2
        report.append(
            {
                "attractor": curves.labels[i],
                "signature": sorted(curves.signatures[i]),
                "min": min(values),
                "max": max(values),
                "amplitude": max(values) - min(values),
                "mean_first_half": sum(values[:half]) / max(half, 1),
                "mean_second_half": sum(values[half:]) / max(len(values) - half, 1),
                "monotone": decreasing or increasing,
                "oscillates": (max(values) - min(values)) > 4 * noise
                and not (decreasing or increasing),
            }
        )
    return report
