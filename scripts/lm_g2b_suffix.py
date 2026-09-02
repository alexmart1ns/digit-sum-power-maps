#!/usr/bin/env python3
"""Route C-B step 2: log-periodic fit on suffix-class rates rho_n(s).

Reads lemma_c_route_ca_latest.json (or reruns lm_suffix). For witness suffixes
tracks rho_18(s) across decade anchors n=9..n_max and fits constant vs cosine
models — Peter (2002) log-periodic phenomenology on suffix-restricted rates.

Writes g2b_suffix_phase_latest.* to data/qclass/split/.

Example
-------
    python scripts/lm_g2b_suffix.py --n-lo 9 --n-max 16
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
ROUTE_CA = OUT_DIR / "lemma_c_route_ca_latest.json"


def _ols(xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n < 2:
        return ys[0] if ys else 0.0, 0.0
    xbar = sum(xs) / n
    ybar = sum(ys) / n
    num = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    den = sum((x - xbar) ** 2 for x in xs)
    b = num / den if den else 0.0
    return ybar - b * xbar, b


def fit_cosine(ns: list[int], ys: list[float], periods: range) -> dict | None:
    best: dict | None = None
    for T in periods:
        cos_vals = [math.cos(2 * math.pi * n / T) for n in ns]
        a, A = _ols(cos_vals, ys)
        sse = sum((y - a - A * c) ** 2 for y, c in zip(ys, cos_vals))
        cand = {
            "period": T,
            "mean": round(a, 6),
            "amplitude": round(abs(A), 6),
            "sse": sse,
            "predict": lambda n, a=a, A=A, T=T: a + A * math.cos(2 * math.pi * n / T),
        }
        if best is None or sse < best["sse"]:
            best = cand
    return best


def load_route_ca(n_max: int) -> dict:
    if ROUTE_CA.exists():
        data = json.loads(ROUTE_CA.read_text(encoding="utf-8"))
        if data.get("n_max", 0) >= n_max:
            return data
    import lm_suffix

    return lm_suffix.run(3, 10, 0, n_max, min_count=20)


def run(n_lo: int, n_max: int, suffixes: list[int]) -> dict:
    data = load_route_ca(n_max)
    mod100 = [
        d
        for d in data["decades"]
        if d.get("suffix_pow") == 2 and n_lo <= d["n"] <= n_max and d.get("buckets_used", 0) >= 50
    ]
    mod100.sort(key=lambda d: d["n"])
    ns = [d["n"] for d in mod100]

    suffix_series: dict[str, list[dict]] = {}
    for s in suffixes:
        key = str(s)
        pts = []
        for d in mod100:
            br = d.get("bucket_rhos") or {}
            if key in br:
                pts.append({"n": d["n"], "rho": br[key]})
        suffix_series[key] = pts

    fits = []
    for key, pts in suffix_series.items():
        if len(pts) < 3:
            continue
        ns_s = [p["n"] for p in pts]
        ys = [p["rho"] for p in pts]
        mean_y = sum(ys) / len(ys)
        const_sse = sum((y - mean_y) ** 2 for y in ys)
        amp = max(ys) - min(ys)
        cos_fit = fit_cosine(ns_s, ys, range(2, 9))
        fits.append(
            {
                "suffix": int(key),
                "points": pts,
                "amplitude_range": round(amp, 6),
                "constant_sse": round(const_sse, 8),
                "cosine_fit": {
                    "period": cos_fit["period"],
                    "mean": cos_fit["mean"],
                    "amplitude": cos_fit["amplitude"],
                    "sse": round(cos_fit["sse"], 8),
                    "sse_improvement": round(const_sse - cos_fit["sse"], 8),
                }
                if cos_fit
                else None,
            }
        )

    # Witness gap [50,55] and [50,95] if available
    gaps = []
    pairs = [(50, 55), (50, 95)]
    for s1, s2 in pairs:
        k1, k2 = str(s1), str(s2)
        common = [d for d in mod100 if k1 in (d.get("bucket_rhos") or {}) and k2 in (d.get("bucket_rhos") or {})]
        if not common:
            continue
        gap_pts = [
            {
                "n": d["n"],
                "gap": abs(d["bucket_rhos"][k1] - d["bucket_rhos"][k2]),
            }
            for d in common
        ]
        gaps.append(
            {
                "pair": [s1, s2],
                "min_gap": round(min(p["gap"] for p in gap_pts), 6),
                "mean_gap": round(sum(p["gap"] for p in gap_pts) / len(gap_pts), 6),
                "points": gap_pts,
            }
        )

    # Verdict: log-periodic cosine beats constant for witness suffixes?
    improved = [f for f in fits if f.get("cosine_fit") and f["cosine_fit"]["sse_improvement"] > 0.01]
    verdict = (
        "log_periodic_phenomenology"
        if len(improved) >= 2
        else "weak_periodic_signal"
        if improved
        else "inconclusive"
    )

    return {
        "pilot": "(k,b)=(3,10), suffix mod 100",
        "n_lo": n_lo,
        "n_max": n_max,
        "suffixes": suffixes,
        "decades_used": len(mod100),
        "suffix_fits": fits,
        "witness_gaps": gaps,
        "verdict": verdict,
        "note": (
            "Route C-B step 2 (empirical): suffix-restricted labelling rates rho_n(s) on "
            "the decade window. Cosine-in-n fits test log-periodic phenomenology (Peter 2002 "
            "philosophy) without a summatory proof. Does not establish limsup rho_n(s) != liminf."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-lo", type=int, default=9)
    ap.add_argument("--n-max", type=int, default=16)
    ap.add_argument("--suffixes", type=int, nargs="+", default=[50, 55, 95])
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = run(args.n_lo, args.n_max, args.suffixes)
    text = json.dumps(payload, indent=2)

    (OUT_DIR / f"g2b_suffix_phase_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "g2b_suffix_phase_latest.json").write_text(text, encoding="utf-8")

    lines = [
        "# G2b suffix log-periodic fit — Route C-B step 2 (pilot 3,10)",
        "",
        f"Decades `n={payload['n_lo']}…{payload['n_max']}`, suffixes `{payload['suffixes']}`.",
        f"**Verdict:** {payload['verdict']}",
        "",
        "## Witness gaps",
        "",
    ]
    for g in payload["witness_gaps"]:
        lines.append(
            f"- Pair `{g['pair']}`: min gap **{g['min_gap']}**, mean **{g['mean_gap']}** "
            f"over {len(g['points'])} decades"
        )
    lines.extend(["", "## Per-suffix fits", ""])
    for f in payload["suffix_fits"]:
        cf = f.get("cosine_fit") or {}
        lines.extend(
            [
                f"### suffix {f['suffix']}",
                "",
                f"- Amplitude range: **{f['amplitude_range']}**",
                f"- Best cosine period: **{cf.get('period', '—')}**, amplitude **{cf.get('amplitude', '—')}**, "
                f"SSE gain vs constant: **{cf.get('sse_improvement', 0)}**",
                "",
                "| n | ρ(s) |",
                "|---|------|",
            ]
        )
        for p in f["points"]:
            lines.append(f"| {p['n']} | {p['rho']} |")
        lines.append("")

    lines.append(payload["note"])
    md = "\n".join(lines) + "\n"

    (OUT_DIR / f"g2b_suffix_phase_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "g2b_suffix_phase_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'g2b_suffix_phase_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
