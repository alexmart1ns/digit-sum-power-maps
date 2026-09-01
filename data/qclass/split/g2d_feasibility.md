# G2d feasibility memo — pilot (3,10)

Sidecar only. Week 3 deliverable per [`EXECUTION_PLAN.md`](EXECUTION_PLAN.md).

---

## 1. Question

Can we cite a published theorem for **pointwise** local limit

`P(s_{10}(n³) = v) ≈ w_L(D) · φ_L(v; μ_L, σ_L)`

on dyadic bands `N_D^{(r)}`?

---

## 2. Literature verdict (unchanged from [`llt_bands.md`](llt_bands.md))

| Source | What it gives | LLT for `n³` at `b=10`? |
|--------|---------------|-------------------------|
| [9] DMR 2011 Thm 2 | AP equidistribution, prime `q` large | **No** — not pointwise; not `q=10` |
| [9] Problem 2 | Pointwise near mean | **Open** for `deg ≥ 3` |
| [15] Thm 8.3.13 | CLT on BK subsequences | **CLT yes** — not LLT |
| [15] Thm 8.3.17 | Local limit completely additive `f` | **No** — wrong subsequence |
| Mauduit–Rivat `n²` | Full local limit template | **No** — degree 2 only |
| Peter 2002 | Summatory `s_q(⌊αn^k⌋)` | **No** — mean/variance, not point mass |

**Conclusion:** G2d **cannot** be closed by citation. Must prove directly or
maintain Hypothesis LLT.

---

## 3. Feasible attack paths (ranked)

| Rank | Route | Effort | Outcome |
|------|-------|--------|---------|
| 1 | **Conditional bridge** — assume LLT; prove Lemma B+C+D | Medium | Publishable conditional chain |
| 2 | **G2d-C** — digit-layer covariance for `k=3`, `b=10` | High | Pilot-specific LLT |
| 3 | **G2d-A** — extend DMR Problem 2 methods | Research | General `deg≥3` |
| 4 | **CLT only** — document insufficiency for bridge | Low | Honest gap statement |

---

## 4. CLT → LLT gap (why CLT is insufficient)

CLT gives interval probabilities `P(a ≤ s_{10}(n³) ≤ b)`. Bridge needs
**point masses** at integer `v` to convolve with fixed labelling `a(v)`.
Discretisation error per point is `O(1/σ_L) = O(1/√D)`; with `O(√D)` points
in window, total error **may** blow up without uniform local limit.

**Pilot empirical:** MAE `≈0.002` suggests LLT holds in practice — motivates
Hypothesis LLT, not proof.

---

## 5. G2b input (Peter 2002)

Peter (*Acta Arith.* **104** (2002), 85–96) establishes Delange-type
asymptotics for `Σ_{n≤x} s_q(⌊α n^k⌋)`. For `q=10`, `k=3`:

- Main term + log-periodic fluctuation in **summatory** function
- Supplies mean `μ_L` and variance `σ_L²` scaling for Gaussian mixture (G2b)
- Does **not** give `P(s_{10}(n³)=v)` for single `v`

**Use in repo:** validate `digit_count_mixture` / `predict_split` scaling;
not a substitute for G2d.

---

## 6. Recommendation

1. **Short term:** package **conditional theorem** (Hypothesis LLT + Lemma B +
   Lemma C empirical + Lemma D depth) in [`lemma.md`](lemma.md).
2. **Medium term:** pursue G2d-C (layer covariance) for `(3,10)` only.
3. **Long term:** external collaboration on [9] Problem 2 for general `k≥3`.

---

*2026-09-01. Sidecar only.*
