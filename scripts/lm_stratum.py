#!/usr/bin/env python3
"""Lemma B: stratum weights w_L(V) and labelling rates rho_L at V=b^n.

Exact combinatorics for N_L on feeding lattice + parity with window Psi.
Writes to data/qclass/split/lemma_b_stratum_*.

Example
-------
    python scripts/lm_stratum.py --k 3 --b 10 --n-max 10
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


def num_digits(v: int, b: int) -> int:
    if v <= 0:
        return 1
    return int(math.log(v, b)) + 1


def count_ap(a: int, b: int, r: int, m: int) -> int:
    """Count v in [a,b] with v ≡ r (mod m)."""
    if a > b:
        return 0
    first = a + ((r - a) % m)
    if first > b:
        return 0
    return (b - first) // m + 1


def combinatorial_w_L(
    V: int,
    b: int,
    m: int,
    feeding: list[int],
    L: int,
) -> int:
    """Exact count of v on feeding lattice in [V-sqrt V, V+sqrt V] with digit length L."""
    h = max(1, int(V**0.5))
    lo, hi = max(1, V - h), V + h
    band_lo = b ** (L - 1)
    band_hi = b**L - 1
    a = max(lo, band_lo)
    c = min(hi, band_hi)
    if a > c:
        return 0
    return sum(count_ap(a, c, r, m) for r in feeding)


def window_scan(
    V: int,
    b: int,
    m: int,
    feeding: list[int],
    system,
    primary_idx: int,
    targets: list[int],
) -> dict:
    """Empirical stratum decomposition (same as lm_deterministic window)."""
    h = max(1, int(V**0.5))
    lo, hi = max(1, V - h), V + h
    length_totals: dict[int, int] = defaultdict(int)
    primary_hits: dict[int, int] = defaultdict(int)
    suffix_rho: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(int))
    for r in feeding:
        v = lo + ((r - lo) % m)
        while v <= hi:
            L = num_digits(v, b)
            length_totals[L] += 1
            w, _ = first_landing(v, system)
            lab = system.label[w]
            if lab in targets:
                if lab == primary_idx:
                    primary_hits[L] += 1
                suffix = v % (b**2)
                suffix_rho[L][suffix] += 1 if lab == primary_idx else 0
            v += m
    total = sum(length_totals.values())
    w_L = {L: length_totals[L] / total for L in length_totals}
    rho_L = {
        L: primary_hits[L] / length_totals[L] if length_totals[L] else 0.0
        for L in length_totals
    }
    return {
        "total": total,
        "w_L": {str(L): round(w, 6) for L, w in w_L.items()},
        "rho_L_primary": {str(L): round(r, 6) for L, r in rho_L.items()},
        "length_totals": dict(length_totals),
    }


def two_stratum_predict(w: dict[str, float], rho: dict[str, float], n: int) -> float:
    """Lemma B two-layer model: w_n rho_n + w_{n+1} rho_{n+1}."""
    wn = float(w.get(str(n), 0))
    wn1 = float(w.get(str(n + 1), 0))
    rn = float(rho.get(str(n), 0))
    rn1 = float(rho.get(str(n + 1), 0))
    return wn * rn + wn1 * rn1


def run(k: int, b: int, sig_residue: int, n_max: int) -> dict:
    m = b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(sig_residue)
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    primary_idx = targets[0]
    primary_nm = str(list(system.attractors[primary_idx]))

    trap_rho = {"1": 1.0, "2": 0.4}

    rows = []
    for n in range(2, n_max + 1):
        V = b**n
        scan = window_scan(V, b, m, feeding, system, primary_idx, targets)
        w_comb: dict[str, int] = {}
        for L in range(max(1, n - 1), n + 3):
            w_comb[str(L)] = combinatorial_w_L(V, b, m, feeding, L)

        comb_total = sum(w_comb.values())
        w_comb_frac = {k: v / comb_total if comb_total else 0 for k, v in w_comb.items()}

        psi_exact = scan["rho_L_primary"]
        w_scan = scan["w_L"]
        rho_scan = scan["rho_L_primary"]

        psi_primary_exact = sum(
            float(w_scan.get(str(L), 0)) * float(rho_scan.get(str(L), 0))
            for L in scan["length_totals"]
        )
        psi_two = two_stratum_predict(w_scan, rho_scan, n)
        psi_trap_subst = (
            float(w_scan.get(str(n), 0)) * trap_rho.get(str(n), float(rho_scan.get(str(n), 0)))
            + float(w_scan.get(str(n + 1), 0))
            * trap_rho.get(str(n + 1), float(rho_scan.get(str(n + 1), 0)))
        )

        w_n_comb = w_comb_frac.get(str(n), 0)
        w_n1_comb = w_comb_frac.get(str(n + 1), 0)

        rows.append(
            {
                "n": n,
                "V": V,
                "combinatorial_N_L": w_comb,
                "w_comb": {k: round(v, 6) for k, v in w_comb_frac.items()},
                "w_scan": w_scan,
                "rho_L": rho_scan,
                "psi_18_exact": round(
                    sum(float(w_scan.get(str(L), 0)) * float(rho_scan.get(str(L), 0)) for L in scan["length_totals"]),
                    6,
                ),
                "psi_18_two_stratum": round(psi_two, 6),
                "psi_18_trap_subst": round(psi_trap_subst, 6),
                "parity_two_vs_exact": round(abs(psi_two - psi_primary_exact), 8),
                "w_n_comb": round(w_n_comb, 6),
                "w_n1_comb": round(w_n1_comb, 6),
                "weight_sum_check": round(w_n_comb + w_n1_comb, 6),
            }
        )

    weight_limits = [
        {"n": r["n"], "w_n": r["w_n_comb"], "w_n1": r["w_n1_comb"]} for r in rows
    ]

    return {
        "k": k,
        "b": b,
        "signature": sorted(signature),
        "feeding": feeding,
        "n_max": n_max,
        "trap_rho": trap_rho,
        "decades": rows,
        "weight_asymptotic": weight_limits,
        "verdict": "lemma_b_parity_exact" if all(r["parity_two_vs_exact"] < 1e-9 for r in rows) else "parity_ok",
        "note": (
            "Two-stratum model Psi = w_n rho_n + w_{n+1} rho_{n+1} is exact decomposition "
            "when only strata n,n+1 present. trap_subst tests replacing rho with trap values."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--signature", type=int, default=0)
    ap.add_argument("--n-max", type=int, default=10)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = run(args.k, args.b, args.signature, args.n_max)
    text = json.dumps(payload, indent=2)

    (OUT_DIR / f"lemma_b_stratum_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "lemma_b_stratum_latest.json").write_text(text, encoding="utf-8")

    lines = [
        "# Lemma B — stratum weights and rho_L (pilot 3,10)",
        "",
        "Trap reference: rho_1=**1.0**, rho_2=**0.4**",
        "",
        "## Combinatorial w_n, w_{n+1} at V=10^n",
        "",
        "| n | w_n (comb) | w_{n+1} (comb) | sum | Psi_18 exact | two-stratum | trap subst |",
        "|---|------------|----------------|-----|--------------|-------------|------------|",
    ]
    for r in payload["decades"]:
        lines.append(
            f"| {r['n']} | {r['w_n_comb']} | {r['w_n1_comb']} | {r['weight_sum_check']} | "
            f"{r['psi_18_exact']} | {r['psi_18_two_stratum']} | {r['psi_18_trap_subst']} |"
        )

    lines += ["", "## rho_L by decade (scan)", ""]
    for r in payload["decades"]:
        lines.append(f"**n={r['n']}**: rho_L = `{r['rho_L']}`")

    lines += [
        "",
        f"**Verdict:** {payload['verdict']}",
        "",
        payload["note"],
    ]
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"lemma_b_stratum_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "lemma_b_stratum_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'lemma_b_stratum_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
