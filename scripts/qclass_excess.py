#!/usr/bin/env python3
"""Local excess Δ for the Q-class sidecar.

Writes only to data/qclass/excess/. Does not re-score the 19.5k sweep or
touch data/mining/summary_latest.json.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.qmaps import (
    build_system_Q,
    format_Q,
    local_excess_Q,
    monomial_Q,
    structure_Q,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "excess"

FAMILY: list[tuple[str, tuple[int, ...]]] = [
    ("x^2", monomial_Q(2)),
    ("x^3", monomial_Q(3)),
    ("x^4", monomial_Q(4)),
    ("x+x^2", (0, 1, 1)),
    ("x^3+1", (1, 0, 0, 1)),
    ("1+x^3", (1, 0, 0, 1)),
    ("2x^2+3x+1", (1, 3, 2)),
]
BASES = (2, 3, 8, 10, 16)


def spearman(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    rx = _ranks(xs)
    ry = _ranks(ys)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry, strict=True))
    den = (
        sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)
    ) ** 0.5
    if den == 0:
        return None
    return num / den


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    records = []
    layer_x: list[float] = []
    delta_y: list[float] = []
    for name, coeffs in FAMILY:
        for b in BASES:
            system = build_system_Q(coeffs, b)
            mod = structure_Q(coeffs, max(system.m, 1))
            rows = local_excess_Q(system)
            delta = system.count - mod.cycle_count
            rec = {
                "name": name,
                "Q": format_Q(coeffs),
                "coeffs": list(coeffs),
                "b": b,
                "m": system.m,
                "M": system.M,
                "C": system.count,
                "Cyc": mod.cycle_count,
                "Delta": delta,
                "tight": delta == 0,
                "local_excess": rows,
                "max_digit_layers": max((r["n_digit_layers"] for r in rows), default=0),
                "note": (
                    "a_i = number of physical cycles in [1,M] ∩ N_i; "
                    "Δ = Σ (a_i - 1). No closed form is claimed."
                ),
            }
            records.append(rec)
            for row in rows:
                layer_x.append(float(row["n_digit_layers"]))
                delta_y.append(float(row["delta_local"]))

    rho = spearman(layer_x, delta_y)
    n_tight = sum(1 for r in records if r["tight"])
    payload = {
        "stamp": stamp,
        "n_pairs": len(records),
        "n_tight_Delta0": n_tight,
        "spearman_layers_vs_delta_local": rho,
        "records": records,
    }
    json_path = OUT_DIR / f"excess_{stamp}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT_DIR / "excess_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Q-class excess",
        "",
        f"Stamp: {stamp}",
        f"Pairs: **{len(records)}**; Δ = 0 on **{n_tight}**",
        f"Spearman(n_digit_layers, delta_local) over signatures: **{rho}**",
        "",
        "Δ = |C| − Cyc(φ_Q) = Σ (a_i − 1), with a_i the number of physical",
        "attractors on modular cycle γ_i inside the contraction window.",
        "",
        "| Q | b | C | Cyc | Δ | max layers | tight |",
        "|---|---|---|-----|---|------------|-------|",
    ]
    for rec in records:
        lines.append(
            f"| {rec['Q']} | {rec['b']} | {rec['C']} | {rec['Cyc']} | {rec['Delta']} | "
            f"{rec['max_digit_layers']} | {rec['tight']} |"
        )
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"excess_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "excess_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {json_path} tight={n_tight} spearman={rho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
