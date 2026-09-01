# LM deterministic bounds (pilot 3,10)

M=57  amplitude over L in [1,M]: **0.6**
Decade window gap (primary): **0.323477**
Feeding residues mod 9: `[0, 3, 6]`

## Finite region [1,M] by digit length

| L | counts | frac primary |
|---|--------|--------------|
| 1 | {'[18]': 1} | 1.0 |
| 2 | {'[18]': 2, '[27]': 3} | 0.4 |

## Preimages on image lattice

- **[18]**: `[9, 18, 45]`
- **[27]**: `[27, 36, 54]`

## Decade windows (exact Psi_j, w_L, rho_L)

| n | V | total | w_n | w_{n+1} | Psi_18 | Psi_27 |
|---|-----|-------|-----|---------|--------|--------|
| 2 | 100 | 7 | 0.571429 | 0.428571 | 0.285714 | 0.714286 |
| 3 | 1000 | 21 | 0.52381 | 0.47619 | 0.238095 | 0.761905 |
| 4 | 10000 | 67 | 0.507463 | 0.492537 | 0.41791 | 0.58209 |
| 5 | 100000 | 211 | 0.50237 | 0.49763 | 0.521327 | 0.478673 |
| 6 | 1000000 | 667 | 0.50075 | 0.49925 | 0.553223 | 0.446777 |
| 7 | 10000000 | 2108 | 0.5 | 0.5 | 0.522296 | 0.477704 |
| 8 | 100000000 | 6667 | 0.500075 | 0.499925 | 0.561572 | 0.438428 |

**Verdict:** deterministic_gap_positive

Exact counts on finite windows (psi_sharp parity with local_mean); does not prove LM theorem (lim inf != lim sup along V->infty).
