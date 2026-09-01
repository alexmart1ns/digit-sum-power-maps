# Topic 10 mining report

**Generated:** 20260831T020654Z  
**Mode:** full  
**gmpy2:** True  
**Cells:** 7470 (7470 ok)  
**Prior:** `data\sweeps\summary_k1-500_b2-40_20260717T191848Z.csv`

## Grid

Strata counts: {'A': 2800, 'D': 776, 'B': 3633, 'E': 16, 'F': 5, 'C': 1221}

Not a rectangle. Layer A hunts tightness at small b; B samples m by ω(m); C/D densify archived Δ peaks and Δ=0 seeds (C is empty in quick mode when the k·M work cap drops the explosion neighbourhood); E/F attach orbit, degree, bounds, and Fourier-vs-Gaussian on a subsample.

## 10.8 Cycle count fold

``cycle_count_formula_folded`` evaluates Cyc by CRT-folding length multiplicity maps (gcd/lcm). It is tested equal to the graph and to the expanded product in ``tests/test_modular.py``.

## Theorems on this grid

- Lower bound |C| ≥ Cyc violations: **0**
- Δ = Σ δ_i failures: **0**
- Signature mass identity failures: **0**

## 10.2 Tightness

- Exact matches Δ=0: **103 / 7470** (rate is range-dependent; do not quote it as a law)
- By base: {2: 5, 3: 3, 4: 2, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2, 10: 2, 11: 1, 12: 2, 13: 1, 14: 2, 15: 1, 16: 1, 17: 2, 18: 3, 19: 2, 20: 2, 21: 1, 22: 1, 23: 2, 24: 2, 25: 1, 26: 4, 27: 2, 28: 2, 29: 1, 30: 2, 31: 1, 32: 2, 33: 3, 34: 1, 35: 2, 36: 1, 37: 1, 38: 2, 39: 1, 40: 1, 41: 1, 42: 2, 44: 2, 47: 2, 48: 2, 50: 1, 52: 1, 54: 2, 56: 1, 58: 1, 59: 2, 60: 2, 62: 2, 65: 2, 66: 1, 68: 2, 70: 1, 72: 2, 74: 2, 78: 1, 80: 2}
- Max k with Δ=0: 381

## 10.1 / 10.7 Local excess

- Max Δ: 122 at (157, 80)
- Signatures with δ_i>0 (mean over ok cells): 6.8423

Report local δ_i inside a fixed m; do not pool moduli.

## 10.3 Orbit length

- Cells with orbit extras: 16
- All sampled bands bounded by 2 + max tail: True

## 10.4 Predecessors

- Cells with degree fit: 16
- Any CSN-plausible power law (p>0.1): False

## 10.5 Upper bound slack

- N* always ≥ |C|: True
- Cyc as upper bound (should be rare): 1

## 10.6 Split models

- Fourier-vs-Gaussian cells: 2
- Fourier MAE mean: 0.01948
- Gaussian MAE mean: 0.019513

The independent-digit convolution is the inverse Fourier transform of φ(t)^L. Delange / Drmota–Grabner already oscillate; whether that implies the split is the convolution with a(v), not a numerical MAE.
