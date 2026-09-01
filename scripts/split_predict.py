#!/usr/bin/env python3
"""Predict the split oscillation from the digit-sum local limit theorem.

No fitted parameters. The first iterate S_b(n^k) is modelled as a digit-count
mixture of Gaussians, restricted to the image lattice $v \equiv r^k \bmod m$
for each residue $r$ feeding the chosen signature (digit-sum congruence:
$S_b(n^k) \equiv n^k \pmod{b-1}$), and convolved with the exact
integer-to-attractor labelling. The
result is compared against a measured curve when one is available.

A caveat on interpreting agreement: with N samples per band the measurement
noise is about 0.5/sqrt(N), so an MAE at that level means the model is
*consistent with* the data, not that it is uniquely selected by it. Use
--samples-hint to print the noise floor alongside the MAE.

Examples
--------
    python scripts/split_predict.py --k 3 --b 10 --signature 0 --d-max 60
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

import _bootstrap  # noqa: F401
from dspm.dynamics import build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto, predict_split

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_measured(k: int, b: int, directory: Path) -> dict | None:
    candidates = sorted(directory.glob(f"split_scale_k{k}_b{b}_*.json"))
    if not candidates:
        return None
    return json.loads(candidates[-1].read_text(encoding="utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--b", type=int, required=True)
    ap.add_argument("--signature", type=int, default=0, help="a residue in the target signature")
    ap.add_argument("--d-min", type=int, default=4)
    ap.add_argument("--d-max", type=int, default=60)
    ap.add_argument("--samples-hint", type=int, default=None, help="samples per band of the measured curve")
    ap.add_argument("--measured-dir", type=Path, default=REPO_ROOT / "data" / "split")
    args = ap.parse_args(argv)

    k, b, m = args.k, args.b, args.b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(args.signature)
    weight = mod.weights[mod.owner[args.signature % m]]

    targets = [i for i in range(system.count) if system.signature(i) == signature]
    if len(targets) < 2:
        print(
            f"signature {sorted(signature)} hosts {len(targets)} attractor(s); "
            "nothing can oscillate. Pick a signature with a positive local excess."
        )
        return 1

    names = {i: str(list(system.attractors[i])) for i in targets}
    ceiling = int((b - 1) / 2 * k * args.d_max) + 400
    labels = attractor_labels_upto(ceiling, system)

    measured = load_measured(k, b, args.measured_dir)

    print("=" * 78)
    print(f"  split_predict  k={k} b={b}  signature {sorted(signature)}  p_i={weight:.4f}")
    print(f"  attractors {list(names.values())}   (no fitted parameters)")
    print("=" * 78)
    head = "   D  | " + " ".join(f"pred {names[i]:>9}" for i in targets)
    if measured:
        head += " | " + " ".join(f"meas {names[i]:>9}" for i in targets)
    print(head)

    deviations = []
    for D in range(args.d_min, args.d_max + 1):
        pred = predict_split(D, system, signature, labels, targets, weight)
        row = f"  {D:3d}  | " + " ".join(f"{pred[i]:14.4f}" for i in targets)
        if measured and D in measured["digit_lengths"]:
            j = measured["digit_lengths"].index(D)
            row += " | " + " ".join(
                f"{measured['curves'][names[i]][j]:14.4f}" for i in targets
            )
            for i in targets:
                deviations.append(abs(pred[i] - measured["curves"][names[i]][j]))
        print(row)

    if deviations:
        mae = mean(deviations)
        print("-" * 78)
        print(f"  MAE predicted vs measured: {mae:.4f}")
        n = args.samples_hint or (measured or {}).get("samples_per_band")
        if n:
            floor = 0.5 / n**0.5
            print(f"  measurement noise floor:   {floor:.4f}  ({n} samples per band)")
            verdict = (
                "MAE is at the noise floor: the model is consistent with the data, "
                "but the test does not discriminate against other models"
                if mae <= 2 * floor
                else "MAE exceeds the noise floor: there is real unexplained structure"
            )
            print(f"  {verdict}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
