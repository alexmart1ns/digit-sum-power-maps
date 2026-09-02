# Lemma C — oscillation analysis (pilot 3,10)

Subsequence `V=10^n`, `n=2…16`.

**Psi_18 gap:** 0.238095 (n=3) to 0.561572 (n=8) → **0.323477**
**rho_n gap:** 0.400366
**Max adjacent |Delta Psi|:** 0.179815

| n | Psi_18 | rho_n | rho_{n+1} | |Delta Psi| |
|---|--------|-------|-----------|-------------|
| 2 | 0.285714 | 0.25 | 0.333333 | 0.0476 |
| 3 | 0.238095 | 0.181818 | 0.3 | 0.1798 |
| 4 | 0.41791 | 0.382353 | 0.454545 | 0.1034 |
| 5 | 0.521327 | 0.575472 | 0.466667 | 0.0319 |
| 6 | 0.553224 | 0.538922 | 0.567568 | 0.0309 |
| 7 | 0.522296 | 0.454459 | 0.590133 | 0.0393 |
| 8 | 0.561572 | 0.582184 | 0.540954 | 0.0629 |
| 9 | 0.498624 | 0.517218 | 0.48003 | 0.0198 |
| 10 | 0.478872 | 0.429681 | 0.528065 | 0.0426 |
| 11 | 0.521506 | 0.489825 | 0.553188 | 0.0358 |
| 12 | 0.485755 | 0.451184 | 0.520327 | 0.0786 |
| 13 | 0.407132 | 0.347945 | 0.466319 | 0.0563 |
| 14 | 0.350874 | 0.240655 | 0.461093 | 0.0121 |
| 15 | 0.363012 | 0.250987 | 0.475036 | 0.0570 |
| 16 | 0.419987 | 0.380399 | 0.459575 | — |

**Verdict:** suggests_oscillation

## Route C-C — convergence refutation

Train `n≤8`, hold-out `n=[9, 10, 11, 12, 13, 14, 15, 16]`. Tolerance `0.05`.

| Model | L̂ / fit | max |error| on hold-out |
|-------|---------|----------------------|
| constant | 0.423601 | **0.182946** |
| linear_inv_n | rho_n = a + b/n | **0.353697** |
| linear_n | rho_n = a + b*n | **0.779187** |
| log_periodic | 0.434192 | **0.314795** |

**ρ running range** at train end: 0.400366; at n=16: **0.400366**
**Full ρ gap:** 0.400366 | **Full Ψ gap:** 0.323477
**Route C-C verdict:** **convergence_refuted**

Route C-C: if rho_n -> L, hold-out decades n>8 should match constant, 1/n-decay, or low-period cosine fit within tolerance. Persistent gap and OOS errors refute convergence on the tested models (empirical only).

Empirical gap on subsequence V=10^n does not prove liminf != limsup. Lemma C requires analytic bound on rho_n or Psi alternation.
