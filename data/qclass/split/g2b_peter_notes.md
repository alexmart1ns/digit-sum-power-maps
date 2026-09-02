# G2b notes — Peter (2002) and Route C-B

Sidecar only. Extends [`g2d_feasibility.md`](g2d_feasibility.md) §5 for
Lemma C / Route C-B.

**Reference:** J. Peter, *On the parity of exponents in the factorization of sums
of digits*, *Acta Arith.* **104** (2002), 85–96.

---

## 1. What Peter gives (for general `q`, `k`)

Summatory asymptotics for `Σ_{n≤x} s_q(⌊α n^k⌋)`:

`Σ_{n≤x} s_q(⌊α n^k⌋) = x · main(α,k,q) + x^{ε} · periodic(log x) + O(1)`

- **Main term:** explicit constant depending on `α, k, q`
- **Periodic part:** log-periodic in `x` (Delange-type)
- **CRT:** valid for composite `q` (including `q=10`)

---

## 2. Pilot instantiation `(k,b)=(3,10)`

Take `Q(n)=n³`, `s_{10}(n³)`, feeding residues `{0,3,6}`.

| G2b target | Peter input | Usable for Lemma C? |
|------------|-------------|---------------------|
| Mean digit-sum per layer `L` | Main term scaling | Validates `μ_L` in `predict_split` |
| Variance `σ_L²` | Second moment methods in Peter + [15] | Mechanistic G2b |
| Covariance across layers | **Not explicit** in Peter — must extract | **Open** |
| Suffix mixture weights `α_n(s)` | Indirect via digit-length geometry | Route C-A empirical |
| Log-periodic `ρ_n(s)` phase | Periodic fluctuation philosophy | **Qualitative only** |

---

## 3. Route C-B programme

**Goal:** show `ρ_n(s)` inherits log-periodic structure from `s_{10}(n³)` layer
sums, preventing `ρ_n(s) → L_s` for each suffix class.

**Steps:**

1. Write `s_{10}(v³)` as sum of dependent digit-layer contributions (cf. [15] §8.2).
2. Apply Peter-type expansion to **partial sums** restricted to
   `{v : |v|=n, v≡s (mod 100)}` on the window — requires new summatory setup.
3. Extract leading oscillatory term `A_s · cos(ω log n + φ_s)` for class rates.
4. Combine with Lemma B: `Ψ_{18}(10^n) ≈ (ρ_n + ρ_{n+1})/2` oscillates.

**Blocker:** Peter is **summatory on n**, not on **window-local v** with fixed
digit length. Bridging window geometry → Peter expansion is the research step.

---

## 4. Honest verdict

| Route | Delivers | Does not deliver |
|-------|----------|------------------|
| C-A mixture | Mechanism + witness pair `c≥0.12` | `limsup≠liminf` theorem |
| C-B / G2b | Path to log-periodic `ρ_n(s)` | Pointwise LLT (G2d) |
| G2d | Bridge `δ=F+o(1)` | LM directly |

**Recommendation:** publish conditional chain; pursue C-B as analytic Lemma C
with external analytic number theorist.

---

## 5. G2b scaling check (pilot mechanistic)

`predict_split` uses `digit_count_mixture(D,k,b)` weights `w_L` and per-layer
Gaussian parameters (CLT / [15] §8.3.13 template):

- `μ_L = (b−1)/2 · L`  (mean digit sum at layer `L`; for `b=10`, `μ_L = 4.5 L`)
- `σ_L² = L · (b²−1)/12`  (variance; for `b=10`, `σ_L² = 8.25 L`)

Peter (2002) gives the same **Θ(L)** main term and **Θ(√L)** fluctuation scale
for summatory `Σ s_{10}(⌊α n³⌋)`; the mixture in `src/dspm/predict.py` is the
discrete digit-length analogue used in §7.5.

**What this validates:** G2b mean/variance scaling in `F_j` — already consistent
with bridge MAE `≈0.0017` on `D≤90`.

**What remains open:** covariance across layers and suffix-restricted partial
sums (Route C-B §3 steps 2–3); Peter does not supply point masses for
`P(s_{10}(n³)=v)` (G2d).

---

## 6. Layer covariance pilot (empirical)

**Compute:** `scripts/lm_g2b_layer.py` → [`g2b_layer_cov_latest.md`](g2b_layer_cov_latest.md)

At decade anchors `V=10^n`, `n=9…16`, labelling rates `ρ(L=n)` and `ρ(L=n+1)` on
the same window show **Pearson r ≈ 0.62** (co-movement). Lag-1 autocorrelation of
`ρ(L=n)` across decades is **≈ 0.63**. Mean `|ρ(L=n) − ρ(L=n+1)| ≈ 0.11`.

**Interpretation:** `predict_split` convolves **independent** per-layer Gaussians;
this pilot detects **positive layer correlation** in the landing labelling rates.
That supports Route C-B phenomenology (log-periodic / correlated layer structure)
without proving a Peter-type expansion on suffix-restricted windows.

Two-stratum `Ψ̂ = w_n ρ_n + w_{n+1} ρ_{n+1}` matches `Ψ` exactly (error 0) because
only layers `{n,n+1}` carry mass — correlation is **within** the two-layer support,
not captured by independent-mixture semantics at the suffix level.

---

## 7. Suffix log-periodic pilot (Route C-B step 2)

**Compute:** `scripts/lm_g2b_suffix.py` → [`g2b_suffix_phase_latest.md`](g2b_suffix_phase_latest.md)

Witness suffixes `50, 55, 95` on `n=9…16`: each shows amplitude range **0.31–0.40**
and a cosine-in-`n` fit (best period **7**) beats the constant model (SSE gain
**0.02–0.07**). Verdict: **`log_periodic_phenomenology`** (empirical).

Witness gaps on eight decades: `[50,95]` min **0.097**; `[50,55]` min **0.058**
(weaker uniform witness than Route C-A on `n≤14` alone).

**Honest limit:** cosine fit in discrete `n` is a phenomenological proxy for
Peter log-periodicity in `log V`; not a summatory theorem on
`Σ_{v≡s (mod 100)} h(v)`.

---

*2026-09-01. Sidecar only; §5–7 added 2026-09-02.*
