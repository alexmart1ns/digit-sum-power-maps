#!/usr/bin/env python3
"""Gaussian-window sweep of the labelling h_j (Conjecture 10.6' diagnostic).

Does not sample n. Pushes h_j(v) = 1_{g(v) in beta_j} through the digit-count
mixture of Gaussians already in ``predict_split``, out to large D.

This is not a test of the local-limit hypothesis (that would require sampling
n^k). It answers: if LLT holds, does the labelling produce a non-constant
Delange factor P_j?

* If the amplitude of delta_j damps to a constant, Conjecture 10.6' fails
  even assuming LLT.
* If the amplitude stays up and the phase organizes by {log_b D}, then under
  LLT the conjecture follows.

Default pilot: (k, b) = (3, 10), signature {0}, attractors {18} and {27},
D = 4 .. 300.

Examples
--------
    python scripts/sweep_label.py
    python scripts/sweep_label.py --d-max 80
    python scripts/sweep_label.py --k 3 --b 10 --signature 0 --d-max 300
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import _bootstrap  # noqa: F401
from dspm.dynamics import FiniteSystem, build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto, predict_split

REPO_ROOT = Path(__file__).resolve().parent.parent


def gaussian_window_ceiling(k: int, b: int, d_max: int, n_sigma: float = 8.0) -> int:
    """Smallest V that covers mu + n_sigma * sigma at L = k * d_max."""
    L = k * d_max
    mu = (b - 1) / 2 * L
    sigma = math.sqrt(L * (b * b - 1) / 12)
    return int(mu + n_sigma * sigma) + 50


def frac_log(D: int, b: int) -> float:
    return math.log(D) / math.log(b) % 1.0


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return float("nan")
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def amplitude(values: list[float]) -> float:
    return max(values) - min(values) if values else 0.0


def decade_groups(
    Ds: list[int], values: list[float], b: int
) -> dict[int, list[tuple[int, float, float]]]:
    """Group (D, value, {log_b D}) by floor(log_b D). One Delange period per exponent."""
    groups: dict[int, list[tuple[int, float, float]]] = {}
    for D, y in zip(Ds, values):
        exp = int(math.floor(math.log(D) / math.log(b)))
        groups.setdefault(exp, []).append((D, y, frac_log(D, b)))
    return dict(sorted(groups.items()))


def _lerp(xs: list[float], ys: list[float], x: float) -> float | None:
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] * (1 - t) + ys[i + 1] * t
    return None


def decade_report(Ds: list[int], values: list[float], b: int) -> list[dict]:
    rows = []
    for exp, pts in decade_groups(Ds, values, b).items():
        ys = [p[1] for p in pts]
        fracs = [p[2] for p in pts]
        lo, hi = b**exp, b ** (exp + 1) - 1
        covered_lo = max(lo, Ds[0])
        covered_hi = min(hi, Ds[-1])
        full = (
            pts[0][0] <= covered_lo
            and pts[-1][0] >= covered_hi
            and (fracs[-1] - fracs[0]) >= 0.85
        )
        rows.append(
            {
                "exponent": exp,
                "D_lo": pts[0][0],
                "D_hi": pts[-1][0],
                "n": len(pts),
                "frac_span": fracs[-1] - fracs[0],
                "full_period": full,
                "amplitude": amplitude(ys),
                "min": min(ys),
                "max": max(ys),
                "mean": mean(ys),
            }
        )
    return rows


def phase_correlation_across_decades(
    Ds: list[int], values: list[float], b: int
) -> dict | None:
    groups = decade_groups(Ds, values, b)
    exps = sorted(groups)
    if len(exps) < 2:
        return None
    # Compare the two longest decades on the overlapping {log_b D} interval.
    a, c = exps[-2], exps[-1]
    pts_a, pts_c = groups[a], groups[c]
    fa, ya = [p[2] for p in pts_a], [p[1] for p in pts_a]
    pairs = []
    for _, y, f in pts_c:
        u = _lerp(fa, ya, f)
        if u is not None:
            pairs.append((y, u))
    if len(pairs) < 8:
        return None
    ys, us = [p[0] for p in pairs], [p[1] for p in pairs]
    return {
        "decade_a": a,
        "decade_c": c,
        "n_overlap": len(pairs),
        "pearson": pearson(ys, us),
        "amp_later_on_overlap": amplitude(ys),
        "amp_earlier_on_overlap": amplitude(us),
    }


def diagnose(
    names: dict[int, str],
    Ds: list[int],
    curves: dict[int, list[float]],
    b: int,
    weight: float,
) -> dict:
    amps = {i: amplitude(curves[i]) for i in curves}
    ranked = sorted(amps, key=lambda i: amps[i], reverse=True)
    primary = ranked[0]
    secondary = ranked[1] if len(ranked) > 1 else None
    y = curves[primary]
    decades = decade_report(Ds, y, b)
    phase = phase_correlation_across_decades(Ds, y, b)
    r = pearson(y, curves[secondary]) if secondary is not None else float("nan")
    algebraic = len(curves) == 2

    full = [row for row in decades if row["full_period"]]
    full_amps = [row["amplitude"] for row in full]
    last_amp = decades[-1]["amplitude"] if decades else 0.0
    first_full = full_amps[0] if full_amps else None
    last_full = full_amps[-1] if full_amps else None
    damps = (
        first_full is not None
        and last_full is not None
        and last_full < 0.4 * first_full
        and last_full < 0.03
    ) or (last_amp < 0.02)
    organizes = phase is not None and phase["pearson"] is not None and phase["pearson"] > 0.5
    stays_up = last_amp >= 0.05 or (last_full is not None and last_full >= 0.05)

    if damps:
        verdict = (
            "DAMPS: decade amplitude collapses; Conjecture 10.6' fails even assuming LLT"
        )
        tag = "damps"
    elif stays_up and organizes:
        verdict = (
            "SURVIVES: decade amplitude stays up and phase correlates across "
            "{log_b D} decades; under LLT, Conjecture 10.6' follows"
        )
        tag = "survives"
    elif stays_up:
        verdict = (
            "AMPLITUDE SURVIVES across decades but cross-decade phase is weak; "
            "extend D through another full decade"
        )
        tag = "amplitude_only"
    else:
        verdict = "INCONCLUSIVE: last decade does not cover a full {log_b D} period"
        tag = "inconclusive"

    return {
        "primary": names[primary],
        "secondary": names[secondary] if secondary is not None else None,
        "amplitudes": {names[i]: amps[i] for i in ranked},
        "decades": decades,
        "phase_across_decades": phase,
        "pearson_primary_secondary": r,
        "antiphase_is_algebraic": algebraic,
        "signature_sum_mean": mean(
            [sum(curves[i][j] for i in curves) for j in range(len(Ds))]
        ),
        "modular_weight": weight,
        "verdict_tag": tag,
        "verdict": verdict,
    }


def run_sweep(
    system: FiniteSystem,
    signature: frozenset[int],
    weight: float,
    d_min: int,
    d_max: int,
) -> tuple[dict[int, str], list[int], dict[int, list[float]], list[int], int]:
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    names = {i: str(list(system.attractors[i])) for i in targets}
    ceiling = gaussian_window_ceiling(system.k, system.b, d_max)
    labels = attractor_labels_upto(ceiling, system)
    Ds = list(range(d_min, d_max + 1))
    curves: dict[int, list[float]] = {i: [] for i in targets}
    for D in Ds:
        pred = predict_split(D, system, signature, labels, targets, weight)
        for i in targets:
            curves[i].append(pred[i])
    return names, Ds, curves, targets, ceiling


def write_markdown(path: Path, meta: dict, diag: dict, names: dict[int, str],
                   Ds: list[int], curves: dict[int, list[float]], b: int) -> None:
    targets = list(names)
    lines = [
        f"# Gaussian label sweep -- Conjecture 10.6' diagnostic",
        "",
        f"- pair: (k, b) = ({meta['k']}, {meta['b']})",
        f"- signature: {meta['signature']}",
        f"- modular weight p_i = {meta['modular_weight']:.6f}",
        f"- D in [{meta['d_min']}, {meta['d_max']}]",
        f"- attractors: {list(names.values())}",
        f"- ceiling V = {meta['ceiling']} (no sampling of n)",
        "",
        "## Verdict",
        "",
        diag["verdict"],
        "",
        f"- primary attractor: {diag['primary']}",
        f"- secondary attractor: {diag['secondary']}",
        f"- Pearson(primary, secondary): {diag['pearson_primary_secondary']:.4f}"
        + (" (algebraic: two attractors sum to p_i)" if diag["antiphase_is_algebraic"] else ""),
        f"- mean signature sum: {diag['signature_sum_mean']:.6f} "
        f"(target {diag['modular_weight']:.6f})",
        "",
        "## Amplitude per {log_b D} decade",
        "",
    ]
    for row in diag["decades"]:
        flag = "full period" if row["full_period"] else "partial period"
        lines.append(
            f"- D={row['D_lo']}..{row['D_hi']}  amp={row['amplitude']:.4f}  "
            f"mean={row['mean']:.4f}  frac_span={row['frac_span']:.3f}  ({flag})"
        )
    phase = diag.get("phase_across_decades")
    if phase:
        lines.extend(
            [
                "",
                "## Cross-decade phase",
                "",
                f"- decades {b}^{phase['decade_a']} vs {b}^{phase['decade_c']}  "
                f"overlap n={phase['n_overlap']}",
                f"- Pearson on {{log_b D}}: {phase['pearson']:.4f}",
                f"- amplitude on overlap: earlier {phase['amp_earlier_on_overlap']:.4f}, "
                f"later {phase['amp_later_on_overlap']:.4f}",
            ]
        )
    lines.extend(
        [
            "",
            "## Curve (every 10th D, plus endpoints)",
            "",
            "    D   {log_b D}  " + "  ".join(f"{names[i]:>10}" for i in targets) + "     sum",
        ]
    )
    show = set(Ds[::10]) | {Ds[0], Ds[-1]}
    for j, D in enumerate(Ds):
        if D not in show:
            continue
        row_mass = "  ".join(f"{curves[i][j]:10.4f}" for i in targets)
        s = sum(curves[i][j] for i in targets)
        lines.append(f"  {D:4d}   {frac_log(D, b):8.4f}  {row_mass}  {s:8.4f}")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--signature", type=int, default=0, help="a residue in the target signature")
    ap.add_argument("--d-min", type=int, default=4)
    ap.add_argument("--d-max", type=int, default=300)
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "data" / "split")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    k, b = args.k, args.b
    m = b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(args.signature)
    weight = mod.weights[mod.owner[args.signature % m]]
    targets_check = [i for i in range(system.count) if system.signature(i) == signature]
    if len(targets_check) < 2:
        print(
            f"signature {sorted(signature)} hosts {len(targets_check)} attractor(s); "
            "nothing can oscillate."
        )
        return 1

    names, Ds, curves, targets, ceiling = run_sweep(
        system, signature, weight, args.d_min, args.d_max
    )
    diag = diagnose(names, Ds, curves, b, weight)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"label_sweep_k{k}_b{b}_sig{args.signature}_D{args.d_max}_{stamp}"
    json_path = args.out_dir / f"{stem}.json"
    md_path = args.out_dir / f"{stem}.md"
    latest_stem = f"label_sweep_k{k}_b{b}_sig{args.signature}_D{args.d_max}_latest"
    latest_json = args.out_dir / f"{latest_stem}.json"
    latest_md = args.out_dir / f"{latest_stem}.md"

    meta = {
        "k": k,
        "b": b,
        "signature": sorted(signature),
        "signature_residue": args.signature,
        "modular_weight": weight,
        "d_min": args.d_min,
        "d_max": args.d_max,
        "ceiling": ceiling,
        "attractors": names,
        "samples_n": False,
        "model": "predict_split (digit-count mixture of Gaussians x exact labelling)",
        "note": (
            "Not a test of LLT. Diagnostic of whether h_j produces a "
            "non-constant P_j under the Gaussian window."
        ),
    }
    payload = {
        **meta,
        "digit_lengths": Ds,
        "frac_log": [frac_log(D, b) for D in Ds],
        "curves": {names[i]: curves[i] for i in targets},
        "diagnostics": diag,
    }
    text = json.dumps(payload, indent=2)
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")
    write_markdown(md_path, meta, diag, names, Ds, curves, b)
    write_markdown(latest_md, meta, diag, names, Ds, curves, b)

    print("=" * 78)
    print(f"  sweep_label  k={k} b={b}  signature {sorted(signature)}  p_i={weight:.4f}")
    print(f"  D={args.d_min}..{args.d_max}  V={ceiling}  (Gaussian window; no sampling of n)")
    print(f"  attractors {list(names.values())}")
    print("=" * 78)
    print(f"  primary {diag['primary']}")
    for row in diag["decades"]:
        flag = "full" if row["full_period"] else "partial"
        print(
            f"    D={row['D_lo']:3d}..{row['D_hi']:3d}  amp={row['amplitude']:.4f}  "
            f"({flag}, frac_span={row['frac_span']:.3f})"
        )
    if diag["secondary"] is not None:
        note = "  [algebraic: 2-split]" if diag["antiphase_is_algebraic"] else ""
        print(
            f"  secondary {diag['secondary']}  "
            f"Pearson={diag['pearson_primary_secondary']:.4f}{note}"
        )
    phase = diag.get("phase_across_decades")
    if phase:
        print(
            f"  cross-decade Pearson={{log_b D}} {phase['pearson']:.4f}  "
            f"amp overlap earlier/later "
            f"{phase['amp_earlier_on_overlap']:.4f}/{phase['amp_later_on_overlap']:.4f}"
        )
    print(f"  signature sum mean={diag['signature_sum_mean']:.6f}")
    print("-" * 78)
    print(f"  {diag['verdict']}")
    print("-" * 78)
    print(f"  wrote {json_path.relative_to(REPO_ROOT)}")
    print(f"  wrote {md_path.relative_to(REPO_ROOT)}")
    print(f"  wrote {latest_json.relative_to(REPO_ROOT)}")
    print(f"  wrote {latest_md.relative_to(REPO_ROOT)}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
