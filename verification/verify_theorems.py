#!/usr/bin/env python3
"""Independent re-verification of the paper's theorems.

Deliberately self-contained: this file imports nothing from ``dspm`` and
reimplements the digit sum, the trapping region, the functional graphs and the
modular structure from scratch. If a bug in the main package made a theorem
appear to hold, this file would not share it.

Checks
------
1. Lemma 3.1   f_{k,b}(n) = n^k mod (b-1) for a large range of n, k, b.
2. Theorem 4.1 |C(k,b)| >= Cyc(phi_{k,b-1}), exhaustively.
3. Lemma 5.1   every attractor's residue signature is a full modular cycle.
4. Prop 5.2    exact integer identity: the physical basin mass of a signature
               equals the count of integers in the window whose residue lies in
               the corresponding modular basin.
5. Theorem 5.3 |q_i(M) - p_i| <= (b-1)/M, and the sharper min(|R_i|, b-2)/M.
6. Prop 6.1    the periodic-point closed form, against brute force.
7. Worked examples for (2,10) and (3,10).

Usage
-----
    python verification/verify_theorems.py
    python verification/verify_theorems.py --b-max 11 --k-max 20
"""

from __future__ import annotations

import argparse
from collections import defaultdict

# ---------------------------------------------------------------- primitives


def digit_sum(n: int, b: int) -> int:
    total = 0
    while n:
        total += n % b
        n //= b
    return total


def f(n: int, k: int, b: int) -> int:
    return digit_sum(n**k, b)


def num_digits(n: int, b: int) -> int:
    count = 0
    while n:
        count += 1
        n //= b
    return max(count, 1)


def factorize(n: int) -> dict:
    fac: dict = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            fac[d] = fac.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        fac[n] = fac.get(n, 0) + 1
    return fac


def cycles_of(nxt: list) -> list:
    state = [0] * len(nxt)
    out = []
    for start in range(len(nxt)):
        if state[start]:
            continue
        path, x = [], start
        while state[x] == 0:
            state[x] = 1
            path.append(x)
            x = nxt[x]
        if state[x] == 1:
            out.append(path[path.index(x):])
        for y in path:
            state[y] = 2
    return out


def drain(nxt: list, cycles: list, size: int, start_at: int = 0) -> list:
    owner = [-1] * size
    for i, cycle in enumerate(cycles):
        for x in cycle:
            owner[x] = i
    for s in range(start_at, size):
        if owner[s] >= 0:
            continue
        path, x = [], s
        while owner[x] < 0:
            path.append(x)
            x = nxt[x]
        for y in path:
            owner[y] = owner[x]
    return owner


def modular(k: int, m: int):
    """cycles, owner (residue -> cycle index), basin sizes."""
    if m <= 1:
        return [[0]], [0], [1]
    nxt = [pow(x, k, m) for x in range(m)]
    cycles = cycles_of(nxt)
    owner = drain(nxt, cycles, m)
    sizes = [0] * len(cycles)
    for r in range(m):
        sizes[owner[r]] += 1
    return cycles, owner, sizes


def trapping_bound(k: int, b: int) -> int:
    """Largest M with M <= (b-1)*digits_b(M^k); [1,M] is then forward invariant."""
    M = b
    while True:
        cap = (b - 1) * num_digits(M**k, b)
        if cap <= M:
            return M
        M = cap


def physical(k: int, b: int):
    """attractors, label (n -> attractor index) on [1, M], basin sizes."""
    M = trapping_bound(k, b)
    nxt = [0] * (M + 1)
    for n in range(1, M + 1):
        y = f(n, k, b)
        while y > M:
            y = f(y, k, b)
        nxt[n] = y
    cycles = [c for c in cycles_of(nxt) if 0 not in c]
    label = drain(nxt, cycles, M + 1, start_at=1)
    sizes = [0] * len(cycles)
    for n in range(1, M + 1):
        sizes[label[n]] += 1
    return M, cycles, label, sizes


def attractor_of(n: int, k: int, b: int, M: int, label: list) -> int:
    while n > M:
        n = f(n, k, b)
    return label[n]


# ---------------------------------------------------------------- checks


def check_lemma_31(b_max: int, k_max: int, n_max: int) -> tuple:
    total = bad = 0
    for b in range(3, b_max + 1):
        m = b - 1
        for k in range(1, k_max + 1):
            for n in range(1, n_max):
                total += 1
                if f(n, k, b) % m != pow(n, k, m):
                    bad += 1
    return total, bad


def check_dynamics(b_max: int, k_max: int) -> dict:
    result = {
        "pairs": 0,
        "lower_bound_violations": [],
        "exact_matches": 0,
        "signature_violations": [],
        "mass_identity_violations": [],
        "bound_violations": [],
        "sharp_bound_violations": [],
        "worst_bound_ratio": 0.0,
        "worst_sharp_ratio": 0.0,
    }
    for b in range(2, b_max + 1):
        m = b - 1
        for k in range(1, k_max + 1):
            M, cycles, label, sizes = physical(k, b)
            mcycles, mowner, msizes = modular(k, m)
            result["pairs"] += 1

            # Theorem 4.1
            if len(cycles) < len(mcycles):
                result["lower_bound_violations"].append((k, b))
            if len(cycles) == len(mcycles):
                result["exact_matches"] += 1

            # Lemma 5.1: each attractor's signature is a whole modular cycle
            for cycle in cycles:
                if m <= 1:
                    continue
                sig = frozenset(x % m for x in cycle)
                owners = {mowner[x % m] for x in cycle}
                if len(owners) != 1 or sig != frozenset(mcycles[owners.pop()]):
                    result["signature_violations"].append((k, b, sorted(cycle)))

            if m <= 1:
                continue

            # Proposition 5.2 as an exact integer identity, and Theorem 5.3
            for window in (M, 1000, 3001):
                phys = defaultdict(int)
                for n in range(1, window + 1):
                    idx = attractor_of(n, k, b, M, label)
                    phys[frozenset(x % m for x in cycles[idx])] += 1
                resid = defaultdict(int)
                for n in range(1, window + 1):
                    resid[frozenset(mcycles[mowner[n % m]])] += 1
                if dict(phys) != dict(resid):
                    result["mass_identity_violations"].append((k, b, window))

                for i, cycle in enumerate(mcycles):
                    p_i = msizes[i] / m
                    q_i = resid[frozenset(cycle)] / window
                    err = abs(q_i - p_i)
                    loose = (b - 1) / window
                    sharp = min(msizes[i], m - 1) / window
                    if err > loose + 1e-12:
                        result["bound_violations"].append((k, b, window, i))
                    if err > sharp + 1e-12:
                        result["sharp_bound_violations"].append((k, b, window, i))
                    if loose:
                        result["worst_bound_ratio"] = max(result["worst_bound_ratio"], err / loose)
                    if sharp:
                        result["worst_sharp_ratio"] = max(result["worst_sharp_ratio"], err / sharp)
    return result


def kappa(N: int, k: int) -> int:
    r = N
    for p in factorize(k):
        while r % p == 0:
            r //= p
    return r


def check_prop_61(m_max: int, k_max: int) -> tuple:
    total = bad = 0
    for m in range(2, m_max):
        for k in range(2, k_max + 1):
            total += 1
            brute = sum(len(c) for c in cycles_of([pow(x, k, m) for x in range(m)]))
            formula = 1
            for p, e in factorize(m).items():
                formula *= 1 + kappa((p - 1) * p ** (e - 1), k)
            if brute != formula:
                bad += 1
    return total, bad


def worked_examples() -> list:
    lines = []
    for k, b in ((2, 10), (3, 10)):
        M, cycles, label, sizes = physical(k, b)
        m = b - 1
        window = 3000
        counts = defaultdict(int)
        for n in range(1, window + 1):
            counts[attractor_of(n, k, b, M, label)] += 1
        parts = []
        for i, cycle in enumerate(cycles):
            parts.append(
                f"{sorted(cycle)} sig={sorted({x % m for x in cycle})} "
                f"dens={counts[i] / window:.4f}"
            )
        lines.append(f"  (k,b)=({k},{b})  M={M}  |C|={len(cycles)}")
        for part in sorted(parts):
            lines.append(f"      {part}")
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--b-max", type=int, default=11)
    ap.add_argument("--k-max", type=int, default=15)
    ap.add_argument("--n-max", type=int, default=300)
    ap.add_argument("--m-max", type=int, default=200)
    args = ap.parse_args(argv)

    failures = 0

    print("=" * 74)
    print("  Independent verification (no dspm imports)")
    print("=" * 74)

    total, bad = check_lemma_31(args.b_max, args.k_max, args.n_max)
    failures += bad
    print(f"  Lemma 3.1  modular invariance ......... {total} tests, {bad} failures")

    dyn = check_dynamics(args.b_max, args.k_max)
    for key, label in (
        ("lower_bound_violations", "Theorem 4.1  |C| >= Cyc"),
        ("signature_violations", "Lemma 5.1    signature = cycle"),
        ("mass_identity_violations", "Prop 5.2     integer identity"),
        ("bound_violations", "Theorem 5.3  (b-1)/M bound"),
        ("sharp_bound_violations", "             sharp min(|R_i|,b-2)/M"),
    ):
        n = len(dyn[key])
        failures += n
        print(f"  {label} ... {dyn['pairs']} pairs, {n} violations")
    print(
        f"               exact |C|=Cyc in {dyn['exact_matches']}/{dyn['pairs']} pairs"
    )
    print(
        f"               worst error/bound ratio: loose {dyn['worst_bound_ratio']:.3f}, "
        f"sharp {dyn['worst_sharp_ratio']:.3f}"
    )
    print(
        "               the loose bound is never approached, so a 100% pass rate\n"
        "               against it is weak evidence; the integer identity is the test"
    )

    total, bad = check_prop_61(args.m_max, 40)
    failures += bad
    print(f"  Prop 6.1   periodic-point formula ..... {total} pairs, {bad} mismatches")

    print("\n  Worked examples")
    for line in worked_examples():
        print(line)

    print("=" * 74)
    print(f"  TOTAL FAILURES: {failures}")
    print("=" * 74)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
