#!/usr/bin/env python3
"""v-space local means of the labelling (Hypothesis LM diagnostic).

Does not sample n and does not assume LLT. For each scale V, compute the mean
of h_j(v) = 1_{g(v) in beta_j} on the sharp window [V - sqrt(V), V + sqrt(V)]
restricted to the residue classes feeding a split signature.

This is the experiment that distinguishes:
* log-periodic: Psi_j(b V) ~ Psi_j(V)
* quasi-periodic with several frequencies
* scale-dependent with no limit (decade collapse fails)

Default pilot: (k, b) = (3, 10), signature {0}, V up to 10^6.

Examples
--------
    python scripts/local_mean.py
    python scripts/local_mean.py --v-max 100000
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

import _bootstrap  # noqa: F401
from dspm.dynamics import FiniteSystem, build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto

REPO_ROOT = Path(__file__).resolve().parent.parent


def window_halfwidth(V: int) -> int:
    return max(1, int(V**0.5))


def psi_sharp(
    labels: list[int],
    V: int,
    m: int,
    feeding: list[int],
    targets: list[int],
) -> dict[int, float]:
    """Mean of h_j on [V-sqrt(V), V+sqrt(V)] intersect feeding residues."""
    h = window_halfwidth(V)
    lo = max(1, V - h)
    hi = min(len(labels) - 1, V + h)
    counts = {t: 0 for t in targets}
    n = 0
    for r in feeding:
        v = lo + ((r - lo) % m)
        while v <= hi:
            lab = labels[v]
            if lab in counts:
                counts[lab] += 1
            n += 1
            v += m
    if n == 0:
        return {t: float("nan") for t in targets}
    return {t: counts[t] / n for t in targets}


def log_grid(v_min: int, v_max: int, per_decade: int) -> list[int]:
    if v_min < 1 or v_max < v_min:
        raise ValueError("need 1 <= v_min <= v_max")
    lo = math.log10(v_min)
    hi = math.log10(v_max)
    n = max(2, int((hi - lo) * per_decade) + 1)
    out: list[int] = []
    seen: set[int] = set()
    for i in range(n):
        t = lo + (hi - lo) * i / (n - 1)
        v = max(v_min, min(v_max, int(round(10**t))))
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return float("nan")
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def amplitude(values: list[float]) -> float:
    return max(values) - min(values) if values else 0.0


def decade_collapse(
    Vs: list[int],
    curve: list[float],
    b: int,
) -> dict | None:
    """Pearson and MAE of Psi(V) vs Psi(b V) on the overlapping log grid."""
    index = {V: y for V, y in zip(Vs, curve)}
    pairs = []
    for V, y in zip(Vs, curve):
        w = b * V
        if w in index:
            pairs.append((y, index[w]))
        else:
            near = min(index, key=lambda u: abs(u - w)) if index else None
            if near is not None and abs(near - w) / w <= 0.02:
                pairs.append((y, index[near]))
    if len(pairs) < 8:
        return None
    a, c = [p[0] for p in pairs], [p[1] for p in pairs]
    mae = mean(abs(x - y) for x, y in zip(a, c))
    return {
        "n_pairs": len(pairs),
        "pearson": pearson(a, c),
        "mae": mae,
        "sd_base": pstdev(a) if len(a) > 1 else 0.0,
        "sd_shifted": pstdev(c) if len(c) > 1 else 0.0,
        "amp_base": amplitude(a),
        "amp_shifted": amplitude(c),
    }


def feeding_residues(k: int, m: int, signature: frozenset[int]) -> list[int]:
    mod = structure(k, m)
    return [r for r in range(m) if frozenset(mod.cycles[mod.owner[r]]) == signature]


def run_psi(
    system: FiniteSystem,
    signature: frozenset[int],
    v_min: int,
    v_max: int,
    per_decade: int,
) -> tuple[dict[int, str], list[int], dict[int, list[float]], list[int], int]:
    m = system.b - 1
    feeding = feeding_residues(system.k, m, signature)
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    names = {i: str(list(system.attractors[i])) for i in targets}
    ceiling = v_max + window_halfwidth(v_max) + 2
    labels = attractor_labels_upto(ceiling, system)
    Vs = log_grid(v_min, v_max, per_decade)
    curves: dict[int, list[float]] = {i: [] for i in targets}
    for V in Vs:
        pred = psi_sharp(labels, V, m, feeding, targets)
        for i in targets:
            curves[i].append(pred[i])
    return names, Vs, curves, targets, ceiling


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--b", type=int, default=10)
    ap.add_argument("--signature", type=int, default=0)
    ap.add_argument("--v-min", type=int, default=100)
    ap.add_argument("--v-max", type=int, default=1_000_000)
    ap.add_argument("--per-decade", type=int, default=40)
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "data" / "split")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    k, b = args.k, args.b
    m = b - 1
    system = build_system(k, b)
    mod = structure(k, m)
    signature = mod.signature_of_residue(args.signature)
    targets_check = [i for i in range(system.count) if system.signature(i) == signature]
    if len(targets_check) < 2:
        print(
            f"signature {sorted(signature)} hosts {len(targets_check)} attractor(s); "
            "nothing to split."
        )
        return 1

    names, Vs, curves, targets, ceiling = run_psi(
        system, signature, args.v_min, args.v_max, args.per_decade
    )
    primary = max(targets, key=lambda i: amplitude(curves[i]))
    collapse = decade_collapse(Vs, curves[primary], b)
    amps = {names[i]: amplitude(curves[i]) for i in targets}

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"local_mean_k{k}_b{b}_sig{args.signature}_V{args.v_max}_{stamp}"
    payload = {
        "k": k,
        "b": b,
        "signature": sorted(signature),
        "v_min": args.v_min,
        "v_max": args.v_max,
        "ceiling": ceiling,
        "window": "sharp [V-sqrt(V), V+sqrt(V)] on feeding residues",
        "samples_n": False,
        "note": (
            "Hypothesis LM diagnostic. Not a test of LLT. Decade collapse "
            "Psi(bV)~Psi(V) would support a period-1 factor in log_b V; failure "
            "supports non-convergence without a single Delange P_j."
        ),
        "scales": Vs,
        "frac_log": [math.log(V) / math.log(b) % 1.0 for V in Vs],
        "curves": {names[i]: curves[i] for i in targets},
        "amplitudes": amps,
        "decade_collapse": collapse,
        "primary": names[primary],
    }
    json_path = args.out_dir / f"{stem}.json"
    latest_json = args.out_dir / "local_mean_latest.json"
    text = json.dumps(payload, indent=2)
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")

    md_lines = [
        f"# v-space local means -- Hypothesis LM diagnostic",
        "",
        f"- pair: (k, b) = ({k}, {b})",
        f"- signature: {sorted(signature)}",
        f"- V in [{args.v_min}, {args.v_max}], {len(Vs)} scales, ceiling {ceiling}",
        f"- window: [V - sqrt(V), V + sqrt(V)] on feeding residues",
        f"- attractors: {list(names.values())}",
        f"- amplitudes: {amps}",
        "",
        "## Decade collapse Psi(V) vs Psi(b V)",
        "",
    ]
    if collapse:
        md_lines.extend(
            [
                f"- n pairs: {collapse['n_pairs']}",
                f"- Pearson: {collapse['pearson']:.4f}",
                f"- MAE: {collapse['mae']:.4f}  (sd base {collapse['sd_base']:.4f}, "
                f"shifted {collapse['sd_shifted']:.4f})",
                f"- amp base / shifted: {collapse['amp_base']:.4f} / {collapse['amp_shifted']:.4f}",
                "",
                "Pearson near 1 with MAE below the within-scale sd would support "
                "a period-1 factor in log_b V. A small Pearson with MAE on the "
                "order of the amplitude supports Hypothesis LM without that form.",
                "",
            ]
        )
    else:
        md_lines.append("- not enough overlapping scales for a decade-collapse test.")
        md_lines.append("")
    md_path = args.out_dir / f"{stem}.md"
    latest_md = args.out_dir / "local_mean_latest.md"
    md_text = "\n".join(md_lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    print("=" * 78)
    print(f"  local_mean  k={k} b={b}  signature {sorted(signature)}")
    print(f"  V={args.v_min}..{args.v_max}  n={len(Vs)}  ceiling={ceiling}")
    print(f"  attractors {list(names.values())}  amps {amps}")
    if collapse:
        print(
            f"  decade collapse Pearson={collapse['pearson']:.4f}  "
            f"MAE={collapse['mae']:.4f}  n={collapse['n_pairs']}"
        )
        if collapse["pearson"] > 0.8 and collapse["mae"] < 0.5 * collapse["sd_base"]:
            print("  form: compatible with period-1 in log_b V")
        elif collapse["mae"] >= 0.5 * max(collapse["amp_base"], 1e-9):
            print("  form: decade collapse fails; keep non-convergence, not P_j({log_b V})")
        else:
            print("  form: inconclusive")
    print("-" * 78)
    print(f"  wrote {json_path.relative_to(REPO_ROOT)}")
    print(f"  wrote {md_path.relative_to(REPO_ROOT)}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
