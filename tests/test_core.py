"""Tests for the map itself and its trapping region."""

from __future__ import annotations

import pytest

from dspm.core import contraction_bound, digit_sum, f_kb, num_digits


@pytest.mark.parametrize(
    "n, b, expected",
    [
        (0, 10, 0),
        (9, 10, 9),
        (10, 10, 1),
        (169, 10, 16),
        (256, 10, 13),
        (0b1011, 2, 3),
        (255, 16, 30),
    ],
)
def test_digit_sum_known_values(n, b, expected):
    assert digit_sum(n, b) == expected


@pytest.mark.parametrize("b", [2, 3, 7, 10, 16, 37])
def test_digit_sum_matches_naive(b):
    def naive(x, base):
        total = 0
        while x:
            total += x % base
            x //= base
        return total

    for n in list(range(200)) + [10**20 + 7, 2**101, 3**77]:
        assert digit_sum(n, b) == naive(n, b)


def test_digit_sum_rejects_bad_input():
    with pytest.raises(ValueError):
        digit_sum(10, 1)
    with pytest.raises(ValueError):
        digit_sum(-1, 10)


def test_casting_out_nines():
    """Lemma 3.1: f_{k,b}(n) = n^k mod (b-1)."""
    for b in range(3, 20):
        m = b - 1
        for k in range(1, 8):
            for n in range(1, 120):
                assert f_kb(n, k, b) % m == pow(n, k, m)


def test_happy_number_contrast():
    """Section 1.1: f_{2,10} is not the happy map."""
    assert f_kb(13, 2, 10) == 16
    assert f_kb(16, 2, 10) == 13


@pytest.mark.parametrize("b", [2, 3, 10, 16])
@pytest.mark.parametrize("k", [1, 2, 3, 7, 20])
def test_contraction_bound_is_forward_invariant(b, k):
    """[1, M] must be closed under f: this is what makes the sweep exhaustive."""
    M = contraction_bound(k, b)
    for n in range(1, M + 1):
        assert f_kb(n, k, b) <= M


@pytest.mark.parametrize("b", [2, 5, 10])
def test_num_digits(b):
    assert num_digits(0, b) == 1
    for n in range(1, 500):
        assert b ** (num_digits(n, b) - 1) <= n < b ** num_digits(n, b)


def test_num_digits_beyond_gmpy2_base_limit():
    """gmpy2.num_digits rejects bases > 62; the fallback must stay exact."""
    b, n = 64, 64**5 + 3
    d = num_digits(n, b)
    assert b ** (d - 1) <= n < b**d
