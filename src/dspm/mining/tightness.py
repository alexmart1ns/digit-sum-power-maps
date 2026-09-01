"""Complete Δ=0 census for tiny bases (Problem 10.2).

For b=2 and b=3 the trapping window M is O(k log k), so a long k-range is
cheap relative to a rectangle in b. The object is the *list* of exact
matches, not a rate.
"""

from __future__ import annotations

from collections.abc import Iterable

from dspm.mining.grid import GridCell

__all__ = ["tightness_cells"]


def tightness_cells(
    k_max: int = 1500,
    bases: Iterable[int] = (2, 3),
    skip: Iterable[tuple[int, int]] | None = None,
) -> list[GridCell]:
    """Every (k, b) with 1 ≤ k ≤ k_max and b in ``bases``, minus ``skip``."""
    seen = set(skip or ())
    cells = []
    for b in bases:
        if b < 2:
            raise ValueError("bases must be >= 2")
        for k in range(1, k_max + 1):
            if (k, b) in seen:
                continue
            cells.append(
                GridCell(
                    k=k,
                    b=b,
                    strata=("A",),
                    reason=f"tightness census b={b} k<={k_max}",
                )
            )
    return cells
