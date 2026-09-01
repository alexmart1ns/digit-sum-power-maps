"""The modular power map phi_{k,m}(x) = x^k mod m.

This is the algebraic skeleton of f_{k,b}(n) = S_b(n^k): by casting out nines
the residue dynamics of f_{k,b} mod (b-1) is exactly phi_{k,b-1}.

Two families of routines live here.

*Graph routines* (`cycles`, `structure`, `cycle_count`, `periodic_point_count`)
build the functional graph explicitly and are the ground truth.

*Closed forms* (`periodic_point_count_formula`, `cycle_count_formula`) compute
the same quantities without building the graph:

    #Per(k,m)  = prod_{p^e || m} ( 1 + kappa_k(phi(p^e)) )                 [Prop 6.1]
    Cyc(k,m)   = sum over tuples of local cycles of  prod(l_i) / lcm(l_i)  [Prop 6.3]

The second formula matters because a widely made shortcut is wrong: #Per is a
function of the *radical* of k, but Cyc is not. Cycle lengths are multiplicative
orders ord_d(k), which see k modulo d, not just the primes dividing k. See
`docs/AUDIT.md` for the counterexamples (e.g. m = 41 gives Cyc = 3, 4, 6 for
k = 2, 4, 16 while #Per is 6 throughout).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import product
from math import gcd, lcm

from .numtheory import (
    divisors,
    euler_phi,
    factorize,
    kappa,
    mobius,
    multiplicative_order,
)

__all__ = [
    "ModularStructure",
    "functional_graph_cycles",
    "cycles",
    "structure",
    "cycle_count",
    "periodic_point_count",
    "periodic_point_count_formula",
    "cycle_count_formula",
    "cycle_count_formula_folded",
    "local_cycle_type",
]


# --------------------------------------------------------------------------
# Generic functional-graph machinery
# --------------------------------------------------------------------------
def functional_graph_cycles(nxt: Sequence[int]) -> list[list[int]]:
    """All cycles of the functional graph i -> nxt[i] on {0, ..., len(nxt)-1}.

    Each cycle is returned in traversal order starting from its first-discovered
    vertex. Linear time: every vertex is pushed on a path at most once.
    """
    n = len(nxt)
    state = bytearray(n)  # 0 = unvisited, 1 = on current path, 2 = settled
    out: list[list[int]] = []
    for start in range(n):
        if state[start]:
            continue
        path: list[int] = []
        x = start
        while state[x] == 0:
            state[x] = 1
            path.append(x)
            x = nxt[x]
        if state[x] == 1:  # closed a new cycle on the current path
            out.append(path[path.index(x):])
        for y in path:
            state[y] = 2
    return out


@dataclass(frozen=True)
class ModularStructure:
    """Complete description of the functional graph of phi_{k,m}.

    Attributes
    ----------
    k, m
        Parameters of the map.
    cycles
        The cycles gamma_1, ..., gamma_c, each as a list of residues.
    owner
        ``owner[r]`` is the index of the cycle that residue ``r`` flows into,
        so ``R_i = {r : owner[r] == i}`` is the modular basin of Definition 2.5.
    basin_sizes
        ``|R_i|`` for each cycle.
    """

    k: int
    m: int
    cycles: tuple[tuple[int, ...], ...]
    owner: tuple[int, ...]
    basin_sizes: tuple[int, ...]

    @property
    def cycle_count(self) -> int:
        return len(self.cycles)

    @property
    def weights(self) -> tuple[float, ...]:
        """The modular weights p_i = |R_i| / m of Definition 2.5."""
        return tuple(s / self.m for s in self.basin_sizes)

    @property
    def signatures(self) -> tuple[frozenset, ...]:
        """Residue signatures gamma_i, as sets, in cycle order."""
        return tuple(frozenset(c) for c in self.cycles)

    def signature_of_residue(self, r: int) -> frozenset:
        """The signature gamma_i with r in R_i."""
        return frozenset(self.cycles[self.owner[r % self.m]])


def _next_table(k: int, m: int) -> list[int]:
    return [pow(x, k, m) for x in range(m)]


def structure(k: int, m: int) -> ModularStructure:
    """Build the full functional graph of phi_{k,m} and its basin partition."""
    if m <= 1:
        # Z/1Z has a single element with a self-loop.
        return ModularStructure(k=k, m=1, cycles=((0,),), owner=(0,), basin_sizes=(1,))

    nxt = _next_table(k, m)
    cyc = functional_graph_cycles(nxt)

    owner = [-1] * m
    for i, c in enumerate(cyc):
        for x in c:
            owner[x] = i
    # Pull every transient residue back to the cycle it drains into.
    for start in range(m):
        if owner[start] >= 0:
            continue
        path: list[int] = []
        x = start
        while owner[x] < 0:
            path.append(x)
            x = nxt[x]
        target = owner[x]
        for y in path:
            owner[y] = target

    sizes = [0] * len(cyc)
    for r in range(m):
        sizes[owner[r]] += 1

    return ModularStructure(
        k=k,
        m=m,
        cycles=tuple(tuple(c) for c in cyc),
        owner=tuple(owner),
        basin_sizes=tuple(sizes),
    )


def cycles(k: int, m: int) -> list[list[int]]:
    """The cycles of phi_{k,m} as lists of residues."""
    return [list(c) for c in structure(k, m).cycles]


def cycle_count(k: int, m: int) -> int:
    """Cyc(phi_{k,m}): the number of cycles. This is the Theorem 4.1 bound."""
    if m <= 1:
        return 1
    return len(functional_graph_cycles(_next_table(k, m)))


def periodic_point_count(k: int, m: int) -> int:
    """#Per(k,m) by explicit enumeration (ground truth for Proposition 6.1)."""
    if m <= 1:
        return 1
    return sum(len(c) for c in functional_graph_cycles(_next_table(k, m)))


# --------------------------------------------------------------------------
# Closed forms
# --------------------------------------------------------------------------
def periodic_point_count_formula(k: int, m: int) -> int:
    """Proposition 6.1: #Per(k,m) = prod_{p^e || m} (1 + kappa_k(phi(p^e))).

    Valid for k >= 2. For k = 1 every point is periodic and the answer is m.
    """
    if m <= 1:
        return 1
    if k == 1:
        return m
    total = 1
    for p, e in factorize(m).items():
        total *= 1 + kappa(euler_phi(p**e), k)
    return total


def _unit_group_k_prime_part(p: int, e: int, k: int) -> list[int]:
    """Cyclic-factor orders of the subgroup H of (Z/p^e)^* of elements whose
    order is coprime to k.

    (Z/p^e)^* is cyclic for odd p, and for p = 2 it is trivial (e=1), cyclic of
    order 2 (e=2), or Z/2 x Z/2^{e-2} (e>=3). H is the k'-Hall subgroup, which
    for an abelian group is the product of the Sylow q-subgroups over q not
    dividing k -- so it is obtained factorwise.
    """
    if p != 2:
        return [kappa((p - 1) * p ** (e - 1), k)]
    if e == 1:
        return [1]
    if e == 2:
        return [kappa(2, k)]
    return [kappa(2, k), kappa(2 ** (e - 2), k)]


def _order_distribution(factor_orders: Sequence[int]) -> dict[int, int]:
    """Map d -> number of elements of order exactly d in the abelian group
    prod_i Z/factor_orders[i].

    Uses #{x : ord(x) | d} = prod_i gcd(d, n_i) and Moebius inversion over the
    divisor lattice of the group exponent.
    """
    exponent = 1
    for n in factor_orders:
        exponent = lcm(exponent, n)

    def count_dividing(d: int) -> int:
        total = 1
        for n in factor_orders:
            total *= gcd(d, n)
        return total

    out: dict[int, int] = {}
    for d in divisors(exponent):
        acc = 0
        for e in divisors(d):
            mu = mobius(d // e)
            if mu:
                acc += mu * count_dividing(e)
        if acc:
            out[d] = acc
    return out


def local_cycle_type(k: int, p: int, e: int) -> list[int]:
    """Multiset of cycle lengths of x -> x^k on the periodic part of Z/p^e Z.

    The periodic set is {0} together with the k'-Hall subgroup H of the unit
    group (a nonzero non-unit is nilpotent under x -> x^k for k >= 2, so it
    drains to 0). An element of H of order d sits on a cycle of length
    ord_d(k), the multiplicative order of k modulo d.
    """
    if k == 1:
        # phi is the identity: every residue is a fixed point.
        return [1] * (p**e)
    lengths: list[int] = [1]  # the fixed point 0
    for d, count in _order_distribution(_unit_group_k_prime_part(p, e, k)).items():
        length = multiplicative_order(k, d) if d > 1 else 1
        lengths.extend([length] * (count // length))
    return lengths


def _local_types(k: int, m: int) -> list[list[int]]:
    return [local_cycle_type(k, p, e) for p, e in factorize(m).items()]


def _cycle_count_from_types_naive(types: Sequence[Sequence[int]]) -> int:
    """Proposition 6.3 as written: sum over tuples of local cycles."""
    total = 0
    for combo in product(*types):
        span = 1
        for length in combo:
            span *= length
        total += span // lcm(*combo)
    return total


def _cycle_count_from_types_folded(types: Sequence[Sequence[int]]) -> int:
    """CRT fold: a pair of cycles of lengths l1, l2 yields gcd(l1, l2) cycles.

    Cost is in the product of the numbers of *distinct* lengths, not in the
    expanded cycle lists. This is the polynomial (in log m and ω(m), times
    local divisor-counts) evaluation asked by Problem 10.8.
    """
    if not types:
        return 0
    acc: Counter[int] = Counter(types[0])
    for local in types[1:]:
        other = Counter(local)
        nxt: Counter[int] = Counter()
        for l1, n1 in acc.items():
            for l2, n2 in other.items():
                nxt[lcm(l1, l2)] += n1 * n2 * gcd(l1, l2)
        acc = nxt
    return int(sum(acc.values()))


def cycle_count_formula(k: int, m: int) -> int:
    """Cyc(phi_{k,m}) in closed form, without building the graph.

    By the Chinese remainder theorem the periodic set of phi_{k,m} is the
    product of the local periodic sets, and phi acts componentwise. A tuple of
    local cycles of lengths (l_1, ..., l_t) spans prod l_i periodic points that
    split into prod(l_i) / lcm(l_1, ..., l_t) cycles, each of length lcm(l_i).
    Summing over all tuples gives the count.

    Note the dependence on k: it enters through the multiplicative orders
    ord_d(k), which is why Cyc -- unlike #Per -- is *not* a function of the
    radical of k.

    The sum is over expanded local cycle lists; ``cycle_count_formula_folded``
    evaluates the same quantity by folding length-multiplicity maps.
    """
    if m <= 1:
        return 1
    if k == 1:
        return m
    return _cycle_count_from_types_naive(_local_types(k, m))


def cycle_count_formula_folded(k: int, m: int) -> int:
    """Problem 10.8: Cyc(phi_{k,m}) by pairwise CRT fold of cycle types.

    Mathematically identical to ``cycle_count_formula``. A cycle of length
    ``l1`` and a cycle of length ``l2`` produce ``gcd(l1, l2)`` cycles of
    length ``lcm(l1, l2)``; folding components two at a time never enumerates
    t-tuples.
    """
    if m <= 1:
        return 1
    if k == 1:
        return m
    return _cycle_count_from_types_folded(_local_types(k, m))
