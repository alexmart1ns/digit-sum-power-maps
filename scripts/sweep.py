#!/usr/bin/env python3
"""Exhaustive parameter sweep over the (k, b) grid.

For every pair the attractors, basins and residue signatures are computed
exhaustively on the rigorous trapping region [1, M] -- this is enumeration,
not sampling. Results stream to JSONL so a long run is never lost, and pairs
that would blow up are skipped with a status instead of killing the sweep.

Examples
--------
    python scripts/sweep.py --k-max 20 --b-max 10
    python scripts/sweep.py --k-max 500 --b-max 40 --workers 28
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

import _bootstrap  # noqa: F401  (adds src/ to sys.path)
from dspm.analysis import analyze_pair
from dspm.core import HAVE_GMPY2

REPO_ROOT = Path(__file__).resolve().parent.parent


def _worker_init(max_str_digits: int) -> None:
    try:
        sys.set_int_max_str_digits(max_str_digits)
    except Exception:
        pass


def _task(args):
    k, b, max_M, max_pow_digits, deep = args
    return analyze_pair(k, b, max_M=max_M, max_pow_digits=max_pow_digits, deep=deep)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--k-min", type=int, default=1)
    ap.add_argument("--k-max", type=int, default=100)
    ap.add_argument("--b-min", type=int, default=2)
    ap.add_argument("--b-max", type=int, default=20)
    ap.add_argument("--workers", type=int, default=max(1, cpu_count() - 1))
    ap.add_argument(
        "--max-M",
        type=int,
        default=2_000_000,
        help="skip a pair whose trapping region exceeds this size",
    )
    ap.add_argument(
        "--max-pow-digits",
        type=int,
        default=200_000,
        help="skip a pair whose M^k has more digits than this",
    )
    ap.add_argument("--deep", dest="deep", action="store_true", default=True)
    ap.add_argument("--no-deep", dest="deep", action="store_false")
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "data" / "sweeps")
    ap.add_argument("--chunksize", type=int, default=1)
    ap.add_argument("--top", type=int, default=15)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tag = f"k{args.k_min}-{args.k_max}_b{args.b_min}-{args.b_max}_{stamp}"
    jsonl_path = args.out_dir / f"results_{tag}.jsonl"
    summary_path = args.out_dir / f"summary_{tag}.json"
    csv_path = args.out_dir / f"summary_{tag}.csv"

    pairs = [
        (k, b)
        for b in range(args.b_min, args.b_max + 1)
        for k in range(args.k_min, args.k_max + 1)
    ]
    total = len(pairs)

    print(f"[sweep] gmpy2={'on' if HAVE_GMPY2 else 'off (pure python fallback)'}")
    print(
        f"[sweep] grid k in [{args.k_min},{args.k_max}] x b in "
        f"[{args.b_min},{args.b_max}] = {total} pairs"
    )
    print(f"[sweep] workers={args.workers} max_M={args.max_M} deep={args.deep}")
    print(f"[sweep] output {jsonl_path}")

    tasks = [(k, b, args.max_M, args.max_pow_digits, args.deep) for k, b in pairs]

    started = time.perf_counter()
    done = ok_pairs = exact_matches = 0
    status_counts: dict = {}
    violations: list = []
    mass_violations: list = []
    max_delta, max_delta_pair = -1, None
    max_M_seen = max_tail_seen = 0

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_f, open(
        jsonl_path, "w", encoding="utf-8"
    ) as jf, Pool(
        processes=args.workers, initializer=_worker_init, initargs=(1_000_000_000,)
    ) as pool:
        writer = csv.writer(csv_f)
        writer.writerow(
            [
                "k", "b", "status", "cyc_modular", "num_attractors", "delta",
                "lower_bound_ok", "signature_mass_all_exact", "M",
                "max_tail_depth_overall", "branching_max",
                "distinct_modular_anchors", "elapsed_s",
            ]
        )

        for rec in pool.imap_unordered(_task, tasks, chunksize=args.chunksize):
            done += 1
            jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            status = rec.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            writer.writerow(
                [
                    rec.get("k"), rec.get("b"), status, rec.get("cyc_modular"),
                    rec.get("num_attractors"), rec.get("delta"),
                    rec.get("lower_bound_ok"), rec.get("signature_mass_all_exact"),
                    rec.get("M"), rec.get("max_tail_depth_overall"),
                    rec.get("branching_max"), rec.get("distinct_modular_anchors"),
                    rec.get("elapsed_s"),
                ]
            )

            if status == "ok":
                ok_pairs += 1
                if rec.get("lower_bound_ok") is False:
                    violations.append((rec["k"], rec["b"]))
                if rec.get("signature_mass_all_exact") is False:
                    mass_violations.append((rec["k"], rec["b"]))
                delta = rec.get("delta", 0)
                exact_matches += int(delta == 0)
                if delta > max_delta:
                    max_delta, max_delta_pair = delta, (rec["k"], rec["b"])
                max_M_seen = max(max_M_seen, rec.get("M") or 0)
                max_tail_seen = max(max_tail_seen, rec.get("max_tail_depth_overall") or 0)

            if done % 50 == 0 or done == total:
                elapsed = time.perf_counter() - started
                rate = done / elapsed if elapsed else 0
                eta = (total - done) / rate if rate else 0
                print(
                    f"[sweep] {done}/{total} ({100 * done / total:4.1f}%) "
                    f"| {rate:6.1f} pairs/s | eta {eta:6.0f}s "
                    f"| maxDelta={max_delta}@{max_delta_pair} viol={len(violations)}",
                    flush=True,
                )

    elapsed = time.perf_counter() - started
    summary = {
        "generated_at": stamp,
        "gmpy2": HAVE_GMPY2,
        "grid": {
            "k_min": args.k_min, "k_max": args.k_max,
            "b_min": args.b_min, "b_max": args.b_max, "total_pairs": total,
        },
        "workers": args.workers,
        "elapsed_s": round(elapsed, 2),
        "status_counts": status_counts,
        "ok_pairs": ok_pairs,
        "lower_bound_violations": violations,
        "lower_bound_holds": not violations,
        "signature_mass_violations": mass_violations,
        "signature_mass_identity_holds": not mass_violations,
        "exact_matches": exact_matches,
        "exact_match_pct": round(100 * exact_matches / ok_pairs, 4) if ok_pairs else None,
        "max_delta": max_delta,
        "max_delta_pair": max_delta_pair,
        "max_M_seen": max_M_seen,
        "max_tail_depth_seen": max_tail_seen,
        "files": {"results_jsonl": jsonl_path.name, "summary_csv": csv_path.name},
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 68)
    print(f"[sweep] finished in {elapsed:.1f}s   status={status_counts}")
    print(
        "[sweep] Theorem 4.1 (|C| >= Cyc): "
        + ("holds, 0 violations" if not violations else f"VIOLATED at {violations[:10]}")
    )
    print(
        "[sweep] Proposition 5.2 (exact integer mass identity): "
        + ("holds, 0 violations" if not mass_violations else f"VIOLATED at {mass_violations[:10]}")
    )
    print(f"[sweep] exact |C|=Cyc: {exact_matches}/{ok_pairs} ({summary['exact_match_pct']}%)")
    print(f"[sweep] largest Delta {max_delta} at (k,b)={max_delta_pair}")
    print(f"[sweep] summary {summary_path}")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
