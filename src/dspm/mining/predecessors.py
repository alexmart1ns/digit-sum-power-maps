"""Predecessor-forest degree distribution (Problem 10.4).

The well-defined graph is the functional graph of f_{k,b} on [1, M]. In-degree
histograms plus a Clauset–Shalizi–Newman discrete power-law fit (xmin, MLE α,
KS). A slope on a log-log plot is not evidence. External predecessors n > M
are out of scope unless sampled separately.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from collections.abc import Sequence
from typing import Any

from dspm.dynamics import FiniteSystem

__all__ = ["degree_histogram", "fit_power_law", "predecessor_report"]


def degree_histogram(indeg: Sequence[int], *, skip_zero_vertex: bool = True) -> dict[int, int]:
    """Map degree -> count. Vertex 0 is unused in FiniteSystem."""
    counts: Counter[int] = Counter()
    start = 1 if skip_zero_vertex else 0
    for d in indeg[start:]:
        counts[int(d)] += 1
    return dict(sorted(counts.items()))


def _zeta(alpha: float, xmin: int, cap: int = 200_000) -> float:
    """Partial Hurwitz zeta Σ_{x=xmin}^∞ x^{-α}, truncated when terms die."""
    total = 0.0
    x = xmin
    while x <= cap:
        term = x ** (-alpha)
        total += term
        if term < 1e-18 and x > xmin + 50:
            break
        x += 1
    return total


def power_law_alpha_mle(samples: Sequence[int], xmin: int) -> float:
    """Discrete power-law MLE for α, golden-section search on (1.01, 8)."""
    xs = [x for x in samples if x >= xmin]
    n = len(xs)
    if n < 8:
        return float("nan")
    log_sum = sum(math.log(x) for x in xs)

    def nll(alpha: float) -> float:
        z = _zeta(alpha, xmin)
        if z <= 0:
            return 1e300
        return n * math.log(z) + alpha * log_sum

    lo, hi = 1.01, 8.0
    phi = (1 + math.sqrt(5)) / 2
    for _ in range(40):
        mid1 = hi - (hi - lo) / phi
        mid2 = lo + (hi - lo) / phi
        if nll(mid1) < nll(mid2):
            hi = mid2
        else:
            lo = mid1
    return 0.5 * (lo + hi)


def _ks(samples: Sequence[int], xmin: int, alpha: float) -> float:
    xs = sorted(x for x in samples if x >= xmin)
    n = len(xs)
    if n == 0 or math.isnan(alpha):
        return 1.0
    z = _zeta(alpha, xmin)
    if z <= 0:
        return 1.0
    worst = 0.0
    cdf_emp = 0.0
    cdf_mod = 0.0
    unique = sorted(set(xs))
    last = xmin - 1
    idx = 0
    for value in unique:
        for t in range(last + 1, value + 1):
            cdf_mod += (t ** (-alpha)) / z
        last = value
        while idx < n and xs[idx] == value:
            cdf_emp += 1 / n
            idx += 1
        worst = max(worst, abs(cdf_emp - cdf_mod))
    return worst


def fit_power_law(
    degrees: Sequence[int],
    xmin_max: int | None = None,
    n_synth: int = 0,
    seed: int = 0,
) -> dict[str, Any]:
    """CSN-style scan over xmin. ``n_synth``>0 adds a cheap KS p-value."""
    positive = [int(d) for d in degrees if d >= 1]
    if len(positive) < 16:
        return {
            "n": len(positive),
            "xmin": None,
            "alpha": None,
            "ks": None,
            "plausible": False,
            "note": "too few positive degrees",
        }
    unique = sorted(set(positive))
    cap = xmin_max or unique[-1]
    unique = [x for x in unique if x <= cap]
    step = max(1, len(unique) // 25)
    xmins = unique[::step][:25]
    best: dict[str, Any] | None = None
    for xmin in xmins:
        n_tail = sum(1 for x in positive if x >= xmin)
        if n_tail < 12:
            continue
        alpha = power_law_alpha_mle(positive, xmin)
        ks = _ks(positive, xmin, alpha)
        row = {"xmin": xmin, "alpha": alpha, "ks": ks, "n_tail": n_tail}
        if best is None or ks < best["ks"]:
            best = row
    if best is None:
        return {"n": len(positive), "xmin": None, "alpha": None, "ks": None, "plausible": False}

    pvalue = None
    if n_synth > 0 and not math.isnan(best["alpha"]):
        pvalue = _ks_pvalue(positive, best["xmin"], best["alpha"], n_synth, seed)

    # A conventional (lenient) CSN cutoff: p > 0.1 is "plausible". Without
    # synthetics we only report the KS and refuse to call it a power law.
    plausible = bool(pvalue is not None and pvalue > 0.1)
    return {
        "n": len(positive),
        "xmin": best["xmin"],
        "alpha": None if math.isnan(best["alpha"]) else round(best["alpha"], 4),
        "ks": round(best["ks"], 4),
        "n_tail": best["n_tail"],
        "p_value": None if pvalue is None else round(pvalue, 4),
        "plausible": plausible,
        "note": "log-log slope is not used; KS+xmin MLE only",
    }


def _sample_discrete_power_law(n: int, alpha: float, xmin: int, rng: random.Random) -> list[int]:
    out = []
    for _ in range(n):
        u = min(max(rng.random(), 1e-12), 1 - 1e-12)
        x = int(xmin * (1 - u) ** (-1 / (alpha - 1)))
        out.append(max(xmin, x))
    return out


def _ks_pvalue(
    samples: Sequence[int], xmin: int, alpha: float, n_synth: int, seed: int
) -> float:
    rng = random.Random(seed)
    tail = [x for x in samples if x >= xmin]
    ks_obs = _ks(tail, xmin, alpha)
    beat = 0
    for _ in range(n_synth):
        synth = _sample_discrete_power_law(len(tail), alpha, xmin, rng)
        if _ks(synth, xmin, alpha) >= ks_obs - 1e-15:
            beat += 1
    return beat / n_synth


def predecessor_report(system: FiniteSystem, n_synth: int = 0) -> dict[str, Any]:
    indeg = system.in_degrees()
    hist = degree_histogram(indeg)
    degrees = [d for d in indeg[1:]]
    attractor_deg = []
    for members in system.attractors:
        attractor_deg.extend(indeg[x] for x in members)
    return {
        "histogram": hist,
        "n_vertices": system.M,
        "max_degree": max(degrees) if degrees else 0,
        "mean_degree": round(sum(degrees) / len(degrees), 4) if degrees else 0.0,
        "zeros": hist.get(0, 0),
        "fit": fit_power_law(degrees, n_synth=n_synth),
        "attractor_degree_mean": (
            round(sum(attractor_deg) / len(attractor_deg), 4) if attractor_deg else 0.0
        ),
    }
