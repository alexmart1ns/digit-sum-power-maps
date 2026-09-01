#!/usr/bin/env python3
"""Per-D bridge check: |delta_j(D) - F_j(D)| on measured split curves.

Compares MC-measured basin masses from split_scale_*_latest.json against
predict_split (image lattice). Writes only stdout; does not modify data/.

Example
-------
    python scripts/bridge_check.py --k 3 --b 10
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.dynamics import build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto, predict_split
from dspm.split import load_split_scale_file

REPO_ROOT = Path(__file__).resolve().parent.parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--b", type=int, required=True)
    ap.add_argument("--signature", type=int, default=0)
    ap.add_argument("--measured-dir", type=Path, default=REPO_ROOT / "data" / "split")
    args = ap.parse_args(argv)

    k, b, m = args.k, args.b, args.b - 1
    measured_path = args.measured_dir / f"split_scale_k{k}_b{b}_latest.json"
    if not measured_path.exists():
        print(f"missing {measured_path}")
        return 1

    measured = load_split_scale_file(measured_path)
    if "digit_lengths" not in measured:
        print("measured file lacks digit_lengths (v2 schema required)")
        return 1

    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(args.signature)
    weight = mod.weights[mod.owner[args.signature % m]]
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    if len(targets) < 2:
        print(f"signature {sorted(signature)} has <2 attractors; nothing to bridge")
        return 1

    labels_json = measured.get("attractor_labels") or {}
    name_to_idx = {labels_json[str(i)]: i for i in targets if str(i) in labels_json}
    if not name_to_idx:
        name_to_idx = {str(list(system.attractors[i])): i for i in targets}

    Ds = measured["digit_lengths"]
    curves = measured["curves"]
    d_max = max(Ds)
    ceiling = int((b - 1) / 2 * k * d_max) + 400
    labels = attractor_labels_upto(ceiling, system)

    rows: list[dict] = []
    abs_errs: list[float] = []
    for j, D in enumerate(Ds):
        pred = predict_split(D, system, signature, labels, targets, weight)
        row: dict = {"D": D}
        for name, idx in name_to_idx.items():
            meas_key = name if name in curves else str(list(system.attractors[idx]))
            mval = curves.get(meas_key, [None] * len(Ds))[j]
            pval = pred.get(idx, float("nan"))
            if mval is not None:
                row[f"meas_{name}"] = round(mval, 6)
                row[f"pred_{name}"] = round(pval, 6)
                row[f"abs_err_{name}"] = round(abs(mval - pval), 6)
                abs_errs.append(abs(mval - pval))
        rows.append(row)

    mae = sum(abs_errs) / len(abs_errs) if abs_errs else float("nan")
    print("=" * 72)
    print(f"  bridge_check  k={k} b={b}  signature {sorted(signature)}")
    print(f"  measured: {measured_path.name}  bands={len(Ds)}  targets={list(name_to_idx)}")
    print(f"  mean |delta_j - F_j| over attractors x bands: {mae:.6f}")
    print("-" * 72)
    print(f"  {'D':>4}  " + "  ".join(f"{n:>12}" for n in name_to_idx))
    for row in rows:
        parts = [f"{row['D']:4d}"]
        for name in name_to_idx:
            parts.append(f"{row.get(f'abs_err_{name}', float('nan')):12.6f}")
        print("  ".join(parts))
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
