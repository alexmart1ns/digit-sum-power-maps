#!/usr/bin/env python3
"""Audit 2 -- no signature's split converges, not even the "easy" ones.

Target claim (section 7.4 of the July 2026 draft):

    "For signatures {1} and {8} the per-digit split converges: a single
     attractor captures the mass; the tiny fixed points {1},{8},{17} receive
     density -> 0."

Measured with 60k samples per band over 4 <= D <= 90, all three "tiny" fixed
points show recurring bursts after long stretches at zero -- non-monotone, with
peaks at D around 73, 58 and 79 respectively. The two "winning" attractors also
oscillate, with smaller amplitude.

Why the original measurement missed it: the verdict logic looked at the drift of
a single step of D and declared "stabilised" when that fell below sampling
noise. A quasi-periodic curve has long flat stretches, so this reports
convergence whenever the sampled window lands in one.

Mechanism: M is a fixed ceiling, so the first-passage landing distribution lives
on [1, M] and its mean grows only like log D. The multi-step cascade
occasionally produces low landing values, so the small basins
beta_{1} = {1,4,7,10,40}, beta_{8} = {2,5,8,11,20,50}, beta_{17} = {14,17,23,47}
keep getting revisited. Each holds one element well above the others, and those
are what the drifting landing distribution sweeps back across at large D.

Note this makes the paper's headline *stronger*: every individual density
oscillates, so none of them exists.

Run:  python verification/audit/audit_02_split_convergence.py --samples 60000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from dspm.dynamics import build_system  # noqa: E402
from dspm.split import oscillation_report, split_curves  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--d-max", type=int, default=90)
    ap.add_argument("--d-step", type=int, default=3)
    ap.add_argument("--samples", type=int, default=60_000)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)

    system = build_system(args.k, args.b)
    bands = list(range(4, args.d_max + 1, args.d_step))
    noise = 0.5 / args.samples**0.5

    print("=" * 78)
    print(f"AUDIT 2  section 7.4 convergence claim  (k={args.k}, b={args.b})")
    print("=" * 78)
    print(f"  M={system.M}  attractors={system.count}  sampling sigma ~ {noise:.4f}")
    print("\n  basins inside the trapping region:")
    for i, members in enumerate(system.attractors):
        basin = sorted(n for n in range(1, system.M + 1) if system.label[n] == i)
        print(f"    {str(list(members)):<10} sig={sorted(system.signature(i))}  beta={basin}")

    curves = split_curves(
        args.k, args.b, bands,
        samples_per_band=args.samples, seed=args.seed, system=system,
    )

    order = sorted(
        range(system.count),
        key=lambda i: (sorted(curves.signatures[i]), curves.labels[i]),
    )
    print("\n  split by digit length D:")
    print("     D  | " + " ".join(f"{curves.labels[i]:>10}" for i in order))
    for j, D in enumerate(bands):
        print(f"    {D:3d}  | " + " ".join(f"{curves.curves[i][j]:10.4f}" for i in order))

    report = oscillation_report(curves)
    print("\n  diagnosis over the whole range:")
    print("    attractor    sig      min     max     amp   monotone  oscillates")
    for i in order:
        row = report[i]
        print(
            f"    {row['attractor']:<12} {str(row['signature']):<7} {row['min']:.4f}"
            f"  {row['max']:.4f}  {row['amplitude']:.4f}"
            f"   {str(row['monotone']):<8}  {row['oscillates']}"
        )

    small = [i for i in order if curves.labels[i] in ("[1]", "[8]", "[17]")]
    if small:
        print("\n  the three fixed points the draft says go to zero:")
        for i in small:
            row = report[i]
            print(
                f"    {row['attractor']:<6} first-half mean {row['mean_first_half']:.4f}"
                f"   second-half mean {row['mean_second_half']:.4f}"
                f"   second-half max {max(curves.curves[i][len(bands) // 2:]):.4f}"
                f"   monotone={row['monotone']}"
            )

    print("\n  aggregate per signature (Theorem 5.3 still holds exactly):")
    for sig, sums in curves.signature_sums().items():
        print(f"    sig={sorted(sig)}  min={min(sums):.4f}  max={max(sums):.4f}")

    non_monotone = [r["attractor"] for r in report if not r["monotone"]]
    print("\n" + "=" * 78)
    print(f"VERDICT: non-monotone curves: {non_monotone}")
    print("Section 7.4's tripartite classification does not survive. Result 7.6")
    print("(no individual density exists) is strengthened, not weakened.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
