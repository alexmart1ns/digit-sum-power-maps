"""Stratified (k, b) grid for the section-10 campaign.

Not a rectangle. Layers densify where the archived sweep already has signal:
exact matches (Δ = 0) and explosion peaks (large Δ). Cost is cut by the same
``M`` ceiling the sweep uses.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from dspm.core import contraction_bound, estimate_pow_digits
from dspm.numtheory import divisors, is_prime, omega

__all__ = [
    "GridCell",
    "GridSpec",
    "default_prior_csv",
    "load_prior_summary",
    "smart_grid",
]

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class GridCell:
    k: int
    b: int
    strata: tuple[str, ...]
    reason: str = ""

    @property
    def m(self) -> int:
        return self.b - 1


@dataclass(frozen=True)
class GridSpec:
    """Size knobs. ``quick`` is for tests; ``full`` is the overnight campaign."""

    k_tight: int = 80
    k_structure: int = 60
    densify_k_window: int = 6
    densify_b_window: int = 2
    top_delta: int = 12
    max_exact_seeds: int = 40
    deep_cap: int = 8
    split_pairs: tuple[tuple[int, int], ...] = ((3, 10), (2, 16), (5, 10))
    max_M: int = 2_000_000
    max_pow_digits: int = 200_000
    max_work: int = 0  # extra cap on k * M; 0 disables
    max_base: int = 80
    structure_moduli: tuple[int, ...] = ()


def quick_spec() -> GridSpec:
    return GridSpec(
        k_tight=24,
        k_structure=20,
        densify_k_window=2,
        densify_b_window=1,
        top_delta=4,
        max_exact_seeds=8,
        deep_cap=3,
        split_pairs=((3, 10), (2, 10)),
        max_M=50_000,
        max_work=400_000,
        max_base=40,
        structure_moduli=(2, 6, 30),
    )


def full_spec() -> GridSpec:
    return GridSpec(
        k_tight=400,
        k_structure=200,
        densify_k_window=8,
        densify_b_window=2,
        top_delta=15,
        max_exact_seeds=69,
        deep_cap=16,
        split_pairs=((3, 10), (2, 16), (5, 10), (3, 16), (7, 10)),
        max_M=2_000_000,
        max_base=80,
        structure_moduli=(),
    )


def default_prior_csv(repo: Path | None = None) -> Path | None:
    sweeps = (repo or REPO_ROOT) / "data" / "sweeps"
    csvs = sorted(sweeps.glob("summary_*.csv"))
    return csvs[-1] if csvs else None


def load_prior_summary(path: Path | None = None) -> list[dict]:
    path = path or default_prior_csv()
    if path is None or not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _as_int(row: dict, key: str) -> int | None:
    raw = row.get(key)
    if raw is None or raw == "":
        return None
    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return None


def _prior_pairs(
    records: Sequence[dict],
    *,
    delta_eq: int | None = None,
    sort_delta_desc: bool = False,
    limit: int | None = None,
) -> list[tuple[int, int, int]]:
    rows = []
    for rec in records:
        if rec.get("status") not in (None, "", "ok"):
            continue
        k, b, delta = _as_int(rec, "k"), _as_int(rec, "b"), _as_int(rec, "delta")
        if k is None or b is None or delta is None:
            continue
        if delta_eq is not None and delta != delta_eq:
            continue
        rows.append((k, b, delta))
    if sort_delta_desc:
        rows.sort(key=lambda t: t[2], reverse=True)
    if limit is not None:
        rows = rows[:limit]
    return rows


def _primes_upto(n: int) -> list[int]:
    return [p for p in range(2, n + 1) if is_prime(p)]


def _primorials_upto(limit: int) -> list[int]:
    out = []
    acc = 1
    for p in _primes_upto(200):
        nxt = acc * p
        if nxt > limit:
            break
        acc = nxt
        out.append(acc)
    return out


def _structure_moduli(spec: GridSpec) -> list[int]:
    if spec.structure_moduli:
        return list(spec.structure_moduli)
    moduli = set(_primorials_upto(30030))  # 2*3*5*7*11*13
    moduli.update(_primes_upto(80))
    moduli.update(p * q for p in _primes_upto(30) for q in _primes_upto(30) if p < q and p * q <= 300)
    moduli.update(p**e for p in (2, 3, 5, 7) for e in range(1, 8) if p**e <= 256)
    moduli.discard(1)
    return sorted(m for m in moduli if m >= 1 and m + 1 <= spec.max_base)


def _k_for_modulus(m: int, k_max: int) -> list[int]:
    ks: set[int] = {1}
    ks.update(p for p in _primes_upto(k_max) if p % 2 == 1)
    e, p2 = 1, 2
    while p2 <= k_max:
        ks.add(p2)
        e += 1
        p2 = 2**e
    for g in divisors(m):
        k = g
        while k <= k_max:
            if k >= 1:
                ks.add(k)
            k += g
            if k // g > 12:
                break
    return sorted(k for k in ks if 1 <= k <= k_max)


def _affordable(k: int, b: int, spec: GridSpec) -> bool:
    if k < 1 or b < 2 or b > spec.max_base:
        return False
    M = contraction_bound(k, b, hard_cap=spec.max_M)
    if M > spec.max_M:
        return False
    if spec.max_work and k * M > spec.max_work:
        return False
    if estimate_pow_digits(k, b, M) > spec.max_pow_digits:
        return False
    return True


def _neighbourhood(
    k0: int, b0: int, spec: GridSpec
) -> Iterable[tuple[int, int]]:
    for k in range(max(1, k0 - spec.densify_k_window), k0 + spec.densify_k_window + 1):
        for b in range(max(2, b0 - spec.densify_b_window), b0 + spec.densify_b_window + 1):
            yield k, b


def _stratum_a(spec: GridSpec) -> list[tuple[int, int, str]]:
    cells = []
    for b in (2, 3, 4, 5, 6, 8, 10):
        for k in range(1, spec.k_tight + 1):
            cells.append((k, b, f"tightness b={b}"))
    return cells


def _stratum_b(spec: GridSpec) -> list[tuple[int, int, str]]:
    cells = []
    for m in _structure_moduli(spec):
        b = m + 1
        for k in _k_for_modulus(m, spec.k_structure):
            cells.append((k, b, f"omega(m)={omega(m)} m={m}"))
    return cells


def _stratum_c(prior: Sequence[dict], spec: GridSpec) -> list[tuple[int, int, str]]:
    cells = []
    seeds = _prior_pairs(prior, sort_delta_desc=True, limit=spec.top_delta)
    if not seeds:
        seeds = [(451, 32, 98), (493, 36, 86), (379, 39, 86), (181, 32, 80)]
        seeds = seeds[: spec.top_delta]
    for k0, b0, delta in seeds:
        for k, b in _neighbourhood(k0, b0, spec):
            cells.append((k, b, f"explode around ({k0},{b0}) Δ={delta}"))
    return cells


def _stratum_d(prior: Sequence[dict], spec: GridSpec) -> list[tuple[int, int, str]]:
    cells = []
    seeds = _prior_pairs(prior, delta_eq=0, limit=spec.max_exact_seeds)
    if not seeds:
        seeds = [(1, 2, 0), (2, 10, 0), (1, 3, 0), (7, 2, 0)]
    for k0, b0, _ in seeds:
        for k, b in _neighbourhood(k0, b0, spec):
            cells.append((k, b, f"exact-match around ({k0},{b0})"))
        cells.append((k0, b0, f"exact-match seed ({k0},{b0})"))
    return cells


PREFERRED_DEEP = (
    (3, 10),
    (2, 10),
    (5, 10),
    (2, 16),
    (3, 16),
    (7, 10),
    (4, 10),
    (3, 8),
)


def _stratum_e(chosen: Sequence[tuple[int, int]], spec: GridSpec) -> list[tuple[int, int, str]]:
    chosen_set = set(chosen)
    picks: list[tuple[int, int, str]] = []
    seen: set[tuple[int, int]] = set()

    def take(k: int, b: int) -> None:
        if (k, b) in seen or (k, b) not in chosen_set:
            return
        if len(picks) >= spec.deep_cap:
            return
        seen.add((k, b))
        picks.append((k, b, "deep orbit+degree"))

    for k, b in PREFERRED_DEEP:
        take(k, b)
    for k, b in sorted(chosen, key=lambda t: (-t[0], t[1])):
        if k >= 2:
            take(k, b)
        if len(picks) >= spec.deep_cap:
            break
    if not picks:
        picks = [(3, 10, "deep orbit+degree"), (2, 10, "deep orbit+degree")]
    return picks


def _stratum_f(spec: GridSpec) -> list[tuple[int, int, str]]:
    return [(k, b, "split Fourier") for k, b in spec.split_pairs]


def smart_grid(
    mode: str = "quick",
    spec: GridSpec | None = None,
    prior_path: Path | None = None,
    repo: Path | None = None,
) -> list[GridCell]:
    """Build the unique (k, b) list tagged with the strata that claimed it."""
    if spec is None:
        spec = quick_spec() if mode != "full" else full_spec()
    prior = load_prior_summary(prior_path or default_prior_csv(repo))

    bag: dict[tuple[int, int], list[tuple[str, str]]] = {}

    def add(stratum: str, items: Iterable[tuple[int, int, str]]) -> None:
        for k, b, reason in items:
            if not _affordable(k, b, spec):
                continue
            bag.setdefault((k, b), []).append((stratum, reason))

    add("A", _stratum_a(spec))
    add("B", _stratum_b(spec))
    add("C", _stratum_c(prior, spec))
    add("D", _stratum_d(prior, spec))
    # E is a subsample of whatever A–D already kept.
    surviving = sorted(bag)
    add("E", _stratum_e(surviving, spec))
    add("F", _stratum_f(spec))

    cells = []
    for (k, b), tags in sorted(bag.items()):
        strata = tuple(sorted({s for s, _ in tags}))
        reason = "; ".join(r for _, r in tags)
        cells.append(GridCell(k=k, b=b, strata=strata, reason=reason))
    return cells


def cells_for_stratum(cells: Sequence[GridCell], name: str) -> list[GridCell]:
    return [c for c in cells if name in c.strata]
