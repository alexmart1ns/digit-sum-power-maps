"""Local bifurcation excess per residue signature (Problems 10.1, 10.7, 10.2).

Global Δ = |C| − Cyc is a sum of local excesses. Lemma 5.1 says every
physical attractor's signature is a whole modular cycle, so

    Δ = Σ_i (a_i − 1)

where a_i is the number of physical attractors carrying γ_i. The working
hypothesis for later analysis (not a theorem): δ_i grows when attractors
sharing γ_i sit at several distinct digit lengths inside [1, M].
"""

from __future__ import annotations

from math import gcd
from typing import Any

from dspm.core import num_digits
from dspm.dynamics import FiniteSystem
from dspm.modular import structure
from dspm.numtheory import omega, v2

__all__ = [
    "excess_identity_holds",
    "local_excess",
    "pair_features",
]


def local_excess(system: FiniteSystem) -> list[dict[str, Any]]:
    """One row per residue signature that actually appears on an attractor."""
    sharing = system.attractors_sharing_signature()
    rows = []
    for sig, indices in sharing.items():
        mins = [system.attractors[i][0] for i in indices]
        lengths = sorted({num_digits(v, system.b) for v in mins})
        rows.append(
            {
                "signature": sorted(sig),
                "a_i": len(indices),
                "delta_local": len(indices) - 1,
                "attractor_mins": mins,
                "cycle_lengths": [len(system.attractors[i]) for i in indices],
                "digit_lengths": lengths,
                "n_digit_layers": len(lengths),
                "basin_sizes": [system.basin_sizes[i] for i in indices],
            }
        )
    rows.sort(key=lambda r: (-r["delta_local"], r["signature"]))
    return rows


def excess_identity_holds(system: FiniteSystem, cyc: int | None = None) -> bool:
    """Δ = Σ δ_i. Uses Cyc from the modular skeleton when ``cyc`` is omitted."""
    if cyc is None:
        cyc = structure(system.k, system.m).cycle_count
    delta = system.count - cyc
    return delta == sum(row["delta_local"] for row in local_excess(system))


def pair_features(k: int, b: int) -> dict[str, int]:
    """Number-theoretic coordinates used intra-modulus, never pooled blindly."""
    m = b - 1
    g = 0 if m < 1 else gcd(k, m)
    return {
        "m": m,
        "gcd_k_m": g,
        "v2_gcd": v2(g),
        "k_odd": int(k % 2 == 1),
        "omega_m": omega(m) if m >= 1 else 0,
        "k_mod_m": (k % m) if m >= 1 else 0,
    }
