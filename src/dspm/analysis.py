"""Per-pair analysis record used by the parameter sweep.

`analyze_pair` never raises: a pair that is too expensive or that fails is
recorded with a status string so that a long sweep degrades gracefully instead
of dying on one bad cell.
"""

from __future__ import annotations

import time
from typing import Any

from .core import contraction_bound, estimate_pow_digits
from .dynamics import build_system
from .modular import cycle_count, structure

__all__ = ["analyze_pair"]


def analyze_pair(
    k: int,
    b: int,
    max_M: int = 2_000_000,
    max_pow_digits: int = 200_000,
    deep: bool = True,
) -> dict[str, Any]:
    """Analyse one (k, b) pair exhaustively.

    Returns a JSON-serialisable record with the modular lower bound, the exact
    attractor count, the bifurcation excess, and -- when ``deep`` -- per
    attractor basin and signature data.
    """
    started = time.perf_counter()
    m = b - 1
    rec: dict[str, Any] = {"k": k, "b": b, "m": m}

    try:
        cyc = cycle_count(k, m)
        rec["cyc_modular"] = cyc

        M = contraction_bound(k, b)
        rec["M"] = M
        if M > max_M:
            rec["status"] = "skipped_large_M"
            rec["elapsed_s"] = round(time.perf_counter() - started, 4)
            return rec

        estimated = estimate_pow_digits(k, b, M)
        if estimated > max_pow_digits:
            rec["status"] = "skipped_large_pow"
            rec["est_pow_digits"] = int(estimated)
            rec["elapsed_s"] = round(time.perf_counter() - started, 4)
            return rec

        system = build_system(k, b, M=M)
        rec["num_attractors"] = system.count
        rec["delta"] = system.count - cyc
        rec["lower_bound_ok"] = system.count >= cyc

        if deep:
            rec.update(_deep_record(system, m))

        rec["status"] = "ok"

    except MemoryError:
        rec["status"] = "error_memory"
    except Exception as exc:  # noqa: BLE001 - a sweep must not die on one cell
        rec["status"] = "error"
        rec["error"] = f"{type(exc).__name__}: {exc}"

    rec["elapsed_s"] = round(time.perf_counter() - started, 4)
    return rec


def _deep_record(system, m: int) -> dict[str, Any]:
    M = system.M
    entries = []
    max_tail_overall = 0
    for i, members in enumerate(system.attractors):
        tail = max(system.tail_depth[n] for n in range(1, M + 1) if system.label[n] == i)
        max_tail_overall = max(max_tail_overall, tail)
        entries.append(
            {
                "cycle": list(members[:32]),
                "length": len(members),
                "min_value": members[0],
                "residues_mod_m": sorted(system.signature(i)),
                "basin_size": system.basin_sizes[i],
                "basin_density": round(system.basin_sizes[i] / M, 6),
                "max_tail_depth": tail,
            }
        )
    entries.sort(key=lambda e: e["basin_size"], reverse=True)

    indeg = system.in_degrees()

    anchors: dict[str, int] = {}
    for entry in entries:
        key = ",".join(map(str, entry["residues_mod_m"]))
        anchors[key] = anchors.get(key, 0) + 1

    # Aggregate mass per signature versus the exact modular weight: this is the
    # sharp integer form of Proposition 5.2 restricted to the window [1, M].
    mod = structure(system.k, m)
    signature_check = []
    physical = system.basin_by_signature()
    for i, cycle in enumerate(mod.cycles):
        sig = frozenset(cycle)
        residues_in_window = sum(
            1 for n in range(1, M + 1) if mod.owner[n % m] == i
        ) if m >= 1 else M
        signature_check.append(
            {
                "signature": sorted(sig),
                "modular_weight": round(mod.weights[i], 8),
                "physical_mass_in_window": physical.get(sig, 0),
                "residue_mass_in_window": residues_in_window,
                "exact_match": physical.get(sig, 0) == residues_in_window,
            }
        )

    return {
        "attractors": entries,
        "max_tail_depth_overall": max_tail_overall,
        "branching_max": max(indeg) if M >= 1 else 0,
        "modular_anchor_counts": anchors,
        "distinct_modular_anchors": len(anchors),
        "signature_mass_check": signature_check,
        "signature_mass_all_exact": all(s["exact_match"] for s in signature_check),
    }
