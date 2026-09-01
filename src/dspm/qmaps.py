"""Sidecar dynamics for f(n) = S_b(Q(n)), Q in Z[x].

This module is a parallel laboratory for Remark 4.1a. It does *not* wrap or
replace ``f_kb``, ``structure(k, m)``, ``build_system``, or ``predict_split``.
Monomial maps Q(x) = x^k are available here so they can be compared in memory
against the existing engine; historical records are never rewritten.

Coefficients are little-endian: ``(a0, a1, ..., ad)`` means a0 + a1 x + ... + ad x^d.
"""

from __future__ import annotations

import math
import random
from array import array
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from .core import HAVE_GMPY2, digit_sum, num_digits
from .modular import functional_graph_cycles

if HAVE_GMPY2:  # pragma: no cover - environment dependent
    from gmpy2 import mpz
else:  # pragma: no cover

    def mpz(x):  # type: ignore[misc]
        return int(x)

__all__ = [
    "QCoeffs",
    "QModularStructure",
    "QSystem",
    "SplitCurvesQ",
    "attractor_labels_upto_Q",
    "build_system_Q",
    "contraction_bound_Q",
    "degree_Q",
    "digit_count_mixture_Q",
    "eval_Q",
    "excess_identity_holds_Q",
    "f_Qb",
    "finite_window_identity_holds",
    "format_Q",
    "leading_Q",
    "local_excess_Q",
    "monomial_Q",
    "oscillation_report_Q",
    "predict_split_Q",
    "split_curves_Q",
    "structure_Q",
]

QCoeffs = tuple[int, ...]


def monomial_Q(k: int) -> QCoeffs:
    """The monomial x^k as little-endian coefficients."""
    if k < 0:
        raise ValueError("k must be >= 0")
    return (0,) * k + (1,)


def _trim(coeffs: Sequence[int]) -> QCoeffs:
    values = tuple(int(a) for a in coeffs)
    if not values:
        raise ValueError("Q must have at least one coefficient")
    end = len(values)
    while end > 1 and values[end - 1] == 0:
        end -= 1
    return values[:end]


def degree_Q(coeffs: Sequence[int]) -> int:
    return len(_trim(coeffs)) - 1


def leading_Q(coeffs: Sequence[int]) -> int:
    return _trim(coeffs)[-1]


def format_Q(coeffs: Sequence[int]) -> str:
    """Human-readable polynomial, e.g. ``x^2 + x`` or ``2x^2 + 3x + 1``."""
    terms: list[str] = []
    for i, a in enumerate(_trim(coeffs)):
        if a == 0:
            continue
        if i == 0:
            terms.append(str(a))
            continue
        mag = abs(a)
        if i == 1:
            stem = "x" if mag == 1 else f"{mag}x"
        else:
            stem = f"x^{i}" if mag == 1 else f"{mag}x^{i}"
        if a < 0:
            terms.append(f"- {stem}" if mag == 1 or i >= 1 else f"- {mag}")
            if mag != 1 and i >= 1:
                terms[-1] = f"- {stem}"
        else:
            terms.append(stem)
    if not terms:
        return "0"
    out = terms[0]
    for t in terms[1:]:
        if t.startswith("- "):
            out += " " + t
        else:
            out += " + " + t
    return out


def eval_Q(n: int, coeffs: Sequence[int]) -> int:
    """Horner evaluation of Q(n)."""
    trimmed = _trim(coeffs)
    acc = mpz(0)
    nn = mpz(n)
    for a in reversed(trimmed):
        acc = acc * nn + int(a)
    return int(acc)


def f_Qb(n: int, coeffs: Sequence[int], b: int) -> int:
    """f(n) = S_b(Q(n)). Requires Q(n) >= 0."""
    value = eval_Q(n, coeffs)
    if value < 0:
        raise ValueError(f"Q({n}) = {value} < 0; digit-sum is defined for n >= 0")
    return digit_sum(value, b)


def contraction_bound_Q(coeffs: Sequence[int], b: int, hard_cap: int = 1 << 20) -> int:
    """A rigorous M with the recurrent set of S_b(Q(n)) inside [1, M].

    Same majorant as Lemma 3.2: S_b(Q(n)) <= (b-1) * digits_b(Q(n)). For
    degree d and leading coefficient a > 0 the digit count is ~ d log_b n.
    Implementation is independent of ``contraction_bound``.
    """
    if b < 2:
        raise ValueError("base must be >= 2")
    trimmed = _trim(coeffs)
    lead = trimmed[-1]
    deg = len(trimmed) - 1
    if lead <= 0:
        raise ValueError("leading coefficient must be positive so Q(n) >= 0 for large n")
    if deg == 0:
        const = trimmed[0]
        return min(max(const, 1), hard_cap)

    x = max(b, 2)
    log_lead = math.log(lead, b)
    for _ in range(500):
        estimated = deg * math.log(x, b) + log_lead + 1.0
        nxt = int((b - 1) * estimated) + 1
        if nxt <= x:
            q = max(eval_Q(x, trimmed), 1)
            exact = (b - 1) * num_digits(q, b)
            M = min(max(x, exact), hard_cap)
            # Enlarge until the majorant at M does not escape [1, M].
            for _ in range(32):
                qM = max(eval_Q(M, trimmed), 1)
                ceiling = (b - 1) * num_digits(qM, b)
                if ceiling <= M:
                    return M
                M = min(max(M, ceiling), hard_cap)
                if M >= hard_cap:
                    return hard_cap
            return M
        x = nxt
        if x > hard_cap:
            return hard_cap
    return min(x, hard_cap)


@dataclass(frozen=True)
class QModularStructure:
    """Functional graph of phi_Q(x) = Q(x) mod m on Z/mZ."""

    coeffs: QCoeffs
    m: int
    cycles: tuple[tuple[int, ...], ...]
    owner: tuple[int, ...]
    basin_sizes: tuple[int, ...]

    @property
    def cycle_count(self) -> int:
        return len(self.cycles)

    @property
    def weights(self) -> tuple[float, ...]:
        return tuple(s / self.m for s in self.basin_sizes)

    def signature_of_residue(self, r: int) -> frozenset[int]:
        return frozenset(self.cycles[self.owner[r % self.m]])


def structure_Q(coeffs: Sequence[int], m: int) -> QModularStructure:
    """Build the functional graph of x |-> Q(x) mod m."""
    trimmed = _trim(coeffs)
    if m <= 1:
        return QModularStructure(
            coeffs=trimmed, m=1, cycles=((0,),), owner=(0,), basin_sizes=(1,)
        )
    nxt = [eval_Q(x, trimmed) % m for x in range(m)]
    cyc = functional_graph_cycles(nxt)
    owner = [-1] * m
    for i, c in enumerate(cyc):
        for x in c:
            owner[x] = i
    for start in range(m):
        if owner[start] >= 0:
            continue
        path: list[int] = []
        x = start
        while owner[x] < 0:
            path.append(x)
            x = nxt[x]
        target = owner[x]
        for y in path:
            owner[y] = target
    sizes = [0] * len(cyc)
    for r in range(m):
        sizes[owner[r]] += 1
    return QModularStructure(
        coeffs=trimmed,
        m=m,
        cycles=tuple(tuple(c) for c in cyc),
        owner=tuple(owner),
        basin_sizes=tuple(sizes),
    )


def _int_array(size: int, fill: int = 0) -> array:
    a = array("i", bytes(4 * size))
    if fill:
        for i in range(size):
            a[i] = fill
    return a


@dataclass
class QSystem:
    """Exhaustive dynamics of S_b(Q(n)) on [1, M]. Parallel to FiniteSystem."""

    coeffs: QCoeffs
    b: int
    M: int
    attractors: tuple[tuple[int, ...], ...]
    label: Sequence[int]
    basin_sizes: tuple[int, ...]
    tail_depth: Sequence[int]
    successor: Sequence[int]

    @property
    def m(self) -> int:
        return self.b - 1

    @property
    def count(self) -> int:
        return len(self.attractors)

    def signature(self, index: int) -> frozenset[int]:
        m = self.m
        if m < 1:
            return frozenset({0})
        return frozenset(x % m for x in self.attractors[index])

    def attractor_of(self, n: int) -> int:
        if n < 1:
            raise ValueError("n must be >= 1")
        while n > self.M:
            n = f_Qb(n, self.coeffs, self.b)
        return self.label[n]

    def attractors_sharing_signature(self) -> dict[frozenset[int], list[int]]:
        out: dict[frozenset[int], list[int]] = {}
        for i in range(self.count):
            out.setdefault(self.signature(i), []).append(i)
        return out

    def basin_by_signature(self) -> dict[frozenset[int], int]:
        out: dict[frozenset[int], int] = {}
        for i in range(self.count):
            sig = self.signature(i)
            out[sig] = out.get(sig, 0) + self.basin_sizes[i]
        return out


def build_system_Q(
    coeffs: Sequence[int], b: int, M: int | None = None
) -> QSystem:
    """Build the exhaustive finite system for S_b(Q(n))."""
    trimmed = _trim(coeffs)
    if M is None:
        M = contraction_bound_Q(trimmed, b)
    nxt = _int_array(M + 1)
    for n in range(1, M + 1):
        v = f_Qb(n, trimmed, b)
        while v > M:
            v = f_Qb(v, trimmed, b)
        nxt[n] = v

    graph = [0] + [nxt[n] for n in range(1, M + 1)]
    cycles = [c for c in functional_graph_cycles(graph) if 0 not in c]

    label = _int_array(M + 1, fill=-1)
    for i, cycle in enumerate(cycles):
        for x in cycle:
            label[x] = i
    for start in range(1, M + 1):
        if label[start] >= 0:
            continue
        path: list[int] = []
        x = start
        while label[x] < 0:
            path.append(x)
            x = nxt[x]
        target = label[x]
        for y in path:
            label[y] = target

    depth = _int_array(M + 1, fill=-1)
    for cycle in cycles:
        for x in cycle:
            depth[x] = 0
    for start in range(1, M + 1):
        if depth[start] >= 0:
            continue
        path = []
        x = start
        while depth[x] < 0:
            path.append(x)
            x = nxt[x]
        d = depth[x]
        for y in reversed(path):
            d += 1
            depth[y] = d

    sizes = [0] * len(cycles)
    for n in range(1, M + 1):
        sizes[label[n]] += 1

    return QSystem(
        coeffs=trimmed,
        b=b,
        M=M,
        attractors=tuple(tuple(sorted(c)) for c in cycles),
        label=label,
        basin_sizes=tuple(sizes),
        tail_depth=depth,
        successor=nxt,
    )


def residue_occupancy(M: int, m: int, r: int) -> int:
    """How many n in [1, M] satisfy n ≡ r (mod m)."""
    if m <= 1:
        return M
    if r == 0:
        return M // m
    if r > M:
        return 0
    return (M - r) // m + 1


def finite_window_identity_holds(system: QSystem) -> bool:
    """Proposition 5.2 on the trapping window [1, M]."""
    m = system.m
    if m <= 1:
        return True
    mod = structure_Q(system.coeffs, m)
    physical = system.basin_by_signature()
    modular: dict[frozenset[int], int] = {}
    for i, cycle in enumerate(mod.cycles):
        sig = frozenset(cycle)
        feeding = [r for r in range(m) if mod.owner[r] == i]
        modular[sig] = sum(residue_occupancy(system.M, m, r) for r in feeding)
    return physical == modular


def local_excess_Q(system: QSystem) -> list[dict[str, Any]]:
    sharing = system.attractors_sharing_signature()
    rows = []
    for sig, indices in sharing.items():
        mins = [system.attractors[i][0] for i in indices]
        lengths = sorted({num_digits(v, system.b) for v in mins})
        rows.append(
            {
                "signature": sorted(sig),
                "a_i": len(indices),
                "delta_local": len(indices) - 1,
                "attractor_mins": mins,
                "cycle_lengths": [len(system.attractors[i]) for i in indices],
                "digit_lengths": lengths,
                "n_digit_layers": len(lengths),
                "basin_sizes": [system.basin_sizes[i] for i in indices],
            }
        )
    rows.sort(key=lambda r: (-r["delta_local"], r["signature"]))
    return rows


def excess_identity_holds_Q(system: QSystem, cyc: int | None = None) -> bool:
    if cyc is None:
        cyc = structure_Q(system.coeffs, max(system.m, 1)).cycle_count
    delta = system.count - cyc
    return delta == sum(row["delta_local"] for row in local_excess_Q(system))


def attractor_labels_upto_Q(V: int, system: QSystem) -> list[int]:
    labels = [-1] * (V + 1)
    for v in range(1, V + 1):
        w = v
        while w > system.M:
            w = f_Qb(w, system.coeffs, system.b)
        labels[v] = system.label[w]
    return labels


def digit_count_mixture_Q(D: int, coeffs: Sequence[int], b: int) -> dict[int, float]:
    """Weights: fraction of D-digit n for which Q(n) has L base-b digits.

    Continuous approximation Q(n) ≈ a n^d with a = leading coefficient > 0.
    """
    trimmed = _trim(coeffs)
    deg = len(trimmed) - 1
    lead = trimmed[-1]
    if deg < 1 or lead <= 0:
        return {1: 1.0}
    lo, hi = b ** (D - 1), b**D
    total = hi - lo
    lead_digits = num_digits(lead, b)
    L_lo = max(1, deg * (D - 1) + lead_digits - 2)
    L_hi = deg * D + lead_digits + 2
    weights: dict[int, float] = {}
    inv_d = 1.0 / deg
    a = float(lead)
    for L in range(L_lo, L_hi + 1):
        left = (b ** (L - 1) / a) ** inv_d
        right = (b**L / a) ** inv_d
        overlap = max(0.0, min(hi, right) - max(lo, left))
        if overlap > 0:
            weights[L] = overlap / total
    s = sum(weights.values())
    if s <= 0:
        mid = max(1, deg * D)
        return {mid: 1.0}
    if abs(s - 1.0) > 1e-9:
        weights = {L: w / s for L, w in weights.items()}
    return weights


def _gaussian(v: float, mu: float, sigma: float) -> float:
    return math.exp(-0.5 * ((v - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def predict_split_Q(
    D: int,
    system: QSystem,
    signature: frozenset[int],
    labels: Sequence[int],
    targets: Sequence[int],
    modular_weight: float,
) -> dict[int, float]:
    """Gaussian-sweep F_j for S_b(Q(n)). Does not call predict_split.

    Lattice: S_b(Q(n)) ≡ Q(n) (mod b-1), so mass sits on v ≡ Q(r) for each
    residue r that feeds ``signature``, not on v ≡ r. The classic
    ``predict_split`` still uses the feeding lattice of n.
    """
    b = system.b
    m = max(b - 1, 1)
    mod = structure_Q(system.coeffs, m)
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    if not feeding:
        raise ValueError(f"no residue class feeds signature {sorted(signature)}")
    images = [eval_Q(r, system.coeffs) % m for r in feeding]

    V = len(labels) - 1
    density: dict[int, float] = {}
    for L, weight in digit_count_mixture_Q(D, system.coeffs, b).items():
        mu = (b - 1) / 2 * L
        sigma = math.sqrt(L * (b * b - 1) / 12) if L > 0 else 1.0
        sigma = max(sigma, 1e-9)
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
        lab = labels[v]
        if lab in out:
            out[lab] += mass / total
    return {t: out[t] * modular_weight for t in out}


@dataclass
class SplitCurvesQ:
    coeffs: QCoeffs
    b: int
    digit_lengths: list[int]
    samples_per_band: int
    labels: list[str]
    signatures: list[frozenset[int]]
    curves: dict[int, list[float]] = field(default_factory=dict)

    def signature_sums(self) -> dict[frozenset[int], list[float]]:
        groups: dict[frozenset[int], list[int]] = {}
        for i, sig in enumerate(self.signatures):
            groups.setdefault(sig, []).append(i)
        return {
            sig: [sum(self.curves[i][j] for i in idx) for j in range(len(self.digit_lengths))]
            for sig, idx in groups.items()
        }


def split_curves_Q(
    coeffs: Sequence[int],
    b: int,
    digit_lengths: Sequence[int],
    samples_per_band: int = 4_000,
    seed: int = 0,
    system: QSystem | None = None,
) -> SplitCurvesQ:
    system = system or build_system_Q(coeffs, b)
    rng = random.Random(seed)
    lengths = list(digit_lengths)
    out = SplitCurvesQ(
        coeffs=system.coeffs,
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


def oscillation_report_Q(curves: SplitCurvesQ, noise: float | None = None) -> list[dict]:
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
