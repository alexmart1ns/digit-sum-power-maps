"""Tests for the modular power map and its two closed forms."""

from __future__ import annotations

import pytest

from dspm.modular import (
    cycle_count,
    cycle_count_formula,
    cycle_count_formula_folded,
    periodic_point_count,
    periodic_point_count_formula,
    structure,
)
from dspm.numtheory import kappa, multiplicative_order


def test_example_4_3():
    """The classic (k,b) = (2,10) modular skeleton."""
    mod = structure(2, 9)
    assert mod.cycle_count == 3
    assert {frozenset(c) for c in mod.cycles} == {
        frozenset({0}),
        frozenset({1}),
        frozenset({4, 7}),
    }
    weights = dict(zip((frozenset(c) for c in mod.cycles), mod.basin_sizes, strict=True))
    assert weights[frozenset({0})] == 3  # residues 0, 3, 6
    assert weights[frozenset({1})] == 2  # residues 1, 8
    assert weights[frozenset({4, 7})] == 4  # residues 2, 4, 5, 7


def test_basin_partition_is_a_partition():
    for m in range(1, 60):
        for k in range(1, 12):
            mod = structure(k, m)
            assert sum(mod.basin_sizes) == m
            assert abs(sum(mod.weights) - 1.0) < 1e-12


@pytest.mark.parametrize("m_max, k_max", [(120, 30)])
def test_periodic_point_formula(m_max, k_max):
    """Proposition 6.1."""
    for m in range(1, m_max):
        for k in range(2, k_max + 1):
            assert periodic_point_count(k, m) == periodic_point_count_formula(k, m)


@pytest.mark.parametrize("m_max, k_max", [(120, 30)])
def test_cycle_count_formula(m_max, k_max):
    """The replacement for the withdrawn Corollary 6.2."""
    for m in range(1, m_max):
        for k in range(1, k_max + 1):
            assert cycle_count(k, m) == cycle_count_formula(k, m)


@pytest.mark.parametrize("m_max, k_max", [(80, 20)])
def test_cycle_count_formula_folded_matches_naive_and_graph(m_max, k_max):
    """Problem 10.8: the CRT fold equals the expanded product and the graph."""
    for m in range(1, m_max):
        for k in range(1, k_max + 1):
            folded = cycle_count_formula_folded(k, m)
            assert folded == cycle_count_formula(k, m)
            assert folded == cycle_count(k, m)


def test_cycle_count_formula_folded_high_omega():
    """Fold stays exact on a highly composite modulus where tuples would bite."""
    m = 210  # 2*3*5*7
    for k in (1, 2, 3, 4, 5, 8, 16, 15, 30):
        assert cycle_count_formula_folded(k, m) == cycle_count(k, m)


def test_periodic_count_covers_non_cyclic_unit_group():
    """(Z/2^e)^* is not cyclic for e >= 3; the Hall-subgroup argument must hold."""
    for e in range(3, 9):
        m = 2**e
        for k in range(2, 20):
            assert periodic_point_count(k, m) == periodic_point_count_formula(k, m)


def test_kappa():
    assert kappa(6, 2) == 3
    assert kappa(40, 2) == 5
    assert kappa(10, 3) == 10
    assert kappa(16, 2) == 1


def test_cycle_count_depends_on_k_beyond_its_radical():
    """The counterexamples that refute Corollary 6.2 of the July 2026 draft."""
    assert [cycle_count(k, 41) for k in (2, 4, 8, 16, 32)] == [3, 4, 3, 6, 3]
    assert cycle_count(2, 37) == 4
    assert cycle_count(4, 37) == 6
    # ...while the periodic-point count cannot tell them apart.
    assert len({periodic_point_count(k, 41) for k in (2, 4, 8, 16, 32)}) == 1
    assert periodic_point_count(2, 37) == periodic_point_count(4, 37)


def test_cycle_length_is_the_multiplicative_order():
    """Why Cyc sees k mod d: an element of order d sits on a cycle of ord_d(k)."""
    assert multiplicative_order(2, 5) == 4
    assert multiplicative_order(4, 5) == 2
    assert multiplicative_order(16, 5) == 1
