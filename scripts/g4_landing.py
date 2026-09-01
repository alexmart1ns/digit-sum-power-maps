#!/usr/bin/env python3
"""G4 analysis: periodicity of first landing g(v) on image lattice.

Finds minimal T (if any) such that a(v) depends only on v mod b^T for v on
feeding/image progressions. Writes to data/qclass/split/g4_landing_*.

Example
-------
    python scripts/g4_landing.py --k 3 --b 10 --signature 0
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
from dspm.predict import first_landing

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "split"


def basin_sets(system) -> dict[int, list[int]]:
    out: dict[int, list[int]] = defaultdict(list)
    for n in range(1, system.M + 1):
        out[system.label[n]].append(n)
    return {k: sorted(v) for k, v in out.items()}


def periodicity_scan(
    system,
    m: int,
    feeding: list[int],
    targets: list[int],
    t_max: int,
    v_sample_max: int,
) -> list[dict]:
    """For each T, check label collisions v vs v + m*b^T on samples."""
    rows = []
    for T in range(1, t_max + 1):
        step = m * (system.b**T)
        mismatches = 0
        checked = 0
        for r in feeding:
            v = r if r >= 1 else r + m
            while v <= v_sample_max:
                v2 = v + step
                if v2 > v_sample_max:
                    break
                w1, s1 = first_landing(v, system)
                w2, s2 = first_landing(v2, system)
                lab1 = system.label[w1]
                lab2 = system.label[w2]
                if lab1 in targets and lab2 in targets:
                    checked += 1
                    if lab1 != lab2:
                        mismatches += 1
                v += m
        rows.append(
            {
                "T": T,
                "modulus": step,
                "checked_pairs": checked,
                "mismatches": mismatches,
                "consistent": mismatches == 0 and checked > 0,
            }
        )
    return rows


def landing_depth_stats(system, feeding: list[int], v_max: int) -> dict:
    depths: list[int] = []
    for v in range(1, min(v_max, 500_000) + 1):
        if all(v % system.m != r for r in feeding):
            continue
        _, steps = first_landing(v, system)
        depths.append(steps)
    if not depths:
        return {"max_steps": 0, "mean_steps": 0.0}
    return {
        "max_steps": max(depths),
        "mean_steps": round(sum(depths) / len(depths), 4),
        "samples": len(depths),
    }


def run(k: int, b: int, sig_residue: int, t_max: int, v_sample_max: int) -> dict:
    m = b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(sig_residue)
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    names = {t: str(list(system.attractors[t])) for t in targets}

    basins = {names[t]: basin_sets(system)[t] for t in targets if t in basin_sets(system)}

    scan = periodicity_scan(system, m, feeding, targets, t_max, v_sample_max)
    minimal_T = next((r["T"] for r in scan if r["consistent"]), None)
    depth = landing_depth_stats(system, feeding, v_sample_max)

    return {
        "k": k,
        "b": b,
        "M": system.M,
        "signature": sorted(signature),
        "feeding": feeding,
        "basins": basins,
        "landing_depth": depth,
        "periodicity_scan": scan,
        "minimal_consistent_T": minimal_T,
        "verdict": "periodic_candidate" if minimal_T else "no_T_found_in_range",
        "note": (
            "Consistent T means a(v)==a(v+m*b^T) for all checked pairs on feeding "
            "lattice; supports Lemma D (G4-finite). Not a proof for all v."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--signature", type=int, default=0)
    ap.add_argument("--t-max", type=int, default=8)
    ap.add_argument("--v-sample-max", type=int, default=1_000_000)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = run(args.k, args.b, args.signature, args.t_max, args.v_sample_max)
    text = json.dumps(payload, indent=2)

    (OUT_DIR / f"g4_landing_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "g4_landing_latest.json").write_text(text, encoding="utf-8")

    lines = [
        "# G4 landing analysis (pilot)",
        "",
        f"M={payload['M']}  minimal consistent T: **{payload['minimal_consistent_T']}**",
        f"Landing depth (samples): max **{payload['landing_depth']['max_steps']}**, "
        f"mean **{payload['landing_depth']['mean_steps']}**",
        "",
        "## Basins in [1,M]",
        "",
    ]
    for nm, pts in payload["basins"].items():
        lines.append(f"- **{nm}**: `{pts}` ({len(pts)} points)")

    lines += ["", "## Periodicity scan (a(v) vs a(v + m·b^T))", ""]
    lines.append("| T | modulus | pairs | mismatches | consistent |")
    lines.append("|---|---------|-------|------------|------------|")
    for row in payload["periodicity_scan"]:
        lines.append(
            f"| {row['T']} | {row['modulus']} | {row['checked_pairs']} | "
            f"{row['mismatches']} | {row['consistent']} |"
        )
    lines += ["", f"**Verdict:** {payload['verdict']}", "", payload["note"]]
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"g4_landing_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "g4_landing_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'g4_landing_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
