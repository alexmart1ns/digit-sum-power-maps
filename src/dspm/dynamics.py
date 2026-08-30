"""The physical dynamics of f_{k,b} on its finite trapping region [1, M].

Everything downstream (attractor counts, basins, residue signatures, the split
measurements) is built on `FiniteSystem`, which is the exhaustive functional
graph of f_{k,b} restricted to [1, M] with M from `core.contraction_bound`.
"""

from __future__ import annotations

from array import array
from collections.abc import Sequence
from dataclasses import dataclass

from .core import contraction_bound, f_kb
from .modular import functional_graph_cycles

__all__ = ["FiniteSystem", "build_system"]


def _int_array(size: int, fill: int = 0) -> array:
    a = array("i", bytes(4 * size))
    if fill:
        for i in range(size):
            a[i] = fill
    return a


@dataclass
class FiniteSystem:
    """Exhaustive dynamics of f_{k,b} on [1, M].

    Attributes
    ----------
    attractors
        Each attractor as a sorted tuple of its members.
    label
        ``label[n]`` is the index of the attractor that n reaches, for
        1 <= n <= M. Index 0 of the array is unused.
    basin_sizes
        Number of n in [1, M] draining to each attractor.
    tail_depth
        ``tail_depth[n]`` is the number of steps from n to its attractor.
    """

    k: int
    b: int
    M: int
    attractors: tuple[tuple[int, ...], ...]
    label: Sequence[int]
    basin_sizes: tuple[int, ...]
    tail_depth: Sequence[int]
    successor: Sequence[int]

    @property
    def m(self) -> int:
        return self.b - 1

    @property
    def count(self) -> int:
        """|C(k,b)|, the number of attractors."""
        return len(self.attractors)

    def signature(self, index: int) -> frozenset[int]:
        """The residue signature sigma(A) of Definition 2.6."""
        m = self.m
        if m < 1:
            return frozenset({0})
        return frozenset(x % m for x in self.attractors[index])

    @property
    def signatures(self) -> tuple[frozenset[int], ...]:
        return tuple(self.signature(i) for i in range(self.count))

    def in_degrees(self) -> list[int]:
        """Branching of the predecessor forest inside [1, M]."""
        indeg = [0] * (self.M + 1)
        for n in range(1, self.M + 1):
            indeg[self.successor[n]] += 1
        return indeg

    def attractor_of(self, n: int) -> int:
        """Index of the attractor reached by n, for any n >= 1.

        For n > M the orbit is advanced until it enters the trapping region;
        by construction of M that happens after finitely many steps.
        """
        if n < 1:
            raise ValueError("n must be >= 1")
        while n > self.M:
            n = f_kb(n, self.k, self.b)
        return self.label[n]

    def basin_by_signature(self) -> dict[frozenset[int], int]:
        """Aggregate basin size per residue signature, within [1, M]."""
        out: dict[frozenset[int], int] = {}
        for i in range(self.count):
            sig = self.signature(i)
            out[sig] = out.get(sig, 0) + self.basin_sizes[i]
        return out

    def attractors_sharing_signature(self) -> dict[frozenset[int], list[int]]:
        """Signature -> list of attractor indices carrying it.

        Signatures with more than one attractor are exactly the ones where the
        intra-signature split question of section 7 is non-trivial.
        """
        out: dict[frozenset[int], list[int]] = {}
        for i in range(self.count):
            out.setdefault(self.signature(i), []).append(i)
        return out


def build_system(k: int, b: int, M: int | None = None) -> FiniteSystem:
    """Build the exhaustive finite system for (k, b).

    Passing ``M`` overrides the computed contraction bound; it must still be
    large enough to contain every attractor.
    """
    if M is None:
        M = contraction_bound(k, b)

    nxt = _int_array(M + 1)
    for n in range(1, M + 1):
        v = f_kb(n, k, b)
        while v > M:  # defensive: M is forward invariant, so this should not run
            v = f_kb(v, k, b)
        nxt[n] = v

    # Vertex 0 is not part of the dynamics; give it a self-loop and drop the
    # resulting spurious cycle afterwards.
    graph = [0] + [nxt[n] for n in range(1, M + 1)]
    cycles = [c for c in functional_graph_cycles(graph) if 0 not in c]

    label = _int_array(M + 1, fill=-1)
    for i, cycle in enumerate(cycles):
        for x in cycle:
            label[x] = i
    for start in range(1, M + 1):
        if label[start] >= 0:
            continue
        path: list[int] = []
        x = start
        while label[x] < 0:
            path.append(x)
            x = nxt[x]
        target = label[x]
        for y in path:
            label[y] = target

    depth = _int_array(M + 1, fill=-1)
    for cycle in cycles:
        for x in cycle:
            depth[x] = 0
    for start in range(1, M + 1):
        if depth[start] >= 0:
            continue
        path = []
        x = start
        while depth[x] < 0:
            path.append(x)
            x = nxt[x]
        d = depth[x]
        for y in reversed(path):
            d += 1
            depth[y] = d

    sizes = [0] * len(cycles)
    for n in range(1, M + 1):
        sizes[label[n]] += 1

    return FiniteSystem(
        k=k,
        b=b,
        M=M,
        attractors=tuple(tuple(sorted(c)) for c in cycles),
        label=label,
        basin_sizes=tuple(sizes),
        tail_depth=depth,
        successor=nxt,
    )
