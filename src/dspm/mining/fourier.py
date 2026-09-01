"""Gaussian vs independent-digit Fourier inversion for the split (Problem 10.6).

The numerical Gaussian of §7.5 is the local-limit leading term for S_b(n^k).
The characteristic function of one base-b digit is φ(t) = (1/b) Σ_{d=0}^{b-1}
e^{it d}; φ(t)^L is inverted exactly by the L-fold convolution of the uniform
digit law. That convolution *is* the truncated Mellin–Perron / Delange local
term for independent digits. Digit dependence inside n^k is the remainder.

Whether the quasi-periodic split is already implied by Delange / Drmota–Grabner
reduces to: the split is this oscillating law convolved with a *fixed*
integer-to-attractor labelling a(v). The oscillation in D is then the
classical log-periodic fluctuation, pushed through a(v). This module compares
MAE, it does not prove the implication.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from dspm.dynamics import FiniteSystem, build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto, digit_count_mixture, predict_split
from dspm.split import split_curves

__all__ = [
    "compare_split_models",
    "independent_digit_sum_pmf",
    "predict_split_fourier",
]


def independent_digit_sum_pmf(L: int, b: int) -> list[float]:
    """P(S = s) for S the sum of L i.i.d. uniform digits in {0, ..., b-1}.

    Exact inverse Fourier transform of φ(t)^L on the integer lattice.
    """
    if L < 0 or b < 2:
        raise ValueError("need L >= 0 and b >= 2")
    pmf = [1.0]
    for _ in range(L):
        nxt = [0.0] * (len(pmf) + b - 1)
        scale = 1.0 / b
        for s, w in enumerate(pmf):
            if w == 0.0:
                continue
            for d in range(b):
                nxt[s + d] += w * scale
        pmf = nxt
    return pmf


def predict_split_fourier(
    D: int,
    system: FiniteSystem,
    signature: frozenset[int],
    labels: Sequence[int],
    targets: Sequence[int],
    modular_weight: float,
) -> dict[int, float]:
    """Same pipeline as ``predict_split``, replacing the Gaussian by φ(t)^L."""
    k, b = system.k, system.b
    m = b - 1
    mod = structure(k, m)
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    if not feeding:
        raise ValueError(f"no residue class feeds signature {sorted(signature)}")

    V = len(labels) - 1
    density: dict[int, float] = {}
    for L, weight in digit_count_mixture(D, k, b).items():
        pmf = independent_digit_sum_pmf(L, b)
        for r in feeding:
            v = r if r != 0 else m
            while v < len(pmf) and v <= V:
                if v >= 1:
                    density[v] = density.get(v, 0.0) + weight * pmf[v]
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


def _mae(pred: dict[int, float], measured: dict[int, float]) -> float:
    keys = [i for i in pred if i in measured]
    if not keys:
        return float("nan")
    return sum(abs(pred[i] - measured[i]) for i in keys) / len(keys)


def compare_split_models(
    k: int = 3,
    b: int = 10,
    digit_lengths: Sequence[int] | None = None,
    samples_per_band: int = 4000,
    seed: int = 0,
    residue: int = 0,
) -> dict[str, Any]:
    """MAE of Gaussian vs independent-digit Fourier vs Monte-Carlo split."""
    lengths = list(digit_lengths or (8, 16, 24, 32))
    system = build_system(k, b)
    mod = structure(k, b - 1)
    signature = mod.signature_of_residue(residue)
    weight = mod.weights[mod.owner[residue % max(b - 1, 1)]]
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    if len(targets) < 2:
        return {
            "k": k,
            "b": b,
            "status": "no_split",
            "note": "signature has a single attractor; Problem 10.6 is vacuous here",
        }

    max_L = k * max(lengths)
    V = min(int((b - 1) * max_L) + 8, 200_000)
    labels = attractor_labels_upto(V, system)
    measured = split_curves(
        k, b, lengths, samples_per_band=samples_per_band, seed=seed, system=system
    )
    noise = 0.5 / math.sqrt(samples_per_band)

    gauss_maes = []
    four_maes = []
    per_D = []
    for j, D in enumerate(lengths):
        g = predict_split(D, system, signature, labels, targets, weight)
        f = predict_split_fourier(D, system, signature, labels, targets, weight)
        mrow = {i: measured.curves[i][j] for i in targets}
        mae_g = _mae(g, mrow)
        mae_f = _mae(f, mrow)
        gauss_maes.append(mae_g)
        four_maes.append(mae_f)
        per_D.append(
            {
                "D": D,
                "mae_gaussian": round(mae_g, 6),
                "mae_fourier": round(mae_f, 6),
                "gaussian": {str(i): round(g[i], 6) for i in targets},
                "fourier": {str(i): round(f[i], 6) for i in targets},
                "measured": {str(i): round(mrow[i], 6) for i in targets},
            }
        )

    return {
        "k": k,
        "b": b,
        "signature": sorted(signature),
        "targets": targets,
        "samples_per_band": samples_per_band,
        "noise_floor": round(noise, 6),
        "mae_gaussian": round(sum(gauss_maes) / len(gauss_maes), 6),
        "mae_fourier": round(sum(four_maes) / len(four_maes), 6),
        "fourier_beats_gaussian": sum(four_maes) < sum(gauss_maes),
        "within_noise": {
            "gaussian": all(x <= 3 * noise for x in gauss_maes),
            "fourier": all(x <= 3 * noise for x in four_maes),
        },
        "per_D": per_D,
        "literature_note": (
            "Delange / Drmota–Grabner already give log-periodic fluctuation of "
            "S_b(n^k). The split is that law convolved with the fixed labelling "
            "a(v); this comparison does not by itself prove the implication."
        ),
    }
