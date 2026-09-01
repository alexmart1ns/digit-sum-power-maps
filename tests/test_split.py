"""Tests for the split measurement and the prediction model.

Sample counts are kept small so the suite stays fast; the assertions are chosen
to be robust at that noise level. The full-resolution measurement lives in
``verification/audit/audit_02_split_convergence.py``.
"""

from __future__ import annotations

from dspm.dynamics import build_system
from dspm.modular import structure
from dspm.predict import attractor_labels_upto, digit_count_mixture, predict_split
from dspm.split import oscillation_report, split_curves


def test_signature_sums_stay_at_the_modular_weight():
    """Theorem 5.3 holds band by band, whatever the split does inside."""
    curves = split_curves(3, 10, [4, 8, 12, 16], samples_per_band=4000, seed=1)
    for sums in curves.signature_sums().values():
        for value in sums:
            assert abs(value - 1 / 3) < 0.03


def test_signature_zero_splits_broadly():
    """{18} and {27} share signature {0} and neither monopolises the mass."""
    system = build_system(3, 10)
    index = {members: i for i, members in enumerate(system.attractors)}
    curves = split_curves(
        3, 10, [16, 25, 49, 64], samples_per_band=4000, seed=2, system=system
    )
    for members in ((18,), (27,)):
        values = curves.curves[index[members]]
        assert max(values) > 0.05
    # ...and they move in opposite directions.
    a = curves.curves[index[(18,)]]
    b = curves.curves[index[(27,)]]
    assert (max(a) - min(a)) > 0.05
    assert (max(b) - min(b)) > 0.05


def test_oscillation_report_shape():
    curves = split_curves(3, 10, [4, 8, 12], samples_per_band=2000, seed=3)
    report = oscillation_report(curves)
    assert len(report) == len(curves.labels)
    for row in report:
        assert row["min"] <= row["max"]
        assert row["amplitude"] == row["max"] - row["min"]


def test_digit_count_mixture_is_a_probability_vector():
    for D in (4, 10, 30):
        for k in (2, 3, 5):
            weights = digit_count_mixture(D, k, 10)
            assert abs(sum(weights.values()) - 1.0) < 1e-9
            assert all(w >= 0 for w in weights.values())


def test_predict_split_sums_to_the_modular_weight():
    system = build_system(3, 10)
    mod = structure(3, 9)
    signature = mod.signature_of_residue(0)
    weight = mod.weights[mod.owner[0]]
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    labels = attractor_labels_upto(int(4.5 * 3 * 40) + 400, system)

    for D in (8, 20, 40):
        predicted = predict_split(D, system, signature, labels, targets, weight)
        assert abs(sum(predicted.values()) - weight) < 0.02


def test_gaussian_label_sweep_pilot_stays_oscillatory():
    """Conjecture 10.6' diagnostic: the Gaussian window does not flatten at modest D.

    No sampling of n. If amplitude already collapsed here, the D=300 sweep
    would be pointless.
    """
    system = build_system(3, 10)
    mod = structure(3, 9)
    signature = mod.signature_of_residue(0)
    weight = mod.weights[mod.owner[0]]
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    names = {i: str(list(system.attractors[i])) for i in targets}
    assert "[18]" in names.values() and "[27]" in names.values()
    d_max = 80
    L = 3 * d_max
    ceiling = int(4.5 * L + 8 * (L * 8.25) ** 0.5) + 50
    labels = attractor_labels_upto(ceiling, system)
    Ds = list(range(10, d_max + 1, 5))
    curves = {i: [] for i in targets}
    for D in Ds:
        pred = predict_split(D, system, signature, labels, targets, weight)
        assert abs(sum(pred.values()) - weight) < 0.02
        for i in targets:
            curves[i].append(pred[i])
    by_name = {names[i]: curves[i] for i in targets}
    a, c = by_name["[18]"], by_name["[27]"]
    assert max(a) - min(a) > 0.05
    assert max(c) - min(c) > 0.05
    ma, mc = sum(a) / len(a), sum(c) / len(c)
    num = sum((x - ma) * (y - mc) for x, y in zip(a, c))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mc) ** 2 for y in c)) ** 0.5
    assert den > 0
    assert num / den < -0.5


def test_v_space_psi_on_signature_zero_sums_to_one():
    """Hypothesis LM diagnostic: feeding residues of {0} label only {18} and {27}."""
    system = build_system(3, 10)
    mod = structure(3, 9)
    signature = mod.signature_of_residue(0)
    targets = [i for i in range(system.count) if system.signature(i) == signature]
    names = {i: str(list(system.attractors[i])) for i in targets}
    assert set(names.values()) == {"[18]", "[27]"}
    labels = attractor_labels_upto(8000, system)
    feeding = [r for r in range(9) if frozenset(mod.cycles[mod.owner[r]]) == signature]
    V = 4000
    h = int(V**0.5)
    lo, hi = V - h, V + h
    counts = {i: 0 for i in targets}
    n = 0
    for r in feeding:
        v = lo + ((r - lo) % 9)
        while v <= hi:
            counts[labels[v]] += 1
            n += 1
            v += 9
    assert n > 20
    shares = {i: counts[i] / n for i in targets}
    assert abs(sum(shares.values()) - 1.0) < 1e-12
    assert max(shares.values()) < 0.95
