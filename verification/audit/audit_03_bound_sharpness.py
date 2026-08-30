#!/usr/bin/env python3
"""Audit 3 -- the (b-1)/M error bound is not saturated, and can be sharpened.

Target claim (section 1.3 of the July 2026 draft):

    "an explicit and *saturated* finite-window error bound (b-1)/M"

It is not saturated. The proof of Theorem 5.3 bounds the deviation of
|N_i cap [1,M]| by |R_i|, but the deviations of all m residue classes sum to
zero, so the aggregate deviation is really bounded by min(|R_i|, m - |R_i|),
and in a window of length M = qm + s by min(|R_i|, s). The valid sharp constant
is therefore min(|R_i|, b-2), and the paper's own section 8.2 already showed the
gap: worst error 0.10 against a bound of 0.40.

Consequence for the verification narrative: reporting "152,276 comparisons,
100.00% within the bound" is a weak test, because the bound is loose by several
times. The sharp statement is the exact integer identity of Proposition 5.2,
checked by verify_theorems.py.

Run:  python verification/audit/audit_03_bound_sharpness.py
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from dspm.modular import structure  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--b-max", type=int, default=20)
    ap.add_argument("--k-max", type=int, default=25)
    args = ap.parse_args(argv)

    loose_viol = sharp_viol = 0
    total = 0
    worst_loose = worst_sharp = 0.0
    worst_loose_at = worst_sharp_at = None

    for b in range(3, args.b_max + 1):
        m = b - 1
        for k in range(1, args.k_max + 1):
            mod = structure(k, m)
            sizes = mod.basin_sizes
            for window in list(range(m, m + 120)) + [500, 1000, 3000]:
                counts = defaultdict(int)
                for n in range(1, window + 1):
                    counts[mod.owner[n % m]] += 1
                for i in range(len(mod.cycles)):
                    total += 1
                    err = abs(counts[i] / window - mod.weights[i])
                    loose = (b - 1) / window
                    sharp = min(sizes[i], m - 1) / window
                    if err > loose + 1e-12:
                        loose_viol += 1
                    if err > sharp + 1e-12:
                        sharp_viol += 1
                    if loose and err / loose > worst_loose:
                        worst_loose, worst_loose_at = err / loose, (k, b, window)
                    if sharp and err / sharp > worst_sharp:
                        worst_sharp, worst_sharp_at = err / sharp, (k, b, window)

    print("=" * 76)
    print("AUDIT 3  is the (b-1)/M bound 'saturated'?  -- NO")
    print("=" * 76)
    print(f"  comparisons: {total}")
    print(f"  violations of the paper's bound (b-1)/M ...... {loose_viol}")
    print(f"  violations of the sharp bound min(|R_i|,b-2)/M {sharp_viol}")
    print(f"  worst error/bound ratio, paper's bound ....... {worst_loose:.4f} at (k,b,M)={worst_loose_at}")
    print(f"  worst error/bound ratio, sharp bound ......... {worst_sharp:.4f} at (k,b,M)={worst_sharp_at}")
    print()
    print("  A ratio well below 1 for the paper's bound means the 100% pass rate")
    print("  reported in section 8.2 is nearly automatic. The sharp bound is")
    print("  approached closely, so it is the one worth stating.")
    print("=" * 76)
    return 0 if (loose_viol == 0 and sharp_viol == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
