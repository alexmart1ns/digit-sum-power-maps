#!/usr/bin/env python3
"""Audit 1 -- the cycle count is not a function of rad(k).

Target claim (Corollary 6.2 of the July 2026 draft, and the "Correction
(important)" of section 9.2):

    "within any fixed modulus the cycle count is flat for v_2 >= 1
     (verified for m = 16, 17, 32, 37, 41, 64)"

The claim is false, and the verification behind it was vacuous. Two independent
defects:

(a) Proposition 6.1 is about periodic *points*. #Per is a function of rad(k).
    The number of *cycles* is not: a periodic element of order d sits on a cycle
    of length ord_d(k), which depends on k mod d.

(b) The supporting script grouped k by (odd part, v_2) of gcd(k, lambda(m)) and
    compared group *means*. For the only two non-degenerate moduli in the list
    (37 and 41) the within-group values are not constant; the means agree
    because the groups hold the same multiset in the same proportions. The four
    other moduli are degenerate: kappa_2 collapses the unit part, #Per = 2, and
    the count is trivially flat.

Run:  python verification/audit/audit_01_cycle_count.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from math import gcd
from pathlib import Path
from statistics import mean, pstdev

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from dspm.modular import cycle_count, periodic_point_count_formula  # noqa: E402
from dspm.numtheory import carmichael_lambda, v2  # noqa: E402

PAPER_MODULI = (16, 17, 32, 37, 41, 64)


def main() -> int:
    print("=" * 76)
    print("AUDIT 1  'Cyc is flat for v2(k) >= 1 within a fixed modulus'  -- FALSE")
    print("=" * 76)

    print("\n(1) Direct counterexamples, no averaging:\n")
    print("      m  | Cyc(k=2) Cyc(k=4) Cyc(k=8) Cyc(k=16) Cyc(k=32) | #Per")
    broken = []
    for m in PAPER_MODULI:
        counts = [cycle_count(k, m) for k in (2, 4, 8, 16, 32)]
        per = periodic_point_count_formula(2, m)
        flat = len(set(counts)) == 1
        if not flat:
            broken.append(m)
        print(
            f"    {m:4d} | " + "".join(f"{c:8d} " for c in counts)
            + f"  | {per:4d}" + ("" if flat else "   <-- NOT FLAT")
        )
    print(f"\n    moduli from the paper's own list that break the claim: {broken}")
    print("    the four that do not break it are degenerate (#Per = 2)")

    print("\n(2) The 'controlled' test reproduced, with the spread it hid:\n")
    print("      m   v2 |    n    mean    min   max   stdev   distinct")
    for m in (37, 41):
        lam = carmichael_lambda(m)
        groups = defaultdict(list)
        for k in range(2, 6 * lam + 2):
            g = gcd(k, lam)
            val = v2(g)
            if g // 2**val == 1:
                groups[val].append(cycle_count(k, m))
        for val in sorted(groups):
            if val == 0:
                continue
            vals = groups[val]
            const = len(set(vals)) == 1
            print(
                f"    {m:4d}  {val:2d} | {len(vals):4d}  {mean(vals):6.2f}"
                f"  {min(vals):5d} {max(vals):5d}  {pstdev(vals):6.2f}"
                f"   {sorted(set(vals))}" + ("" if const else "   <-- NOT CONSTANT")
            )
    print("\n    equal means across v2 groups, non-constant within each group")

    print("\n(3) Scale of the problem:\n")
    differ = [m for m in range(2, 500) if cycle_count(2, m) != cycle_count(4, m)]
    same_per = [
        m for m in differ
        if periodic_point_count_formula(2, m) == periodic_point_count_formula(4, m)
    ]
    grid = [m for m in range(2, 40) if cycle_count(2, m) != cycle_count(4, m)]
    print(f"    m in [2,500)  with Cyc(2,m) != Cyc(4,m): {len(differ)}/498")
    print(f"    ...of those, with identical #Per:        {len(same_per)}")
    print(f"    within the paper's grid (m = b-1 <= 39): {len(grid)}/38")
    print(f"    {grid}")

    print("\n" + "=" * 76)
    print("VERDICT: claim refuted. See docs/ERRATA.md; the replacement is the")
    print("closed form dspm.modular.cycle_count_formula, verified separately.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
