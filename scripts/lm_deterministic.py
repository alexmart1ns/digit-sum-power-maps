#!/usr/bin/env python3
"""Deterministic LM bounds: exact Psi_j(V) on feeding-residue windows.

Matches scripts/local_mean.py psi_sharp (no Monte Carlo).
Writes only to data/qclass/split/lm_deterministic_*.

Example
-------
    python scripts/lm_deterministic.py
    python scripts/lm_deterministic.py --v-max 10000000
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


def window_psi(
    V: int,
    m: int,
    feeding: list[int],
    labels: list[int],
    targets: list[int],
    target_names: dict[int, str],
) -> dict:
    """Exact Psi_j(V) — same logic as local_mean.psi_sharp."""
    h = max(1, int(V**0.5))
    lo = max(1, V - h)
    hi = min(len(labels) - 1, V + h)
    counts = {t: 0 for t in targets}
    n = 0
    by_L: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for r in feeding:
        v = lo + ((r - lo) % m)
        while v <= hi:
            lab = labels[v]
            if lab in counts:
                counts[lab] += 1
                by_L[num_digits(v, 10)][lab] += 1
            n += 1
            v += m

    fracs = {target_names[t]: (counts[t] / n if n else 0.0) for t in targets}
    primary = targets[0]
    length_rows = []
    for L in sorted(by_L):
        row = dict(by_L[L])
        tot = sum(row.values())
        if tot == 0:
            continue
        length_rows.append(
            {
                "L": L,
                "counts": {target_names[t]: row.get(t, 0) for t in targets},
                "total": tot,
                "frac_primary": round(row.get(primary, 0) / tot, 6),
            }
        )
    return {
        "V": V,
        "window": [lo, hi],
        "total_on_lattice": n,
        "fracs": {k: round(v, 6) for k, v in fracs.items()},
        "by_digit_length": length_rows,
    }


def finite_region_table(
    system,
    m: int,
    images: set[int],
    labels: list[int],
    target_idx: dict[str, int],
) -> dict:
    """Full deterministic partition of [1,M] on image lattice."""
    rows = []
    by_L: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    preimages: dict[str, list[int]] = defaultdict(list)
    for v in range(1, system.M + 1):
        if v % m not in images:
            continue
        lab = labels[v]
        for nm, idx in target_idx.items():
            if lab == idx:
                by_L[num_digits(v, system.b)][nm] += 1
                preimages[nm].append(v)
                break
    fracs_primary: list[float] = []
    primary_nm = list(target_idx.keys())[0]
    for L in sorted(by_L):
        row = dict(by_L[L])
        tot = sum(row.values())
        f0 = row.get(primary_nm, 0) / tot if tot else 0.0
        fracs_primary.append(f0)
        rows.append({"L": L, "counts": row, "total": tot, "frac_primary": round(f0, 6)})
    return {
        "M": system.M,
        "by_digit_length": rows,
        "frac_primary_amplitude": round(max(fracs_primary) - min(fracs_primary), 6)
        if fracs_primary
        else 0.0,
        "preimages": {k: sorted(v) for k, v in preimages.items()},
    }


def run(k: int, b: int, sig_residue: int, v_max: int) -> dict:
    m = b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(sig_residue)
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    images = {pow(r, k, m) for r in feeding}
    names = {t: str(list(system.attractors[t])) for t in targets}
    target_idx = {names[t]: t for t in targets}

    labels = attractor_labels_upto(v_max, system)
    finite = finite_region_table(system, m, images, labels, target_idx)

    anchors = [b**n for n in range(2, int(math.log(v_max, b)) + 2) if b**n <= v_max]
    window_rows = [
        window_psi(V, m, feeding, labels, targets, names) for V in anchors
    ]

    primary_nm = names[targets[0]]
    psi_primary = [r["fracs"].get(primary_nm, 0.0) for r in window_rows]
    gap = max(psi_primary) - min(psi_primary) if psi_primary else 0.0

    return {
        "k": k,
        "b": b,
        "signature": sorted(signature),
        "feeding": feeding,
        "v_max": v_max,
        "attractors": list(target_idx.keys()),
        "finite_region": finite,
        "decade_windows": window_rows,
        "decade_gap_primary": round(gap, 6),
        "verdict": "deterministic_gap_positive" if gap > 0.05 else "gap_small",
        "proof_status": {
            "finite_M_partition": "proven_exact",
            "window_psi_at_finite_V": "proven_exact_matches_local_mean",
            "liminf_ne_limsup": "open_requires_infinite_sequence",
        },
        "note": (
            "Exact counts on finite windows (psi_sharp parity with local_mean); "
            "does not prove LM theorem (lim inf != lim sup along V->infty)."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--signature", type=int, default=0)
    ap.add_argument("--v-max", type=int, default=10_000_000)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = run(args.k, args.b, args.signature, args.v_max)
    text = json.dumps(payload, indent=2)

    (OUT_DIR / f"lm_deterministic_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "lm_deterministic_latest.json").write_text(text, encoding="utf-8")

    fin = payload["finite_region"]
    lines = [
        "# LM deterministic bounds (pilot 3,10)",
        "",
        f"M={fin['M']}  amplitude over L in [1,M]: **{fin['frac_primary_amplitude']}**",
        f"Decade window gap (primary): **{payload['decade_gap_primary']}**",
        f"Feeding residues mod {args.b - 1}: `{payload['feeding']}`",
        "",
        "## Finite region [1,M] by digit length",
        "",
        "| L | counts | frac primary |",
        "|---|--------|--------------|",
    ]
    for row in fin["by_digit_length"]:
        lines.append(f"| {row['L']} | {row['counts']} | {row['frac_primary']} |")

    lines += ["", "## Preimages on image lattice", ""]
    for nm, vals in fin["preimages"].items():
        lines.append(f"- **{nm}**: `{vals}`")

    attrs = payload["attractors"]
    lines += ["", "## Decade windows (exact Psi_j, psi_sharp parity)", ""]
    lines.append("| V | total | " + " | ".join(attrs) + " |")
    lines.append("|---|-------|" + "|".join(["---"] * len(attrs)) + "|")
    for row in payload["decade_windows"]:
        fr = row["fracs"]
        cols = " | ".join(str(fr.get(a, 0)) for a in attrs)
        lines.append(f"| {row['V']} | {row['total_on_lattice']} | {cols} |")

    lines += [
        "",
        f"**Verdict:** {payload['verdict']}",
        "",
        payload["note"],
    ]
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"lm_deterministic_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "lm_deterministic_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'lm_deterministic_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
