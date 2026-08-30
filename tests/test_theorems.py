"""Tests of the paper's actual claims, on the exhaustive finite dynamics."""

from __future__ import annotations

from collections import defaultdict

import pytest

from dspm.dynamics import build_system
from dspm.modular import cycle_count, structure

GRID = [(k, b) for b in range(2, 12) for k in range(1, 13)]


def test_example_4_3_attractors():
    system = build_system(2, 10)
    assert system.attractors == ((1,), (13, 16), (9,))
    assert system.count == cycle_count(2, 9) == 3


def test_example_4_4_attractors():
    """(3,10) has seven attractors against a modular lower bound of three."""
    system = build_system(3, 10)
    assert set(system.attractors) == {(1,), (8,), (17,), (18,), (19, 28), (26,), (27,)}
    assert system.count == 7
    assert cycle_count(3, 9) == 3
    assert system.count - cycle_count(3, 9) == 4


@pytest.mark.parametrize("k, b", GRID)
def test_theorem_4_1_lower_bound(k, b):
    """|C(k,b)| >= Cyc(phi_{k,b-1})."""
    system = build_system(k, b)
    assert system.count >= cycle_count(k, b - 1)


@pytest.mark.parametrize("k, b", GRID)
def test_lemma_5_1_signature_is_a_whole_modular_cycle(k, b):
    m = b - 1
    if m <= 1:
        pytest.skip("Z/1Z is degenerate")
    system = build_system(k, b)
    mod = structure(k, m)
    for i in range(system.count):
        residues = system.signature(i)
        owners = {mod.owner[r] for r in residues}
        assert len(owners) == 1
        assert residues == frozenset(mod.cycles[owners.pop()])


@pytest.mark.parametrize("k, b", GRID)
@pytest.mark.parametrize("window", [1000, 3001])
def test_proposition_5_2_exact_integer_identity(k, b, window):
    """The sharp form: physical signature mass == residue-class mass, exactly."""
    m = b - 1
    if m <= 1:
        pytest.skip("Z/1Z is degenerate")
    system = build_system(k, b)
    mod = structure(k, m)

    physical = defaultdict(int)
    for n in range(1, window + 1):
        physical[system.signature(system.attractor_of(n))] += 1

    residue = defaultdict(int)
    for n in range(1, window + 1):
        residue[frozenset(mod.cycles[mod.owner[n % m]])] += 1

    assert dict(physical) == dict(residue)


@pytest.mark.parametrize("k, b", GRID)
def test_theorem_5_3_bounds(k, b):
    """Both the paper's bound and the sharper min(|R_i|, b-2)/M."""
    m = b - 1
    if m <= 1:
        pytest.skip("Z/1Z is degenerate")
    mod = structure(k, m)
    for window in (m, 137, 1000):
        counts = defaultdict(int)
        for n in range(1, window + 1):
            counts[mod.owner[n % m]] += 1
        for i in range(len(mod.cycles)):
            error = abs(counts[i] / window - mod.weights[i])
            assert error <= (b - 1) / window + 1e-12
            assert error <= min(mod.basin_sizes[i], m - 1) / window + 1e-12


def test_example_5_5_the_22_33_44_law():
    """(2,10) basins carry 2/9, 3/9, 4/9 of the integers."""
    system = build_system(2, 10)
    window = 3000
    counts = defaultdict(int)
    for n in range(1, window + 1):
        counts[system.attractors[system.attractor_of(n)]] += 1
    assert abs(counts[(1,)] / window - 2 / 9) < 0.003
    assert abs(counts[(9,)] / window - 3 / 9) < 0.003
    assert abs(counts[(13, 16)] / window - 4 / 9) < 0.003


def test_basins_partition_the_window():
    system = build_system(3, 10)
    assert sum(system.basin_sizes) == system.M
