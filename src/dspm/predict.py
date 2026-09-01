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

__all__ = [
    "attractor_labels_upto",
    "digit_count_mixture",
    "first_landing",
    "predict_split",
]


def first_landing(v: int, system: FiniteSystem) -> tuple[int, int]:
    """First iterate of f_{k,b} that lies in [1, M], and step count.

  Returns ``(w, t)`` with ``w = g(v)`` the landing value and ``t`` the number
  of map applications (``t = 0`` when ``v <= M``).
    """
    if v < 1:
        raise ValueError("v must be >= 1")
    steps = 0
    w = v
    while w > system.M:
        w = f_kb(w, system.k, system.b)
        steps += 1
    return w, steps


def attractor_labels_upto(V: int, system: FiniteSystem) -> list[int]:
    """a(v) for 1 <= v <= V: index of the attractor that v reaches."""
    labels = [-1] * (V + 1)
    for v in range(1, V + 1):
        w, _ = first_landing(v, system)
        labels[v] = system.label[w]
    return labels


def digit_count_mixture(D: int, k: int, b: int) -> dict[int, float]:
    """Weights w_L = fraction of n with D base-b digits whose k-th power has L.

    Continuous approximation: n^k has L digits exactly when n lies in
    [b^((L-1)/k), b^(L/k)), and n is uniform on the band.
    """
    lo_log, hi_log = float(D - 1), float(D)
    band_log_w = hi_log - lo_log
    denom = float(b) ** band_log_w - 1.0
    weights: dict[int, float] = {}
    for L in range(k * (D - 1) + 1, k * D + 1):
        left_log = (L - 1) / k
        right_log = L / k
        t_lo = max(lo_log, left_log)
        t_hi = min(hi_log, right_log)
        if t_hi <= t_lo:
            continue
        num = float(b) ** (t_hi - lo_log) - float(b) ** (t_lo - lo_log)
        if num > 0:
            weights[L] = num / denom
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

    The first iterate is modelled as a digit-count mixture of Gaussians.
    Digit-sum congruence is S_b(n^k) ≡ n^k (mod b-1), so the lattice is
    v ≡ r^k for each residue r feeding ``signature`` — not v ≡ r. Then
    convolved with the exact labelling and scaled by the modular weight p_i.
    """
    k, b = system.k, system.b
    m = b - 1
    mod = structure(k, m)
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    if not feeding:
        raise ValueError(f"no residue class feeds signature {sorted(signature)}")
    images = [pow(r, k, m) for r in feeding]

    V = len(labels) - 1
    density: dict[int, float] = {}
    for L, weight in digit_count_mixture(D, k, b).items():
        mu = (b - 1) / 2 * L
        sigma = math.sqrt(L * (b * b - 1) / 12)
        lo = max(1, int(mu - 6 * sigma))
        hi = min(V, int(mu + 6 * sigma))
        for q in images:
            v = lo + ((q - lo) % m)
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
