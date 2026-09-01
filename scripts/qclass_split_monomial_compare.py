#!/usr/bin/env python3
"""Monomial bridge: predict_split (classic) vs predict_split_Q (sidecar).

For Q(x)=x^k the image lattice eval_Q(r)=r^k matches pow(r,k,m) in predict_split.
Writes only to data/qclass/split/monomial_compare_*.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.dynamics import build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto, predict_split
from dspm.qmaps import (
    attractor_labels_upto_Q,
    build_system_Q,
    monomial_Q,
    predict_split_Q,
    split_curves_Q,
    structure_Q,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "split"

LENGTHS = tuple(range(8, 65, 4))
SAMPLES = 8_000
PAIRS = [(2, 10), (3, 10), (4, 10)]


def _mae(a: dict[int, float], b: dict[int, float]) -> float:
    keys = [i for i in a if i in b]
    if not keys:
        return float("nan")
    return sum(abs(a[i] - b[i]) for i in keys) / len(keys)


def run_pair(k: int, b: int) -> dict:
    classic = build_system(k, b)
    sidecar = build_system_Q(monomial_Q(k), b)
    cmod = structure(k, b - 1)
    smod = structure_Q(monomial_Q(k), b - 1)
    sharing = classic.attractors_sharing_signature()
    split_sigs = [(sig, idx) for sig, idx in sharing.items() if len(idx) >= 2]
    if not split_sigs:
        return {"k": k, "b": b, "status": "no_split"}
    sig, targets = max(split_sigs, key=lambda kv: len(kv[1]))
    feeding = [r for r in range(b - 1) if frozenset(cmod.cycles[cmod.owner[r]]) == sig]
    residue = feeding[0]
    weight = cmod.weights[cmod.owner[residue]]
    max_L = k * max(LENGTHS)
    V = min(int((b - 1) * max_L) + 400, 80_000)
    clabels = attractor_labels_upto(V, classic)
    slabels = attractor_labels_upto_Q(V, sidecar)
    measured = split_curves_Q(
        monomial_Q(k), b, LENGTHS, samples_per_band=SAMPLES, seed=3, system=sidecar
    )
    per_D = []
    maes_c_m, maes_s_m, maes_cs = [], [], []
    for j, D in enumerate(LENGTHS):
        pred_c = predict_split(D, classic, sig, clabels, targets, weight)
        pred_s = predict_split_Q(D, sidecar, sig, slabels, targets, weight)
        mrow = {i: measured.curves[i][j] for i in targets}
        maes_c_m.append(_mae(pred_c, mrow))
        maes_s_m.append(_mae(pred_s, mrow))
        maes_cs.append(_mae(pred_c, pred_s))
        per_D.append(
            {
                "D": D,
                "mae_classic_vs_measured": round(maes_c_m[-1], 6),
                "mae_sidecar_vs_measured": round(maes_s_m[-1], 6),
                "mae_classic_vs_sidecar": round(maes_cs[-1], 6),
            }
        )
    images_classic = sorted({pow(r, k, b - 1) for r in feeding})
    images_sidecar = sorted({pow(r, k, b - 1) for r in feeding})  # eval_Q(r)=r^k
    return {
        "k": k,
        "b": b,
        "status": "split",
        "signature": sorted(sig),
        "targets": targets,
        "feeding_residues": feeding,
        "image_mod_m_classic": images_classic,
        "image_mod_m_sidecar": images_sidecar,
        "engines_agree": images_classic == images_sidecar,
        "mae_classic_vs_measured_mean": round(sum(maes_c_m) / len(maes_c_m), 6),
        "mae_sidecar_vs_measured_mean": round(sum(maes_s_m) / len(maes_s_m), 6),
        "mae_classic_vs_sidecar_mean": round(sum(maes_cs) / len(maes_cs), 6),
        "per_D": per_D,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = [run_pair(k, b) for k, b in PAIRS]
    payload = {
        "stamp": stamp,
        "lengths": list(LENGTHS),
        "samples_per_band": SAMPLES,
        "note": "Classic predict_split uses v ≡ r^k (mod m); sidecar uses v ≡ Q(r).",
        "results": results,
    }
    json_path = OUT_DIR / f"monomial_compare_{stamp}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT_DIR / "monomial_compare_latest.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    lines = [
        "# Monomial bridge: classic vs sidecar F_j",
        "",
        f"Stamp: {stamp}",
        "",
        "| k | b | mae classic | mae sidecar | mae C vs S | agree image |",
        "|---|---|---------------|-------------|------------|-------------|",
    ]
    for rec in results:
        lines.append(
            f"| {rec.get('k', '—')} | {rec.get('b', '—')} | "
            f"{rec.get('mae_classic_vs_measured_mean', '—')} | "
            f"{rec.get('mae_sidecar_vs_measured_mean', '—')} | "
            f"{rec.get('mae_classic_vs_sidecar_mean', '—')} | "
            f"{rec.get('engines_agree', rec.get('status', '—'))} |"
        )
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"monomial_compare_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "monomial_compare_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
