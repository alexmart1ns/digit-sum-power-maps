#!/usr/bin/env python3
"""Audit 5 -- the Gaussian sweep model must use the image lattice.

Target claim (§7.5, Appendix B.5):

    The parameter-free model F_j places mass on residue classes feeding
    each signature.

Casting out nines forces S_b(n^k) == n^k (mod b-1), so mass must sit on
v == r^k (mod m), not v == r. Using the wrong lattice inflated MAE on the
(3,10) pilot signature {0} from about 0.04 to about 0.003 on D in [8, 64].

Run:  python verification/audit/audit_05_lattice.py
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from dspm.dynamics import build_system  # noqa: E402
from dspm.modular import structure  # noqa: E402
from dspm.predict import (  # noqa: E402
    attractor_labels_upto,
    digit_count_mixture,
    predict_split,
)
from dspm.split import load_split_scale_file  # noqa: E402


def _predict_wrong_lattice(D, system, signature, labels, targets, modular_weight):
    """Legacy bug: place mass on v == r instead of v == r^k."""
    k, b = system.k, system.b
    m = b - 1
    mod = structure(k, m)
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    V = len(labels) - 1
    density: dict[int, float] = {}
    for L, weight in digit_count_mixture(D, k, b).items():
        mu = (b - 1) / 2 * L
        sigma = math.sqrt(L * (b * b - 1) / 12)
        lo = max(1, int(mu - 6 * sigma))
        hi = min(V, int(mu + 6 * sigma))
        for q in feeding:
            v = lo + ((q - lo) % m)
            while v <= hi:
                if v >= 1:
                    z = (v - mu) / sigma
                    density[v] = density.get(v, 0.0) + weight * math.exp(-0.5 * z * z) / (
                        sigma * math.sqrt(2 * math.pi)
                    )
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--d-min", type=int, default=8)
    ap.add_argument("--d-max", type=int, default=64)
    args = ap.parse_args(argv)

    repo = Path(__file__).resolve().parents[2]
    measured_path = repo / "data" / "split" / f"split_scale_k{args.k}_b{args.b}_latest.json"
    if not measured_path.exists():
        candidates = sorted((repo / "data" / "split").glob(f"split_scale_k{args.k}_b{args.b}_*.json"))
        measured_path = candidates[-1] if candidates else measured_path
    measured = load_split_scale_file(measured_path)
    if measured is None:
        print(f"FAIL: no measured split file at {measured_path}")
        return 1

    system = build_system(args.k, args.b)
    mod = structure(args.k, args.b - 1)
    signature = mod.signature_of_residue(0)
    weight = mod.weights[mod.owner[0]]
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    ceiling = int((args.b - 1) / 2 * args.k * args.d_max) + 400
    labels = attractor_labels_upto(ceiling, system)
    names = {i: str(list(system.attractors[i])) for i in targets}

    right_err, wrong_err = [], []
    for D in range(args.d_min, args.d_max + 1):
        if D not in measured["digit_lengths"]:
            continue
        j = measured["digit_lengths"].index(D)
        right = predict_split(D, system, signature, labels, targets, weight)
        wrong = _predict_wrong_lattice(D, system, signature, labels, targets, weight)
        for i in targets:
            mv = measured["curves"][names[i]][j]
            right_err.append(abs(right[i] - mv))
            wrong_err.append(abs(wrong[i] - mv))

    mae_right = mean(right_err)
    mae_wrong = mean(wrong_err)
    print("=" * 72)
    print("  audit_05_lattice  image lattice v == r^k (mod m)")
    print(f"  pair ({args.k},{args.b})  signature {sorted(signature)}  D={args.d_min}..{args.d_max}")
    print("=" * 72)
    print(f"  MAE image lattice (correct):  {mae_right:.4f}")
    print(f"  MAE feeding lattice (wrong): {mae_wrong:.4f}")
    print(f"  ratio wrong/correct:           {mae_wrong / max(mae_right, 1e-9):.1f}x")
    ok = mae_right < 0.01 and mae_wrong > 3 * mae_right
    print("-" * 72)
    print("  VERDICT:", "PASS" if ok else "FAIL")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
