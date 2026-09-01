# Q-class split / F_j

Stamp: 20260901T161557Z
Bands D: [6, 10, 14, 18, 22], samples/band: 3000

F_j := Gaussian mixture of digits of Q(n), restricted to feeding residues,
convolved with the exact labelling a(v), scaled by p_i.

| Q | b | status | mae F_j | osc? | aggregate ≈ p_i |
|---|---|--------|---------|------|-----------------|
| x^3 | 10 | split | 0.006093 | False | True |
| x + x^2 | 10 | split | 0.002444 | False | True |
| 1 + x^3 | 10 | no_split | — | — | — |
| 1 + 3x + 2x^2 | 10 | split | 0.018257 | True | True |
