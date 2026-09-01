#!/usr/bin/env python3
"""Section-10 mining campaign: stratified grid, not a k×b rectangle.

Reuses the archived sweep under data/sweeps/ as prior (exact-match seeds and
Δ peaks). Exhaustive dynamics still go through dspm.analyze_pair.

Examples
--------
    python scripts/mine_topic10.py --quick
    python scripts/mine_topic10.py --mode full --workers 8
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from multiprocessing import Pool, cpu_count
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.core import HAVE_GMPY2
from dspm.mining.grid import GridCell, default_prior_csv, full_spec, quick_spec, smart_grid
from dspm.mining.record import mine_pair

REPO_ROOT = Path(__file__).resolve().parent.parent


def _worker_init(max_str_digits: int) -> None:
    try:
        sys.set_int_max_str_digits(max_str_digits)
    except Exception:
        pass


def _task(payload):
    cell_dict, max_M, max_pow, samples_orbit, samples_split = payload
    cell = GridCell(
        k=cell_dict["k"],
        b=cell_dict["b"],
        strata=tuple(cell_dict["strata"]),
        reason=cell_dict["reason"],
    )
    return mine_pair(
        cell,
        max_M=max_M,
        max_pow_digits=max_pow,
        samples_orbit=samples_orbit,
        samples_split=samples_split,
    )


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--mode", choices=("quick", "full"), default="quick")
    ap.add_argument("--quick", action="store_true", help="alias for --mode quick")
    ap.add_argument("--workers", type=int, default=max(1, cpu_count() - 1))
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "data" / "mining")
    ap.add_argument("--prior", type=Path, default=None)
    ap.add_argument("--resume", action="store_true", default=True)
    ap.add_argument("--no-resume", dest="resume", action="store_false")
    ap.add_argument("--samples-orbit", type=int, default=80)
    ap.add_argument("--samples-split", type=int, default=2500)
    return ap.parse_args(argv)


def _done_keys(jsonl_path: Path) -> set[tuple[int, int]]:
    done: set[tuple[int, int]] = set()
    if not jsonl_path.is_file():
        return done
    with jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            k, b = rec.get("k"), rec.get("b")
            if isinstance(k, int) and isinstance(b, int):
                done.add((k, b))
    return done


def _write_report(path: Path, summary: dict, records: list[dict]) -> None:
    ok = [r for r in records if r.get("status") == "ok"]
    exact = [r for r in ok if r.get("delta") == 0]
    identity_fail = [r for r in ok if r.get("excess_identity_ok") is False]
    lb_fail = [r for r in ok if r.get("lower_bound_ok") is False]
    by_base: dict[int, int] = {}
    for rec in exact:
        by_base[rec["b"]] = by_base.get(rec["b"], 0) + 1

    lines = [
        "# Topic 10 mining report",
        "",
        f"**Generated:** {summary['generated_at']}  ",
        f"**Mode:** {summary['mode']}  ",
        f"**gmpy2:** {summary['gmpy2']}  ",
        f"**Cells:** {summary['n_cells']} ({summary['ok_pairs']} ok)  ",
        f"**Prior:** `{summary.get('prior')}`",
        "",
        "## Grid",
        "",
        f"Strata counts: {summary['stratum_counts']}",
        "",
        "Not a rectangle. Layer A hunts tightness at small b; B samples m by "
        "ω(m); C/D densify archived Δ peaks and Δ=0 seeds (C is empty in "
        "quick mode when the k·M work cap drops the explosion neighbourhood); "
        "E/F attach orbit, degree, bounds, and Fourier-vs-Gaussian on a subsample.",
        "",
        "## 10.8 Cycle count fold",
        "",
        "``cycle_count_formula_folded`` evaluates Cyc by CRT-folding length "
        "multiplicity maps (gcd/lcm). It is tested equal to the graph and to "
        "the expanded product in ``tests/test_modular.py``.",
        "",
        "## Theorems on this grid",
        "",
        f"- Lower bound |C| ≥ Cyc violations: **{len(lb_fail)}**",
        f"- Δ = Σ δ_i failures: **{len(identity_fail)}**",
        f"- Signature mass identity failures: **{summary['mass_violations']}**",
        "",
        "## 10.2 Tightness",
        "",
        f"- Exact matches Δ=0: **{len(exact)} / {len(ok)}** "
        f"(rate is range-dependent; do not quote it as a law)",
        f"- By base: {dict(sorted(by_base.items()))}",
        f"- Max k with Δ=0: {max((r['k'] for r in exact), default=None)}",
        "",
        "## 10.1 / 10.7 Local excess",
        "",
        f"- Max Δ: {summary['max_delta']} at {summary['max_delta_pair']}",
        f"- Signatures with δ_i>0 (mean over ok cells): {summary['mean_split_signatures']}",
        "",
        "Report local δ_i inside a fixed m; do not pool moduli.",
        "",
        "## 10.3 Orbit length",
        "",
        f"- Cells with orbit extras: {summary['n_orbit']}",
        f"- All sampled bands bounded by 2 + max tail: {summary['orbit_bound_holds']}",
        "",
        "## 10.4 Predecessors",
        "",
        f"- Cells with degree fit: {summary['n_pred']}",
        f"- Any CSN-plausible power law (p>0.1): {summary['power_law_plausible']}",
        "",
        "## 10.5 Upper bound slack",
        "",
        f"- N* always ≥ |C|: {summary['Nstar_holds']}",
        f"- Cyc as upper bound (should be rare): {summary['Cyc_as_upper']}",
        "",
        "## 10.6 Split models",
        "",
        f"- Fourier-vs-Gaussian cells: {summary['n_split']}",
        f"- Fourier MAE mean: {summary['mae_fourier']}",
        f"- Gaussian MAE mean: {summary['mae_gaussian']}",
        "",
        "The independent-digit convolution is the inverse Fourier transform of "
        "φ(t)^L. Delange / Drmota–Grabner already oscillate; whether that "
        "implies the split is the convolution with a(v), not a numerical MAE.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.quick:
        args.mode = "quick"
    spec = quick_spec() if args.mode == "quick" else full_spec()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    prior = args.prior or default_prior_csv(REPO_ROOT)
    cells = smart_grid(mode=args.mode, spec=spec, prior_path=prior, repo=REPO_ROOT)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tag = f"{args.mode}_{stamp}"
    jsonl_path = args.out_dir / f"results_{tag}.jsonl"
    summary_path = args.out_dir / f"summary_{tag}.json"
    csv_path = args.out_dir / f"summary_{tag}.csv"
    report_path = args.out_dir / f"report_{tag}.md"
    latest_report = args.out_dir / "report_latest.md"
    latest_summary = args.out_dir / "summary_latest.json"

    done = _done_keys(jsonl_path) if args.resume else set()
    pending = [c for c in cells if (c.k, c.b) not in done]

    print(f"[mine] gmpy2={'on' if HAVE_GMPY2 else 'off'}")
    print(f"[mine] mode={args.mode} cells={len(cells)} pending={len(pending)}")
    print(f"[mine] workers={args.workers} max_M={spec.max_M}")
    print(f"[mine] output {jsonl_path}")

    payloads = [
        (
            {"k": c.k, "b": c.b, "strata": list(c.strata), "reason": c.reason},
            spec.max_M,
            spec.max_pow_digits,
            args.samples_orbit,
            args.samples_split,
        )
        for c in pending
    ]

    started = time.perf_counter()
    records: list[dict] = []
    stratum_counts: dict[str, int] = {}
    for c in cells:
        for s in c.strata:
            stratum_counts[s] = stratum_counts.get(s, 0) + 1

    with jsonl_path.open("a", encoding="utf-8") as jf, csv_path.open(
        "w", newline="", encoding="utf-8"
    ) as csv_f, Pool(
        processes=max(1, args.workers),
        initializer=_worker_init,
        initargs=(1_000_000_000,),
    ) as pool:
        writer = csv.writer(csv_f)
        writer.writerow(
            [
                "k", "b", "status", "strata", "cyc_modular", "num_attractors",
                "delta", "delta_local_sum", "excess_identity_ok", "M",
            ]
        )
        iterator = (
            pool.imap_unordered(_task, payloads, chunksize=1) if payloads else []
        )
        done_n = 0
        for rec in iterator:
            records.append(rec)
            jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            writer.writerow(
                [
                    rec.get("k"), rec.get("b"), rec.get("status"),
                    "|".join(rec.get("strata") or []),
                    rec.get("cyc_modular"), rec.get("num_attractors"),
                    rec.get("delta"), rec.get("delta_local_sum"),
                    rec.get("excess_identity_ok"), rec.get("M"),
                ]
            )
            done_n += 1
            if done_n % 25 == 0 or done_n == len(payloads):
                elapsed = time.perf_counter() - started
                rate = done_n / elapsed if elapsed else 0
                print(
                    f"[mine] {done_n}/{len(payloads)} {100 * done_n / max(len(payloads), 1):4.1f}% "
                    f"| {rate:5.2f}/s",
                    flush=True,
                )

    # Reload full jsonl for the report if we resumed into a fresh stamp file
    # (this run's file only contains this run).
    ok = [r for r in records if r.get("status") == "ok"]
    orbit_recs = [r for r in ok if r.get("orbit_bands")]
    pred_recs = [r for r in ok if r.get("predecessors")]
    split_recs = [r for r in ok if isinstance(r.get("split_models"), dict) and r["split_models"].get("mae_gaussian") is not None]
    bound_recs = [r for r in ok if r.get("bounds")]

    max_delta, max_pair = -1, None
    for rec in ok:
        d = rec.get("delta") or 0
        if d > max_delta:
            max_delta, max_pair = d, (rec["k"], rec["b"])

    mae_g = [r["split_models"]["mae_gaussian"] for r in split_recs]
    mae_f = [r["split_models"]["mae_fourier"] for r in split_recs]

    summary = {
        "generated_at": stamp,
        "mode": args.mode,
        "gmpy2": HAVE_GMPY2,
        "n_cells": len(cells),
        "n_run": len(records),
        "ok_pairs": len(ok),
        "status_counts": {},
        "stratum_counts": stratum_counts,
        "elapsed_s": round(time.perf_counter() - started, 2),
        "prior": (
            str(Path(prior).resolve().relative_to(REPO_ROOT))
            if prior and Path(prior).resolve().is_relative_to(REPO_ROOT)
            else (str(prior) if prior else None)
        ),
        "lower_bound_violations": sum(1 for r in ok if r.get("lower_bound_ok") is False),
        "mass_violations": sum(1 for r in ok if r.get("signature_mass_all_exact") is False),
        "excess_identity_failures": sum(1 for r in ok if r.get("excess_identity_ok") is False),
        "exact_matches": sum(1 for r in ok if r.get("delta") == 0),
        "max_delta": max_delta,
        "max_delta_pair": max_pair,
        "mean_split_signatures": (
            round(sum(r.get("n_signatures_split") or 0 for r in ok) / len(ok), 4) if ok else None
        ),
        "n_orbit": len(orbit_recs),
        "orbit_bound_holds": all(
            (r.get("orbit_bands") or {}).get("bounded_by_two_plus_tail") for r in orbit_recs
        ) if orbit_recs else None,
        "n_pred": len(pred_recs),
        "power_law_plausible": any(
            (r.get("predecessors") or {}).get("fit", {}).get("plausible") for r in pred_recs
        ),
        "n_split": len(split_recs),
        "mae_gaussian": round(sum(mae_g) / len(mae_g), 6) if mae_g else None,
        "mae_fourier": round(sum(mae_f) / len(mae_f), 6) if mae_f else None,
        "Nstar_holds": all(r["bounds"]["holds_as_upper"]["N_star"] for r in bound_recs) if bound_recs else None,
        "Cyc_as_upper": sum(1 for r in bound_recs if r["bounds"]["holds_as_upper"]["Cyc"]),
        "files": {
            "results_jsonl": jsonl_path.name,
            "summary_csv": csv_path.name,
            "report": report_path.name,
        },
    }
    for rec in records:
        st = rec.get("status", "unknown")
        summary["status_counts"][st] = summary["status_counts"].get(st, 0) + 1

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_report(report_path, summary, records)
    latest_report.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")

    print("\n" + "=" * 68)
    print(f"[mine] finished in {summary['elapsed_s']}s  status={summary['status_counts']}")
    print(f"[mine] excess identity failures={summary['excess_identity_failures']}")
    print(f"[mine] exact delta=0: {summary['exact_matches']}/{summary['ok_pairs']}")
    print(f"[mine] report {report_path}")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
