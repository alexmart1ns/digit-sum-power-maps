#!/usr/bin/env python3
"""Count side of the modular power map x -> x^k mod m.

Replaces the earlier ``cycle_collapse.py``, which drew a false conclusion. The
history is worth stating because the failure mode is instructive.

That script grouped k by (odd part, v_2) of gcd(k, lambda(m)), averaged the
cycle count within each group, observed that the group *means* agreed for
v_2 = 1, 2, 3, and concluded that the cycle count is flat for v_2 >= 1. Both
steps were wrong:

1. Equal group means do not imply a constant. For m = 37 the group values are
   {4, 6, 10} and for m = 41 they are {3, 4, 6}; the means coincide only
   because the groups contain the same multiset in the same proportions.
2. The closed form of Proposition 6.1 counts periodic *points*, and #Per is
   indeed a function of the radical of k. The number of *cycles* is not:
   cycle lengths are multiplicative orders ord_d(k), which see k modulo d.

Direct counterexamples, no averaging: Cyc(2, 41) = 3, Cyc(4, 41) = 4,
Cyc(16, 41) = 6, all with #Per = 6.

What this script does instead:

  A. checks the periodic-point closed form against brute force;
  B. checks the *cycle-count* closed form against brute force;
  C. prints the within-group spread that the old script averaged away;
  D. reports how often Cyc(2, m) != Cyc(4, m) across a range of moduli.

Usage
-----
    python scripts/cycle_structure.py
    python scripts/cycle_structure.py --m-max 400 --k-max 80
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from math import gcd
from statistics import mean, pstdev

import _bootstrap  # noqa: F401
from dspm.modular import (
    cycle_count,
    cycle_count_formula,
    periodic_point_count,
    periodic_point_count_formula,
)
from dspm.numtheory import carmichael_lambda, v2

DEFAULT_MODULI = (16, 17, 32, 37, 41, 64)


def check_closed_forms(m_max: int, k_max: int) -> dict:
    per_bad, cyc_bad, total = [], [], 0
    for m in range(2, m_max):
        for k in range(2, k_max + 1):
            total += 1
            if periodic_point_count(k, m) != periodic_point_count_formula(k, m):
                per_bad.append((k, m))
            if cycle_count(k, m) != cycle_count_formula(k, m):
                cyc_bad.append((k, m))
    return {"total": total, "per_bad": per_bad, "cyc_bad": cyc_bad}


def within_group_spread(moduli=DEFAULT_MODULI, span: int = 6) -> list:
    """Replicate the old grouping, but report spread rather than only the mean."""
    rows = []
    for m in moduli:
        lam = carmichael_lambda(m)
        groups: dict = defaultdict(list)
        for k in range(2, span * lam + 2):
            g = gcd(k, lam)
            valuation = v2(g)
            if g // 2**valuation == 1:  # odd part fixed at 1, as before
                groups[valuation].append(cycle_count(k, m))
        for valuation in sorted(groups):
            if valuation == 0:
                continue
            values = groups[valuation]
            rows.append(
                {
                    "m": m,
                    "v2": valuation,
                    "n": len(values),
                    "mean": mean(values),
                    "min": min(values),
                    "max": max(values),
                    "stdev": pstdev(values) if len(values) > 1 else 0.0,
                    "distinct": sorted(set(values)),
                    "constant": len(set(values)) == 1,
                }
            )
    return rows


def radical_sensitivity(m_max: int) -> dict:
    """How often does Cyc distinguish k = 2 from k = 4 (same radical)?"""
    differ = [m for m in range(2, m_max) if cycle_count(2, m) != cycle_count(4, m)]
    same_per = [
        m for m in differ
        if periodic_point_count_formula(2, m) == periodic_point_count_formula(4, m)
    ]
    return {"n_moduli": m_max - 2, "differ": differ, "differ_same_per": same_per}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--m-max", type=int, default=300)
    ap.add_argument("--k-max", type=int, default=60)
    args = ap.parse_args(argv)

    print("=" * 72)
    print("A/B  closed forms vs brute force")
    print("=" * 72)
    result = check_closed_forms(args.m_max, args.k_max)
    print(f"  pairs tested (k in [2,{args.k_max}], m in [2,{args.m_max})): {result['total']}")
    print(f"  #Per(k,m) = prod (1 + kappa_k(phi(p^e)))        mismatches: {len(result['per_bad'])}")
    print(f"  Cyc(k,m)  = sum over local cycle tuples          mismatches: {len(result['cyc_bad'])}")
    if result["per_bad"]:
        print(f"    first #Per mismatches: {result['per_bad'][:5]}")
    if result["cyc_bad"]:
        print(f"    first Cyc mismatches: {result['cyc_bad'][:5]}")

    print("\n" + "=" * 72)
    print("C  the old 'controlled' test, with the spread it averaged away")
    print("=" * 72)
    print("    m   v2 |    n    mean    min   max   stdev   distinct values")
    for row in within_group_spread():
        flag = "" if row["constant"] else "   <-- NOT CONSTANT"
        print(
            f"  {row['m']:4d}  {row['v2']:2d} | {row['n']:4d}  {row['mean']:6.2f}"
            f"  {row['min']:5d} {row['max']:5d}  {row['stdev']:6.2f}   {row['distinct']}{flag}"
        )
    print("\n  Equal means across v2 groups is not flatness. Direct values:")
    for m in (37, 41):
        print(
            f"    m={m}: "
            + "  ".join(f"Cyc(k={k})={cycle_count(k, m)}" for k in (2, 4, 8, 16, 32))
            + f"   (#Per = {periodic_point_count_formula(2, m)} for all of them)"
        )

    print("\n" + "=" * 72)
    print("D  Cyc is not a function of rad(k)")
    print("=" * 72)
    sens = radical_sensitivity(500)
    print(
        f"  moduli m in [2,500) with Cyc(2,m) != Cyc(4,m): "
        f"{len(sens['differ'])}/{sens['n_moduli']}"
    )
    print(f"  ...of which #Per is identical: {len(sens['differ_same_per'])}")
    print(f"  first few: {sens['differ'][:12]}")
    print("=" * 72)
    return 0 if not (result["per_bad"] or result["cyc_bad"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
