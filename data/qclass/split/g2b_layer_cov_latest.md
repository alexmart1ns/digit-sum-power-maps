# G2b layer covariance — Route C-B proxy (pilot 3,10)

Decade anchors `V=10^n`, `n=9…16`.

**Pearson ρ(L=n) vs ρ(L=n+1) at same anchor:** **0.623147**
**Lag-1 autocorr ρ(L=n):** 0.631219
**Mean |ρ_n − ρ_n+1|:** 0.113764
**Max two-stratum |Ψ − Ψ̂|:** 0.0
**Verdict:** layer_correlation_detected

| n | ρ(L=n) | ρ(L=n+1) | |Δρ| | Ψ_18 | two-stratum err |
|---|--------|----------|------|------|-----------------|
| 9 | 0.517218 | 0.48003 | 0.037188 | 0.498624 | 0.0 |
| 10 | 0.429681 | 0.528065 | 0.098384 | 0.478872 | 0.0 |
| 11 | 0.489825 | 0.553188 | 0.063363 | 0.521506 | 0.0 |
| 12 | 0.451184 | 0.520327 | 0.069143 | 0.485755 | 0.0 |
| 13 | 0.347945 | 0.466319 | 0.118374 | 0.407132 | 0.0 |
| 14 | 0.240655 | 0.461093 | 0.220438 | 0.350874 | 0.0 |
| 15 | 0.250987 | 0.475036 | 0.224049 | 0.363012 | 0.0 |
| 16 | 0.380399 | 0.459575 | 0.079176 | 0.419987 | 0.0 |

Route C-B proxy: at anchor V=10^n, labelling rates at digit layers L=n and L=n+1 are measured on the same window. Pearson r quantifies co-movement (G2b covariance phenomenology). predict_split treats layers as independent Gaussians; two-stratum error near 0 shows the dominant mass is in {n,n+1} but does not imply layer independence for suffix-restricted rates rho_n(s).
