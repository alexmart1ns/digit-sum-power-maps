#!/usr/bin/env python3
"""Pilot of S_b(Q(n)) on a small polynomial class.

Writes only to data/qclass/pilot/. Compares monomials to build_system in
memory; never overwrites data/sweeps or data/split.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.dynamics import build_system
from dspm.qmaps import (
    build_system_Q,
    excess_identity_holds_Q,
    finite_window_identity_holds,
    format_Q,
    monomial_Q,
    structure_Q,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "pilot"

FAMILY: list[tuple[str, tuple[int, ...], int | None]] = [
    ("x^2", monomial_Q(2), 2),
    ("x^3", monomial_Q(3), 3),
    ("x^4", monomial_Q(4), 4),
    ("x+x^2", (0, 1, 1), None),
    ("x^3+1", (1, 0, 0, 1), None),
    ("1+x^3", (1, 0, 0, 1), None),
    ("2x^2+3x+1", (1, 3, 2), None),
]
BASES = (2, 3, 8, 10, 16)


def pair_record(name: str, coeffs: tuple[int, ...], k: int | None, b: int) -> dict:
    system = build_system_Q(coeffs, b)
    mod = structure_Q(coeffs, max(system.m, 1))
    cyc = mod.cycle_count
    delta = system.count - cyc
    sharing = system.attractors_sharing_signature()
    splits = {str(sorted(sig)): len(idx) for sig, idx in sharing.items() if len(idx) >= 2}
    rec: dict = {
        "name": name,
        "Q": format_Q(coeffs),
        "coeffs": list(coeffs),
        "k_monomial": k,
        "b": b,
        "m": system.m,
        "M": system.M,
        "C": system.count,
        "Cyc": cyc,
        "Delta": delta,
        "lower_bound_holds": system.count >= cyc,
        "excess_identity": excess_identity_holds_Q(system, cyc),
        "window_identity": finite_window_identity_holds(system),
        "attractors": [list(a) for a in system.attractors],
        "split_signatures": splits,
        "n_split_signatures": len(splits),
        "weights": list(mod.weights),
    }
    if k is not None:
        classic = build_system(k, b)
        rec["monomial_match"] = set(system.attractors) == set(classic.attractors)
        rec["classic_C"] = classic.count
        rec["classic_M"] = classic.M
    return rec


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    records = []
    failed = []
    for name, coeffs, k in FAMILY:
        for b in BASES:
            rec = pair_record(name, coeffs, k, b)
            records.append(rec)
            ok = rec["lower_bound_holds"] and rec["excess_identity"] and rec["window_identity"]
            if k is not None:
                ok = ok and rec.get("monomial_match") is True
            if not ok:
                failed.append((name, b, rec))

    jsonl_path = OUT_DIR / f"pilot_{stamp}.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
    (OUT_DIR / "pilot_latest.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8"
    )

    n = len(records)
    n_split = sum(1 for r in records if r["n_split_signatures"] > 0)
    n_exact = sum(1 for r in records if r["Delta"] == 0)
    lines = [
        "# Q-class pilot",
        "",
        f"Stamp: {stamp}",
        f"Pairs: **{n}** (family × bases {list(BASES)})",
        f"Lower bound + excess identity + window identity failed: **{len(failed)}**",
        f"Pairs with a split signature (a_i ≥ 2): **{n_split}**",
        f"Pairs with Δ = 0: **{n_exact}**",
        "",
        "| Q | b | C | Cyc | Δ | split? | monomial match |",
        "|---|---|---|-----|---|--------|----------------|",
    ]
    for rec in records:
        match = rec.get("monomial_match", "—")
        lines.append(
            f"| {rec['Q']} | {rec['b']} | {rec['C']} | {rec['Cyc']} | {rec['Delta']} | "
            f"{rec['n_split_signatures'] > 0} | {match} |"
        )
    if failed:
        lines += ["", "## Failures", ""]
        for name, b, rec in failed:
            lines.append(
                f"- {name}, b={b}: lower={rec['lower_bound_holds']} "
                f"excess={rec['excess_identity']} window={rec['window_identity']} "
                f"monomial={rec.get('monomial_match')}"
            )
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"pilot_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "pilot_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {jsonl_path} failed={len(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
