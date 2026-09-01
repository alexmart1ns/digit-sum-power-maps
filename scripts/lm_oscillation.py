#!/usr/bin/env python3
"""Lemma C: oscillation analysis of Psi_j(10^n) and rho_n.

Reads lemma_b_stratum output or recomputes. Writes lemma_c_oscillation_*.

Example
-------
    python scripts/lm_oscillation.py --n-max 14
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


def _ols(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Least squares: y ≈ a + b*x. Returns (a, b)."""
    n = len(xs)
    if n < 2:
        return ys[0] if ys else 0.0, 0.0
    xbar = sum(xs) / n
    ybar = sum(ys) / n
    num = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    den = sum((x - xbar) ** 2 for x in xs)
    b = num / den if den else 0.0
    a = ybar - b * xbar
    return a, b


def _fit_log_periodic(ns: list[int], ys: list[float], periods: range) -> dict | None:
    """Fit rho ≈ L + A*cos(2π n / T) for integer period T; return best by SSE."""
    best: dict | None = None
    for T in periods:
        cos_vals = [math.cos(2 * math.pi * n / T) for n in ns]
        a, A = _ols(cos_vals, ys)
        sse = sum((y - a - A * c) ** 2 for y, c in zip(ys, cos_vals))
        pred = lambda n: a + A * math.cos(2 * math.pi * n / T)  # noqa: E731
        cand = {"period": T, "L": round(a, 6), "amplitude": round(abs(A), 6), "sse": sse, "predict": pred}
        if best is None or sse < best["sse"]:
            best = cand
    return best


def route_cc_refutation(ns: list[int], rho: list[float], psi: list[float], train_hi: int = 8) -> dict:
    """Route C-C: if rho_n -> L, regression on early decades predicts late ones."""
    train_idx = [i for i, n in enumerate(ns) if n <= train_hi]
    test_idx = [i for i, n in enumerate(ns) if n > train_hi]
    train_ns = [ns[i] for i in train_idx]
    train_rho = [rho[i] for i in train_idx]
    test_ns = [ns[i] for i in test_idx]
    test_rho = [rho[i] for i in test_idx]
    test_psi = [psi[i] for i in test_idx]

    # Model 1: constant limit L = mean(train)
    L_const = sum(train_rho) / len(train_rho)
    const_preds = {n: L_const for n in test_ns}
    const_errs = {n: round(abs(r - L_const), 6) for n, r in zip(test_ns, test_rho)}

    # Model 2: rho = a + b/n
    inv_n = [1.0 / n for n in train_ns]
    a_inv, b_inv = _ols(inv_n, train_rho)
    inv_preds = {n: round(a_inv + b_inv / n, 6) for n in test_ns}
    inv_errs = {n: round(abs(r - inv_preds[n]), 6) for n, r in zip(test_ns, test_rho)}

    # Model 3: rho = a + b*n (drift — should fail if oscillating)
    a_lin, b_lin = _ols([float(n) for n in train_ns], train_rho)
    lin_preds = {n: round(a_lin + b_lin * n, 6) for n in test_ns}
    lin_errs = {n: round(abs(r - lin_preds[n]), 6) for n, r in zip(test_ns, test_rho)}

    # Model 4: best log-periodic on train
    lp = _fit_log_periodic(train_ns, train_rho, range(2, 8))
    lp_preds = {}
    lp_errs = {}
    if lp:
        for n, r in zip(test_ns, test_rho):
            p = lp["predict"](n)
            lp_preds[n] = round(p, 6)
            lp_errs[n] = round(abs(r - p), 6)

    # Running range: should shrink toward 0 if converging
    running_range = []
    for i in range(len(rho)):
        running_range.append(round(max(rho[: i + 1]) - min(rho[: i + 1]), 6))

    # Tail gap on full sequence
    rho_gap_full = round(max(rho) - min(rho), 6)
    psi_gap_full = round(max(psi) - min(psi), 6)

    # Refutation criteria (empirical, not proof)
    tol = 0.05
    max_const_err = max(const_errs.values()) if const_errs else 0.0
    max_inv_err = max(inv_errs.values()) if inv_errs else 0.0
    max_lp_err = max(lp_errs.values()) if lp_errs else float("inf")
    range_shrinks = running_range[-1] < running_range[train_idx[-1]] * 0.5

    refuted = (
        rho_gap_full >= 0.25
        and max_const_err > tol
        and max_inv_err > tol
        and (not lp or max_lp_err > tol)
        and not range_shrinks
    )

    models = {
        "constant": {
            "L_hat": round(L_const, 6),
            "train_n": train_hi,
            "test_predictions": const_preds,
            "test_abs_errors": const_errs,
            "max_test_error": round(max_const_err, 6),
        },
        "linear_inv_n": {
            "a": round(a_inv, 6),
            "b": round(b_inv, 6),
            "formula": "rho_n = a + b/n",
            "test_predictions": inv_preds,
            "test_abs_errors": inv_errs,
            "max_test_error": round(max_inv_err, 6),
        },
        "linear_n": {
            "a": round(a_lin, 6),
            "b": round(b_lin, 6),
            "formula": "rho_n = a + b*n",
            "test_predictions": lin_preds,
            "test_abs_errors": lin_errs,
            "max_test_error": round(max(lin_errs.values()) if lin_errs else 0, 6),
        },
    }
    if lp:
        models["log_periodic"] = {
            "period_T": lp["period"],
            "L_hat": lp["L"],
            "amplitude": lp["amplitude"],
            "formula": f"rho_n = L + A*cos(2π n / {lp['period']})",
            "test_predictions": lp_preds,
            "test_abs_errors": lp_errs,
            "max_test_error": round(max_lp_err, 6),
        }

    return {
        "train_hi": train_hi,
        "test_ns": test_ns,
        "rho_running_range": dict(zip(ns, running_range)),
        "rho_gap_full": rho_gap_full,
        "psi_gap_full": psi_gap_full,
        "range_at_train_end": running_range[train_idx[-1]],
        "range_at_end": running_range[-1],
        "range_shrinks": range_shrinks,
        "tolerance": tol,
        "models": models,
        "verdict": "convergence_refuted" if refuted else "inconclusive",
        "note": (
            "Route C-C: if rho_n -> L, hold-out decades n>8 should match constant, "
            "1/n-decay, or low-period cosine fit within tolerance. Persistent gap "
            "and OOS errors refute convergence on the tested models (empirical only)."
        ),
    }


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

    route_cc = route_cc_refutation(ns, rho_n, psi, train_hi=8)

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
        "route_cc": route_cc,
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
    lines += ["", f"**Verdict:** {result['verdict']}", ""]

    cc = result.get("route_cc", {})
    if cc:
        lines += [
            "## Route C-C — convergence refutation",
            "",
            f"Train `n≤{cc['train_hi']}`, hold-out `n={cc['test_ns']}`. Tolerance `{cc['tolerance']}`.",
            "",
            f"| Model | L̂ / fit | max |error| on hold-out |",
            f"|-------|---------|----------------------|",
        ]
        for name, m in cc["models"].items():
            L = m.get("L_hat", m.get("formula", "—"))
            lines.append(f"| {name} | {L} | **{m['max_test_error']}** |")
        lines += [
            "",
            f"**ρ running range** at train end: {cc['range_at_train_end']}; at n={result['n_range'][1]}: **{cc['range_at_end']}**",
            f"**Full ρ gap:** {cc['rho_gap_full']} | **Full Ψ gap:** {cc['psi_gap_full']}",
            f"**Route C-C verdict:** **{cc['verdict']}**",
            "",
            cc["note"],
            "",
        ]

    lines.append(result["note"])
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"lemma_c_oscillation_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "lemma_c_oscillation_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'lemma_c_oscillation_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
