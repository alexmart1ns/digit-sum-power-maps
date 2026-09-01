#!/usr/bin/env python3
"""Measure the intra-signature basin split as a function of digit length.

Theorem 5.3 fixes the aggregate mass of each residue signature at p_i exactly.
This script measures how that mass divides among the attractors sharing a
signature, restricted to integers with exactly D base-b digits.

On reading the output: the earlier version of this script printed a verdict
based on the drift of one step of D and reported "stabilised" whenever that
drift fell below the sampling noise. That is unsound -- a quasi-periodic curve
has long flat stretches, and landing in one of them looks exactly like
convergence. It led to the false claim that the split converges for some
signatures. This version reports the full curve plus amplitude over the whole
range, and never calls convergence from a local slope.

Examples
--------
    python scripts/split_scale.py --k 3 --b 10 --d-max 90 --samples 40000
    python scripts/split_scale.py --k 2 --b 16 --d-max 60
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.dynamics import build_system
from dspm.split import oscillation_report, split_curves

REPO_ROOT = Path(__file__).resolve().parent.parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--b", type=int, required=True)
    ap.add_argument("--d-min", type=int, default=4)
    ap.add_argument("--d-max", type=int, default=60)
    ap.add_argument("--d-step", type=int, default=1)
    ap.add_argument("--samples", type=int, default=20_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "data" / "split")
    args = ap.parse_args(argv)

    started = time.time()
    system = build_system(args.k, args.b)
    bands = list(range(args.d_min, args.d_max + 1, args.d_step))

    curves = split_curves(
        args.k, args.b, bands,
        samples_per_band=args.samples, seed=args.seed, system=system,
    )
    noise = 0.5 / args.samples**0.5

    print("=" * 78)
    print(f"  split_scale  k={args.k} b={args.b}  M={system.M}  attractors={system.count}")
    print(f"  {args.samples} samples per band, sampling sigma ~ {noise:.4f}")
    print("=" * 78)

    order = sorted(range(system.count), key=lambda i: (sorted(curves.signatures[i]), curves.labels[i]))
    header = "   D  | " + " ".join(f"{curves.labels[i]:>10}" for i in order)
    print(header)
    for j, D in enumerate(bands):
        print(f"  {D:3d}  | " + " ".join(f"{curves.curves[i][j]:10.4f}" for i in order))

    print("\n  per-attractor summary over the whole range")
    print("   attractor      sig      min      max      amp   monotone  oscillates")
    report = oscillation_report(curves)
    for i in order:
        row = report[i]
        print(
            f"   {row['attractor']:<12} {str(row['signature']):<8} {row['min']:.4f}"
            f"  {row['max']:.4f}  {row['amplitude']:.4f}"
            f"   {str(row['monotone']):<8} {row['oscillates']}"
        )

    print("\n  aggregate mass per signature at each D (Theorem 5.3 forces p_i)")
    for sig, sums in curves.signature_sums().items():
        print(f"   sig={sorted(sig)}  min={min(sums):.4f}  max={max(sums):.4f}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "k": args.k, "b": args.b, "M": system.M,
        "samples_per_band": args.samples, "seed": args.seed,
        "digit_lengths": bands,
        "attractors": curves.labels,
        "signatures": [sorted(s) for s in curves.signatures],
        "curves": {curves.labels[i]: curves.curves[i] for i in range(system.count)},
        "report": report,
        "elapsed_s": round(time.time() - started, 1),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    out_path = args.out_dir / f"split_scale_k{args.k}_b{args.b}_{stamp}.json"
    out_path.write_text(text, encoding="utf-8")
    latest_path = args.out_dir / f"split_scale_k{args.k}_b{args.b}_latest.json"
    latest_path.write_text(text, encoding="utf-8")
    print(f"\n  json: {out_path}")
    print(f"  latest: {latest_path}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
