# Bridge lemma: δ_j(D) = F_j(D) + o(1) (sidecar draft)

Not peer-reviewed. Does not modify `paper/en/paper.md` until external review.

Cross-refs: [`lemma.md`](lemma.md) (conditional non-convergence), [`checks/LITERATURE.md`](../checks/LITERATURE.md) (LM verdict).

---

## 0. Setup (monomial case f_{k,b})

Fix `k ≥ 2`, `b ≥ 2`, `m = b − 1`. Let `f(n) = S_b(n^k)`, `M = M(k,b)` the
contraction threshold, `g(v)` the first iterate inside `[1,M]`, and `a(v)` the
attractor label. For signature `γ_i` with modular weight `p_i`, define

`δ_j(D) = #{ n ∈ N_D : first landing in A_j } / |N_D|`

where `N_D = { n : b^{D-1} ≤ n < b^D }`.

`F_j(D)` is the output of `predict_split(D, ·)` in [`src/dspm/predict.py`](../../../src/dspm/predict.py):
digit-count mixture × Gaussian LLT on **image lattice** `v ≡ r^k (mod m)` ×
labelling `a(v)`, scaled by `p_i`.

---

## 1. Hypothesis LLT(k,b,r)

For each residue `r` feeding signature `γ_i` (`a_i ≥ 2`), and `n` uniform on
`N_D ∩ (r + mℤ)`, the law of `S_b(n^k)` admits a Gaussian approximation

`P( S_b(n^k) = v ) ≈ w_L(D) · φ_L(v; μ_L, σ_L)`

with `μ_L = (b−1)L/2`, `σ_L = √{L(b²−1)/12}`, and mixture weights `w_L(D)` from
`digit_count_mixture(D,k,b)` (continuous band overlap model).

**Status:** **Hypothesis** — not citable as theorem. CLT leg may cite [15] §8.3.2;
pointwise LLT (G2d) is **open** for `k≥3` at `b=10` ([9] Problem 2; see
[`llt_bands.md`](llt_bands.md) §6.3). Do not cite [9] Thm 2 as LLT for composite base.

---

## 2. Proposition (bridge; draft)

**Statement (mechanistic bridge).** Assume Hypothesis LLT(k,b,r) for every
feeding residue `r` of signature `γ_i`. Let `A_j` be an attractor of that
signature. Then

`δ_j(D) = F_j(D) + o(1)`  as `D → ∞`,

where `F_j` is the functional implemented by `predict_split` (no fitted parameters).

**Proof sketch (gap list explicit).**

1. **Decompose by residue.** `N_D = ⊔_r (N_D ∩ (r+mℤ))`. By equidistribution
   of digit-length bands, mass on each progression is `p_r + o(1)` with
   `Σ p_r = p_i`.

2. **Pushforward under n ↦ S_b(n^k).** LLT gives a mixture of Gaussians on
   integers `v`, with mass on the arithmetic progression `v ≡ r^k (mod m)`
   (casting out nines: `S_b(n^k) ≡ n^k (mod m)`). **Errata B.5:** use image
   lattice `r^k`, not `r`.

3. **First landing.** For `v` in the Gaussian window, `g(v)` is computed from
   the finite dynamics on `[1,M]`. The exact labelling `a(v)` is piecewise
   constant on attractor basins in the trapping region.

4. **Convolution.** `δ_j(D)` equals the modular weight times the fraction of
   the Gaussian mixture landing on `{ v : a(v) = j }`, which is exactly the
   integral discretization coded in `predict_split`.

5. **Error budget (named gaps).**
   - **(G1)** Replace discrete `n` by continuous band overlap: `o(1)` from
     boundary effects of `digit_count_mixture` (controlled for fixed `D` growth).
   - **(G2)** Gaussian LLT remainder on each progression: `o(1)` from [9] if
     uniform in `D` on dyadic bands — **not yet formalized** for our `N_D`.
   - **(G3)** Truncation at `μ ± 6σ` in code: exponential tail bound.
   - **(G4)** Identification of “first landing” mass with `a(v)` on the window:
     see **§7 (Lemma D-revised)** — bounded depth `≤2`, no simple `b^T` periodicity.

**Status:** Sketch with gaps **G2d** (pointwise LLT) the main analytic blocker.
**G4** partially closed via bounded-depth lemma. Empirically: MAE ≈ 0.002 on
`(3,10)` (audit_05, split_scale 120k samples).

---

## 7. Lemma D-revised (G4; bounded landing depth)

Cross-ref: [`lemma_d_g4.md`](lemma_d_g4.md), [`g4_landing_latest.md`](g4_landing_latest.md).

**Lemma D-depth (pilot).** For `(k,b)=(3,10)`, `M=57`, every `v ≥ 1` reaches
`[1,M]` under at most **2** applications of `f_{3,10}`. API: `first_landing(v)`
in `src/dspm/predict.py`.

*Evidence:* `scripts/g4_landing.py` on `v ≤ 10^6`: `max_steps = 2`.

**Corollary (bridge step 3).** For `v` in the LLT window at scale `D`, the label
`a(v)` depends on `v` only through finitely many base-`10` digits altered by
at most two digit-sum maps. This replaces the retracted naive periodicity
`a(v) = a(v + 9·b^T)` (falsified: ~47% mismatch at `T=1`).

**Remaining G4 gap:** show the Gaussian-window mass on `{v : a(v)=j}` equals the
first-landing mass up to `o(1)` — needs G2d or CLT sandwich + tail bounds (G3).

**Bridge impact:** Step 3 of §2 is **conditional on G2d**; G4 reduces to
finite-digit sufficiency, not full identification.

---

## 3. Lemma (conditional non-convergence; see lemma.md)

If, in addition, **Hypothesis LM(k,b,j)** holds for each attractor `A_j` of the
signature (`Ψ_j(V)` does not converge), then `lim_{D→∞} δ_j(D)` does not exist.

**Proof idea (conditional).** Bridge gives `δ_j(D) = F_j(D) + o(1)`. LM forces
`F_j` (hence `δ_j`) to inherit non-convergent window behaviour of `Ψ_j` along
`V ≈ Θ(b^D)`. Cumulative density on `[1,b^D]` follows from geometric band
weights `1 − 1/b` (§7.5).

---

## 4. Q-class variant

For `Q ∈ ℤ[x]` replace `r^k` by `Q(r) mod m` and `predict_split` by
`predict_split_Q` in [`src/dspm/qmaps.py`](../../../src/dspm/qmaps.py). The
same bridge structure applies; LLT for general `Q` is **open** (Hare–Laishram–Stoll
gives size bounds only).

Monomial bridge: `monomial_compare_latest.md` (classic ≡ sidecar for k=3,4).

---

## 5. What this does NOT claim

- No single Delange factor `P_j({log_b D})` with `δ_j = P_j + o(1)` (decade
  collapse fails; `label_sweep_k3_b10_sig0_D300_latest.md`).
- LM is **not** proved by bridge agreement (Gaussian vs Fourier at noise floor).
- Non-convergence of `δ_j` is **conditional** on LM until a new lemma is proved.

---

## 6. Next analytic steps

| ID | Task |
|----|------|
| G2d | Pointwise LLT — see [`g2d_feasibility.md`](g2d_feasibility.md) |
| G2b | Peter (2002) summatory input — see §9 below |
| LM | Lemma C empirical done; analytic proof open — [`lemma_c_oscillation.md`](lemma_c_oscillation.md) |
| G4 | Depth lemma done; window identification needs G2d — §7 `bridge_lemma.md` |
| Q | Extend LLT input beyond monomials |

---

## 9. G2b — Peter (2002) summatory input

J. Peter, *On the parity of exponents in the factorization of sums of digits*,
*Acta Arith.* **104** (2002), 85–96 (cited in [9], [15]).

**What it gives:** Delange-type asymptotics for `Σ_{n≤x} s_q(⌊α n^k⌋)` at any
`q ≥ 2` (CRT over prime powers). Main term plus **log-periodic** fluctuation.

| Use in repo | Status |
|-------------|--------|
| Mean/variance scaling of Gaussian mixture in `predict_split` | Mechanistic validation |
| Digit-layer covariance bounds (G2b) | **Open** — extract from Peter's error terms |
| Pointwise LLT (G2d) | **Does not supply** |

**Pilot note:** Peter (2002) supports the **log-periodic philosophy** behind
oscillating `ρ_n` in Lemma C but does not prove LM for labelling `h_j`.
