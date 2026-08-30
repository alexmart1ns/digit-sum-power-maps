"""Statistical patterns over a sweep dataset.

These are honest correlations, not closed forms. Two cautions are built in
because the first pass got them wrong:

*Parity confound.* Comparing "prime k" against "composite k" mostly measures
parity, since 2 is the only even prime and about half of the composites are
even, while ``2 | k`` collapses the 2-part of every local unit group and so
cuts the cycle count hard. `exponent_class_table` therefore reports the
odd-only comparison alongside the raw one.

*Aggregation across moduli.* Grouping by v_2(gcd(k, b-1)) across different b
mixes moduli with different 2-power structure, which manufactures a spurious
geometric trend. `gcd_table` reports within-modulus spread so the reader can
see whether a group mean means anything.
"""

from __future__ import annotations

import gzip
import json
import math
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .numtheory import is_prime, num_divisors, omega, v2

__all__ = [
    "load_records",
    "enrich",
    "pearson",
    "correlation_table",
    "gcd_table",
    "exponent_class_table",
    "density_law_check",
    "exact_match_profile",
]


def load_records(path: str | Path, status: str = "ok") -> list[dict[str, Any]]:
    """Read a ``results_*.jsonl`` (optionally gzipped) sweep dataset."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    records = []
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue  # tolerate a partial last line from a live run
            if status is None or rec.get("status") == status:
                records.append(rec)
    return records


def enrich(records: Iterable[dict[str, Any]]) -> None:
    """Attach number-theoretic predictors to each record, in place."""
    for rec in records:
        k, m = rec["k"], rec["m"]
        g = math.gcd(k, m) if m >= 1 else 0
        rec["gcd_k_m"] = g
        rec["v2_gcd"] = v2(g)
        rec["k_prime"] = int(is_prime(k))
        rec["k_odd"] = int(k % 2 == 1)
        rec["k_ndiv"] = num_divisors(k)
        rec["omega_m"] = omega(m)
        rec["k_mod_m"] = (k % m) if m >= 1 else 0


def pearson(pairs: Sequence[tuple[float, float]]) -> tuple[float | None, int]:
    """Pearson R and sample size. Returns (None, n) when a variance vanishes."""
    n = len(pairs)
    if n < 2:
        return None, n
    mx = sum(x for x, _ in pairs) / n
    my = sum(y for _, y in pairs) / n
    cov = sum((x - mx) * (y - my) for x, y in pairs)
    vx = sum((x - mx) ** 2 for x, _ in pairs)
    vy = sum((y - my) ** 2 for _, y in pairs)
    if vx == 0 or vy == 0:
        return None, n
    return cov / math.sqrt(vx * vy), n


def correlation_table(
    records: Sequence[dict[str, Any]],
    predictors: Sequence[str] = (
        "gcd_k_m",
        "v2_gcd",
        "k_prime",
        "k_odd",
        "k_ndiv",
        "omega_m",
        "k",
        "b",
        "k_mod_m",
    ),
    targets: Sequence[str] = ("cyc_modular", "num_attractors", "delta", "max_tail_depth_overall"),
) -> list[dict[str, Any]]:
    rows = []
    for p in predictors:
        row: dict[str, Any] = {"predictor": p}
        for t in targets:
            pairs = [
                (float(r[p]), float(r[t]))
                for r in records
                if r.get(p) is not None and r.get(t) is not None
            ]
            r_value, n = pearson(pairs)
            row[t] = r_value
            row[f"n_{t}"] = n
        rows.append(row)
    return rows


def gcd_table(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Excess statistics grouped by gcd(k, b-1), with spread and modulus count.

    ``n_moduli`` and ``delta_stdev`` are the honesty columns: a group mean built
    from many different moduli, with large spread, is not evidence of a
    per-system law.
    """
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        groups[rec["gcd_k_m"]].append(rec)

    rows = []
    for g in sorted(groups):
        sub = groups[g]
        deltas = [r["delta"] for r in sub]
        rows.append(
            {
                "gcd": g,
                "n_pairs": len(sub),
                "n_moduli": len({r["m"] for r in sub}),
                "delta_mean": mean(deltas),
                "delta_stdev": pstdev(deltas) if len(deltas) > 1 else 0.0,
                "delta_max": max(deltas),
                "count_mean": mean([r["num_attractors"] for r in sub]),
            }
        )
    return rows


def exponent_class_table(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attractor counts by exponent class, with the parity confound controlled.

    The raw prime-versus-composite contrast is reported first, then the same
    contrast restricted to odd k, then parity on its own. If the odd-only rows
    agree, the effect is parity and not primality.
    """
    def stats(label: str, subset: Sequence[dict[str, Any]]) -> dict[str, Any] | None:
        if not subset:
            return None
        return {
            "class": label,
            "n": len(subset),
            "count_mean": mean([r["num_attractors"] for r in subset]),
            "cyc_mean": mean([r["cyc_modular"] for r in subset]),
            "delta_mean": mean([r["delta"] for r in subset]),
        }

    usable = [r for r in records if r["k"] >= 2]
    rows = [
        stats("prime k (raw)", [r for r in usable if r["k_prime"]]),
        stats("composite k (raw)", [r for r in usable if not r["k_prime"]]),
        stats("odd prime k", [r for r in usable if r["k_prime"] and r["k_odd"]]),
        stats("odd composite k", [r for r in usable if not r["k_prime"] and r["k_odd"]]),
        stats("odd k (any)", [r for r in usable if r["k_odd"]]),
        stats("even k (any)", [r for r in usable if not r["k_odd"]]),
    ]
    return [r for r in rows if r is not None]


def density_law_check(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Verify the aggregate density law on the sweep records.

    Uses the integer form when the sweep stored ``signature_mass_check``: the
    physical basin mass of each signature must equal, exactly, the count of
    integers in the window whose residue lies in that modular basin. That is a
    far stronger test than checking |q_i - p_i| against a loose bound.
    """
    exact_total = exact_ok = 0
    errors: list[float] = []
    for rec in records:
        checks = rec.get("signature_mass_check")
        if not checks:
            continue
        for entry in checks:
            exact_total += 1
            exact_ok += int(entry["exact_match"])
            window = rec["M"]
            if window:
                measured = entry["residue_mass_in_window"] / window
                errors.append(abs(measured - entry["modular_weight"]))
    return {
        "integer_identity_checked": exact_total,
        "integer_identity_exact": exact_ok,
        "integer_identity_rate": (exact_ok / exact_total) if exact_total else None,
        "mean_abs_error": mean(errors) if errors else None,
        "max_abs_error": max(errors) if errors else None,
    }


def exact_match_profile(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Where does |C| = Cyc hold exactly? (Problem 10.2)"""
    exact = [r for r in records if r.get("delta") == 0]
    by_base: dict[int, int] = defaultdict(int)
    for rec in exact:
        by_base[rec["b"]] += 1
    return {
        "n_exact": len(exact),
        "n_total": len(records),
        "rate": (len(exact) / len(records)) if records else None,
        "by_base": dict(sorted(by_base.items())),
        "max_k_with_exact": max((r["k"] for r in exact), default=None),
        "note": "the rate is strongly range-dependent; see Problem 10.2",
    }
