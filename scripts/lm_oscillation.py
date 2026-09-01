#!/usr/bin/env python3
"""Lemma C: oscillation analysis of Psi_j(10^n) and rho_n.

Reads lemma_b_stratum output or recomputes. Writes lemma_c_oscillation_*.

Example
-------
    python scripts/lm_oscillation.py --n-max 12
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "split"
STRATUM = OUT_DIR / "lemma_b_stratum_latest.json"


def load_or_run(n_max: int) -> list[dict]:
    if STRATUM.exists():
        data = json.loads(STRATUM.read_text(encoding="utf-8"))
        decades = [d for d in data["decades"] if d["n"] <= n_max]
        if decades and decades[-1]["n"] >= min(n_max, decades[-1]["n"]):
            return decades
    import lm_stratum

    payload = lm_stratum.run(3, 10, 0, n_max)
    return payload["decades"]


def analyze(decades: list[dict]) -> dict:
    psi = [d["psi_18_exact"] for d in decades]
    ns = [d["n"] for d in decades]
    rho_n = [float(d["rho_L"].get(str(d["n"]), 0)) for d in decades]
    rho_n1 = [float(d["rho_L"].get(str(d["n"] + 1), 0)) for d in decades]

    gaps_psi = [abs(psi[i + 1] - psi[i]) for i in range(len(psi) - 1)]
    gaps_rho = [abs(rho_n[i + 1] - rho_n[i]) for i in range(len(rho_n) - 1)]

    psi_min = min(psi)
    psi_max = max(psi)
    psi_gap = psi_max - psi_min
    rho_gap = max(rho_n) - min(rho_n)

    min_n = ns[psi.index(psi_min)]
    max_n = ns[psi.index(psi_max)]

    rows = []
    for d, p, rn, rn1, i in zip(decades, psi, rho_n, rho_n1, range(len(decades))):
        rows.append(
            {
                "n": d["n"],
                "V": d["V"],
                "psi_18": p,
                "rho_n": rn,
                "rho_n1": rn1,
                "delta_psi_next": round(gaps_psi[i], 6) if i < len(gaps_psi) else None,
                "delta_rho_next": round(gaps_rho[i], 6) if i < len(gaps_rho) else None,
            }
        )

    return {
        "n_range": [ns[0], ns[-1]],
        "psi_18": {
            "values": dict(zip(ns, psi)),
            "min": round(psi_min, 6),
            "max": round(psi_max, 6),
            "gap": round(psi_gap, 6),
            "min_at_n": min_n,
            "max_at_n": max_n,
        },
        "rho_n": {
            "values": dict(zip(ns, [round(r, 6) for r in rho_n])),
            "gap": round(rho_gap, 6),
        },
        "adjacent_gaps_psi": gaps_psi,
        "adjacent_gaps_rho": gaps_rho,
        "max_adjacent_psi": round(max(gaps_psi), 6) if gaps_psi else 0,
        "decades": rows,
        "verdict": "suggests_oscillation" if psi_gap >= 0.25 else "gap_small",
        "lemma_c_empirical_gap": round(psi_gap, 6),
        "note": (
            "Empirical gap on subsequence V=10^n does not prove liminf != limsup. "
            "Lemma C requires analytic bound on rho_n or Psi alternation."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-max", type=int, default=12)
    args = ap.parse_args()

    decades = load_or_run(args.n_max)
    if not decades or decades[-1]["n"] < args.n_max:
        import lm_stratum

        payload = lm_stratum.run(3, 10, 0, args.n_max)
        decades = payload["decades"]
        STRATUM.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    result = analyze(decades)
    result["n_max"] = args.n_max

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    text = json.dumps(result, indent=2)
    (OUT_DIR / f"lemma_c_oscillation_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "lemma_c_oscillation_latest.json").write_text(text, encoding="utf-8")

    p = result["psi_18"]
    lines = [
        "# Lemma C — oscillation analysis (pilot 3,10)",
        "",
        f"Subsequence `V=10^n`, `n={result['n_range'][0]}…{result['n_range'][1]}`.",
        "",
        f"**Psi_18 gap:** {p['min']} (n={p['min_at_n']}) to {p['max']} (n={p['max_at_n']}) → **{p['gap']}**",
        f"**rho_n gap:** {result['rho_n']['gap']}",
        f"**Max adjacent |Delta Psi|:** {result['max_adjacent_psi']}",
        "",
        "| n | Psi_18 | rho_n | rho_{n+1} | |Delta Psi| |",
        "|---|--------|-------|-----------|-------------|",
    ]
    for row in result["decades"]:
        dpsi = row["delta_psi_next"]
        dpsi_s = f"{dpsi:.4f}" if dpsi is not None else "—"
        lines.append(
            f"| {row['n']} | {row['psi_18']} | {row['rho_n']} | {row['rho_n1']} | {dpsi_s} |"
        )
    lines += ["", f"**Verdict:** {result['verdict']}", "", result["note"]]
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"lemma_c_oscillation_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "lemma_c_oscillation_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'lemma_c_oscillation_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
