#!/usr/bin/env python3
"""Route C-A: suffix-class labelling rates rho at stratum L=n.

Since first_landing depth <= 2 (G4), classify v by v mod b^d and measure
rho_18 per suffix bucket at digit-length stratum n in window [V-sqrt V, V+sqrt V].

Writes lemma_c_route_ca_* to data/qclass/split/.

Example
-------
    python scripts/lm_suffix.py --n-max 14
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


def effective_min_count(stratum_total: int, min_count: int) -> int:
    """Scale threshold so small strata and mod-1000 buckets remain usable."""
    return max(3, min(min_count, stratum_total // 80))


def suffix_scan_decade(
    V: int,
    n: int,
    b: int,
    m: int,
    feeding: list[int],
    system,
    primary_idx: int,
    suffix_pow: int,
    min_count: int,
) -> dict:
    """rho_18 per suffix bucket at stratum L=n only."""
    h = max(1, int(V**0.5))
    lo, hi = max(1, V - h), V + h
    mod = b**suffix_pow
    buckets: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    stratum_total = 0
    stratum_hits = 0

    for r in feeding:
        v = lo + ((r - lo) % m)
        while v <= hi:
            if num_digits(v, b) == n:
                key = v % mod
                buckets[key][0] += 1
                stratum_total += 1
                w, _ = first_landing(v, system)
                if system.label[w] == primary_idx:
                    buckets[key][1] += 1
                    stratum_hits += 1
            v += m

    thresh = effective_min_count(stratum_total, min_count)
    rows = []
    for key in sorted(buckets):
        tot, hits = buckets[key]
        if tot < thresh:
            continue
        rows.append(
            {
                "suffix": key,
                "suffix_mod": mod,
                "count": tot,
                "rho_18": round(hits / tot, 6),
            }
        )

    best_gap = 0.0
    best_pair: tuple[int, int] | None = None
    best_rhos: tuple[float, float] | None = None
    for i, a in enumerate(rows):
        for b_row in rows[i + 1 :]:
            gap = abs(a["rho_18"] - b_row["rho_18"])
            if gap > best_gap:
                best_gap = gap
                best_pair = (a["suffix"], b_row["suffix"])
                best_rhos = (a["rho_18"], b_row["rho_18"])

    return {
        "n": n,
        "V": V,
        "suffix_pow": suffix_pow,
        "suffix_mod": mod,
        "min_count_used": thresh,
        "stratum_total": stratum_total,
        "stratum_rho": round(stratum_hits / stratum_total, 6) if stratum_total else 0.0,
        "buckets_used": len(rows),
        "buckets_all": len(buckets),
        "max_suffix_gap": round(best_gap, 6),
        "best_pair": list(best_pair) if best_pair else None,
        "best_rhos": list(best_rhos) if best_rhos else None,
        "bucket_rhos": {str(r["suffix"]): r["rho_18"] for r in rows},
        "top_buckets": sorted(rows, key=lambda r: r["rho_18"], reverse=True)[:5],
        "bottom_buckets": sorted(rows, key=lambda r: r["rho_18"])[:5],
    }


def stable_pair_analysis(decades: list[dict], n_lo: int = 9) -> dict:
    """Suffix pairs (mod 100) with gap present in every decade n >= n_lo."""
    mod100 = [d for d in decades if d["suffix_pow"] == 2 and d["n"] >= n_lo]
    if not mod100:
        return {"top_stable_pairs_mod100": [], "witness_pair": None}

    common_suffixes: set[str] | None = None
    per_decade: dict[int, dict[str, float]] = {}
    for dec in mod100:
        br = dec.get("bucket_rhos") or {}
        per_decade[dec["n"]] = br
        keys = set(br)
        common_suffixes = keys if common_suffixes is None else common_suffixes & keys

    pair_stats: list[dict] = []
    if common_suffixes and len(common_suffixes) >= 2:
        suffix_list = sorted(common_suffixes, key=int)
        for i, s1 in enumerate(suffix_list):
            for s2 in suffix_list[i + 1 :]:
                gaps = [abs(per_decade[n][s1] - per_decade[n][s2]) for n in per_decade]
                pair_stats.append(
                    {
                        "pair": [int(s1), int(s2)],
                        "decades": len(gaps),
                        "min_gap": round(min(gaps), 6),
                        "mean_gap": round(sum(gaps) / len(gaps), 6),
                    }
                )
        pair_stats.sort(key=lambda x: x["min_gap"], reverse=True)

    mod100_gaps = [d["max_suffix_gap"] for d in mod100]
    witness = mod100[mod100_gaps.index(max(mod100_gaps))]

    return {
        "n_lo": n_lo,
        "top_stable_pairs_mod100": pair_stats[:10],
        "witness_pair": {
            "n": witness["n"],
            "pair": witness["best_pair"],
            "rhos": witness["best_rhos"],
            "gap": witness["max_suffix_gap"],
        },
        "min_max_gap_n_ge_lo": round(min(mod100_gaps), 6),
    }


def run(k: int, b: int, sig_residue: int, n_max: int, min_count: int) -> dict:
    m = b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(sig_residue)
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    feeding = [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    primary_idx = targets[0]

    decades: list[dict] = []
    for n in range(2, n_max + 1):
        V = b**n
        for suffix_pow in (2, 3):
            decades.append(
                suffix_scan_decade(
                    V, n, b, m, feeding, system, primary_idx, suffix_pow, min_count
                )
            )

    mod100 = [d for d in decades if d["suffix_pow"] == 2]
    mod100_large = [d for d in mod100 if d["n"] >= 9 and d["buckets_used"] >= 90]
    mod100_gaps = [d["max_suffix_gap"] for d in mod100]
    mod100_large_gaps = [d["max_suffix_gap"] for d in mod100_large]
    global_max = max(mod100_gaps) if mod100_gaps else 0.0

    stable = stable_pair_analysis(decades, n_lo=9)

    refuted_uniform = (
        stable.get("min_max_gap_n_ge_lo", 0) >= 0.15
        and len(mod100_large_gaps) >= 3
        and all(g >= 0.15 for g in mod100_large_gaps)
    )

    return {
        "k": k,
        "b": b,
        "signature": sorted(signature),
        "n_max": n_max,
        "min_count": min_count,
        "route": "C-A",
        "decades": decades,
        "summary": {
            "mod100_gap_min_over_n": round(min(mod100_gaps), 6) if mod100_gaps else 0,
            "mod100_gap_min_n_ge_9": stable.get("min_max_gap_n_ge_lo", 0),
            "mod100_gap_max_over_n": round(global_max, 6),
            "mod100_gap_at_n14": round(mod100[-1]["max_suffix_gap"], 6) if mod100 else 0,
            "stable_pairs": stable,
        },
        "verdict": "suffix_gap_confirmed" if refuted_uniform else "suffix_gap_partial",
        "note": (
            "Route C-A: if rho_n converged via mixing, suffix buckets mod b^d would "
            "homogenize. Persistent max |rho(s1)-rho(s2)| >= c across decades supports "
            "intrinsic suffix-class variation (empirical; not a limit proof)."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--signature", type=int, default=0)
    ap.add_argument("--n-max", type=int, default=14)
    ap.add_argument("--min-count", type=int, default=50)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = run(args.k, args.b, args.signature, args.n_max, args.min_count)
    text = json.dumps(payload, indent=2)

    (OUT_DIR / f"lemma_c_route_ca_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "lemma_c_route_ca_latest.json").write_text(text, encoding="utf-8")

    s = payload["summary"]
    lines = [
        "# Route C-A — suffix-class rho gap (pilot 3,10)",
        "",
        f"Stratum `L=n` at `V=10^n`, `n=2…{args.n_max}`. Buckets `v mod b^d`, `d=2,3`.",
        "",
        f"**Min max-suffix-gap (mod 100), n≥9:** **{s.get('mod100_gap_min_n_ge_9', 0)}**",
        f"**Max suffix-gap (mod 100):** {s['mod100_gap_max_over_n']}",
        f"**At n={args.n_max} (mod 100):** {s['mod100_gap_at_n14']}",
        "",
        f"**Verdict:** {payload['verdict']}",
        "",
        "## Stable pair witness (n≥9, mod 100)",
        "",
    ]
    witness = s.get("stable_pairs", {}).get("witness_pair")
    if witness:
        lines.append(
            f"At `n={witness['n']}`: suffixes `{witness['pair']}` have "
            f"rho `{witness['rhos']}` → gap **{witness['gap']}**."
        )
        top = s.get("stable_pairs", {}).get("top_stable_pairs_mod100") or []
        if top:
            w = top[0]
            lines.append(
                f"Best cross-decade pair: `{w['pair']}` with min gap **{w['min_gap']}** "
                f"over `{w['decades']}` decades."
            )
    lines += [
        "",
        "## Per-decade max gap (mod 100)",
        "",
        "| n | stratum rho | buckets | max |rho(s1)-rho(s2)| | pair |",
        "|---|-------------|---------|-------------------|------|",
    ]
    for d in payload["decades"]:
        if d["suffix_pow"] != 2:
            continue
        pair = d["best_pair"] or ["—", "—"]
        lines.append(
            f"| {d['n']} | {d['stratum_rho']} | {d['buckets_used']} | "
            f"**{d['max_suffix_gap']}** | {pair[0]}, {pair[1]} |"
        )
    lines += ["", payload["note"]]
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"lemma_c_route_ca_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "lemma_c_route_ca_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'lemma_c_route_ca_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
