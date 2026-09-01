#!/usr/bin/env python3
"""Regenerate paper split figures from measured and predicted curves.

Writes ``paper/figures/split_predict_overlay.svg`` and optionally
``paper/figures/split_oscillation.svg``.

Examples
--------
    python scripts/plot_split_figures.py --k 3 --b 10
    python scripts/plot_split_figures.py --k 3 --b 10 --lang en
"""

from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean

import _bootstrap  # noqa: F401
from dspm.dynamics import build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto, predict_split
from dspm.split import load_split_scale_file

REPO_ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = REPO_ROOT / "paper" / "figures"


def _load_measured(k: int, b: int, directory: Path) -> dict | None:
    latest = directory / f"split_scale_k{k}_b{b}_latest.json"
    if latest.exists():
        return load_split_scale_file(latest)
    candidates = sorted(directory.glob(f"split_scale_k{k}_b{b}_*.json"))
    if not candidates:
        return None
    return load_split_scale_file(candidates[-1])


def _scale_x(d: int, d_min: int, d_max: int, x0: float, x1: float) -> float:
    if d_max == d_min:
        return (x0 + x1) / 2
    return x0 + (d - d_min) * (x1 - x0) / (d_max - d_min)


def _scale_y(v: float, y_min: float, y_max: float, y0: float, y1: float) -> float:
    if y_max == y_min:
        return (y0 + y1) / 2
    return y1 - (v - y_min) * (y1 - y0) / (y_max - y_min)


def _polyline(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def write_overlay_svg(
    *,
    d_values: list[int],
    pred_primary: list[float],
    meas_primary: list[float] | None,
    mae: float | None,
    out_path: Path,
    lang: str,
) -> None:
    width, height = 780, 440
    margin_l, margin_r, margin_t, margin_b = 54, 54, 54, 54
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    y_min, y_max = 0.0, max(max(pred_primary), max(meas_primary or pred_primary)) * 1.05

    if lang == "pt":
        title = "Oscilacao do split delta(18) — PREVISTO (gaussiana) vs MEDIDO"
        leg_pred = "previsto (modelo, sem MC)"
        leg_meas = "medido (Monte Carlo)"
        mae_note = (
            f"ponte MAE = {mae:.4f} (D={d_values[0]}..{d_values[-1]}, ruido ~0.0014)"
            if mae is not None
            else ""
        )
    else:
        title = "Split oscillation delta(18) — PREDICTED (Gaussian) vs MEASURED"
        leg_pred = "predicted (model, no MC)"
        leg_meas = "measured (Monte Carlo)"
        mae_note = (
            f"bridge MAE = {mae:.4f} (D={d_values[0]}..{d_values[-1]}, noise ~0.0014)"
            if mae is not None
            else ""
        )

    d_min, d_max = d_values[0], d_values[-1]
    pred_pts = [
        (_scale_x(d, d_min, d_max, margin_l, margin_l + plot_w), _scale_y(v, y_min, y_max, margin_t, margin_t + plot_h))
        for d, v in zip(d_values, pred_primary)
    ]
    meas_pts = None
    if meas_primary is not None:
        meas_pts = [
            (_scale_x(d, d_min, d_max, margin_l, margin_l + plot_w), _scale_y(v, y_min, y_max, margin_t, margin_t + plot_h))
            for d, v in zip(d_values, meas_primary)
        ]

    ticks = [d_min + i * (d_max - d_min) // 5 for i in range(6)]
    y_ticks = [y_min + i * (y_max - y_min) / 2 for i in range(3)]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="sans-serif">',
        f'<rect width="{width}" height="{height}" fill="#0d1117"/>',
        f'<text x="{width/2:.1f}" y="24" fill="#e6edf3" font-size="15" text-anchor="middle">{title}</text>',
        f'<line x1="{margin_l}" y1="{margin_t + plot_h:.1f}" x2="{margin_l + plot_w}" y2="{margin_t + plot_h:.1f}" stroke="#30363d"/>',
        f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t + plot_h:.1f}" stroke="#30363d"/>',
    ]
    for t in ticks:
        x = _scale_x(t, d_min, d_max, margin_l, margin_l + plot_w)
        parts.append(f'<text x="{x:.1f}" y="{margin_t + plot_h + 16:.1f}" fill="#8b949e" font-size="11" text-anchor="middle">D={t}</text>')
    for t in y_ticks:
        y = _scale_y(t, y_min, y_max, margin_t, margin_t + plot_h)
        parts.append(f'<text x="{margin_l - 6}" y="{y + 4:.1f}" fill="#8b949e" font-size="10" text-anchor="end">{t:.1f}</text>')

    parts.append(f'<polyline points="{_polyline(pred_pts)}" fill="none" stroke="#f778ba" stroke-width="2.4"/>')
    if meas_pts:
        for x, y in meas_pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#58a6ff"/>')

    parts.extend(
        [
            f'<line x1="550" y1="50" x2="570" y2="50" stroke="#f778ba" stroke-width="3"/>',
            f'<text x="576" y="54" fill="#e6edf3" font-size="12">{leg_pred}</text>',
            f'<circle cx="560" cy="70" r="3" fill="#58a6ff"/>',
            f'<text x="576" y="74" fill="#e6edf3" font-size="12">{leg_meas}</text>',
        ]
    )
    if mae_note:
        parts.append(f'<text x="550" y="92" fill="#8b949e" font-size="11">{mae_note}</text>')
    parts.append("</svg>")
    out_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_oscillation_svg(
    *,
    d_values: list[int],
    curves: dict[str, list[float]],
    series: list[tuple[str, str, str]],
    ref_line: float | None,
    out_path: Path,
    lang: str,
) -> None:
    width, height = 780, 460
    margin_l, margin_r, margin_t, margin_b = 56, 56, 56, 56
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    all_vals = [v for series in curves.values() for v in series]
    y_min, y_max = 0.0, max(all_vals + ([ref_line] if ref_line else [])) * 1.05
    d_min, d_max = d_values[0], d_values[-1]

    if lang == "pt":
        title = "Split por comprimento de digitos D — assinatura [0]: pontos fixos 18 vs 27 oscilam"
        ref_label = "- - -  massa da assinatura = 1/3"
    else:
        title = "Split by digit length D — signature [0]: fixed points 18 vs 27 oscillate"
        ref_label = "- - -  signature mass = 1/3"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="sans-serif">',
        f'<rect width="{width}" height="{height}" fill="#0d1117"/>',
        f'<text x="{width/2:.1f}" y="24" fill="#e6edf3" font-size="15" text-anchor="middle">{title}</text>',
        f'<line x1="{margin_l}" y1="{margin_t + plot_h:.1f}" x2="{margin_l + plot_w}" y2="{margin_t + plot_h:.1f}" stroke="#30363d"/>',
        f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{margin_t + plot_h:.1f}" stroke="#30363d"/>',
    ]
    if ref_line is not None:
        y_ref = _scale_y(ref_line, y_min, y_max, margin_t, margin_t + plot_h)
        parts.append(
            f'<line x1="{margin_l}" y1="{y_ref:.3f}" x2="{margin_l + plot_w}" y2="{y_ref:.3f}" stroke="#8b949e" stroke-dasharray="4 3"/>'
        )
        parts.append(f'<text x="570" y="106" fill="#8b949e" font-size="11">{ref_label}</text>')

    for idx, (key, legend, color) in enumerate(series):
        pts = [
            (_scale_x(d, d_min, d_max, margin_l, margin_l + plot_w), _scale_y(v, y_min, y_max, margin_t, margin_t + plot_h))
            for d, v in zip(d_values, curves[key])
        ]
        width_line = "1.4" if color == "#3fb950" else "2.0"
        parts.append(f'<polyline points="{_polyline(pts)}" fill="none" stroke="{color}" stroke-width="{width_line}"/>')
        parts.append(f'<text x="570" y="{52 + 18 * idx}" fill="{color}" font-size="12">{legend}</text>')

    parts.append("</svg>")
    out_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--signature", type=int, default=0)
    ap.add_argument("--d-min", type=int, default=4)
    ap.add_argument("--d-max", type=int, default=90)
    ap.add_argument("--measured-dir", type=Path, default=REPO_ROOT / "data" / "split")
    ap.add_argument("--out-dir", type=Path, default=FIG_DIR)
    ap.add_argument("--lang", choices=("en", "pt"), default="pt")
    ap.add_argument("--oscillation", action="store_true", help="also write split_oscillation.svg")
    args = ap.parse_args(argv)

    k, b, m = args.k, args.b, args.b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(args.signature)
    weight = mod.weights[mod.owner[args.signature % m]]
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    if len(targets) < 2:
        raise SystemExit("need a split signature with at least two attractors")

    primary = targets[0]
    primary_label = str(list(system.attractors[primary]))
    ceiling = int((b - 1) / 2 * k * args.d_max) + 400
    labels_map = attractor_labels_upto(ceiling, system)
    d_values = list(range(args.d_min, args.d_max + 1))

    pred = {i: [] for i in targets}
    for d in d_values:
        row = predict_split(d, system, signature, labels_map, targets, weight)
        for i in targets:
            pred[i].append(row[i])

    measured = _load_measured(k, b, args.measured_dir)
    meas_primary = None
    deviations: list[float] = []
    if measured and "digit_lengths" in measured and "curves" in measured:
        name = primary_label
        if name in measured["curves"]:
            idx = {d: j for j, d in enumerate(measured["digit_lengths"])}
            meas_primary = []
            for d in d_values:
                if d in idx:
                    mv = measured["curves"][name][idx[d]]
                    meas_primary.append(mv)
                    deviations.append(abs(pred[primary][len(meas_primary) - 1] - mv))
                else:
                    meas_primary.append(float("nan"))

    mae = mean(deviations) if deviations else None
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_overlay_svg(
        d_values=d_values,
        pred_primary=pred[primary],
        meas_primary=meas_primary,
        mae=mae,
        out_path=args.out_dir / "split_predict_overlay.svg",
        lang=args.lang,
    )
    print(f"wrote {args.out_dir / 'split_predict_overlay.svg'}  MAE={mae}")

    if args.oscillation and measured:
        d_vals = [d for d in measured["digit_lengths"] if args.d_min <= d <= args.d_max]
        sub = {}
        for label in ("[18]", "[27]", "[26]"):
            if label in measured["curves"]:
                sub[label] = [measured["curves"][label][measured["digit_lengths"].index(d)] for d in d_vals]
        series = []
        for label, color, text in (
            ("[18]", "#f778ba", "delta(18)  [fixed, sig 0]"),
            ("[27]", "#58a6ff", "delta(27)  [fixed, sig 0]"),
            ("[26]", "#3fb950", "delta(26)  [sig 8]"),
        ):
            if label in sub:
                series.append((label, text, color))
        write_oscillation_svg(
            d_values=d_vals,
            curves=sub,
            series=series,
            ref_line=1 / 3,
            out_path=args.out_dir / "split_oscillation.svg",
            lang=args.lang,
        )
        print(f"wrote {args.out_dir / 'split_oscillation.svg'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
