"""Empirical upper-bound candidates for |C(k,b)| (Problem 10.5).

|C| ≤ N* is true and useless: N* bounds attractor *values*, not their count.
This module records slack against sharper candidates so a surviving inequality
can be promoted later. No candidate is claimed as a theorem.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from dspm.core import num_digits
from dspm.dynamics import FiniteSystem
from dspm.modular import periodic_point_count_formula, structure

__all__ = [
    "bound_candidates",
    "bound_candidates_from_record",
    "residue_occupancy",
    "score_bound_candidates",
    "summarize_bound_scores",
]


def residue_occupancy(M: int, m: int, r: int) -> int:
    """How many n in [1, M] satisfy n ≡ r (mod m)."""
    if M < 1:
        return 0
    if m <= 1:
        return M if r % max(m, 1) == 0 else 0
    r = r % m
    if r == 0:
        return M // m
    if r > M:
        return 0
    return (M - r) // m + 1


def _cycle_window(M: int, m: int, residues: Sequence[int]) -> int:
    return sum(residue_occupancy(M, m, r) for r in residues)


def score_bound_candidates(
    k: int,
    b: int,
    C: int,
    M: int,
    digit_layer_values: Sequence[int] | None = None,
    cyc: int | None = None,
    per: int | None = None,
) -> dict[str, Any]:
    """Score cheap upper-bound candidates without rebuilding the system."""
    m = max(b - 1, 1)
    mod = structure(k, m)
    if cyc is None:
        cyc = mod.cycle_count
    if per is None:
        per = periodic_point_count_formula(k, m)
    layers = sorted(set(int(x) for x in (digit_layer_values or []) if x))
    n_layers = max(len(layers), 1)
    cap_sum_window = sum(_cycle_window(M, m, cycle) for cycle in mod.cycles)
    candidates = {
        "N_star": M,
        "Cyc": cyc,
        "Per": per,
        "digit_layers": n_layers,
        "Cyc_times_layers": cyc * n_layers,
        "sum_signature_windows": cap_sum_window,
    }
    slack = {name: bound - C for name, bound in candidates.items()}
    holds = {name: bound >= C for name, bound in candidates.items()}
    return {
        "C": C,
        "candidates": candidates,
        "slack": slack,
        "holds_as_upper": holds,
        "digit_layer_values": layers,
        "note": "N* is Lemma 3.2; Cyc is Theorem 4.1 (lower). Only holds_as_upper matters here.",
    }


def bound_candidates(system: FiniteSystem) -> dict[str, Any]:
    digit_layers = sorted({num_digits(members[0], system.b) for members in system.attractors})
    return score_bound_candidates(
        system.k,
        system.b,
        C=system.count,
        M=system.M,
        digit_layer_values=digit_layers,
    )


def bound_candidates_from_record(rec: dict[str, Any]) -> dict[str, Any]:
    layers: set[int] = set()
    for row in rec.get("local_excess") or []:
        layers.update(int(x) for x in (row.get("digit_lengths") or []))
    return score_bound_candidates(
        int(rec["k"]),
        int(rec["b"]),
        C=int(rec["num_attractors"]),
        M=int(rec["M"]),
        digit_layer_values=sorted(layers),
        cyc=rec.get("cyc_modular"),
    )


def summarize_bound_scores(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Hold rates and mean slack for every candidate, on already-mined records."""
    ok = [
        r
        for r in records
        if r.get("status") == "ok" and r.get("num_attractors") is not None and r.get("M")
    ]
    names: list[str] = []
    holds: dict[str, int] = {}
    slack_sum: dict[str, float] = {}
    slack_min: dict[str, int] = {}
    min_slack_at: dict[str, dict[str, Any]] = {}
    n_scored = 0
    worst_fail: dict[str, dict[str, Any]] = {}

    for rec in ok:
        scored = rec.get("bounds") if isinstance(rec.get("bounds"), dict) else None
        if not scored or "holds_as_upper" not in scored:
            scored = bound_candidates_from_record(rec)
        n_scored += 1
        if not names:
            names = list(scored["candidates"])
        for name in scored["candidates"]:
            holds.setdefault(name, 0)
            slack_sum.setdefault(name, 0.0)
            if scored["holds_as_upper"][name]:
                holds[name] += 1
            sl = int(scored["slack"][name])
            slack_sum[name] += sl
            if name not in slack_min or sl < slack_min[name]:
                slack_min[name] = sl
                min_slack_at[name] = {
                    "k": rec["k"],
                    "b": rec["b"],
                    "C": scored["C"],
                    "M": rec.get("M"),
                    "bound": scored["candidates"][name],
                    "slack": sl,
                }
            if not scored["holds_as_upper"][name]:
                cur = worst_fail.get(name)
                if cur is None or sl < cur["slack"]:
                    worst_fail[name] = {
                        "k": rec["k"],
                        "b": rec["b"],
                        "C": scored["C"],
                        "bound": scored["candidates"][name],
                        "slack": sl,
                    }

    always = [n for n in names if holds.get(n, 0) == n_scored]
    never = [n for n in names if holds.get(n, 0) == 0]
    surviving = []
    for n in always:
        surviving.append(
            {
                "name": n,
                "mean_slack": round(slack_sum[n] / n_scored, 4) if n_scored else None,
                "min_slack": slack_min.get(n),
                "min_slack_at": min_slack_at.get(n),
            }
        )
    surviving.sort(key=lambda row: (row["mean_slack"] is None, row["mean_slack"] or 0))

    return {
        "n_scored": n_scored,
        "hold_count": holds,
        "hold_rate": {
            n: round(holds[n] / n_scored, 6) if n_scored else None for n in names
        },
        "mean_slack": {
            n: round(slack_sum[n] / n_scored, 4) if n_scored else None for n in names
        },
        "min_slack": slack_min,
        "min_slack_at": min_slack_at,
        "always_holds": always,
        "never_holds": never,
        "tightest_surviving": surviving[0] if surviving else None,
        "surviving_ranked": surviving,
        "worst_counterexample": worst_fail,
        "note": (
            "A surviving upper bound must hold on every scored pair. "
            "N* always holds and is useless (slack ~ M). Cyc is a lower bound."
        ),
    }
