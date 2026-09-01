#!/usr/bin/env python3
"""Isolated OEIS / survey-table check against the existing engine.

Writes only to data/qclass/checks/. Never touches data/sweeps, data/mining,
or data/split. Uses build_system(k, 10), not historical JSONL.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.dynamics import build_system

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "checks"

# Alcântara survey (July 2026) Tables 2–3, independently the rows of OEIS A152147
# plus the listed non-fixed cycles. Not copied into data/sweeps.
SURVEY_FIXED = {
    2: [1, 9],
    3: [1, 8, 17, 18, 26, 27],
    4: [1, 7, 22, 25, 28, 36],
    5: [1, 28, 35, 36, 46],
    6: [1, 18, 45, 54, 64],
    7: [1, 18, 27, 31, 34, 43, 53, 58, 68],
    8: [1, 46, 54, 63],
    9: [1, 54, 71, 81],
    10: [1, 82, 85, 94, 97, 106, 117],
}

SURVEY_PAIRS = {
    2: [(13, 16)],
    3: [(19, 28)],
    4: [(18, 27)],
    5: [(23, 29), (31, 34)],
    6: [],
    7: [(38, 47), (44, 62), (46, 55), (56, 65)],
    8: [(64, 73)],
    9: [(35, 80)],
    10: [],
}

SURVEY_LONGER = {
    2: [],
    3: [],
    4: [],
    5: [(7, 22, 25, 40)],
    6: [],
    7: [(36, 54, 63, 72)],
    8: [(31, 52, 67, 70)],
    9: [(73, 82, 91), (45, 72, 90, 99)],
    10: [(43, 61, 70), (45, 63, 72, 81, 90, 99)],
}


def _norm(cycle: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(cycle))


def expected_attractors(k: int) -> set[tuple[int, ...]]:
    out: set[tuple[int, ...]] = set()
    for x in SURVEY_FIXED[k]:
        out.add((x,))
    for pair in SURVEY_PAIRS[k]:
        out.add(_norm(tuple(pair)))
    for cyc in SURVEY_LONGER[k]:
        out.add(_norm(tuple(cyc)))
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows = []
    all_ok = True
    for k in range(2, 11):
        system = build_system(k, 10)
        got = {tuple(a) for a in system.attractors}
        exp = expected_attractors(k)
        match = got == exp
        all_ok = all_ok and match
        rows.append(
            {
                "k": k,
                "b": 10,
                "M": system.M,
                "count": system.count,
                "attractors": [list(a) for a in system.attractors],
                "survey_expected": [list(a) for a in sorted(exp, key=lambda t: (len(t), t))],
                "match": match,
                "missing": [list(a) for a in sorted(exp - got)],
                "extra": [list(a) for a in sorted(got - exp)],
            }
        )

    payload = {
        "stamp": stamp,
        "source": "Alcântara survey Tables 2–3 / OEIS A152147, checked via build_system",
        "note": "In-memory comparison only. Does not rewrite data/sweeps or data/split.",
        "all_match": all_ok,
        "rows": rows,
    }
    json_path = OUT_DIR / f"oeis_k2-10_{stamp}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT_DIR / "oeis_k2-10.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Survey / OEIS check (isolated)",
        "",
        f"Stamp: {stamp}",
        f"All match: **{all_ok}**",
        "",
        "| k | |C| | match | missing | extra |",
        "|---|-----|-------|---------|-------|",
    ]
    for row in rows:
        lines.append(
            f"| {row['k']} | {row['count']} | {row['match']} | "
            f"{row['missing'] or '—'} | {row['extra'] or '—'} |"
        )
    md_path = OUT_DIR / f"oeis_k2-10_{stamp}.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT_DIR / "oeis_k2-10.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {json_path} all_match={all_ok}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
