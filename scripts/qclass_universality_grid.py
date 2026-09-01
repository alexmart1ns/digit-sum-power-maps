#!/usr/bin/env python3
"""Universality grid for S_b(Q(n)): pilot scan + split/F_j on key pairs.

Writes only under data/qclass/. See data/qclass/README.md for the summary table.

Examples
--------
    python scripts/qclass_universality_grid.py
    python scripts/qclass_universality_grid.py --quick
"""

from __future__ import annotations

import json
import math
import random
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
OUT_DIR = REPO_ROOT / "data" / "qclass" / "universality"

GRID: list[tuple[str, tuple[int, ...], int, int | None]] = [
    ("x^2", monomial_Q(2), 10, None),
    ("x^2", monomial_Q(2), 16, None),
    ("x^3", monomial_Q(3), 10, 0),
    ("x^3", monomial_Q(3), 16, None),
    ("x^4", monomial_Q(4), 10, None),
    ("x^4", monomial_Q(4), 16, None),
    ("x+x^2", (0, 1, 1), 10, None),
    ("x+x^2", (0, 1, 1), 8, None),
    ("1+3x+2x^2", (1, 3, 2), 10, None),
    ("1+3x+2x^2", (1, 3, 2), 8, None),
    ("1+x^3", (1, 0, 0, 1), 10, None),
    ("1+x^3", (1, 0, 0, 1), 8, None),
]

LENGTHS = tuple(range(8, 65, 4))
SAMPLES = 8_000 if "--quick" in __import__("sys").argv else 12_000


def _mae(pred: dict[int, float], measured: dict[int, float]) -> float:
    keys = [i for i in pred if i in measured]
    if not keys:
        return float("nan")
    return sum(abs(pred[i] - measured[i]) for i in keys) / len(keys)


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys, strict=True))
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    return num / den if den else None


def evaluate_pair(name: str, coeffs: tuple[int, ...], b: int, sig_residue: int | None) -> dict:
    system = build_system_Q(coeffs, b)
    mod = structure_Q(coeffs, max(system.m, 1))
    sharing = system.attractors_sharing_signature()
    split_sigs = [sig for sig, idx in sharing.items() if len(idx) >= 2]
    rec: dict = {
        "name": name,
        "Q": format_Q(coeffs),
        "b": b,
        "C": system.count,
        "Cyc": mod.cycle_count,
        "Delta": system.count - mod.cycle_count,
        "has_split": bool(split_sigs),
        "split_signatures": [sorted(s) for s in split_sigs],
    }
    if not split_sigs:
        return rec

    if sig_residue is not None:
        signature = mod.signature_of_residue(sig_residue)
    else:
        signature = max(split_sigs, key=lambda s: len(sharing[s]))
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    weight = mod.weights[mod.owner[next(iter(signature)) % mod.m]]

    curves = split_curves_Q(
        coeffs, b, list(LENGTHS), samples_per_band=SAMPLES, seed=0, system=system
    )
    report = oscillation_report_Q(curves)
    amps = [report[i]["amplitude"] for i in targets]
    rec["signature"] = sorted(signature)
    rec["n_attractors"] = len(targets)
    rec["amplitude_max"] = max(amps) if amps else 0.0
    rec["antiphase_r"] = _pearson(
        [curves.curves[targets[0]][j] for j in range(len(LENGTHS))],
        [curves.curves[targets[1]][j] for j in range(len(LENGTHS))],
    ) if len(targets) == 2 else None

    ceiling = int((b - 1) / 2 * (len(coeffs) - 1) * max(LENGTHS)) + 400
    labels = attractor_labels_upto_Q(ceiling, system)
    maes = []
    for j, D in enumerate(LENGTHS):
        pred = predict_split_Q(D, system, signature, labels, targets, weight)
        for i in targets:
            maes.append(abs(pred[i] - curves.curves[i][j]))
    rec["F_j_mae"] = sum(maes) / len(maes) if maes else float("nan")
    return rec


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows = [evaluate_pair(name, coeffs, b, sig) for name, coeffs, b, sig in GRID]
    payload = {"stamp": stamp, "samples_per_band": SAMPLES, "lengths": list(LENGTHS), "rows": rows}
    text = json.dumps(payload, indent=2)
    (OUT_DIR / f"grid_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "grid_latest.json").write_text(text, encoding="utf-8")

    lines = [
        "# Q-class universality grid",
        "",
        f"Stamp: {stamp}",
        f"Band: D in {list(LENGTHS)}; samples/band={SAMPLES}",
        "",
        "| Q | b | split? | Δ | amp | antiphase r | F_j MAE |",
        "|---|---|--------|---|-----|-------------|---------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['Q']} | {r['b']} | {r['has_split']} | {r['Delta']} | "
            f"{r.get('amplitude_max', '—')} | {r.get('antiphase_r', '—')} | "
            f"{r.get('F_j_mae', '—')} |"
        )
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"grid_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "grid_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'grid_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
