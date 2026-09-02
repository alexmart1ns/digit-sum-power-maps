"""The map f_{k,b}(n) = S_b(n^k) and its rigorous trapping region.

`gmpy2` is used when present -- it makes the bignum powers and digit
extraction substantially faster -- but everything here has a pure-Python
fallback and the two paths agree exactly.
"""

from __future__ import annotations

import math
import sys

try:  # pragma: no cover - environment dependent
    import gmpy2
    from gmpy2 import mpz

    HAVE_GMPY2 = True
except Exception:  # pragma: no cover
    gmpy2 = None
    HAVE_GMPY2 = False

    def mpz(x):  # type: ignore[misc]
        return int(x)


# CPython 4.3+ caps int<->str conversion. Nothing here converts through str,
# but third-party code and tracebacks might, so lift the ceiling defensively.
try:
    sys.set_int_max_str_digits(1_000_000_000)
except Exception:  # pragma: no cover
    pass


__all__ = [
    "HAVE_GMPY2",
    "digit_sum",
    "f_kb",
    "iterate",
    "num_digits",
    "contraction_bound",
    "estimate_pow_digits",
]


# For each base b, the largest power b^p that still fits in 62 bits. Summing
# digits chunk-by-chunk turns one huge division chain into few big divisions.
_CHUNK_CACHE: dict[int, tuple[int, int]] = {}


def _chunk_params(b: int) -> tuple[int, int]:
    cached = _CHUNK_CACHE.get(b)
    if cached is not None:
        return cached
    power, value, limit = 1, b, 1 << 62
    while value * b < limit:
        value *= b
        power += 1
    _CHUNK_CACHE[b] = (power, value)
    return power, value


def digit_sum(x: int, b: int) -> int:
    """S_b(x): sum of the base-b digits of x >= 0."""
    if b < 2:
        raise ValueError("base must be >= 2")
    xi = int(x)
    if xi < 0:
        raise ValueError("digit_sum requires x >= 0")
    if xi < b:
        return xi
    _, chunk = _chunk_params(b)
    if HAVE_GMPY2:
        x = mpz(x)
        chunk = mpz(chunk)
    total = 0
    while x:
        x, rest = divmod(x, chunk)
        rest = int(rest)
        while rest:
            total += rest % b
            rest //= b
    return total


def f_kb(n: int, k: int, b: int) -> int:
    """f_{k,b}(n) = S_b(n^k)."""
    power = mpz(n) ** k if HAVE_GMPY2 else n**k
    return digit_sum(power, b)


def iterate(n: int, k: int, b: int, steps: int) -> int:
    """Apply f_{k,b} the given number of times."""
    for _ in range(steps):
        n = f_kb(n, k, b)
    return n


def num_digits(y: int, b: int) -> int:
    """Exact number of base-b digits of y.

    ``gmpy2.num_digits`` is documented as possibly returning one more than the
    true length, so its answer is corrected downwards. Getting this exactly
    right matters: the value feeds `contraction_bound`, and an overestimate
    silently inflates the trapping region.
    """
    if y < 0:
        raise ValueError(f"num_digits requires y >= 0, got {y}")
    if y == 0:
        return 1
    # gmpy2.num_digits only accepts bases in [2, 62].
    if HAVE_GMPY2 and 2 <= b <= 62:
        count = int(gmpy2.num_digits(mpz(y), b))
        if count > 1 and mpz(b) ** (count - 1) > y:
            count -= 1
        return count
    count, y = 0, int(y)
    while y > 0:
        y //= b
        count += 1
    return count


def contraction_bound(k: int, b: int, hard_cap: int = 1 << 40) -> int:
    """A rigorous M with the recurrent set of f_{k,b} inside [1, M].

    Lemma 3.2 gives S_b(n^k) <= (b-1) * digits_b(n^k), and the right-hand side
    grows logarithmically in n while n grows linearly. The fixed point of that
    majorant is therefore a genuine ceiling: for every n <= M we have
    f(n) <= M, so [1, M] is forward invariant and sweeping it finds *all*
    attractors. This is exhaustive, not sampling.
    """
    if k < 1 or b < 2:
        raise ValueError("require k >= 1 and b >= 2")
    x = b
    for _ in range(500):
        estimated = k * math.log(x, b) + 1.0
        nxt = int((b - 1) * estimated) + 1
        if nxt <= x:
            # Near the fixed point, replace the estimate by the exact count.
            exact = (b - 1) * num_digits(pow(x, k), b)
            return min(max(x, exact), hard_cap)
        x = nxt
        if x > hard_cap:
            return hard_cap
    return min(x, hard_cap)


def estimate_pow_digits(k: int, b: int, M: int) -> float:
    """Cheap estimate of the base-b digit count of M^k, for cost guards."""
    if M < 2:
        return 1.0
    return k * math.log(M, b) + 1.0
