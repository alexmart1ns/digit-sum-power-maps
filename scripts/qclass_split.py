#!/usr/bin/env python3
"""Split / F_j diagnostics for the Q-class sidecar.

Writes only to data/qclass/split/. Does not call scripts/local_mean.py or
scripts/sweep_label.py and does not write under data/split/.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.qmaps import (
    attractor_labels_upto_Q,
    build_system_Q,
    format_Q,
    monomial_Q,
    oscillation_report_Q,
    predict_split_Q,
    split_curves_Q,
    structure_Q,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "split"

# Modest bands: enough to see oscillation, cheap enough for a sidecar run.
LENGTHS = (6, 10, 14, 18, 22)
SAMPLES = 3000

TARGETS = [
    ("x^3", monomial_Q(3), 10, 0),  # Conjecture 10.6' reproduced in the sidecar
    ("x^2+x", (0, 1, 1), 10, None),
    ("x^3+1", (1, 0, 0, 1), 10, None),
    ("2x^2+3x+1", (1, 3, 2), 10, None),
]


def _mae(pred: dict[int, float], measured: dict[int, float]) -> float:
    keys = [i for i in pred if i in measured]
    if not keys:
        return float("nan")
    return sum(abs(pred[i] - measured[i]) for i in keys) / len(keys)


def diagnose(name: str, coeffs: tuple[int, ...], b: int, residue: int | None) -> dict:
    system = build_system_Q(coeffs, b)
    mod = structure_Q(coeffs, max(system.m, 1))
    sharing = system.attractors_sharing_signature()
    split_sigs = [(sig, idx) for sig, idx in sharing.items() if len(idx) >= 2]
    if not split_sigs:
        return {
            "name": name,
            "Q": format_Q(coeffs),
            "b": b,
            "status": "no_split",
            "C": system.count,
            "Cyc": mod.cycle_count,
        }

    if residue is None:
        sig, targets = max(split_sigs, key=lambda kv: len(kv[1]))
        feeding = [r for r in range(mod.m) if frozenset(mod.cycles[mod.owner[r]]) == sig]
        residue = feeding[0]
    else:
        sig = mod.signature_of_residue(residue)
        targets = sharing.get(sig, [])
        if len(targets) < 2:
            return {
                "name": name,
                "Q": format_Q(coeffs),
                "b": b,
                "status": "requested_residue_does_not_split",
                "residue": residue,
            }

    weight = mod.weights[mod.owner[residue % mod.m]]
    measured = split_curves_Q(
        coeffs, b, LENGTHS, samples_per_band=SAMPLES, seed=0, system=system
    )
    noise = 0.5 / math.sqrt(SAMPLES)
    max_L = (len(coeffs) - 1) * max(LENGTHS)
    V = min(int((b - 1) * max_L) + 400, 80_000)
    labels = attractor_labels_upto_Q(V, system)

    per_D = []
    maes = []
    for j, D in enumerate(LENGTHS):
        pred = predict_split_Q(D, system, sig, labels, targets, weight)
        mrow = {i: measured.curves[i][j] for i in targets}
        mae = _mae(pred, mrow)
        maes.append(mae)
        per_D.append(
            {
                "D": D,
                "mae_Fj": round(mae, 6),
                "F_j": {str(i): round(pred[i], 6) for i in targets},
                "measured": {str(i): round(mrow[i], 6) for i in targets},
            }
        )

    osc = [row for row in oscillation_report_Q(measured) if row["signature"] == sorted(sig)]
    agg = measured.signature_sums()[sig]
    return {
        "name": name,
        "Q": format_Q(coeffs),
        "b": b,
        "status": "split",
        "signature": sorted(sig),
        "targets": targets,
        "attractor_labels": [measured.labels[i] for i in targets],
        "p_i": weight,
        "samples_per_band": SAMPLES,
        "noise_floor": round(noise, 6),
        "mae_Fj_mean": round(sum(maes) / len(maes), 6),
        "within_3_noise": all(x <= 3 * noise for x in maes),
        "aggregate_stays_near_pi": all(abs(v - weight) < 0.05 for v in agg),
        "any_oscillates": any(row["oscillates"] for row in osc),
        "oscillation": osc,
        "per_D": per_D,
        "note": (
            "F_j is predict_split_Q (Gaussian sweep on the Q(n) mod m lattice). "
            "No period-1 Delange factor is claimed."
        ),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = [diagnose(*row) for row in TARGETS]
    payload = {"stamp": stamp, "lengths": list(LENGTHS), "results": results}
    json_path = OUT_DIR / f"split_{stamp}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT_DIR / "split_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Q-class split / F_j",
        "",
        f"Stamp: {stamp}",
        f"Bands D: {list(LENGTHS)}, samples/band: {SAMPLES}",
        "",
        "F_j := Gaussian on the lattice v ≡ Q(r) (mod m), convolved with a(v), scaled by p_i.",
        "",
        "| Q | b | status | mae F_j | osc? | aggregate ≈ p_i |",
        "|---|---|--------|---------|------|-----------------|",
    ]
    for rec in results:
        lines.append(
            f"| {rec['Q']} | {rec['b']} | {rec['status']} | "
            f"{rec.get('mae_Fj_mean', '—')} | {rec.get('any_oscillates', '—')} | "
            f"{rec.get('aggregate_stays_near_pi', '—')} |"
        )
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"split_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "split_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
