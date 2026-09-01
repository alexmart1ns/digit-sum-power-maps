# Lemma C analytic — suffix mixture (Route C-A)

Decades `n=9…14`, suffix `v mod 100`.

**Mixture identity** `rho_n = Σ alpha_n(s) rho_n(s)`: **exact** (True)
**Witness pair:** `[50, 55]` with min gap **0.122112**
**Max suffix rho drift:** 0.274149 | **Max alpha drift:** 6.6e-05
**Verdict:** witness_gap_uniform

## Tail-digit dependence (label vs v mod b^d)

| tail digits | pairs checked | mismatches | determines? |
|-------------|---------------|------------|-------------|
| 2 | 636 | 636 | no |
| 3 | 336 | 336 | no |
| 4 | 0 | 0 | no |

Analytic Route C-A: rho_n = sum_s alpha_n(s)*rho_n(s) exactly on stratum L=n. Uniform witness pair gap >= c across decades blocks naive convergence of rho_n(s). Oscillation driver: suffix-class rates rho_n(s) vary with n (max drift 0.274149), not mixture weights alpha_n(s) (max drift 6.6e-05). Tail digits do not alone determine label.
