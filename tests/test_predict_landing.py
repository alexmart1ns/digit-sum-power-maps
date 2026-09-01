"""Tests for first_landing API (Lemma D / G4)."""

from dspm.dynamics import build_system
from dspm.predict import attractor_labels_upto, first_landing


def test_first_landing_matches_labels_for_pilot():
    system = build_system(3, 10)
    labels = attractor_labels_upto(10_000, system)
    for v in range(1, 10_001):
        w, steps = first_landing(v, system)
        assert 1 <= w <= system.M
        assert labels[v] == system.label[w]
        if v <= system.M:
            assert steps == 0 and w == v


def test_first_landing_steps_nonnegative():
    system = build_system(3, 10)
    for v in [100, 1000, 10_000, 1_000_000]:
        w, steps = first_landing(v, system)
        assert steps >= 0
        assert 1 <= w <= system.M
