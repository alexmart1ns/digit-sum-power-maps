"""One mining record per (k, b) cell."""

from __future__ import annotations

from typing import Any

from dspm.analysis import analyze_pair
from dspm.core import contraction_bound, estimate_pow_digits
from dspm.dynamics import build_system

from .bounds import bound_candidates
from .excess import excess_identity_holds, local_excess, pair_features
from .fourier import compare_split_models
from .grid import GridCell
from .orbit import max_orbit_in_window, sample_orbit_by_digits
from .predecessors import predecessor_report

__all__ = ["mine_pair"]


def mine_pair(
    cell: GridCell,
    max_M: int = 2_000_000,
    max_pow_digits: int = 200_000,
    samples_orbit: int = 80,
    samples_split: int = 2500,
    power_law_synth: int = 0,
) -> dict[str, Any]:
    """Exhaustive pair analysis plus the extras the cell's strata asked for."""
    rec = analyze_pair(
        cell.k, cell.b, max_M=max_M, max_pow_digits=max_pow_digits, deep=True
    )
    rec["strata"] = list(cell.strata)
    rec["grid_reason"] = cell.reason
    rec.update(pair_features(cell.k, cell.b))

    if rec.get("status") != "ok":
        return rec

    M = rec.get("M") or contraction_bound(cell.k, cell.b)
    if estimate_pow_digits(cell.k, cell.b, M) > max_pow_digits:
        rec["status"] = "skipped_large_pow"
        return rec

    system = build_system(cell.k, cell.b, M=M)
    rows = local_excess(system)
    rec["local_excess"] = rows
    rec["delta_local_sum"] = sum(r["delta_local"] for r in rows)
    rec["excess_identity_ok"] = excess_identity_holds(system, rec.get("cyc_modular"))
    rec["n_signatures_split"] = sum(1 for r in rows if r["delta_local"] > 0)
    rec["max_digit_layers"] = max((r["n_digit_layers"] for r in rows), default=0)

    extras = set(cell.strata)
    if "E" in extras:
        rec["orbit_window"] = max_orbit_in_window(system)
        Ds = [d for d in (3, 6, 10, 16) if cell.b ** (d - 1) >= 1]
        rec["orbit_bands"] = sample_orbit_by_digits(
            system, Ds, samples_per_band=samples_orbit, seed=cell.k * 1000 + cell.b
        )
        rec["predecessors"] = predecessor_report(system, n_synth=power_law_synth)
        rec["bounds"] = bound_candidates(system)

    if "F" in extras:
        rec["split_models"] = compare_split_models(
            cell.k,
            cell.b,
            digit_lengths=(6, 10, 14) if max_M <= 50_000 else (8, 16, 24),
            samples_per_band=samples_split,
            seed=cell.k + cell.b,
        )

    return rec
