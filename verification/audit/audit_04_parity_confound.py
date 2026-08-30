#!/usr/bin/env python3
"""Audit 4 -- "prime exponents amplify attractors" is a parity effect.

Target claim (section 9.3 of the July 2026 draft):

    "Prime k: mean |C| = 31.82 vs 18.26 for composite (~74% more)"

The direction replicates, but the contrast is confounded. 2 is the only even
prime, and about half of the composites are even, while 2 | k collapses the
2-part of every local unit group (kappa_k strips it, Proposition 6.1) and so
cuts both Cyc and |C| sharply. Controlling for parity, odd primes and odd
composites are statistically indistinguishable, whereas odd and even differ by
roughly a factor of two.

Run:  python verification/audit/audit_04_parity_confound.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import mean, pstdev

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from dspm.dynamics import build_system  # noqa: E402
from dspm.modular import cycle_count  # noqa: E402
from dspm.numtheory import is_prime  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--b-max", type=int, default=24)
    ap.add_argument("--k-max", type=int, default=60)
    args = ap.parse_args(argv)

    rows = []
    for b in range(3, args.b_max + 1):
        for k in range(2, args.k_max + 1):
            system = build_system(k, b)
            rows.append((k, b, system.count, cycle_count(k, b - 1)))

    def group(name, predicate):
        counts = [r[2] for r in rows if predicate(r[0])]
        cycs = [r[3] for r in rows if predicate(r[0])]
        if not counts:
            return None
        return {
            "class": name,
            "n": len(counts),
            "count_mean": mean(counts),
            "count_sd": pstdev(counts) if len(counts) > 1 else 0.0,
            "cyc_mean": mean(cycs),
        }

    groups = [
        group("prime k (raw)", is_prime),
        group("composite k (raw)", lambda k: not is_prime(k)),
        group("odd prime k", lambda k: is_prime(k) and k % 2 == 1),
        group("odd composite k", lambda k: not is_prime(k) and k % 2 == 1),
        group("odd k (any)", lambda k: k % 2 == 1),
        group("even k (any)", lambda k: k % 2 == 0),
    ]

    print("=" * 76)
    print("AUDIT 4  'prime k amplifies |C|' -- confounded with parity")
    print("=" * 76)
    print(f"  grid: k in [2,{args.k_max}], b in [3,{args.b_max}]  ({len(rows)} pairs)\n")
    print("    class                  n     mean |C|   sd      mean Cyc")
    for g in groups:
        if g:
            print(
                f"    {g['class']:<20} {g['n']:5d}   {g['count_mean']:8.2f}"
                f" {g['count_sd']:7.2f}   {g['cyc_mean']:8.2f}"
            )

    odd_prime = next(g for g in groups if g and g["class"] == "odd prime k")
    odd_comp = next(g for g in groups if g and g["class"] == "odd composite k")
    gap_controlled = abs(odd_prime["count_mean"] - odd_comp["count_mean"])
    odd_any = next(g for g in groups if g and g["class"] == "odd k (any)")
    even_any = next(g for g in groups if g and g["class"] == "even k (any)")
    gap_parity = abs(odd_any["count_mean"] - even_any["count_mean"])

    print()
    print(f"  gap between odd prime and odd composite: {gap_controlled:.2f}")
    print(f"  gap between odd and even:                {gap_parity:.2f}")
    print()
    print("=" * 76)
    if gap_parity > 3 * max(gap_controlled, 1e-9):
        print("VERDICT: the effect is the parity of k, not its primality.")
    else:
        print("VERDICT: inconclusive on this grid; widen --k-max/--b-max.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
