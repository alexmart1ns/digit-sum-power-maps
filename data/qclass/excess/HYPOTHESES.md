# Hypotheses for Δ(k,b) and local excess (Problem A)

**Observations only** — not a closed conjecture. Pre-registered tests against
existing data (`excess_latest.json`, sweep summary v2.1, pilot grid).

---

## Definitions

- **Global** `Δ = |C| − Cyc(φ_{Q,b−1})` (or `φ_{k,b−1}` for monomials).
- **Local** `δ_i = a_i − 1` per modular signature `γ_i` (`a_i` physical attractors
  on that signature inside `[1,M]`).
- **Split (window):** ∃ signature with `a_i ≥ 2`.
- **Split (band D):** oscillation of `δ_j(D)` between attractors sharing a
  signature — Problem B, not Problem A.

---

## Hypothesis table

| ID | Statement | Test | Verdict | Notes |
|----|-----------|------|---------|-------|
| **H1** | Digit-layer count `n_digit_layers` predicts local `δ_i` | Spearman over 35 `(Q,b)` signatures | **Partial** | r ≈ **0.885** — correlational, not causal |
| **H2a** | `Δ>0` ⇔ ∃ split signature (`a_i≥2`) | Definition + 19.5k sweep | **Accepted (tautology)** | 0 pairs with `Δ=0` and split sig |
| **H2b** | `Δ>0` predicts band oscillation strength | Grid amp vs Δ | **Rejected** | e.g. x⁴,b=10: Δ=3, amp=0.05; x³,b=16: Δ=5, amp=0.02 |
| **H3** | Parity of `k` dominates `Δ(k,b)` | Mean Δ odd vs even on sweep | **Supported** | mean **18.1** (odd) vs **7.9** (even); Pearson(parity,Δ)≈**0.48** |
| **H4** | `ω(b−1)` predicts `Δ` | Pearson on sweep (n=19500) | **Moderate** | r ≈ **0.39** (paper §9: 0.44 with Cyc) |
| **H5** | `gcd(k,b−1)` predicts `Δ` | Pearson on sweep | **Rejected** | r ≈ **−0.05** (paper §9) |

---

## H1 detail

Spearman(`n_digit_layers`, `δ_local`) = **0.885** over signatures in
`excess_latest.json` (35 pairs). High correlation reflects that extra attractors
often sit on different digit scales, but **does not** imply a closed formula
`Δ = f(layers)`. Do not promote to conjecture.

---

## H2 detail (count vs oscillation)

**H2a** is algebraic: `Δ = Σ δ_i` and `δ_i = a_i − 1`, so `Δ>0` iff some
`a_i ≥ 2`. Verified on all 19 500 monomial pairs in
`summary_k1-500_b2-40_20260901T170425Z.csv` (0 exceptions).

**H2b** separates **attractor count** from **mass oscillation**. Band-level
split diagnostics (`grid_latest.md`) show weak or absent oscillation for some
`Δ>0` pairs and strong oscillation for others with similar Δ.

**Correction:** earlier README text claiming `x+x^2`, `b=10` has `Δ=0` with
split is **incorrect** — excess records `Δ=1` for that pair. Split and excess
are still **orthogonal** to Problem B via H2b.

---

## H3–H4 detail (monomial sweep)

Computed from `summary_k1-500_b2-40_20260901T170425Z.csv` (19500 ok pairs):

```
mean Δ (k odd)  = 18.14
mean Δ (k even) =  7.92
Pearson(parity, Δ)     ≈ 0.48
Pearson(ω(b−1), Δ)     ≈ 0.39
Pearson(gcd(k,b−1), Δ) ≈ −0.05
```

Aligns with paper §9 (parity confound B.4; ω as structural predictor). No closed
form `Δ(k,b) = F(k,b,ω,…)` is proposed.

---

## What we do NOT claim

- No formula `Δ(k,b)` or `Δ(Q,b)`.
- No implication `Δ → δ_j(D)` behaviour.
- Spearman 0.89 is **not** a theorem.

---

## Minimal extension (done)

Regression statistics computed from existing sweep summary — no new
`mine_topic10` run required. Further mining (`data/mining/`) optional for
intra-modulus slices only.

---

## See also

- [`excess_latest.md`](excess_latest.md) — pair table
- [`THEORY_NOTE.md`](../universality/THEORY_NOTE.md) — Problem C
- [`proof_pilot_3_10.md`](../split/proof_pilot_3_10.md) — Problem B
