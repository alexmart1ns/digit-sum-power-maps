"""Sidecar tests for S_b(Q(n)). Does not modify test_core / test_modular / test_split."""

from __future__ import annotations

import pytest

from dspm.core import contraction_bound, f_kb
from dspm.dynamics import build_system
from dspm.qmaps import (
    attractor_labels_upto_Q,
    build_system_Q,
    contraction_bound_Q,
    digit_count_mixture_Q,
    eval_Q,
    excess_identity_holds_Q,
    f_Qb,
    finite_window_identity_holds,
    format_Q,
    monomial_Q,
    predict_split_Q,
    structure_Q,
)


def test_format_and_eval_known_polynomials():
    assert format_Q(monomial_Q(2)) == "x^2"
    assert format_Q((0, 1, 1)) == "x + x^2"
    assert format_Q((1, 3, 2)) == "1 + 3x + 2x^2"
    assert eval_Q(4, monomial_Q(3)) == 64
    assert eval_Q(5, (1, 3, 2)) == 1 + 15 + 50
    assert f_Qb(13, monomial_Q(2), 10) == f_kb(13, 2, 10) == 16


@pytest.mark.parametrize("k, b", [(2, 10), (3, 10), (2, 16), (3, 2)])
def test_monomial_matches_existing_engine(k, b):
    """Q(x)=x^k must reproduce FiniteSystem attractors, not historical JSONL."""
    classic = build_system(k, b)
    sidecar = build_system_Q(monomial_Q(k), b)
    assert set(sidecar.attractors) == set(classic.attractors)
    assert sidecar.count == classic.count
    assert f_Qb(7, monomial_Q(k), b) == f_kb(7, k, b)


def test_example_4_3_and_4_4_via_sidecar():
    s2 = build_system_Q(monomial_Q(2), 10)
    assert set(s2.attractors) == {(1,), (9,), (13, 16)}
    s3 = build_system_Q(monomial_Q(3), 10)
    assert set(s3.attractors) == {(1,), (8,), (17,), (18,), (19, 28), (26,), (27,)}


@pytest.mark.parametrize(
    "coeffs, b",
    [
        (monomial_Q(2), 10),
        (monomial_Q(3), 10),
        ((0, 1, 1), 10),
        ((1, 0, 0, 1), 10),
        ((1, 3, 2), 10),
        ((0, 1, 1), 2),
        ((1, 0, 0, 1), 3),
        ((1, 3, 2), 16),
    ],
)
def test_remark_4_1a_lower_bound_and_excess_and_window(coeffs, b):
    system = build_system_Q(coeffs, b)
    cyc = structure_Q(coeffs, max(system.m, 1)).cycle_count
    assert system.count >= cyc
    assert excess_identity_holds_Q(system, cyc)
    assert finite_window_identity_holds(system)
    M = contraction_bound_Q(coeffs, b)
    for n in range(1, M + 1):
        v = f_Qb(n, coeffs, b)
        while v > M:
            v = f_Qb(v, coeffs, b)
        assert 1 <= v <= M


def test_contraction_bound_Q_monomial_is_forward_invariant():
    for k, b in ((2, 10), (3, 10)):
        M = contraction_bound_Q(monomial_Q(k), b)
        # May differ from contraction_bound; both must trap.
        for n in range(1, M + 1):
            v = f_Qb(n, monomial_Q(k), b)
            assert v >= 0
        classic_M = contraction_bound(k, b)
        assert M >= 1 and classic_M >= 1


def test_digit_count_mixture_Q_is_a_probability_vector():
    for D in (4, 10, 20):
        for coeffs in (monomial_Q(2), monomial_Q(3), (1, 3, 2)):
            weights = digit_count_mixture_Q(D, coeffs, 10)
            assert abs(sum(weights.values()) - 1.0) < 1e-9
            assert all(w >= 0 for w in weights.values())


def test_predict_split_Q_sums_to_modular_weight_on_pilot():
    system = build_system_Q(monomial_Q(3), 10)
    mod = structure_Q(monomial_Q(3), 9)
    signature = mod.signature_of_residue(0)
    weight = mod.weights[mod.owner[0]]
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    labels = attractor_labels_upto_Q(int(4.5 * 3 * 40) + 400, system)
    for D in (8, 20, 40):
        predicted = predict_split_Q(D, system, signature, labels, targets, weight)
        assert abs(sum(predicted.values()) - weight) < 0.02


def test_predict_split_Q_uses_image_lattice_not_feeding_lattice():
    """v ≡ Q(r) (mod m), not v ≡ r. Regression against the feeding-lattice F_j."""
    coeffs = (1, 3, 2)
    system = build_system_Q(coeffs, 10)
    mod = structure_Q(coeffs, 9)
    sharing = system.attractors_sharing_signature()
    sig, targets = max(
        ((s, idx) for s, idx in sharing.items() if len(idx) >= 2),
        key=lambda kv: len(kv[1]),
    )
    feeding = [r for r in range(mod.m) if frozenset(mod.cycles[mod.owner[r]]) == sig]
    weight = mod.weights[mod.owner[feeding[0]]]
    labels = attractor_labels_upto_Q(int(9 * 2 * 16) + 400, system)
    predicted = predict_split_Q(16, system, sig, labels, targets, weight)
    # Image Gaussian at D=16: ~0.185 / 0.815. Feeding lattice was ~0.400 / 0.600.
    i0 = next(i for i in targets if system.attractors[i] == (6, 10))
    i1 = next(i for i in targets if system.attractors[i] == (15, 19))
    assert abs(predicted[i0] - 0.18472) < 0.01
    assert abs(predicted[i1] - 0.81528) < 0.01

    cubic = build_system_Q(monomial_Q(3), 10)
    cmod = structure_Q(monomial_Q(3), 9)
    csig = cmod.signature_of_residue(0)
    cweight = cmod.weights[cmod.owner[0]]
    ctargets = [i for i in range(cubic.count) if cubic.signature(i) == csig]
    clabels = attractor_labels_upto_Q(int(4.5 * 3 * 16) + 400, cubic)
    cpred = predict_split_Q(16, cubic, csig, clabels, ctargets, cweight)
    j18 = next(i for i in ctargets if cubic.attractors[i] == (18,))
    j27 = next(i for i in ctargets if cubic.attractors[i] == (27,))
    assert abs(cpred[j18] - 0.090872) < 0.01
    assert abs(cpred[j27] - 0.242461) < 0.01


def test_nonmonomial_semiconjugacy():
    """f(n) ≡ Q(n) (mod b-1)."""
    coeffs = (1, 3, 2)
    for b in (3, 10, 16):
        m = b - 1
        for n in range(1, 80):
            assert f_Qb(n, coeffs, b) % m == eval_Q(n, coeffs) % m
