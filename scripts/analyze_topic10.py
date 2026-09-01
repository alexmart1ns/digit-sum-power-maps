#!/usr/bin/env python3
"""Post-grid Topic-10 work: intra-modulus slices, tightness census, bound scores.

Does *not* launch another k×b rectangle. Reads the full mining JSONL, scores
upper-bound candidates on every ok pair, optionally extends the b=2,3 Δ=0
census, and mines a handful of large-M cells for orbit/predecessor extras.

Examples
--------
    python scripts/analyze_topic10.py
    python scripts/analyze_topic10.py --skip-tightness --skip-deep
    python scripts/analyze_topic10.py --k-max 800 --workers 8
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from multiprocessing import Pool, cpu_count
from pathlib import Path

import _bootstrap  # noqa: F401
from dspm.core import HAVE_GMPY2
from dspm.mining.bounds import summarize_bound_scores
from dspm.mining.grid import GridCell
from dspm.mining.intra import analyze_intra_modulus, load_jsonl
from dspm.mining.record import mine_pair
from dspm.mining.tightness import tightness_cells

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEEP = ((157, 80), (499, 37), (493, 38))


def _worker_init(max_str_digits: int) -> None:
    try:
        sys.set_int_max_str_digits(max_str_digits)
    except Exception:
        pass


def _task(payload):
    cell_dict, max_M, max_pow, samples_orbit = payload
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
        samples_split=0,
    )


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--jsonl",
        type=Path,
        default=None,
        help="Full mining JSONL (default: latest results_full_*.jsonl)",
    )
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / "data" / "mining")
    ap.add_argument("--k-max", type=int, default=1500, help="Tightness census k <= K for b=2,3")
    ap.add_argument("--workers", type=int, default=max(1, cpu_count() - 1))
    ap.add_argument("--skip-tightness", action="store_true")
    ap.add_argument("--skip-deep", action="store_true")
    ap.add_argument("--samples-orbit", type=int, default=80)
    ap.add_argument("--max-M", type=int, default=2_000_000)
    ap.add_argument("--max-pow-digits", type=int, default=200_000)
    return ap.parse_args(argv)


def _latest_full_jsonl(out_dir: Path) -> Path:
    hits = sorted(out_dir.glob("results_full_*.jsonl"))
    if not hits:
        raise FileNotFoundError(f"no results_full_*.jsonl under {out_dir}")
    return hits[-1]


def _done_keys(jsonl_path: Path) -> set[tuple[int, int]]:
    done: set[tuple[int, int]] = set()
    if not jsonl_path.is_file():
        return done
    with jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            k, b = rec.get("k"), rec.get("b")
            if isinstance(k, int) and isinstance(b, int):
                done.add((k, b))
    return done


def _run_pool(cells: list[GridCell], jsonl_path: Path, args) -> list[dict]:
    payloads = [
        (
            {"k": c.k, "b": c.b, "strata": list(c.strata), "reason": c.reason},
            args.max_M,
            args.max_pow_digits,
            args.samples_orbit,
        )
        for c in cells
    ]
    records: list[dict] = []
    if not payloads:
        return records
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with jsonl_path.open("a", encoding="utf-8") as jf, Pool(
        processes=max(1, args.workers),
        initializer=_worker_init,
        initargs=(1_000_000_000,),
    ) as pool:
        done_n = 0
        for rec in pool.imap_unordered(_task, payloads, chunksize=1):
            records.append(rec)
            jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            done_n += 1
            if done_n % 10 == 0 or done_n == len(payloads):
                elapsed = time.perf_counter() - started
                rate = done_n / elapsed if elapsed else 0
                print(
                    f"[analyze] {done_n}/{len(payloads)} "
                    f"{100 * done_n / len(payloads):4.1f}% | {rate:5.2f}/s",
                    flush=True,
                )
    return records


def _fmt_rho(value) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def _write_report(path: Path, payload: dict) -> None:
    intra = payload["intra"]
    bounds = payload["bounds"]
    tight = payload.get("tightness") or {}
    deep = payload.get("deep") or {}
    lines = [
        "# Topic 10 follow-up (intra-modulus, tightness, bounds)",
        "",
        f"**Generated:** {payload['generated_at']}  ",
        f"**Source JSONL:** `{payload['source_jsonl']}`  ",
        f"**gmpy2:** {payload['gmpy2']}",
        "",
        "## 10.1 / 10.7 Intra-modulus local excess",
        "",
        f"- Ok pairs with local_excess: **{intra['n_ok']}** across **{intra['n_moduli']}** moduli",
        f"- Split signatures at one digit layer: **{intra['same_layer_splits']}**",
        f"- Split signatures at two or more layers: **{intra['multi_layer_splits']}**",
        f"- Moduli with Spearman(delta_local, n_digit_layers) defined: {intra['moduli_with_layer_spearman']}",
        f"- Of those, Spearman > 0: **{intra['moduli_layer_spearman_positive']}**",
        f"- Moduli with mean Delta (k odd) > mean Delta (k even): "
        f"{intra['moduli_mean_delta_odd_gt_even']} / {intra['moduli_parity_compared']}",
        "",
        intra["note"],
        "",
        "Same-layer splits are physical attractors sharing a residue cycle but "
        "sitting at a single digit length. They block the working hypothesis "
        "that excess is just 'more digit layers'.",
        "",
        "### Highlighted moduli",
        "",
        "| m | b | pairs | mean Delta | mean Delta odd | mean Delta even | "
        "rho layers (local) | same-layer splits | multi-layer splits |",
        "|---|---|------:|-----------:|---------------:|----------------:|--------------------:|"
        "------------------:|-------------------:|",
    ]
    for row in intra["highlight_moduli"]:
        lines.append(
            f"| {row['m']} | {row['b']} | {row['n_pairs']} | {row['mean_delta']} | "
            f"{row['mean_delta_k_odd']} | {row['mean_delta_k_even']} | "
            f"{_fmt_rho(row['spearman_delta_local_vs_layers'])} | "
            f"{row['split_same_layer']} | {row['split_multi_layer']} |"
        )
    lines += [
        "",
        "## 10.5 Upper-bound candidates (existing records)",
        "",
        f"- Scored pairs: **{bounds['n_scored']}**",
        f"- Always holds: {bounds['always_holds']}",
        f"- Never holds: {bounds['never_holds']}",
            f"- Tightest surviving: {bounds['tightest_surviving']}",
            "",
            "Min slack 2 on both survivors is the tiny pair (k,b)=(1,2) "
            "(M=3, |C|=1). It is not a near-sharp bound on large systems. "
            "Mean slack stays O(M).",
        "",
        "| candidate | hold rate | mean slack | min slack |",
        "|-----------|----------:|-----------:|----------:|",
    ]
    for name, rate in (bounds.get("hold_rate") or {}).items():
        lines.append(
            f"| {name} | {rate} | {bounds['mean_slack'][name]} | {bounds['min_slack'][name]} |"
        )
    lines += [
        "",
        bounds["note"],
        "",
        "### Worst counterexamples (most negative slack)",
        "",
    ]
    for name, ex in (bounds.get("worst_counterexample") or {}).items():
        lines.append(
            f"- `{name}` fails at (k,b)=({ex['k']},{ex['b']}): "
            f"|C|={ex['C']} bound={ex['bound']} slack={ex['slack']}"
        )
    if tight:
        exact = tight.get("exact") or []
        lines += [
            "",
            "## 10.2 Tightness census (b=2,3)",
            "",
            f"- k_max: **{tight.get('k_max')}**",
            f"- Pairs in census (including reused full-run cells): **{tight.get('n_pairs')}**",
            f"- Newly mined: {tight.get('n_new')}",
            f"- Exact Delta=0: **{len(exact)}**",
            f"- Exact k for b=2: {tight.get('exact_k_b2')}",
            f"- Exact k for b=3: {tight.get('exact_k_b3')}",
            f"- Max k with Delta=0: {tight.get('max_k_exact')}",
            "",
            "This is a complete list on the rectangle {1..k_max} x {2,3}, not a rate.",
        ]
    if deep:
        recs = deep.get("records") or []
        prior = deep.get("prior_e_cells") or []
        lines += [
            "",
            "## 10.3 / 10.4 Orbit and predecessors",
            "",
            f"- Prior E cells in the full run: **{len(prior)}** "
            f"(bands<=2+tail: {all(p.get('bounded') for p in prior) if prior else None}; "
            f"any CSN-plausible: {any(p.get('plausible') for p in prior)})",
            f"- Extra large-M cells this run: **{len(recs)}**",
        ]
        all_bands = True
        any_plausible = False
        for rec in recs:
            bands = rec.get("orbit_bands") or {}
            pred = rec.get("predecessors") or {}
            fit = pred.get("fit") or {}
            bounded = bands.get("bounded_by_two_plus_tail")
            if bounded is False:
                all_bands = False
            if fit.get("plausible"):
                any_plausible = True
            lines.append(
                f"- (k,b)=({rec.get('k')},{rec.get('b')}) M={rec.get('M')} "
                f"Delta={rec.get('delta')} L_window={ (rec.get('orbit_window') or {}).get('L') } "
                f"bands<=2+tail={bounded} CSN_plausible={fit.get('plausible')} "
                f"alpha={fit.get('alpha')}"
            )
        lines += [
            "",
            f"- All new bands bounded by 2 + max tail: **{all_bands}**",
            f"- Any CSN-plausible power law: **{any_plausible}**",
        ]
    lines += [
        "",
        "## Stopped",
        "",
        "- 10.6 Fourier vs Gaussian: MAE already matches noise; no more cells.",
        "- 10.8 Folded Cyc formula: already tested equal to the graph.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _existing_for_bases(records: list[dict], bases: tuple[int, ...], k_max: int) -> list[dict]:
    out = []
    want = set(bases)
    for rec in records:
        if rec.get("status") != "ok":
            continue
        if rec.get("b") in want and 1 <= int(rec["k"]) <= k_max:
            out.append(rec)
    return out


def main(argv=None) -> int:
    args = parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    source = args.jsonl or _latest_full_jsonl(args.out_dir)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"[analyze] gmpy2={'on' if HAVE_GMPY2 else 'off'}")
    print(f"[analyze] source {source}")
    records = load_jsonl(source)
    print(f"[analyze] loaded {len(records)} records")

    intra = analyze_intra_modulus(records)
    print(
        f"[analyze] intra-modulus: {intra['n_ok']} pairs, {intra['n_moduli']} moduli, "
        f"same-layer splits={intra['same_layer_splits']}"
    )

    bounds = summarize_bound_scores(records)
    print(
        f"[analyze] bounds: scored={bounds['n_scored']} "
        f"always={bounds['always_holds']} tightest={bounds['tightest_surviving']}"
    )

    tightness_payload = None
    if not args.skip_tightness:
        skip = {(r["k"], r["b"]) for r in records if r.get("status") == "ok"}
        for extra in args.out_dir.glob("results_tightness_*.jsonl"):
            skip |= _done_keys(extra)
        pending = tightness_cells(k_max=args.k_max, bases=(2, 3), skip=skip)
        tight_jsonl = args.out_dir / f"results_tightness_{stamp}.jsonl"
        print(f"[analyze] tightness pending={len(pending)} k_max={args.k_max} -> {tight_jsonl}")
        new_recs = _run_pool(pending, tight_jsonl, args) if pending else []
        combined = _existing_for_bases(records, (2, 3), args.k_max)
        seen_kb = {(r["k"], r["b"]) for r in combined}
        extra_recs = list(new_recs)
        for extra in args.out_dir.glob("results_tightness_*.jsonl"):
            extra_recs.extend(load_jsonl(extra))
        for rec in extra_recs:
            if rec.get("status") != "ok":
                continue
            key = (rec["k"], rec["b"])
            if key in seen_kb or rec.get("b") not in (2, 3) or int(rec["k"]) > args.k_max:
                continue
            combined.append(rec)
            seen_kb.add(key)
        exact = [r for r in combined if r.get("delta") == 0]
        exact.sort(key=lambda r: (r["b"], r["k"]))
        tightness_payload = {
            "k_max": args.k_max,
            "n_new": len(new_recs),
            "n_pairs": len(combined),
            "jsonl": tight_jsonl.name if pending else None,
            "exact": [{"k": r["k"], "b": r["b"], "C": r.get("num_attractors")} for r in exact],
            "exact_k_b2": [r["k"] for r in exact if r["b"] == 2],
            "exact_k_b3": [r["k"] for r in exact if r["b"] == 3],
            "max_k_exact": max((r["k"] for r in exact), default=None),
        }
        print(
            f"[analyze] tightness exact={len(exact)}/{len(combined)} "
            f"max_k={tightness_payload['max_k_exact']}"
        )

    existing_e = [r for r in records if r.get("orbit_bands")]
    deep_payload = {
        "prior_e_cells": [
            {
                "k": r.get("k"),
                "b": r.get("b"),
                "M": r.get("M"),
                "delta": r.get("delta"),
                "bounded": (r.get("orbit_bands") or {}).get("bounded_by_two_plus_tail"),
                "plausible": ((r.get("predecessors") or {}).get("fit") or {}).get("plausible"),
            }
            for r in existing_e
        ],
        "records": [],
    }
    if not args.skip_deep:
        skip = {(r["k"], r["b"]) for r in records if r.get("orbit_bands")}
        deep_cells = [
            GridCell(k=k, b=b, strata=("E",), reason="large-M extras 10.3/10.4")
            for k, b in DEFAULT_DEEP
            if (k, b) not in skip
        ]
        deep_jsonl = args.out_dir / f"results_deep_{stamp}.jsonl"
        print(f"[analyze] deep pending={len(deep_cells)} -> {deep_jsonl}")
        deep_recs = _run_pool(deep_cells, deep_jsonl, args) if deep_cells else []
        deep_payload["jsonl"] = deep_jsonl.name if deep_cells else None
        deep_payload["records"] = deep_recs

    # Drop bulky per-modulus rows from the JSON summary except highlights + counts.
    intra_out = dict(intra)
    intra_out["moduli"] = intra["highlight_moduli"]
    intra_out["n_moduli_listed"] = len(intra["highlight_moduli"])

    payload = {
        "generated_at": stamp,
        "gmpy2": HAVE_GMPY2,
        "source_jsonl": str(source.relative_to(REPO_ROOT)) if source.is_relative_to(REPO_ROOT) else str(source),
        "intra": intra_out,
        "intra_full_moduli": intra["moduli"],
        "bounds": bounds,
        "tightness": tightness_payload,
        "deep": deep_payload,
    }
    report_path = args.out_dir / f"report_followup_{stamp}.md"
    json_path = args.out_dir / f"summary_followup_{stamp}.json"
    latest_report = args.out_dir / "report_followup_latest.md"
    latest_json = args.out_dir / "summary_followup_latest.json"
    # Keep the JSON summary lean: moduli table is useful, drop deep attractor lists.
    json_payload = dict(payload)
    if deep_payload:
        json_payload["deep"] = {
            "jsonl": deep_payload.get("jsonl"),
            "prior_e_cells": deep_payload.get("prior_e_cells") or [],
            "records": [
                {
                    "k": r.get("k"),
                    "b": r.get("b"),
                    "M": r.get("M"),
                    "delta": r.get("delta"),
                    "status": r.get("status"),
                    "orbit_window": r.get("orbit_window"),
                    "orbit_bands": {
                        "bounded_by_two_plus_tail": (r.get("orbit_bands") or {}).get(
                            "bounded_by_two_plus_tail"
                        ),
                        "max_tail_on_M": (r.get("orbit_bands") or {}).get("max_tail_on_M"),
                        "L_global_max": (r.get("orbit_bands") or {}).get("L_global_max"),
                    }
                    if r.get("orbit_bands")
                    else None,
                    "predecessors": {
                        "max_degree": (r.get("predecessors") or {}).get("max_degree"),
                        "fit": (r.get("predecessors") or {}).get("fit"),
                    }
                    if r.get("predecessors")
                    else None,
                }
                for r in deep_payload.get("records") or []
            ],
        }
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    _write_report(report_path, payload)
    latest_report.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[analyze] report {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
