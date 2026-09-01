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

**Status:** Input from Drmota–Mauduit–Rivat [9] for monomials, restricted to
dyadic bands and progressions. Not claimed as a theorem in the paper.

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
     requires `M` fixed and `v` large enough; standard for the pilot.

**Status:** Sketch with gaps **G2** (uniform LLT on bands) and **G4** (landing
vs label) the main analytic work. Empirically: MAE ≈ 0.002 on `(3,10)` (audit_05,
split_scale 120k samples).

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
  collapse fails; `label_sweep_latest.md`).
- LM is **not** proved by bridge agreement (Gaussian vs Fourier at noise floor).
- Non-convergence of `δ_j` is **conditional** on LM until a new lemma is proved.

---

## 6. Next analytic steps

| ID | Task |
|----|------|
| G2 | Formalize DMR restriction to `N_D^(r)` with explicit `o(1)` |
| LM | Prove or refute LM for pilot labelling `h_{18}, h_{27}` |
| Q | Extend LLT input beyond monomials |
