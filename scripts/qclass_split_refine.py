#!/usr/bin/env python3
"""Longer-band split + F_j failure diagnosis.

Primary target: Q(x) = 1+3x+2x^2 at b=10 (new oscillation; Gaussian MAE was 0.17).
Secondary: Q(x) = x^3 at b=10 (Conjecture 10.6' window was too short).

Writes only to data/qclass/split/refine_*. Does not overwrite split_latest
from the first sidecar run, and does not touch data/split/.
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.core import num_digits
from dspm.qmaps import (
    attractor_labels_upto_Q,
    build_system_Q,
    digit_count_mixture_Q,
    eval_Q,
    f_Qb,
    format_Q,
    monomial_Q,
    oscillation_report_Q,
    predict_split_Q,
    split_curves_Q,
    structure_Q,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "split"

LENGTHS = tuple(range(8, 65, 4))
SAMPLES = 12_000
DIAG_D = (8, 16, 24, 40, 56)
DIAG_SAMPLES = 5_000

TARGETS = [
    ("2x^2+3x+1", (1, 3, 2), 10, None),
    ("x^3", monomial_Q(3), 10, 0),
]


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
    den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
    if den == 0:
        return None
    return num / den


def _tv(p: dict[int, float], q: dict[int, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def diagnose_landing(
    coeffs: tuple[int, ...],
    b: int,
    D: int,
    system,
    feeding: list[int],
    n_samples: int,
    seed: int,
) -> dict:
    """Compare actual S_b(Q(n)) and digit length of Q(n) to the Gaussian-sweep assumptions."""
    rng = random.Random(seed)
    m = max(b - 1, 1)
    feeding_set = set(feeding)
    lo, hi = b ** (D - 1), b**D - 1
    mix = digit_count_mixture_Q(D, coeffs, b)
    L_emp: Counter[int] = Counter()
    m1_vals: list[int] = []
    steps_list: list[int] = []
    mean_given_L: dict[int, list[int]] = {}
    n_ok = 0
    guard = 0
    while n_ok < n_samples and guard < n_samples * 40:
        guard += 1
        n = rng.randint(lo, hi)
        if (n % m) not in feeding_set:
            continue
        qn = eval_Q(n, coeffs)
        L = num_digits(max(qn, 1), b)
        m1 = f_Qb(n, coeffs, b)
        L_emp[L] += 1
        m1_vals.append(m1)
        mean_given_L.setdefault(L, []).append(m1)
        w = m1
        steps = 1
        while w > system.M:
            w = f_Qb(w, coeffs, b)
            steps += 1
        steps_list.append(steps)
        n_ok += 1
    if n_ok == 0:
        return {"D": D, "status": "no_samples"}

    emp_L = {L: c / n_ok for L, c in L_emp.items()}
    mu_hat = sum(m1_vals) / n_ok
    var_hat = sum((x - mu_hat) ** 2 for x in m1_vals) / n_ok
    sig_hat = var_hat**0.5
    # Model: mixture of independent-digit Gaussians on L.
    mu_model = sum(mix.get(L, 0.0) * (b - 1) / 2 * L for L in mix)
    var_model = 0.0
    for L, w in mix.items():
        mu_L = (b - 1) / 2 * L
        sig_L2 = L * (b * b - 1) / 12
        var_model += w * (sig_L2 + (mu_L - mu_model) ** 2)
    sig_model = var_model**0.5
    mean_L_emp = sum(L * emp_L[L] for L in emp_L)
    mean_L_mix = sum(L * mix[L] for L in mix)
    p_need_second = sum(1 for s in steps_list if s >= 2) / n_ok
    ratios = []
    for L, vals in mean_given_L.items():
        expected = ((b - 1) / 2) * L
        if expected > 0:
            ratios.append((sum(vals) / len(vals)) / expected)
    return {
        "D": D,
        "n": n_ok,
        "tv_digit_length": round(_tv(emp_L, mix), 4),
        "mean_L_empirical": round(mean_L_emp, 3),
        "mean_L_mixture_Q": round(mean_L_mix, 3),
        "mean_m1_empirical": round(mu_hat, 2),
        "mean_m1_gaussian": round(mu_model, 2),
        "std_m1_empirical": round(sig_hat, 2),
        "std_m1_gaussian": round(sig_model, 2),
        "mean_m1_over_4.5L": round(mu_hat / max(mean_L_emp, 1e-9) / ((b - 1) / 2), 4),
        "mean_m1_given_L_vs_indep": None
        if not ratios
        else round(sum(ratios) / len(ratios), 4),
        "frac_needs_iterate_past_M": round(p_need_second, 4),
        "mean_steps_to_trap": round(sum(steps_list) / n_ok, 3),
        "M": system.M,
    }


def run_one(name: str, coeffs: tuple[int, ...], b: int, residue: int | None) -> dict:
    system = build_system_Q(coeffs, b)
    mod = structure_Q(coeffs, max(system.m, 1))
    sharing = system.attractors_sharing_signature()
    split_sigs = [(sig, idx) for sig, idx in sharing.items() if len(idx) >= 2]
    if not split_sigs:
        return {
            "name": name,
            "Q": format_Q(coeffs),
            "b": b,
            "status": "no_split",
            "C": system.count,
            "Cyc": mod.cycle_count,
        }
    if residue is None:
        sig, targets = max(split_sigs, key=lambda kv: len(kv[1]))
        feeding = [r for r in range(mod.m) if frozenset(mod.cycles[mod.owner[r]]) == sig]
        residue = feeding[0]
    else:
        sig = mod.signature_of_residue(residue)
        targets = sharing.get(sig, [])
        if len(targets) < 2:
            return {
                "name": name,
                "Q": format_Q(coeffs),
                "b": b,
                "status": "requested_residue_does_not_split",
                "residue": residue,
            }
        feeding = [r for r in range(mod.m) if frozenset(mod.cycles[mod.owner[r]]) == sig]

    weight = mod.weights[mod.owner[residue % mod.m]]
    measured = split_curves_Q(
        coeffs, b, LENGTHS, samples_per_band=SAMPLES, seed=1, system=system
    )
    noise = 0.5 / math.sqrt(SAMPLES)
    deg = len(coeffs) - 1
    max_L = max(1, deg) * max(LENGTHS) + 8
    V = min(int((b - 1) * max_L) + 400, 80_000)
    labels = attractor_labels_upto_Q(V, system)

    per_D = []
    maes = []
    for j, D in enumerate(LENGTHS):
        pred = predict_split_Q(D, system, sig, labels, targets, weight)
        mrow = {i: measured.curves[i][j] for i in targets}
        mae = _mae(pred, mrow)
        maes.append(mae)
        per_D.append(
            {
                "D": D,
                "mae_Fj": round(mae, 6),
                "F_j": {str(i): round(pred[i], 6) for i in targets},
                "measured": {str(i): round(mrow[i], 6) for i in targets},
                "aggregate": round(sum(mrow.values()), 6),
            }
        )

    osc = [row for row in oscillation_report_Q(measured) if row["signature"] == sorted(sig)]
    curves = [measured.curves[i] for i in targets]
    rho = _pearson(curves[0], curves[1]) if len(curves) >= 2 else None
    landing = [
        diagnose_landing(coeffs, b, D, system, feeding, DIAG_SAMPLES, seed=7 + D)
        for D in DIAG_D
    ]
    # Where the Gaussian assumption is worst: digit-length TV and m1 mean gap.
    worst_tv = max(row["tv_digit_length"] for row in landing if "tv_digit_length" in row)
    mean_rel_mu = sum(
        abs(row["mean_m1_empirical"] - row["mean_m1_gaussian"])
        / max(row["mean_m1_gaussian"], 1e-9)
        for row in landing
        if "mean_m1_gaussian" in row
    ) / len(landing)

    mean_mae = sum(maes) / len(maes)
    if mean_mae <= 3 * noise:
        fj_fail = "image lattice v ≡ Q(r) (mod m); Gaussian F_j matches MC"
    elif worst_tv > 0.15:
        fj_fail = "digit_count_mixture_Q (L of Q(n) is not a n^d)"
    elif mean_rel_mu > 0.15:
        fj_fail = "independent-digit Gaussian for S_b(Q(n)) (mean/var mismatch)"
    else:
        fj_fail = "labelling sensitivity beyond first-iterate location"

    return {
        "name": name,
        "Q": format_Q(coeffs),
        "b": b,
        "status": "split",
        "M": system.M,
        "signature": sorted(sig),
        "targets": targets,
        "attractor_labels": [measured.labels[i] for i in targets],
        "p_i": weight,
        "samples_per_band": SAMPLES,
        "noise_floor": round(noise, 6),
        "mae_Fj_mean": round(sum(maes) / len(maes), 6),
        "mae_Fj_tail": round(sum(maes[-6:]) / 6, 6),
        "within_3_noise": all(x <= 3 * noise for x in maes),
        "any_oscillates": any(row["oscillates"] for row in osc),
        "antiphase_pearson": None if rho is None else round(rho, 4),
        "oscillation": osc,
        "Fj_failure_mode": fj_fail,
        "landing_diagnostics": landing,
        "per_D": per_D,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = [run_one(*row) for row in TARGETS]
    payload = {
        "stamp": stamp,
        "lengths": list(LENGTHS),
        "samples_per_band": SAMPLES,
        "note": "Does not overwrite split_latest.json from the first sidecar run.",
        "results": results,
    }
    json_path = OUT_DIR / f"refine_{stamp}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT_DIR / "refine_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Q-class split refine",
        "",
        f"Stamp: {stamp}",
        f"D = {LENGTHS[0]}..{LENGTHS[-1]} step 4; samples/band = {SAMPLES}",
        "",
        "Does not overwrite `split_latest` from the short-band run.",
        "",
        "| Q | mae F_j | mae tail | osc? | antiphase r | F_j failure mode |",
        "|---|---------|----------|------|-------------|------------------|",
    ]
    for rec in results:
        lines.append(
            f"| {rec['Q']} | {rec.get('mae_Fj_mean', '—')} | {rec.get('mae_Fj_tail', '—')} | "
            f"{rec.get('any_oscillates', rec.get('status', '—'))} | "
            f"{rec.get('antiphase_pearson', '—')} | {rec.get('Fj_failure_mode', rec.get('status', '—'))} |"
        )
    lines += ["", "## Landing diagnostics (selected D)", ""]
    for rec in results:
        if "landing_diagnostics" not in rec:
            continue
        lines.append(f"### {rec['Q']}")
        lines.append("")
        lines.append("| D | TV(L) | mean L emp/mix | mean m1 emp/gauss | std emp/gauss | P(steps≥2) |")
        lines.append("|---|-------|----------------|-------------------|---------------|------------|")
        for row in rec["landing_diagnostics"]:
            lines.append(
                f"| {row['D']} | {row.get('tv_digit_length')} | "
                f"{row.get('mean_L_empirical')}/{row.get('mean_L_mixture_Q')} | "
                f"{row.get('mean_m1_empirical')}/{row.get('mean_m1_gaussian')} | "
                f"{row.get('std_m1_empirical')}/{row.get('std_m1_gaussian')} | "
                f"{row.get('frac_needs_iterate_past_M')} |"
            )
        lines.append("")
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"refine_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "refine_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
