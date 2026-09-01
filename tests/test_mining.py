"""Tests for the section-10 mining package."""

from __future__ import annotations

import pytest

from dspm.dynamics import build_system
from dspm.mining.bounds import bound_candidates, bound_candidates_from_record, residue_occupancy
from dspm.mining.excess import excess_identity_holds, local_excess
from dspm.mining.fourier import compare_split_models, independent_digit_sum_pmf
from dspm.mining.grid import GridSpec, smart_grid
from dspm.mining.orbit import orbit_length, sample_orbit_by_digits
from dspm.mining.predecessors import fit_power_law, predecessor_report
from dspm.mining.record import mine_pair
from dspm.modular import cycle_count


def test_smart_grid_quick_is_stratified_and_unique():
    cells = smart_grid(mode="quick")
    assert cells
    seen = set()
    strata = set()
    for cell in cells:
        assert (cell.k, cell.b) not in seen
        seen.add((cell.k, cell.b))
        assert cell.k >= 1 and cell.b >= 2
        strata.update(cell.strata)
    assert {"A", "B", "E", "F"} <= strata
    assert any(c.k == 3 and c.b == 10 and "F" in c.strata for c in cells)


def test_smart_grid_respects_M_budget():
    spec = GridSpec(k_tight=80, k_structure=10, max_M=200, structure_moduli=(2, 6))
    cells = smart_grid(mode="quick", spec=spec)
    from dspm.core import contraction_bound

    for cell in cells:
        M = contraction_bound(cell.k, cell.b, hard_cap=spec.max_M)
        assert M <= spec.max_M
        if spec.max_work:
            assert cell.k * M <= spec.max_work


def test_local_excess_identity_example_4_4():
    system = build_system(3, 10)
    rows = local_excess(system)
    assert sum(r["delta_local"] for r in rows) == 4
    assert excess_identity_holds(system, cycle_count(3, 9))
    zero = next(r for r in rows if r["signature"] == [0])
    assert zero["a_i"] >= 2
    assert 18 in zero["attractor_mins"]
    assert 27 in zero["attractor_mins"]


@pytest.mark.parametrize("k, b", [(2, 10), (3, 10), (4, 10), (5, 8), (1, 2)])
def test_local_excess_identity_small_grid(k, b):
    system = build_system(k, b)
    assert excess_identity_holds(system, cycle_count(k, b - 1))


def test_orbit_length_large_n_is_short():
    system = build_system(3, 10)
    n = 10**12
    length = orbit_length(n, system)
    max_tail = max(int(system.tail_depth[i]) for i in range(1, system.M + 1))
    assert length <= 2 + max_tail


def test_orbit_bands_respect_two_plus_tail():
    system = build_system(3, 10)
    report = sample_orbit_by_digits(system, [4, 8, 12], samples_per_band=40, seed=1)
    assert report["bounded_by_two_plus_tail"]


def test_predecessor_histogram_and_fit_shape():
    system = build_system(3, 10)
    report = predecessor_report(system)
    assert sum(report["histogram"].values()) == system.M
    assert report["max_degree"] >= 1
    assert "alpha" in report["fit"]


def test_power_law_fit_on_synthetic_zipf_has_finite_alpha():
    # Approximate discrete Zipf via inverse-CDF samples.
    rng_vals = [int(1 * (1 - (i + 0.5) / 400) ** (-1 / 1.5)) for i in range(400)]
    rng_vals = [max(1, min(v, 80)) for v in rng_vals]
    fit = fit_power_law(rng_vals, n_synth=0)
    assert fit["alpha"] is not None
    assert 1.0 < fit["alpha"] < 8.0


def test_Nstar_upper_bounds_count_but_Cyc_need_not():
    system = build_system(3, 10)
    rec = bound_candidates(system)
    assert rec["holds_as_upper"]["N_star"]
    assert rec["C"] == 7
    assert rec["candidates"]["Cyc"] == 3
    assert rec["holds_as_upper"]["Cyc"] is False


def test_independent_digit_pmf_is_a_probability():
    for L, b in ((1, 10), (4, 10), (8, 2), (5, 3)):
        pmf = independent_digit_sum_pmf(L, b)
        assert abs(sum(pmf) - 1.0) < 1e-9
        assert pmf[0] > 0
        assert len(pmf) == (b - 1) * L + 1


def test_fourier_model_runs_on_split_system():
    rec = compare_split_models(3, 10, digit_lengths=(6, 10), samples_per_band=800, seed=0)
    assert rec.get("status") != "no_split"
    assert rec["mae_gaussian"] >= 0
    assert rec["mae_fourier"] >= 0
    assert rec["noise_floor"] > 0


def test_residue_occupancy_matches_scan():
    for M, m in ((20, 9), (57, 9), (100, 1), (15, 2), (1, 5)):
        for r in range(m):
            brute = sum(1 for n in range(1, M + 1) if n % m == r)
            assert residue_occupancy(M, m, r) == brute


def test_bound_candidates_from_record_matches_system():
    from dspm.mining.grid import GridCell
    from dspm.mining.record import mine_pair

    system = build_system(3, 10)
    rec = mine_pair(GridCell(k=3, b=10, strata=("A",), reason="test"))
    from_sys = bound_candidates(system)
    from_rec = bound_candidates_from_record(rec)
    assert from_sys["candidates"] == from_rec["candidates"]
    assert from_sys["holds_as_upper"] == from_rec["holds_as_upper"]


def test_intra_modulus_keeps_moduli_separate():
    from dspm.mining.intra import analyze_intra_modulus

    records = [
        {
            "status": "ok",
            "k": 3,
            "b": 10,
            "m": 9,
            "k_odd": 1,
            "delta": 4,
            "max_digit_layers": 2,
            "local_excess": [
                {"delta_local": 3, "n_digit_layers": 2, "signature": [0], "digit_lengths": [1, 2], "cycle_lengths": [1, 1]},
                {"delta_local": 1, "n_digit_layers": 1, "signature": [9], "digit_lengths": [2], "cycle_lengths": [1]},
            ],
        },
        {
            "status": "ok",
            "k": 2,
            "b": 2,
            "m": 1,
            "k_odd": 0,
            "delta": 0,
            "max_digit_layers": 1,
            "local_excess": [
                {"delta_local": 0, "n_digit_layers": 1, "signature": [0], "digit_lengths": [1], "cycle_lengths": [1]},
            ],
        },
    ]
    out = analyze_intra_modulus(records)
    assert out["n_moduli"] == 2
    ms = {row["m"] for row in out["moduli"]}
    assert ms == {1, 9}
    nine = next(row for row in out["moduli"] if row["m"] == 9)
    assert nine["split_multi_layer"] == 1
    assert nine["split_same_layer"] == 1


def test_tightness_cells_skip_and_range():
    from dspm.mining.tightness import tightness_cells

    cells = tightness_cells(k_max=4, bases=(2, 3), skip={(1, 2), (2, 3)})
    keys = {(c.k, c.b) for c in cells}
    assert (1, 2) not in keys
    assert (2, 3) not in keys
    assert (4, 2) in keys
    assert (1, 3) in keys
    assert len(cells) == 6


def test_mine_pair_attaches_local_excess():
    from dspm.mining.grid import GridCell

    rec = mine_pair(GridCell(k=3, b=10, strata=("A",), reason="test"))
    assert rec["status"] == "ok"
    assert rec["excess_identity_ok"] is True
    assert rec["delta_local_sum"] == rec["delta"] == 4
