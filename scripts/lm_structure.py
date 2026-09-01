#!/usr/bin/env python3
"""Deterministic structure of the labelling h_j on the trapping region.

For Hypothesis LM: reports how attractor labels vary with digit length and
scale on the image lattice. Writes only to data/qclass/split/lm_structure_*.

Example
-------
    python scripts/lm_structure.py --k 3 --b 10 --signature 0
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.dynamics import build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "split"


def num_digits(v: int, b: int) -> int:
    if v <= 0:
        return 1
    return int(math.log(v, b)) + 1


def run(k: int, b: int, sig_residue: int) -> dict:
    m = b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(sig_residue)
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    images = sorted({pow(r, k, m) for r in feeding})

    labels = attractor_labels_upto(system.M, system)
    names = {t: str(list(system.attractors[t])) for t in targets}

    by_length: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    on_lattice = 0
    for v in range(1, system.M + 1):
        if v % m not in images:
            continue
        on_lattice += 1
        L = num_digits(v, b)
        lab = labels[v]
        if lab in targets:
            by_length[L][names[lab]] += 1

    length_rows = []
    fracs_18: list[float] = []
    for L in sorted(by_length):
        row = dict(by_length[L])
        tot = sum(row.values())
        if tot == 0:
            continue
        f18 = row.get(names[targets[0]], 0) / tot if len(targets) >= 1 else 0.0
        fracs_18.append(f18)
        length_rows.append({"L": L, "counts": row, "frac_primary": round(f18, 4), "total": tot})

    amp = max(fracs_18) - min(fracs_18) if fracs_18 else 0.0

    return {
        "k": k,
        "b": b,
        "signature": sorted(signature),
        "M": system.M,
        "feeding": feeding,
        "image_mod_m": images,
        "attractors": [names[t] for t in targets],
        "on_lattice_count": on_lattice,
        "by_digit_length": length_rows,
        "frac_primary_amplitude_over_L": round(amp, 4),
        "note": "Oscillation in frac_primary across L supports LM mechanism on finite window; does not prove non-convergence of Psi(V).",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--signature", type=int, default=0)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = run(args.k, args.b, args.signature)
    text = json.dumps(payload, indent=2)

    (OUT_DIR / f"lm_structure_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "lm_structure_latest.json").write_text(text, encoding="utf-8")

    lines = [
        "# Labelling structure (LM diagnostic)",
        "",
        f"Pilot: k={args.k} b={args.b} signature {payload['signature']}",
        f"M={payload['M']}  image mod m={payload['image_mod_m']}",
        f"Amplitude of primary fraction across digit lengths L: **{payload['frac_primary_amplitude_over_L']}**",
        "",
        "| L | counts | frac primary |",
        "|---|--------|--------------|",
    ]
    for row in payload["by_digit_length"]:
        lines.append(
            f"| {row['L']} | {row['counts']} | {row['frac_primary']} |"
        )
    lines.append("")
    lines.append(payload["note"])
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"lm_structure_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "lm_structure_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'lm_structure_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
