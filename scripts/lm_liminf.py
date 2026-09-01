#!/usr/bin/env python3
"""liminf/limsup analysis of Psi_j(V) from local_mean output.

Reads data/split/local_mean_*_latest.json (or --input). Writes only to
data/qclass/split/lm_liminf_*.

Example
-------
    python scripts/lm_liminf.py
    python scripts/lm_liminf.py --input data/split/local_mean_latest.json
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "qclass" / "split"
DEFAULT_INPUT = REPO_ROOT / "data" / "split" / "local_mean_latest.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _nearest_index(scales: list[int], target: int) -> int:
    return min(range(len(scales)), key=lambda i: abs(scales[i] - target))


def analyze(payload: dict) -> dict:
    scales: list[int] = payload["scales"]
    curves: dict[str, list[float]] = payload["curves"]
    names = sorted(curves.keys())
    out: dict = {
        "k": payload.get("k"),
        "b": payload.get("b"),
        "signature": payload.get("signature"),
        "v_min": payload.get("v_min"),
        "v_max": payload.get("v_max"),
        "source": "local_mean",
    }

    global_stats = {}
    for name in names:
        ys = curves[name]
        global_stats[name] = {
            "liminf": min(ys),
            "limsup": max(ys),
            "range": max(ys) - min(ys),
            "mean": sum(ys) / len(ys),
        }
    out["global"] = global_stats

    # Powers of b (decade anchors)
    b = int(payload.get("b", 10))
    decade_rows = []
    for n in range(2, int(math.log10(scales[-1])) + 2):
        target = b**n
        if target < scales[0] or target > scales[-1]:
            continue
        j = _nearest_index(scales, target)
        row = {"n": n, "V_target": target, "V_used": scales[j], "frac_log": payload.get("frac_log", [None])[j]}
        for name in names:
            row[name] = curves[name][j]
        decade_rows.append(row)
    out["decade_anchors"] = decade_rows

    if len(decade_rows) >= 2:
        gaps = []
        for i in range(len(decade_rows) - 1):
            a, b_row = decade_rows[i], decade_rows[i + 1]
            gap = {k: b_row[k] - a[k] for k in names if isinstance(a.get(k), (int, float))}
            gap["n_from"] = a["n"]
            gap["n_to"] = b_row["n"]
            gaps.append(gap)
        out["decade_deltas"] = gaps

    # liminf/limsup along subsequence V = b^n only
    subseq = {}
    for name in names:
        vals = [row[name] for row in decade_rows if name in row]
        if vals:
            subseq[name] = {
                "liminf": min(vals),
                "limsup": max(vals),
                "range": max(vals) - min(vals),
                "values": vals,
            }
    out["subsequence_b_powers"] = subseq

    # LM-pilot criterion: liminf < limsup on full range?
    out["lm_pilot_evidence"] = {
        name: global_stats[name]["range"] > 0.05 for name in names
    }
    out["verdict"] = (
        "suggests_non_convergence"
        if all(out["lm_pilot_evidence"].values())
        else "inconclusive"
    )
    out["note"] = (
        "Range > 0.05 on Psi_j supports LM but does not prove lim inf != lim sup. "
        "Subsequence b^n analysis refines decade-collapse test."
    )
    return out


def write_md(result: dict) -> str:
    lines = [
        "# LM liminf/limsup analysis",
        "",
        f"Source: local_mean  k={result.get('k')} b={result.get('b')}  "
        f"V in [{result.get('v_min')}, {result.get('v_max')}]",
        "",
        "## Global (all scales)",
        "",
        "| attractor | liminf | limsup | range | mean |",
        "|-----------|--------|--------|-------|------|",
    ]
    for name, st in result.get("global", {}).items():
        lines.append(
            f"| {name} | {st['liminf']:.4f} | {st['limsup']:.4f} | "
            f"{st['range']:.4f} | {st['mean']:.4f} |"
        )
    lines.extend(["", "## Subsequence V ≈ b^n", ""])
    for name, st in result.get("subsequence_b_powers", {}).items():
        lines.append(
            f"- **{name}**: liminf={st['liminf']:.4f}, limsup={st['limsup']:.4f}, "
            f"range={st['range']:.4f}"
        )
    lines.extend(["", "## Decade anchors", "", "| n | V | " + " | ".join(result.get("global", {})) + " |"])
    for row in result.get("decade_anchors", []):
        cols = " | ".join(f"{row.get(n, '—'):.4f}" if isinstance(row.get(n), float) else str(row.get(n, '—')) for n in result.get("global", {}))
        lines.append(f"| {row['n']} | {row['V_used']} | {cols} |")
    lines.extend([
        "",
        f"**Verdict:** {result.get('verdict')}",
        "",
        result.get("note", ""),
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = ap.parse_args()
    if not args.input.exists():
        print(f"missing {args.input}")
        return 1

    payload = _load(args.input)
    result = analyze(payload)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2)
    (OUT_DIR / f"lm_liminf_{stamp}.json").write_text(text, encoding="utf-8")
    (OUT_DIR / "lm_liminf_latest.json").write_text(text, encoding="utf-8")
    md = write_md(result)
    (OUT_DIR / f"lm_liminf_{stamp}.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "lm_liminf_latest.md").write_text(md, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'lm_liminf_latest.md'}")
    print(f"verdict: {result['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
