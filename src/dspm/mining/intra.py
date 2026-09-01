"""Intra-modulus slices of local excess (Problems 10.1 and 10.7).

Δ = Σ δ_i is already an identity. What remains is *where* the split lives:
digit layers, k parity, and modular cycle length, **inside a fixed m = b−1**.
Pooling distinct moduli reintroduces the section-9 parity confound.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

__all__ = ["analyze_intra_modulus", "load_jsonl"]


def load_jsonl(path) -> list[dict[str, Any]]:
    import json
    from pathlib import Path

    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _mean(xs: list[float]) -> float | None:
    return round(sum(xs) / len(xs), 6) if xs else None


def _ranks(values: list[float]) -> list[float]:
    n = len(values)
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = 0.5 * (i + j) + 1.0
        for t in range(i, j + 1):
            ranks[order[t]] = avg
        i = j + 1
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 5 or n != len(ys):
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0.0 or dy == 0.0:
        return None
    return round(num / (dx * dy), 6)


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 8 or len(xs) != len(ys):
        return None
    return _pearson(_ranks(xs), _ranks(ys))


def _ok_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in records if r.get("status") == "ok" and r.get("local_excess") is not None]


def analyze_intra_modulus(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Slice δ_i inside each m. Never report a pooled correlation as a finding."""
    ok = _ok_records(records)
    by_m: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for rec in ok:
        m = rec.get("m")
        if m is None:
            m = rec["b"] - 1
        by_m[int(m)].append(rec)

    moduli = []
    same_layer_splits = 0
    multi_layer_splits = 0
    n_rho_layers_pos = 0
    n_rho_layers = 0
    n_odd_gt_even = 0
    n_parity_compared = 0

    for m in sorted(by_m):
        group = by_m[m]
        deltas = [float(r.get("delta") or 0) for r in group]
        layers = [float(r.get("max_digit_layers") or 0) for r in group]
        k_odd = [int(r.get("k_odd") or 0) for r in group]
        delta_odd = [d for d, o in zip(deltas, k_odd) if o]
        delta_even = [d for d, o in zip(deltas, k_odd) if not o]

        loc_delta: list[float] = []
        loc_layers: list[float] = []
        loc_mod_len: list[float] = []
        loc_fixed: list[float] = []
        n_split_same = 0
        n_split_multi = 0
        n_unsplit = 0
        by_mod_len: dict[int, list[float]] = defaultdict(list)

        for rec in group:
            for row in rec.get("local_excess") or []:
                dloc = float(row.get("delta_local") or 0)
                nlay = int(row.get("n_digit_layers") or 0)
                sig = row.get("signature") or []
                mod_len = len(sig)
                phys = row.get("cycle_lengths") or []
                loc_delta.append(dloc)
                loc_layers.append(float(nlay))
                loc_mod_len.append(float(mod_len))
                loc_fixed.append(1.0 if phys and all(c == 1 for c in phys) else 0.0)
                by_mod_len[mod_len].append(dloc)
                if dloc > 0 and nlay <= 1:
                    n_split_same += 1
                elif dloc > 0:
                    n_split_multi += 1
                else:
                    n_unsplit += 1

        rho_pair = _spearman(deltas, layers)
        rho_local = _spearman(loc_delta, loc_layers)
        rho_modlen = _spearman(loc_delta, loc_mod_len)
        mean_odd = _mean(delta_odd)
        mean_even = _mean(delta_even)
        if rho_local is not None:
            n_rho_layers += 1
            if rho_local > 0:
                n_rho_layers_pos += 1
        if mean_odd is not None and mean_even is not None:
            n_parity_compared += 1
            if mean_odd > mean_even:
                n_odd_gt_even += 1

        same_layer_splits += n_split_same
        multi_layer_splits += n_split_multi

        moduli.append(
            {
                "m": m,
                "b": m + 1,
                "n_pairs": len(group),
                "n_signatures": len(loc_delta),
                "mean_delta": _mean(deltas),
                "mean_delta_k_odd": mean_odd,
                "mean_delta_k_even": mean_even,
                "spearman_delta_vs_max_layers": rho_pair,
                "spearman_delta_local_vs_layers": rho_local,
                "spearman_delta_local_vs_mod_cycle_len": rho_modlen,
                "split_same_layer": n_split_same,
                "split_multi_layer": n_split_multi,
                "unsplit": n_unsplit,
                "mean_delta_local_fixed_points": _mean(
                    [d for d, f in zip(loc_delta, loc_fixed) if f]
                ),
                "mean_delta_local_longer_cycles": _mean(
                    [d for d, f in zip(loc_delta, loc_fixed) if not f]
                ),
                "mean_delta_local_by_mod_cycle_len": {
                    str(L): _mean(vs) for L, vs in sorted(by_mod_len.items())
                },
            }
        )

    # Highlight a few moduli the paper already talks about; still intra-m.
    highlight_ms = [m for m in (1, 2, 9, 15, 31, 79) if m in by_m]

    return {
        "n_ok": len(ok),
        "n_moduli": len(by_m),
        "same_layer_splits": same_layer_splits,
        "multi_layer_splits": multi_layer_splits,
        "moduli_with_layer_spearman": n_rho_layers,
        "moduli_layer_spearman_positive": n_rho_layers_pos,
        "moduli_mean_delta_odd_gt_even": n_odd_gt_even,
        "moduli_parity_compared": n_parity_compared,
        "highlight_moduli": [row for row in moduli if row["m"] in highlight_ms],
        "moduli": moduli,
        "note": (
            "Correlations are computed inside each m=b-1 separately. "
            "Do not pool rows across moduli. Same-layer splits (delta_local>0 "
            "and n_digit_layers=1) are the obstruction to 'layers cause excess'."
        ),
    }
