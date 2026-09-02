# Route C-A — suffix-class rho gap (pilot 3,10)

Stratum `L=n` at `V=10^n`, `n=2…16`. Buckets `v mod b^d`, `d=2,3`.

**Min max-suffix-gap (mod 100), n≥9:** **0.174573**
**Max suffix-gap (mod 100), n≥9:** 0.371428
**At n=16 (mod 100):** 0.249306

**Verdict:** suffix_gap_confirmed

## Stable pair witness (n≥9, mod 100)

At `n=9`: suffixes `[1, 59]` have rho `[0.685714, 0.314286]` → gap **0.371428**.
Best cross-decade pair: `[50, 95]` with min gap **0.09705** over `8` decades.

## Per-decade max gap (mod 100)

| n | stratum rho | buckets | max |rho(s1)-rho(s2)| | pair |
|---|-------------|---------|-------------------|------|
| 2 | 0.25 | 0 | **0.0** | —, — |
| 3 | 0.181818 | 0 | **0.0** | —, — |
| 4 | 0.382353 | 0 | **0.0** | —, — |
| 5 | 0.575472 | 0 | **0.0** | —, — |
| 6 | 0.538922 | 0 | **0.0** | —, — |
| 7 | 0.454459 | 0 | **0.0** | —, — |
| 8 | 0.582184 | 0 | **0.0** | —, — |
| 9 | 0.517218 | 100 | **0.371428** | 1, 59 |
| 10 | 0.429681 | 100 | **0.265424** | 0, 35 |
| 11 | 0.489825 | 100 | **0.174573** | 50, 61 |
| 12 | 0.451184 | 100 | **0.221656** | 30, 99 |
| 13 | 0.347945 | 100 | **0.28337** | 70, 99 |
| 14 | 0.240655 | 100 | **0.289158** | 0, 49 |
| 15 | 0.250987 | 100 | **0.207056** | 17, 99 |
| 16 | 0.380399 | 100 | **0.249306** | 70, 89 |

Route C-A: if rho_n converged via mixing, suffix buckets mod b^d would homogenize. Persistent max |rho(s1)-rho(s2)| >= c across decades supports intrinsic suffix-class variation (empirical; not a limit proof).
