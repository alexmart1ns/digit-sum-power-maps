# Isolated literature notes for the Q-class sidecar

Sources live in `C:\Users\Alex Martins\Downloads\estudo` and are **not** copied
into `data/sweeps`, `data/mining`, or `data/split`.

## Koppelaar–Nasehpour 2020

H. Koppelaar and P. Nasehpour, *On Hardy’s Apology numbers*, Journal of
Algorithms and Computation **52**(2) (2020), 67–83. arXiv:2008.08187.

Finitude of solutions of `n = s_b(P(n))` for suitable polynomials P
(Hardy / Dudeney / Wells types), with explicit search bounds. Transferable
to **fixed points** of `S_b(Q(n))` only — not to cycles, excess, or the split.

## Hare–Laishram–Stoll 2011

K. G. Hare, S. Laishram and T. Stoll, *Stolarsky’s conjecture and the sum of
digits of polynomial values*, Proc. Amer. Math. Soc. **139** (2011), 39–49.
arXiv:1001.4169.

`liminf s_q(P(n))/s_q(n) = 0` for `deg P ≥ 2`. Class-B analytic input for
digital fluctuation of polynomial values, parallel to Mauduit–Rivat for `n^k`.

## Alcântara survey tables

Cycle lists for `T_{10,k}`, `2 ≤ k ≤ 10`, checked in-memory against
`build_system(k, 10)` by `scripts/qclass_check.py`. See `oeis_k2-10.json`.
Do not merge those tables into the 19.5k sweep.

## Delange / Drmota–Grabner (Hypothesis LM)

Delange (1975): digital functions have Fourier expansions with log-periodic
fluctuation. Drmota–Grabner monograph [15]: Mellin–Perron machinery for sums of
digits of polynomial sequences.

**Open question for LM:** does the fixed labelling `h_j(v)=1_{g(v)∈β_j}` inherit
non-convergence of its window means `Ψ_j(V)` from the digital structure of
`g`, without a `C^1` Delange factor? The `local_mean` diagnostic tests decade
collapse `Ψ(V)` vs `Ψ(bV)`; extended runs to `V=10^7` are in
`data/split/local_mean_latest.md`.

**Not sufficient alone:** comparing Fourier vs Gaussian MAE (both at noise floor)
does not establish LM — see paper §10.
