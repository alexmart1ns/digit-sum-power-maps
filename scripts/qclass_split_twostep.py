#!/usr/bin/env python3
"""Where Gaussian F_j fails: m1 vs m2 laws, independent-digit pmf.

``predict_split_Q`` already applies labels[v], which iterates until <= M.
A naive 'Gaussian then one f_Qb' is the same functional. This script instead:

1. Compares the empirical law of m1 = S_b(Q(n)) to the Gaussian lattice density.
2. Pushes both through f_Qb to m2 (almost always the trap landing) and compares.
3. Replaces the Gaussian by an exact independent-digit sum pmf (leading digit
   1..b-1) — not ``dspm.mining.fourier``, which is monomial-only.

Writes only to data/qclass/split/twostep_*. Does not overwrite refine_latest
or split_latest, and does not touch data/split/.
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.qmaps import (
    attractor_labels_upto_Q,
    build_system_Q,
    digit_count_mixture_Q,
    eval_Q,
    f_Qb,
    format_Q,
    monomial_Q,
    predict_split_Q,
    structure_Q,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "split"
REFINE_JSON = OUT_DIR / "refine_latest.json"

DIAG_D = (8, 16, 24, 40, 56, 64)
DIAG_SAMPLES = 8_000

TARGETS = [
    ("2x^2+3x+1", (1, 3, 2), 10, None),
    ("x^3", monomial_Q(3), 10, 0),
]


def _mae(pred: dict[int, float], measured: dict[int, float]) -> float:
    keys = [i for i in pred if i in measured]
    if not keys:
        return float("nan")
    return sum(abs(pred[i] - measured[i]) for i in keys) / len(keys)


def _tv(p: dict[int, float], q: dict[int, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def _skew(xs: list[int]) -> float:
    n = len(xs)
    if n < 3:
        return float("nan")
    mu = sum(xs) / n
    var = sum((x - mu) ** 2 for x in xs) / n
    if var <= 0:
        return 0.0
    sig = var**0.5
    return sum(((x - mu) / sig) ** 3 for x in xs) / n


def _normalize(hist: dict[int, float]) -> dict[int, float]:
    s = sum(hist.values())
    if s <= 0:
        return {}
    return {k: v / s for k, v in hist.items()}


def l_digit_sum_pmf(L: int, b: int) -> list[float]:
    """P(S = s) for an L-digit base-b number: leading digit 1..b-1, rest 0..b-1."""
    if L < 1 or b < 2:
        raise ValueError("need L >= 1 and b >= 2")
    pmf = [0.0] * b
    lead = 1.0 / (b - 1)
    for d in range(1, b):
        pmf[d] = lead
    for _ in range(L - 1):
        nxt = [0.0] * (len(pmf) + b - 1)
        scale = 1.0 / b
        for s, w in enumerate(pmf):
            if w == 0.0:
                continue
            for d in range(b):
                nxt[s + d] += w * scale
        pmf = nxt
    return pmf


def _gaussian(v: float, mu: float, sigma: float) -> float:
    return math.exp(-0.5 * ((v - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def gaussian_density(D: int, coeffs, b: int, feeding: list[int], V: int) -> dict[int, float]:
    m = max(b - 1, 1)
    density: dict[int, float] = {}
    for L, weight in digit_count_mixture_Q(D, coeffs, b).items():
        mu = (b - 1) / 2 * L
        sigma = math.sqrt(L * (b * b - 1) / 12) if L > 0 else 1.0
        sigma = max(sigma, 1e-9)
        lo = max(1, int(mu - 6 * sigma))
        hi = min(V, int(mu + 6 * sigma))
        for r in feeding:
            v = lo + ((r - lo) % m)
            while v <= hi:
                if v >= 1:
                    density[v] = density.get(v, 0.0) + weight * _gaussian(v, mu, sigma)
                v += m
    return _normalize(density)


def image_gaussian_density(
    D: int, coeffs, b: int, feeding: list[int], V: int
) -> dict[int, float]:
    """Gaussian on v, but v ≡ Q(r) (mod m) for each feeding residue r of n.

    ``predict_split_Q`` now places v ≡ Q(r). Digit-sum congruence is S_b(Q(n)) ≡ Q(n)
    (mod b-1), so the lattice of m1 is the image of Q, not the feeding set of n.
    """
    m = max(b - 1, 1)
    images = [eval_Q(r, coeffs) % m for r in feeding]
    density: dict[int, float] = {}
    for L, weight in digit_count_mixture_Q(D, coeffs, b).items():
        mu = (b - 1) / 2 * L
        sigma = math.sqrt(L * (b * b - 1) / 12) if L > 0 else 1.0
        sigma = max(sigma, 1e-9)
        lo = max(1, int(mu - 6 * sigma))
        hi = min(V, int(mu + 6 * sigma))
        for q in images:
            v = lo + ((q - lo) % m)
            while v <= hi:
                if v >= 1:
                    density[v] = density.get(v, 0.0) + weight * _gaussian(v, mu, sigma)
                v += m
    return _normalize(density)


def idigit_density(D: int, coeffs, b: int, feeding: list[int], V: int) -> dict[int, float]:
    m = max(b - 1, 1)
    feeding_set = set(feeding)
    density: dict[int, float] = {}
    for L, weight in digit_count_mixture_Q(D, coeffs, b).items():
        pmf = l_digit_sum_pmf(L, b)
        for v, p in enumerate(pmf):
            if v < 1 or v > V or p == 0.0:
                continue
            if (v % m) not in feeding_set:
                continue
            density[v] = density.get(v, 0.0) + weight * p
    return _normalize(density)


def push_m2(density: dict[int, float], coeffs, b: int) -> dict[int, float]:
    out: dict[int, float] = {}
    for v, mass in density.items():
        w = f_Qb(v, coeffs, b)
        out[w] = out.get(w, 0.0) + mass
    return _normalize(out)


def split_from_density(
    density: dict[int, float],
    labels: list[int],
    targets: list[int],
    weight: float,
    coeffs,
    b: int,
    M: int,
) -> dict[int, float]:
    V = len(labels) - 1
    out = {t: 0.0 for t in targets}
    total = 0.0
    for v, mass in density.items():
        if v <= V:
            lab = labels[v]
        else:
            w = v
            while w > M:
                w = f_Qb(w, coeffs, b)
            lab = labels[w] if w <= V else -1
        if lab in out:
            out[lab] += mass
        total += mass
    if total <= 0:
        return {t: float("nan") for t in targets}
    return {t: (out[t] / total) * weight for t in out}


def empirical_landings(
    coeffs, b: int, D: int, feeding: list[int], n_samples: int, seed: int, M: int
) -> tuple[list[int], list[int], dict[int, float]]:
    rng = random.Random(seed)
    m = max(b - 1, 1)
    feeding_set = set(feeding)
    lo, hi = b ** (D - 1), b**D - 1
    m1s: list[int] = []
    m2s: list[int] = []
    residue_m1: Counter[int] = Counter()
    n_ok = 0
    guard = 0
    while n_ok < n_samples and guard < n_samples * 40:
        guard += 1
        n = rng.randint(lo, hi)
        if (n % m) not in feeding_set:
            continue
        m1 = f_Qb(n, coeffs, b)
        m2 = f_Qb(m1, coeffs, b) if m1 > M else m1
        m1s.append(m1)
        m2s.append(m2)
        residue_m1[m1 % m] += 1
        n_ok += 1
    occ = {r: residue_m1[r] / n_ok for r in feeding} if n_ok else {}
    return m1s, m2s, occ


def hist(xs: list[int]) -> dict[int, float]:
    c = Counter(xs)
    n = max(len(xs), 1)
    return {k: v / n for k, v in c.items()}


def _load_refine() -> dict[str, dict]:
    payload = json.loads(REFINE_JSON.read_text(encoding="utf-8"))
    return {rec["name"]: rec for rec in payload["results"]}


def run_one(name: str, coeffs: tuple[int, ...], b: int, residue: int | None, refine: dict) -> dict:
    system = build_system_Q(coeffs, b)
    mod = structure_Q(coeffs, max(system.m, 1))
    sharing = system.attractors_sharing_signature()
    split_sigs = [(sig, idx) for sig, idx in sharing.items() if len(idx) >= 2]
    if residue is None:
        sig, targets = max(split_sigs, key=lambda kv: len(kv[1]))
        feeding = [r for r in range(mod.m) if frozenset(mod.cycles[mod.owner[r]]) == sig]
        residue = feeding[0]
    else:
        sig = mod.signature_of_residue(residue)
        targets = sharing[sig]
        feeding = [r for r in range(mod.m) if frozenset(mod.cycles[mod.owner[r]]) == sig]
    weight = mod.weights[mod.owner[residue % mod.m]]
    deg = len(coeffs) - 1
    max_L = max(1, deg) * max(DIAG_D) + 8
    V = min(int((b - 1) * max_L) + 400, 80_000)
    labels = attractor_labels_upto_Q(V, system)

    measured_by_D = {}
    fj_by_D = {}
    for row in refine.get("per_D", []):
        D = row["D"]
        measured_by_D[D] = {int(k): v for k, v in row["measured"].items()}
        fj_by_D[D] = {int(k): v for k, v in row["F_j"].items()}

    uniform_feed = {r: 1.0 / len(feeding) for r in feeding}
    per_D = []
    for D in DIAG_D:
        m1s, m2s, occ = empirical_landings(
            coeffs, b, D, feeding, DIAG_SAMPLES, seed=11 + D, M=system.M
        )
        g = gaussian_density(D, coeffs, b, feeding, V)
        img = image_gaussian_density(D, coeffs, b, feeding, V)
        iden = idigit_density(D, coeffs, b, feeding, V)
        emp_m1 = hist(m1s)
        emp_m2 = hist(m2s)
        g_m2 = push_m2(g, coeffs, b)
        img_m2 = push_m2(img, coeffs, b)
        image_occ: dict[int, float] = {}
        for r in feeding:
            q = eval_Q(r, coeffs) % mod.m
            image_occ[q] = image_occ.get(q, 0.0) + 1.0 / len(feeding)
        measured = measured_by_D.get(D)
        pred_g = predict_split_Q(D, system, sig, labels, targets, weight)
        pred_img = split_from_density(img, labels, targets, weight, coeffs, b, system.M)
        pred_id = split_from_density(iden, labels, targets, weight, coeffs, b, system.M)
        pred_emp = split_from_density(emp_m1, labels, targets, weight, coeffs, b, system.M)
        row = {
            "D": D,
            "n": len(m1s),
            "skew_m1": round(_skew(m1s), 4),
            "tv_m1_vs_gaussian": round(_tv(emp_m1, g), 4),
            "tv_m1_vs_image": round(_tv(emp_m1, img), 4),
            "tv_m1_vs_idigit": round(_tv(emp_m1, iden), 4),
            "tv_m2_emp_vs_gauss_push": round(_tv(emp_m2, g_m2), 4),
            "tv_m2_emp_vs_image_push": round(_tv(emp_m2, img_m2), 4),
            "tv_m1_residue_vs_uniform_feeding": round(_tv(occ, uniform_feed), 4),
            "tv_m1_residue_vs_Q_image": round(_tv(occ, image_occ), 4),
            "frac_m2_le_M": round(sum(1 for x in m2s if x <= system.M) / max(len(m2s), 1), 4),
            "mean_m1": round(sum(m1s) / len(m1s), 2),
            "mean_m2": round(sum(m2s) / len(m2s), 2),
            "Q_image_mod_m": sorted(image_occ),
        }
        if measured is not None:
            row["mae_gaussian"] = round(_mae(pred_g, measured), 6)
            row["mae_image"] = round(_mae(pred_img, measured), 6)
            row["mae_idigit"] = round(_mae(pred_id, measured), 6)
            row["mae_emp_m1"] = round(_mae(pred_emp, measured), 6)
            row["F_image"] = {str(i): round(pred_img[i], 6) for i in targets}
            row["F_idigit"] = {str(i): round(pred_id[i], 6) for i in targets}
            row["F_emp_m1"] = {str(i): round(pred_emp[i], 6) for i in targets}
            row["measured"] = {str(i): round(measured[i], 6) for i in targets}
        per_D.append(row)

    maes_g = [r["mae_gaussian"] for r in per_D if "mae_gaussian" in r]
    maes_img = [r["mae_image"] for r in per_D if "mae_image" in r]
    maes_id = [r["mae_idigit"] for r in per_D if "mae_idigit" in r]
    maes_emp = [r["mae_emp_m1"] for r in per_D if "mae_emp_m1" in r]
    tv_res_img = [r["tv_m1_residue_vs_Q_image"] for r in per_D]
    mean_g = sum(maes_g) / len(maes_g) if maes_g else None
    mean_img = sum(maes_img) / len(maes_img) if maes_img else None
    mean_emp = sum(maes_emp) / len(maes_emp) if maes_emp else None
    if mean_emp is not None and mean_emp < 0.03 and mean_img is not None and mean_g is not None:
        if mean_img < 0.5 * mean_g:
            verdict = "lattice of m1 is Q(n) mod m, not feeding residues of n; image Gaussian is the F_j correction"
        else:
            verdict = "true m1 law + labelling recovers the split; Gaussian/idigit on the wrong lattice"
    else:
        verdict = "labelling remains sensitive beyond mean/var of m1"
    return {
        "name": name,
        "Q": format_Q(coeffs),
        "b": b,
        "M": system.M,
        "signature": sorted(sig),
        "targets": targets,
        "p_i": weight,
        "Q_image_mod_m": sorted({eval_Q(r, coeffs) % mod.m for r in feeding}),
        "refine_mae_Fj_mean": refine.get("mae_Fj_mean"),
        "mae_gaussian_mean": None if mean_g is None else round(mean_g, 6),
        "mae_image_mean": None if mean_img is None else round(mean_img, 6),
        "mae_idigit_mean": round(sum(maes_id) / len(maes_id), 6) if maes_id else None,
        "mae_emp_m1_mean": None if mean_emp is None else round(mean_emp, 6),
        "tv_residue_vs_Q_image_mean": round(sum(tv_res_img) / len(tv_res_img), 4) if tv_res_img else None,
        "verdict": verdict,
        "per_D": per_D,
    }


def main() -> int:
    if not REFINE_JSON.is_file():
        raise SystemExit(f"missing {REFINE_JSON}; run qclass_split_refine.py first")
    refine = _load_refine()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = []
    for name, coeffs, b, residue in TARGETS:
        rec = refine.get(name)
        if rec is None:
            results.append({"name": name, "status": "no_refine_record"})
            continue
        results.append(run_one(name, coeffs, b, residue, rec))
    payload = {
        "stamp": stamp,
        "D": list(DIAG_D),
        "samples": DIAG_SAMPLES,
        "note": (
            "Does not overwrite refine_latest or split_latest. "
            "Gaussian then one iterate equals predict_split_Q; this file compares laws."
        ),
        "results": results,
    }
    json_path = OUT_DIR / f"twostep_{stamp}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT_DIR / "twostep_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Q-class two-step / independent-digit diagnosis",
        "",
        f"Stamp: {stamp}",
        f"D = {list(DIAG_D)}; empirical samples = {DIAG_SAMPLES}",
        "",
        "Gaussian + labels is already `predict_split_Q`. Image Gaussian places",
        "m1 on Q(r) (mod m) instead of on feeding residues of n.",
        "",
        "| Q | mae gauss | mae image | mae emp m1 | TV residue vs Q(n) | verdict |",
        "|---|-----------|-----------|------------|--------------------|---------|",
    ]
    for rec in results:
        lines.append(
            f"| {rec.get('Q', rec['name'])} | {rec.get('mae_gaussian_mean', '—')} | "
            f"{rec.get('mae_image_mean', '—')} | {rec.get('mae_emp_m1_mean', '—')} | "
            f"{rec.get('tv_residue_vs_Q_image_mean', '—')} | "
            f"{rec.get('verdict', rec.get('status', '—'))} |"
        )
    lines += ["", "## Per D", ""]
    for rec in results:
        if "per_D" not in rec:
            continue
        lines.append(f"### {rec['Q']}")
        lines.append("")
        lines.append("| D | TV res vs image | mae G | mae image | mae emp | m2≤M |")
        lines.append("|---|-----------------|-------|-----------|---------|------|")
        for row in rec["per_D"]:
            lines.append(
                f"| {row['D']} | {row.get('tv_m1_residue_vs_Q_image')} | "
                f"{row.get('mae_gaussian', '—')} | {row.get('mae_image', '—')} | "
                f"{row.get('mae_emp_m1', '—')} | {row.get('frac_m2_le_M')} |"
            )
        lines.append("")
    md = "\n".join(lines) + "\n"
    (OUT_DIR / f"twostep_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "twostep_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
