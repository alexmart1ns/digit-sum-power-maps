#!/usr/bin/env python3
"""Turn a sweep dataset into a patterns report.

Reports the correlations of section 9 of the paper, with two guards that the
first pass lacked: the prime-versus-composite contrast is shown alongside its
odd-only control (the raw contrast mostly measures parity of k), and gcd groups
carry their within-group spread and modulus count (a mean pooled across many
moduli is not evidence of a per-system law).

Examples
--------
    python scripts/analyze_patterns.py
    python scripts/analyze_patterns.py --input data/sweeps/results_k1-500_b2-40_*.jsonl.gz
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.patterns import (
    correlation_table,
    density_law_check,
    enrich,
    exact_match_profile,
    exponent_class_table,
    gcd_table,
    load_records,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def fmt(value, spec=".3f", dash="--"):
    return dash if value is None else format(value, spec)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=str, default=None, help="results_*.jsonl[.gz]; default: newest in data/sweeps")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    sweeps = REPO_ROOT / "data" / "sweeps"
    if args.input:
        matches = sorted(sweeps.parent.glob(args.input)) or [Path(args.input)]
        source = matches[-1]
    else:
        candidates = sorted(sweeps.glob("results_*.jsonl*"))
        if not candidates:
            print("no results_*.jsonl in data/sweeps; run scripts/sweep.py first")
            return 1
        source = candidates[-1]

    records = load_records(source)
    if not records:
        print(f"no 'ok' records in {source}")
        return 1
    enrich(records)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = args.out or sweeps / f"patterns_{stamp}.md"

    violations = [(r["k"], r["b"]) for r in records if not r.get("lower_bound_ok")]
    density = density_law_check(records)
    exact = exact_match_profile(records)

    md: list[str] = [
        "# Patterns report",
        "",
        f"**Source:** `{source.name}`  ",
        f"**Generated:** {stamp}  ",
        f"**Pairs with status ok:** {len(records)}",
        "",
        "## 0. Theorem sanity",
        f"- Lower-bound violations (|C| < Cyc): **{len(violations)}**"
        + ("" if not violations else f" at {violations[:10]}"),
        f"- Largest bifurcation excess observed: **{max(r['delta'] for r in records)}**",
        f"- Grid reach: k <= {max(r['k'] for r in records)}, b <= {max(r['b'] for r in records)}",
        "",
        "## 1. Aggregate density law (Proposition 5.2, integer form)",
        f"- Signature comparisons with an exact integer match: "
        f"**{density['integer_identity_exact']}/{density['integer_identity_checked']}**",
        f"- Mean |q_i - p_i| over the same windows: {fmt(density['mean_abs_error'], '.6f')}",
        f"- Worst |q_i - p_i|: {fmt(density['max_abs_error'], '.6f')}",
        "",
        "The integer identity is the sharp statement. Checking |q_i - p_i| against",
        "the loose bound (b-1)/M passes almost automatically and should not be",
        "reported as the headline verification.",
        "",
        "## 2. Correlations (Pearson R)",
        "",
        "| predictor | Cyc | \\|C\\| | Delta | max tail |",
        "|---|---|---|---|---|",
    ]
    for row in correlation_table(records):
        md.append(
            f"| `{row['predictor']}` | {fmt(row['cyc_modular'], '+.3f')} | "
            f"{fmt(row['num_attractors'], '+.3f')} | {fmt(row['delta'], '+.3f')} | "
            f"{fmt(row['max_tail_depth_overall'], '+.3f')} |"
        )

    md += [
        "",
        "## 3. Excess by gcd(k, b-1)",
        "",
        "`n_moduli` and `stdev` are the honesty columns: a mean pooled over many",
        "moduli with large spread is an aggregation artifact, not a law.",
        "",
        "| gcd | pairs | moduli | mean Delta | stdev | max Delta | mean \\|C\\| |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in gcd_table(records):
        md.append(
            f"| {row['gcd']} | {row['n_pairs']} | {row['n_moduli']} | "
            f"{row['delta_mean']:.2f} | {row['delta_stdev']:.2f} | "
            f"{row['delta_max']} | {row['count_mean']:.2f} |"
        )

    md += [
        "",
        "## 4. Exponent class, with the parity confound controlled",
        "",
        "| class of k | n | mean \\|C\\| | mean Cyc | mean Delta |",
        "|---|---|---|---|---|",
    ]
    for row in exponent_class_table(records):
        md.append(
            f"| {row['class']} | {row['n']} | {row['count_mean']:.2f} | "
            f"{row['cyc_mean']:.2f} | {row['delta_mean']:.2f} |"
        )
    md += [
        "",
        "If the two odd-only rows agree while odd and even differ sharply, the",
        "effect is the parity of k, not its primality -- which is what",
        "Proposition 6.1 predicts, since 2 | k strips the 2-part of every local",
        "unit group.",
        "",
        "## 5. Exact match |C| = Cyc (Problem 10.2)",
        f"- Exact matches: **{exact['n_exact']}/{exact['n_total']}** "
        f"({fmt(exact['rate'] and 100 * exact['rate'], '.2f')}%)",
        f"- By base: {exact['by_base']}",
        f"- Largest k with an exact match: {exact['max_k_with_exact']}",
        f"- {exact['note']}",
        "",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(md), encoding="utf-8")

    print(f"[patterns] source {source.name}")
    print(f"[patterns] ok pairs {len(records)} | lower-bound violations {len(violations)}")
    print(
        f"[patterns] integer mass identity "
        f"{density['integer_identity_exact']}/{density['integer_identity_checked']}"
    )
    print(f"[patterns] report {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
