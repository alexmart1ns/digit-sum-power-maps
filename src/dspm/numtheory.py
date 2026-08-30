"""Elementary number-theoretic helpers.

Pure standard library. Everything here is exact integer arithmetic; no
floating point is used for anything that feeds a mathematical claim.
"""

from __future__ import annotations

from functools import cache
from math import gcd

__all__ = [
    "factorize",
    "divisors",
    "radical",
    "omega",
    "num_divisors",
    "is_prime",
    "v_p",
    "v2",
    "euler_phi",
    "carmichael_lambda",
    "kappa",
    "multiplicative_order",
    "mobius",
]


@cache
def factorize(n: int) -> dict[int, int]:
    """Prime factorization of n >= 1 as {prime: exponent}."""
    if n < 1:
        raise ValueError("factorize requires n >= 1")
    fac: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            fac[d] = fac.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        fac[n] = fac.get(n, 0) + 1
    return fac


def divisors(n: int) -> list[int]:
    """All positive divisors of n, ascending."""
    out = [1]
    for p, e in factorize(n).items():
        out = [d * p**i for d in out for i in range(e + 1)]
    return sorted(out)


def radical(n: int) -> int:
    """Product of the distinct primes dividing n."""
    r = 1
    for p in factorize(n):
        r *= p
    return r


def omega(n: int) -> int:
    """Number of distinct prime factors of n. omega(1) = 0."""
    return 0 if n <= 1 else len(factorize(n))


def num_divisors(n: int) -> int:
    if n < 1:
        return 0
    total = 1
    for e in factorize(n).values():
        total *= e + 1
    return total


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def v_p(n: int, p: int) -> int:
    """p-adic valuation of n."""
    if n == 0:
        raise ValueError("v_p(0) is undefined")
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def v2(n: int) -> int:
    """2-adic valuation; v2(0) = 0 by convention here."""
    if n == 0:
        return 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v


def euler_phi(n: int) -> int:
    if n == 1:
        return 1
    result = n
    for p in factorize(n):
        result = result // p * (p - 1)
    return result


def carmichael_lambda(n: int) -> int:
    """Exponent of the group (Z/nZ)^*."""
    from math import lcm

    if n == 1:
        return 1
    result = 1
    for p, e in factorize(n).items():
        if p == 2:
            local = 1 if e == 1 else (2 if e == 2 else 2 ** (e - 2))
        else:
            local = (p - 1) * p ** (e - 1)
        result = lcm(result, local)
    return result


def kappa(N: int, k: int) -> int:
    """Largest divisor of N coprime to k.

    This is the kappa_k(N) of the periodic-point formula: stripping from N
    every prime that divides k.
    """
    r = N
    for p in factorize(k):
        while r % p == 0:
            r //= p
    return r


def multiplicative_order(a: int, n: int) -> int:
    """Least t >= 1 with a^t = 1 (mod n). Requires gcd(a, n) = 1.

    Returns 1 when n == 1.
    """
    if n == 1:
        return 1
    a %= n
    if gcd(a, n) != 1:
        raise ValueError(f"multiplicative_order requires gcd(a,n)=1, got a={a}, n={n}")
    # The order divides lambda(n); test its divisors in increasing order.
    for d in divisors(carmichael_lambda(n)):
        if pow(a, d, n) == 1:
            return d
    raise AssertionError("unreachable: order must divide lambda(n)")


def mobius(n: int) -> int:
    if n == 1:
        return 1
    mu = 1
    for e in factorize(n).values():
        if e > 1:
            return 0
        mu = -mu
    return mu
