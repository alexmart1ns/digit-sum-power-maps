"""Topic-10 mining: smart grid, local excess, orbit length, predecessors.

The exhaustive engine remains ``dspm.dynamics`` / ``analyze_pair``. This
package only decides *which* pairs to run and which extra measurements to
attach. Correlations that mix distinct moduli are out of scope -- see
section 9 of the paper and ``docs/AUDIT.md``.
"""

from __future__ import annotations

from .bounds import bound_candidates, bound_candidates_from_record, summarize_bound_scores
from .excess import excess_identity_holds, local_excess
from .fourier import compare_split_models, independent_digit_sum_pmf
from .grid import GridCell, default_prior_csv, smart_grid
from .intra import analyze_intra_modulus, load_jsonl
from .orbit import max_orbit_in_window, orbit_length, sample_orbit_by_digits
from .predecessors import degree_histogram, fit_power_law
from .record import mine_pair
from .tightness import tightness_cells

__all__ = [
    "GridCell",
    "analyze_intra_modulus",
    "bound_candidates",
    "bound_candidates_from_record",
    "compare_split_models",
    "default_prior_csv",
    "degree_histogram",
    "excess_identity_holds",
    "fit_power_law",
    "independent_digit_sum_pmf",
    "load_jsonl",
    "local_excess",
    "max_orbit_in_window",
    "mine_pair",
    "summarize_bound_scores",
    "tightness_cells",
    "orbit_length",
    "sample_orbit_by_digits",
    "smart_grid",
]
