# Attack plan: open gaps for pilot (3,10) — PhD roadmap

Sidecar only. Not peer-reviewed. Companion to [`proof_pilot_3_10.md`](proof_pilot_3_10.md),
[`llt_bands.md`](llt_bands.md), [`lm_pilot.md`](lm_pilot.md), [`bridge_lemma.md`](bridge_lemma.md).

**Audience:** researcher with analytic number theory + finite dynamics background.

---

## 1. Executive summary

| Gap | Blocks | Feasibility | Impact | **Priority** |
|-----|--------|-------------|--------|--------------|
| **LM 4.2.3–4** (non-convergence of Ψ_j) | Conjecture 10.6 directly | **Medium** — finite trap data + exact decade Ψ constrain the lemma; no Delange for `h_j` | High | **1** |
| **G4** (first-landing ≡ labelling) | Bridge `δ_j = F_j + o(1)` | **Medium–high** — combinatorics on fixed `M` + tail bounds | High | **2** |
| **G2d** (pointwise LLT, `k≥3`) | Hypothesis LLT / bridge error budget | **Low** — explicitly open in [9] Problem 2 and [15] §8.4.1 | High | **3** |
| **G2a–G2b** (uniform band LLT + mixture) | Polish of G2d | Low (depends on G2d) | Medium | 4 |

**Recommendation:** attack **LM first** with a *finite shadow lemma* lifting trap
oscillation `ρ_L` (proven for `L=1,2`) to large-`L` windows via periodicity of
`g(v)` modulo a scale dependent on `M`. Parallel track: close **G4** as a
deterministic finite-`M` lemma (should be provable in-house). Reserve **G2d**
for external collaboration or a dedicated LLT paper — literature does not
currently supply a citation for `s_{10}(n³)`.

Empirical constraints any lemma must respect:

- Trap amplitude `|ρ_1 − ρ_2| = 0.6` on image lattice in `[1,M]`
- Decade-anchor gap `≥ 0.315` for `Ψ_{18}(10^n)`, `n=2…7` (exact, not MC)
- Bridge MAE `≈ 0.002` — any LM lemma incompatible with `F_j` is falsified

---

## 2. G2d — pointwise LLT for `s_{10}(n³)`

**Target.** For each feeding residue `r ∈ {0,3,6}`, each digit length `L` in the
active band, and `v` on the image progression `v ≡ 0 (mod 9)` near
`μ_L = 9(L−1)/2`, `σ_L = √(10²−1)L/12`:

`#{ n ∈ N_D^{(r)} : s_{10}(n³) = v } = |N_D^{(r)}| · w_L(D) · φ_L(v) / m + o(|N_D^{(r)}|)`

with `w_L(D)` from `digit_count_mixture` and `φ_L` Gaussian.

### Route G2d-A — Extend DMR Problem 2 methods (hard)

- **Idea:** DMR [9] solve pointwise counts for `deg P = 2`; Problem 2 is open
  for `deg ≥ 3` because Fourier estimates in `α` are not uniform.
- **Pilot task:** specialise their generating-function setup to `P(n)=n³`, `q=10`,
  and `N_D^{(r)}` instead of `n ≤ x`.
- **Difficulty:** Research-level; likely needs new exponential-sum bound uniform
  in `α` near the mean. Prime-base remark does not help at `q=10`.
- **Payoff:** Closes G2d and G2a simultaneously.

### Route G2d-B — CLT + discretisation lemma (medium-hard)

- **Idea:** Accept [15] Thm 8.3.13 CLT on `Ω_N = N_D^{(r)}`. Prove a
  **Berry–Esseen-type** bound with explicit constant for the digit-sum of `n³`
  at scale `σ_L`, then discretise: point mass at integer `v` differs from
  Gaussian density by `O(1/σ_L)`.
- **Gap:** CLT gives interval probabilities, not point masses. Need local
  mod-`m` equidistribution of `s_{10}(n³)` at scale `1` near the mean — exactly
  what [9] Problem 2 asks for.
- **Honest verdict:** CLT alone is **insufficient** for bridge; documents why
  G2d cannot be deferred to [15].

### Route G2d-C — Carry / layer decomposition (pilot-specific)

- **Idea:** Write `s_{10}(n³) = Σ_{ℓ=0}^{L−1} d_ℓ(n³)` with digits `d_ℓ`.
  For `n` in a narrow band of digit length `L`, higher digits of `n` are
  constrained; use Peter (2002) summatory asymptotics for `s_{10}(⌊α n³⌋)` to
  control **mean and variance** of each layer, then prove weak dependence across
  layers (covariance G2b).
- **Pilot deliverable:** Lemma giving Gaussian **mixture** with explicit
  `w_L(D)` matching `digit_count_mixture` — even a **lower-bound** LLT
  (sandwich between two Gaussians) may suffice for bridge error `o(1)`.
- **Difficulty:** Medium; mostly in-house if layer covariance is tame for `k=3`.

### Route G2d-D — Computational verification as hypothesis (fallback)

- Document Hypothesis LLT as **computationally validated** (MAE 0.002, survives
  D=1000) and pursue 10.6′ conditionally. Does **not** close the proof chain.

---

## 3. G4 — first-landing mass ≡ labelling `a(v)`

**Target.** For `v` in the LLT window `I_L = [μ_L − Cσ_L, μ_L + Cσ_L]` on the
image lattice,

`#{ n ∈ N_D^{(r)} : S_{10}(n³) = v }`  induces the same first-landing
distribution as counting `v` with label `a(v)` in the trapping region.

### Route G4-A — Fixed-`M` sufficiency (should be provable)

**Lemma G4-finite (candidate).** Fix `(k,b)=(3,10)`, `M=57`. For all `v ≥ 1`,
let `g(v)` be the unique `w ∈ [1,M]` reached by iterating `f_{3,10}` until
`w ≤ M`. Then `a(v) = label[g(v)]` depends only on `v mod M'` for an explicit
`M' = M · b^{t(k,b)}` (preperiod bound from contraction).

*Proof sketch.* Forward invariance of `[1,M]` and monotonicity of digit length
imply that for `v > M`, the first landing is determined by the `t`-th iterate
where `t = O(log v)` but only through `v mod b^t` in the low digits. For the
pilot, enumerate preimages of `[1,M]` under `t` steps — finite computation
generalises to a periodicity statement.

**Status:** In-house; needs formalising `t(k,b)` from `contraction_bound`.

### Route G4-B — Error from values outside window

- Truncation at `μ ± 6σ` (G3): exponential tail `o(1)`.
- Boundary: mass at `v` with `L(v) ≠ L` contributes `O(1/b)` per band — controlled
  by `digit_count_mixture` overlap bounds already in `predict.py`.

### Route G4-C — Coupling to G2d

- If only **weak** LLT (interval CLT) is available, G4 still needs that
  conditional law of `g(v) | S_{10}(n³)=v` concentrates on `a(v)`. This is
  a **conditional independence** claim — strictly harder than G4-A.

**Recommendation:** prove **G4-finite** first, independent of G2d.

---

## 4. LM — steps 4.2.3–4 (non-convergence of Ψ_j)

**Target.** `liminf_{V→∞} Ψ_{18}(V) < limsup_{V→∞} Ψ_{18}(V)`, or equivalently
`(Ψ_{18}(10^n))` does not converge with gap `≥ c > 0`.

### What is already proved

- `β_{18}`, `β_{27}` explicit in `[1,M]`; `ρ_1=1`, `ρ_2=0.4` on image lattice
- `Ψ_j(10^n)` exact for `n≤7`; gap `0.315`

### Route LM-A — Shadow lemma (periodic extension of trap labelling)

**Lemma LM-shadow (candidate).** There exists `c_* > 0` and a sequence
`n_k → ∞` such that for `V = 10^{n_k}`, the sharp window
`W(V) = [V−√V, V+√V] ∩ (0+9ℤ)` satisfies:

`Ψ_{18}(V) = Σ_{ℓ ∈ {n_k, n_k+1}} w_ℓ(V) · ρ̃_ℓ + O(b^{−n_k/2})`

where `ρ̃_ℓ` are **periodic** in `ℓ mod T` for some `T = T(k,b,M)`, and
`|ρ̃_ℓ − ρ̃_{ℓ+T}| ≥ c_*` for some phase of `ℓ`.

*Mechanism.* For `v ∈ W(V)` with `L(v) = ℓ ≫ log M`, the first landing
`g(v)` depends on the **low `O(log M)` base-`b` digits** of `v` (carry
propagation length bounded by contraction). The map `v ↦ g(v) mod M` is
eventually periodic in the high-digit skeleton; `ρ̃_ℓ` is the average of
`h_{18}` over one period.

**Why plausible.** Trap `ρ_1, ρ_2` are the `ℓ=1,2` instances. Decade anchors
show `Ψ_{18}` does not stabilise — consistent with non-zero `c_*`.

**Tasks:** (i) bound carry depth for `(3,10)`; (ii) prove periodicity of
`v ↦ g(v)` on each digit-length stratum; (iii) compute `T` and `ρ̃_ℓ` for
`ℓ mod T` numerically then prove.

### Route LM-B — Delange push-through (hard)

- Peter (2002) + Delange (1975) give log-periodic fluctuation for **summatory**
  functions of `s_b(n^k)`. Attempt to push to `h_j ∘ g` via Mellin–Perron.
- **Obstacle:** `h_j` is not a digital function of `n`; it is a function of
  **orbit** of `n`. No theorem in [13]–[15] covers this composition.
- **Possible sub-lemma:** if `g(v)` depends only on `v mod b^L`, then `h_j`
  is a digital function of the **digits of `v`** — reduces to LM-A.

### Route LM-C — Two-scale subsequence (medium)

- Exhibit two infinite subsequences `V_n = 10^{3n}` and `V'_n = 10^{3n+1}` with
  `Ψ_{18}(V_n) − Ψ_{18}(V'_n) ≥ c` for explicit `c` from limit of exact
  finite computations + periodicity lemma.
- **Weaker than full LM** but enough for Conjecture 10.6 if bridge is proved.

### Route LM-D — Refutation search (sanity)

- If `Ψ_{18}(V) → L` exists, predict `L` from Gaussian sweep; test against
  `local_mean` at `V = 10^8, 10^9` (compute). A convergence trend would
  **refute** LM and force revision of 10.6.

---

## 5. Candidate lemmas (precise statements)

### Lemma 1 — G4-finite (in-house)

> Fix `k≥2`, `b≥2`, `M = M(k,b)`. There exists `T(k,b) ∈ ℕ` such that for all
> `v ≥ b^T`, the first landing `g(v) ∈ [1,M]` depends only on the residue
> `v mod b^T`. Consequently `a(v) = a(v + m·b^T)` on each feeding progression.

*Closes G4 for bridge.* Proof: finite preimages + contraction.

### Lemma 2 — LM-shadow (conditional on carry bound)

> Under Lemma 1, for `(3,10)` and attractor `18`, the sequence
> `(Ψ_{18}(10^n))_{n≥2}` is a weighted average of `ρ̃_n` and `ρ̃_{n+1}`
> with weights in `[0.4, 0.6]`, where `(ρ̃_ℓ)` is periodic in `ℓ` with period `T`
> and amplitude `≥ 0.3`.

*Implies LM-pilot* with `c ≥ 0.3` (consistent with observed `0.315`).

### Lemma 3 — G2d-weak (sandwich LLT)

> For `n` uniform in `N_D^{(r)}`, the law of `s_{10}(n³)` is sandwiched between
> two Gaussian mixtures with the same weights `w_L(D)` and means `μ_L`, variances
> `σ_L^2(1 ± ε_L(D))` with `ε_L(D) → 0` as `D → ∞` uniformly on finitely many `L`.

*Sufficient for bridge* if `ε_L(D) = o(1)` and G4 holds.

### Lemma 4 — CLT-on-band (citable now)

> For `P(n)=n³`, `f=s_{10}$, the set `Ω_{D,r} = N_D ∩ (r+9ℤ)` satisfies the
> BK-Property of [15] Def. 8.3.11; hence `Σ_{n∈Ω_{D,r}} f(P(n))` obeys CLT
> with variance `Θ(|Ω_{D,r}| D)`.

*Closes G2c CLT leg* — write-up only, no new mathematics.

---

## 6. Literature to read next

| Reference | Relevance |
|-----------|-----------|
| **Mauduit–Rivat (2009)** *Ann. Inst. Fourier* — `s_q(n²)` LLT | Template for k=2; shows what a full G2d proof might look like |
| **Drmota–Mauduit–Rivat (2011)** [9] Problem 2, §3–4 | Direct attack on G2d-A |
| **Peter (2002)** *Acta Arith.* 104 | Summatory `s_q(⌊α n^k⌋)`; mean/variance for LM-B |
| **Bassily–Kátai (1995)** | BK-Property backbone for Lemma 4 |
| **Suria (2020?)** / **Koninck–Luca** digit sums of polynomials | Alternative CLT/LLT routes |
| **Gelfond (1952)** / **Delange (1975)** | Log-periodic framework; not directly for `h_j` |
| **Hare–Laishram–Stoll (2011)** | Size bounds; does not replace G2d |
| **Dartyge–Tenenbaum** | Digit-sum in APs at composite moduli — weak input for AP step |

---

## 7. Four-week programme (single researcher)

### Week 1 — Finite dynamics formalisation

1. Prove **Lemma 1 (G4-finite)**: carry depth + periodicity of `g(v)`.
2. Export `first_landing(v)` in `src/dspm/predict.py` or `dynamics.py`.
3. Numerical: compute `ρ̃_ℓ` for `ℓ = 1…20` on image lattice via exact
   enumeration; check periodicity onset.

### Week 2 — LM-shadow

4. Draft **Lemma 2** proof conditional on Week 1.
5. Extend `lm_deterministic.py` to report `ρ̃_ℓ` for `ℓ ≤ 20` and
   `w_ℓ(V)` at `V = 10^n`.
6. Optional: run `local_mean` at `V_max = 10^8` for one decade (compute budget).

### Week 3 — Bridge closure

7. Write **Lemma 4** (CLT citation note) in `llt_bands.md` as numbered lemma.
8. Combine G4-finite + G2d-weak **or** document G2d as explicit hypothesis.
9. Update `bridge_lemma.md` error budget with explicit `o(1)` terms.

### Week 4 — G2d or external

10. Attempt **Route G2d-C** (layer covariance) for `(3,10)` only.
11. If blocked, prepare 2-page **problem sheet** for external expert (Problem 2
    specialist).
12. Update `proof_pilot_3_10.md` checklist; do not promote to paper without review.

---

## 8. What not to do

- Do not cite [9] Thm 2 as LLT for `b=10`, `k=3`.
- Do not claim decade gap `0.315` is a proof of LM.
- Do not reuse retracted thin-window Delange lemma (Appendix B).
- Do not merge sidecar lemmas into `paper/en/paper.md` until external review.

---

*Draft v1 — 2026-09-01. Revise after specialist review.*
