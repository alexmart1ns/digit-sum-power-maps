"""dspm -- iterated digit-sum power maps  f_{k,b}(n) = S_b(n^k).

Reference implementation for the paper *Iterated Digit-Sum Power Maps: A Lower
Bound Theorem, an Exact Basin Density Law, and the Oscillation of
Intra-Signature Basin Splits* (see ``paper/``).

Layout
------
``core``       the map itself, and the rigorous trapping region [1, M]
``numtheory``  elementary integer helpers (exact, no floating point)
``modular``    the modular power map x -> x^k mod m: graph, cycles, closed forms
``dynamics``   exhaustive physical dynamics on [1, M]: attractors and basins
``analysis``   one JSON record per (k, b) pair, used by the sweep
``split``      Monte-Carlo measurement of the intra-signature basin split
``predict``    parameter-free Gaussian-sweep model for the split oscillation
``patterns``   statistics over a sweep dataset

Quick start
-----------
>>> from dspm import build_system, cycle_count
>>> system = build_system(2, 10)
>>> sorted(system.attractors)
[(1,), (9,), (13, 16)]
>>> cycle_count(2, 9)
3
"""

from __future__ import annotations

from .core import HAVE_GMPY2, contraction_bound, digit_sum, f_kb, iterate, num_digits
from .dynamics import FiniteSystem, build_system
from .modular import (
    ModularStructure,
    cycle_count,
    cycle_count_formula,
    cycle_count_formula_folded,
    periodic_point_count,
    periodic_point_count_formula,
    structure,
)

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "HAVE_GMPY2",
    "digit_sum",
    "f_kb",
    "iterate",
    "num_digits",
    "contraction_bound",
    "FiniteSystem",
    "build_system",
    "ModularStructure",
    "structure",
    "cycle_count",
    "cycle_count_formula",
    "cycle_count_formula_folded",
    "periodic_point_count",
    "periodic_point_count_formula",
]
