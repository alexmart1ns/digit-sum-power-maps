#!/usr/bin/env python3
"""Route C-B / G2b: adjacent-layer rate correlation at decade anchors V=10^n.

Reads lemma_b_stratum_latest.json (or recomputes via lm_stratum). Measures whether
rho_L at layers n and n+1 co-move across decades — a covariance proxy for the
independence assumption in predict_split's digit-count mixture.

Writes g2b_layer_cov_latest.* to data/qclass/split/.

Example
-------
    python scripts/lm_g2b_layer.py --n-lo 9 --n-max 16
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


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def load_decades(n_max: int) -> list[dict]:
    if STRATUM.exists():
        data = json.loads(STRATUM.read_text(encoding="utf-8"))
        decades = [d for d in data["decades"] if d["n"] <= n_max]
        if decades and decades[-1]["n"] >= min(n_max, decades[-1]["n"]):
            return decades
    import lm_stratum

    payload = lm_stratum.run(3, 10, 0, n_max)
    return payload["decades"]


def run(n_lo: int, n_max: int) -> dict:
    decades = [d for d in load_decades(n_max) if n_lo <= d["n"] <= n_max]
    rows = []
    rho_n_seq: list[float] = []
    rho_n1_seq: list[float] = []
    psi_seq: list[float] = []
    two_seq: list[float] = []
    ns: list[int] = []

    for d in decades:
        n = d["n"]
        rho = d["rho_L"]
        w = d["w_scan"]
        rn = float(rho.get(str(n), 0))
        rn1 = float(rho.get(str(n + 1), 0))
        wn = float(w.get(str(n), 0))
        wn1 = float(w.get(str(n + 1), 0))
        psi = float(d["psi_18_exact"])
        two = float(d["psi_18_two_stratum"])
        rows.append(
            {
                "n": n,
                "rho_L_n": round(rn, 6),
                "rho_L_n1": round(rn1, 6),
                "delta_rho_layers": round(abs(rn - rn1), 6),
                "w_n": round(wn, 6),
                "w_n1": round(wn1, 6),
                "psi_18": psi,
                "psi_two_stratum": two,
                "two_stratum_error": round(abs(psi - two), 8),
            }
        )
        ns.append(n)
        rho_n_seq.append(rn)
        rho_n1_seq.append(rn1)
        psi_seq.append(psi)
        two_seq.append(two)

    r_layers = pearson(rho_n_seq, rho_n1_seq)
    r_psi_two = pearson(psi_seq, two_seq)
    # Lag-1 autocorrelation of rho_L(n) across consecutive decades
    rho_lag = pearson(rho_n_seq[:-1], rho_n_seq[1:]) if len(rho_n_seq) > 2 else None

    mean_layer_gap = sum(abs(a - b) for a, b in zip(rho_n_seq, rho_n1_seq)) / len(rho_n_seq)
    max_two_err = max(r["two_stratum_error"] for r in rows) if rows else 0.0

    # G2b verdict: strong same-anchor layer correlation => mixture not layer-independent
    if r_layers is not None and abs(r_layers) >= 0.5:
        verdict = "layer_correlation_detected"
    elif r_layers is not None and abs(r_layers) >= 0.3:
        verdict = "weak_layer_correlation"
    else:
        verdict = "layer_correlation_low"

    return {
        "pilot": "(k,b)=(3,10), attractor {18}",
        "n_lo": n_lo,
        "n_max": n_max,
        "decades": rows,
        "pearson_rho_L_n_vs_n_plus_1": round(r_layers, 6) if r_layers is not None else None,
        "pearson_rho_L_n_lag1": round(rho_lag, 6) if rho_lag is not None else None,
        "pearson_psi_exact_vs_two_stratum": round(r_psi_two, 6) if r_psi_two is not None else None,
        "mean_abs_rho_n_minus_rho_n1": round(mean_layer_gap, 6),
        "max_two_stratum_error": max_two_err,
        "verdict": verdict,
        "note": (
            "Route C-B proxy: at anchor V=10^n, labelling rates at digit layers L=n and L=n+1 "
            "are measured on the same window. Pearson r quantifies co-movement (G2b covariance "
            "phenomenology). predict_split treats layers as independent Gaussians; "
            "two-stratum error near 0 shows the dominant mass is in {n,n+1} but does not "
            "imply layer independence for suffix-restricted rates rho_n(s)."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-lo", type=int, default=9)
    ap.add_argument("--n-max", type=int, default=16)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = run(args.n_lo, args.n_max)
    text = json.dumps(payload, indent=2)

    (OUT_DIR / f"g2b_layer_cov_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "g2b_layer_cov_latest.json").write_text(text, encoding="utf-8")

    r = payload["pearson_rho_L_n_vs_n_plus_1"]
    lines = [
        "# G2b layer covariance — Route C-B proxy (pilot 3,10)",
        "",
        f"Decade anchors `V=10^n`, `n={payload['n_lo']}…{payload['n_max']}`.",
        "",
        f"**Pearson ρ(L=n) vs ρ(L=n+1) at same anchor:** **{r}**",
        f"**Lag-1 autocorr ρ(L=n):** {payload['pearson_rho_L_n_lag1']}",
        f"**Mean |ρ_n − ρ_n+1|:** {payload['mean_abs_rho_n_minus_rho_n1']}",
        f"**Max two-stratum |Ψ − Ψ̂|:** {payload['max_two_stratum_error']}",
        f"**Verdict:** {payload['verdict']}",
        "",
        "| n | ρ(L=n) | ρ(L=n+1) | |Δρ| | Ψ_18 | two-stratum err |",
        "|---|--------|----------|------|------|-----------------|",
    ]
    for row in payload["decades"]:
        lines.append(
            f"| {row['n']} | {row['rho_L_n']} | {row['rho_L_n1']} | "
            f"{row['delta_rho_layers']} | {row['psi_18']} | {row['two_stratum_error']} |"
        )
    lines.extend(["", payload["note"]])
    md = "\n".join(lines) + "\n"

    (OUT_DIR / f"g2b_layer_cov_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "g2b_layer_cov_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'g2b_layer_cov_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
