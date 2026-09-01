# LM deterministic bounds (pilot 3,10)

M=57  amplitude over L in [1,M]: **0.6**
Decade window gap (primary): **0.315128**
Feeding residues mod 9: `[0, 3, 6]`

## Finite region [1,M] by digit length

| L | counts | frac primary |
|---|--------|--------------|
| 1 | {'[18]': 1} | 1.0 |
| 2 | {'[18]': 2, '[27]': 3} | 0.4 |

## Preimages on image lattice

- **[18]**: `[9, 18, 45]`
- **[27]**: `[27, 36, 54]`

## Decade windows (exact Psi_j, psi_sharp parity)

| V | total | [18] | [27] |
|---|-------|---|---|
| 100 | 7 | 0.285714 | 0.714286 |
| 1000 | 21 | 0.238095 | 0.761905 |
| 10000 | 67 | 0.41791 | 0.58209 |
| 100000 | 211 | 0.521327 | 0.478673 |
| 1000000 | 667 | 0.553223 | 0.446777 |
| 10000000 | 1054 | 0.454459 | 0.545541 |

**Verdict:** deterministic_gap_positive

Exact counts on finite windows (psi_sharp parity with local_mean); does not prove LM theorem (lim inf != lim sup along V->infty).
