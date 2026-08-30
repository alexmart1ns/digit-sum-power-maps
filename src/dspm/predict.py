"""Parameter-free prediction of the split oscillation (section 7.5).

The mechanism: basin membership of a large n is decided by where its orbit
first lands inside the trapping region [1, M]. The first iterate
m_1 = S_b(n^k) is asymptotically Gaussian with mean (b-1)/2 per digit and
variance (b^2-1)/12 per digit -- the local limit theorem for digit sums of
polynomial sequences. As D grows the Gaussian centre sweeps upward across the
*fixed* integer-to-attractor labelling, and the share falling in each
attractor's basin oscillates.

Nothing here is fitted. The only empirical ingredient is the exact labelling
a(v), computed from the dynamics itself.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from .core import f_kb
from .dynamics import FiniteSystem
from .modular import structure

__all__ = ["attractor_labels_upto", "digit_count_mixture", "predict_split"]


def attractor_labels_upto(V: int, system: FiniteSystem) -> list[int]:
    """a(v) for 1 <= v <= V: index of the attractor that v reaches."""
    labels = [-1] * (V + 1)
    for v in range(1, V + 1):
        w = v
        while w > system.M:
            w = f_kb(w, system.k, system.b)
        labels[v] = system.label[w]
    return labels


def digit_count_mixture(D: int, k: int, b: int) -> dict[int, float]:
    """Weights w_L = fraction of n with D base-b digits whose k-th power has L.

    Continuous approximation: n^k has L digits exactly when n lies in
    [b^((L-1)/k), b^(L/k)), and n is uniform on the band.
    """
    lo, hi = b ** (D - 1), b**D
    total = hi - lo
    weights: dict[int, float] = {}
    for L in range(k * (D - 1) + 1, k * D + 1):
        left = b ** ((L - 1) / k)
        right = b ** (L / k)
        overlap = max(0.0, min(hi, right) - max(lo, left))
        if overlap > 0:
            weights[L] = overlap / total
    return weights


def _gaussian(v: float, mu: float, sigma: float) -> float:
    return math.exp(-0.5 * ((v - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def predict_split(
    D: int,
    system: FiniteSystem,
    signature: frozenset[int],
    labels: Sequence[int],
    targets: Sequence[int],
    modular_weight: float,
) -> dict[int, float]:
    """Predicted global mass of each target attractor at digit length D.

    The first iterate is modelled as a digit-count mixture of Gaussians,
    restricted to the residue classes feeding ``signature``, then convolved
    with the exact labelling and scaled by the signature's modular weight p_i.
    """
    k, b = system.k, system.b
    m = b - 1
    mod = structure(k, m)
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    if not feeding:
        raise ValueError(f"no residue class feeds signature {sorted(signature)}")

    V = len(labels) - 1
    density: dict[int, float] = {}
    for L, weight in digit_count_mixture(D, k, b).items():
        mu = (b - 1) / 2 * L
        sigma = math.sqrt(L * (b * b - 1) / 12)
        lo = max(1, int(mu - 6 * sigma))
        hi = min(V, int(mu + 6 * sigma))
        for r in feeding:
            v = lo + ((r - lo) % m)
            while v <= hi:
                if v >= 1:
                    density[v] = density.get(v, 0.0) + weight * _gaussian(v, mu, sigma)
                v += m

    total = sum(density.values())
    out = {t: 0.0 for t in targets}
    if total == 0:
        return {t: float("nan") for t in targets}
    for v, mass in density.items():
        label = labels[v]
        if label in out:
            out[label] += mass / total
    return {t: out[t] * modular_weight for t in out}
