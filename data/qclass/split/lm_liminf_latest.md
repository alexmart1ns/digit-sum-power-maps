# LM liminf/limsup analysis

Source: local_mean  k=3 b=10  V in [100, 10000000]

## Global (all scales)

| attractor | liminf | limsup | range | mean |
|-----------|--------|--------|-------|------|
| [18] | 0.0909 | 0.7586 | 0.6677 | 0.5065 |
| [27] | 0.2414 | 0.9091 | 0.6677 | 0.4935 |

## Subsequence V ≈ b^n

- **[18]**: liminf=0.2381, limsup=0.5532, range=0.3151
- **[27]**: liminf=0.4468, limsup=0.7619, range=0.3151

## Decade anchors

| n | V | [18] | [27] |
| 2 | 100 | 0.2857 | 0.7143 |
| 3 | 1000 | 0.2381 | 0.7619 |
| 4 | 10000 | 0.4179 | 0.5821 |
| 5 | 100000 | 0.5213 | 0.4787 |
| 6 | 1000000 | 0.5532 | 0.4468 |
| 7 | 10000000 | 0.5223 | 0.4777 |

**Verdict:** suggests_non_convergence

Range > 0.05 on Psi_j supports LM but does not prove lim inf != lim sup. Subsequence b^n analysis refines decade-collapse test.
