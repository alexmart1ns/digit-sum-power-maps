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

*2026-09-01. Sidecar only.*
