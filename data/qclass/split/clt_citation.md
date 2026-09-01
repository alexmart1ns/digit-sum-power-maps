# CLT citation note — pilot (3,10), signature {0}

Sidecar only. Closes **G2c CLT leg** per [`llt_bands.md`](llt_bands.md) §6.3 and
[`ATTACK_PLAN.md`](ATTACK_PLAN.md) Lemma A.

---

## Target statement

For `f = s_{10}`, `P(n) = n³`, and dyadic band

`Ω_{D,r} = N_D ∩ (r + 9ℤ) = { n : 10^{D-1} ≤ n < 10^D, n ≡ r (mod 9) }`,

the Bassily–Kátai property holds and

`(Σ_{n∈Ω_{D,r}} f(P(n)) − |Ω_{D,r}| · E[f]) / √(Var)  →  N(0,1)`

in distribution as `D → ∞`, with `E[f] = Θ(D)`, `Var = Θ(D)`.

---

## Citation chain

| Step | Reference | Content |
|------|-----------|---------|
| 1 | [15] Def. 8.3.11 | BK-Property for subsequences `Ω_N` |
| 2 | [15] Lemma 8.3.14 + Ex. 8.3.15 | `{P(n) : n < N}` satisfies BK for polynomial `P` |
| 3 | [15] Thm 8.3.13 | CLT for `f(P(n))` on any BK subsequence |
| 4 | [15] Thm 8.3.10 | Backbone via Bassily–Kátai (1995); **any** `q ≥ 2` |
| 5 | **Lemma A** (`llt_bands.md` §7) | `|Ω_{D,r}| = (10^D − 10^{D-1})/9 + O(1)` |

**Pilot feeding residues** for signature `{0}`: `r ∈ {0, 3, 6}`.

---

## Checklist (verify before paper promotion)

- [x] BK-Property for `P(n)=n³` on initial segments — Ex. 8.3.15
- [ ] BK-Property on **progression slice** `n ≡ r (mod 9)` — same exponential-sum
      input as Ex. 8.3.15; write one-line reduction
- [x] Composite base `b=10` — no prime restriction in §8.3.2
- [x] Band cardinality — Lemma A (combinatorial)
- [ ] Explicit variance constant for `s_{10}(n³)` on `Ω_{D,r}` — cite Peter (2002)
      for mean/variance asymptotics (G2b input)

---

## What this does NOT give

- Pointwise LLT (`P(s_{10}(n³)=v) ≈ φ(...)`) — **G2d**, open
- LM for labelling `h_j` — independent gap
- Bridge `δ_j = F_j + o(1)` — needs G2d or weaker discretisation + G4

---

## Status

**CLT leg: citable** (pending progression-slice verification paragraph).
**LLT leg: open** (G2d).
