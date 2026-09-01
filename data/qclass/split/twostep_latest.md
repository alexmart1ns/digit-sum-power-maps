# Q-class two-step / independent-digit diagnosis

Stamp: 20260901T161041Z
D = [8, 16, 24, 40, 56, 64]; empirical samples = 8000

Gaussian + labels is already `predict_split_Q`. Image Gaussian places
m1 on Q(r) (mod m) instead of on feeding residues of n.

| Q | mae gauss | mae image | mae emp m1 | TV residue vs Q(n) | verdict |
|---|-----------|-----------|------------|--------------------|---------|
| 1 + 3x + 2x^2 | 0.182027 | 0.006976 | 0.005972 | 0.0066 | lattice of m1 is Q(n) mod m, not feeding residues of n; image Gaussian is the F_j correction |
| x^3 | 0.041021 | 0.002434 | 0.003416 | 0.0 | lattice of m1 is Q(n) mod m, not feeding residues of n; image Gaussian is the F_j correction |

## Per D

### 1 + 3x + 2x^2

| D | TV res vs image | mae G | mae image | mae emp | m2≤M |
|---|-----------------|-------|-----------|---------|------|
| 8 | 0.0052 | 0.168285 | 0.023119 | 0.001458 | 1.0 |
| 16 | 0.0092 | 0.220121 | 0.00447 | 0.00575 | 1.0 |
| 24 | 0.0063 | 0.118636 | 0.001759 | 0.01125 | 1.0 |
| 40 | 0.0092 | 0.165962 | 0.000111 | 0.00625 | 1.0 |
| 56 | 0.0051 | 0.185158 | 0.011994 | 0.009042 | 0.9849 |
| 64 | 0.0047 | 0.234003 | 0.000405 | 0.002083 | 0.9748 |

### x^3

| D | TV res vs image | mae G | mae image | mae emp | m2≤M |
|---|-----------------|-------|-----------|---------|------|
| 8 | 0.0 | 0.055429 | 0.000333 | 0.001666 | 1.0 |
| 16 | 0.0 | 0.050627 | 0.002292 | 0.005333 | 1.0 |
| 24 | 0.0 | 0.001123 | 0.00133 | 0.001875 | 1.0 |
| 40 | 0.0 | 0.054765 | 0.002901 | 0.003875 | 1.0 |
| 56 | 0.0 | 0.008632 | 0.003 | 0.003 | 1.0 |
| 64 | 0.0 | 0.075549 | 0.00475 | 0.00475 | 0.9775 |

