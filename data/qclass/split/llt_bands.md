# G2: LLT on dyadic bands N_D (sidecar draft)

Formalizes gap **G2** from [`bridge_lemma.md`](bridge_lemma.md). Not a theorem —
a precise statement to extract from Drmota–Mauduit–Rivat [9] for the pilot
`(k,b)=(3,10)` and a template for general `k`.

Paper reference: Hypothesis LLT in §10 (`paper/en/paper.md`).

---

## 1. Bands and progressions

Fix `b ≥ 2`, `k ≥ 2`, `m = b − 1`. The **D-digit band** is

`N_D = { n ∈ ℤ⁺ : b^{D−1} ≤ n < b^D }`.

For `r ∈ {0,…,m−1}`, the **progression slice** is

`N_D^{(r)} = N_D ∩ (r + mℤ)`.

Casting out nines: `S_b(n^k) ≡ n^k (mod m)` for all `n`. On each slice feeding a
split signature, mass of `S_b(n^k)` lies on `v ≡ r^k (mod m)` (image lattice).

---

## 2. Target statement (Lemma G2 — to prove from [9])

**Lemma G2 (band-restricted LLT; monomial).** Let `k ≥ 2`, `b ≥ 2`, `r mod m`
feed a signature with `a_i ≥ 2`. For `n` uniform on `N_D^{(r)}` as `D → ∞`:

1. **Mean and variance:** `E[S_b(n^k)] = μ_D` with `μ_D / D → (b−1)/2 · k` (leading
   digit-count mixture), and `Var(S_b(n^k)) = Θ(D)`.

2. **Local CLT:** with `σ_D = √Var(S_b(n^k))`, for every fixed `C`,

   `sup_{|v−μ_D| ≤ C σ_D} | σ_D · P(S_b(n^k)=v) − φ((v−μ_D)/σ_D) | → 0`.

3. **Tail:** `P(|S_b(n^k) − μ_D| > C σ_D) → 0` uniformly in `D` as `C → ∞`.

4. **Lattice:** all mass on `v ≡ r^k (mod m)`.

**Status:** Standard LLT for polynomial digit sums [9] is stated for intervals
`[1,x]` or full ranges; **G2** requires verifying that restriction to the
thin dyadic band `N_D` and fixed progression `r` preserves the local limit
uniformly in `D`.

---

## 3. Reduction recipe (DMR → G2)

| Step | Action | Citation / note |
|------|--------|-----------------|
| 1 | Express `|N_D^{(r)}| = (b^D − b^{D−1})/m + O(1)` | Equidistribution of residues in band |
| 2 | Relate `n^k` digit length mixture to `μ_D, σ_D` | `digit_count_mixture` in `predict.py` |
| 3 | Apply DMR local limit on each length layer `L` | [9], Theorem-level CLT for `s_b(n^k)` |
| 4 | Combine layers with weights `w_L(D)` | Convolution of Gaussians → mixture |
| 5 | Restrict to `v ≡ r^k (mod m)` | Exact congruence, not approximate |

**Gap G2a:** DMR does not literally state “uniform in dyadic band index `D`”;
need to track error terms when `x` runs through `b^D` with `D → ∞`.

**Gap G2b:** Independence of digit layers in the Gaussian model is the
mechanistic approximation of §7.5; rigorous proof may need covariance bounds
from [9] or [15].

---

## 4. Pilot (3,10)

- Feeding residues for `{0}`: `r ∈ {0,3,6}` (all `≡ 0 mod 3`).
- Image lattice: `v ≡ 0 (mod 9)`.
- DMR applies to `S_{10}(n^3)`; Hypothesis LLT in the paper is the operational
  form.

**Deliverable for closed G2:** a lemma citing [9] with explicit error
`O(D^{-1/2} log D)` or similar on each `N_D^{(r)}`, sufficient for bridge
Proposition in `bridge_lemma.md`.

---

## 5. What G2 enables

Once G2 is proved for all feeding `r` of a split signature:

`P(S_b(n^k) = v | n ∈ N_D^{(r)})` ≈ Gaussian mixture on the image lattice.

Convolution with the deterministic labelling `a(v)` and summation over `r` yields
the bridge `δ_j(D) = F_j(D) + o(1)` (modulo gap G4 on first landing).

---

## 6. What [9] actually proves (scope check)

Drmota–Mauduit–Rivat, *J. London Math. Soc.* **84**(1) (2011), 81–102 ([arXiv:1001.4169](https://arxiv.org/abs/1001.4169)):

| Result in [9] | Statement (paraphrase) | Usable for G2? |
|---------------|------------------------|----------------|
| Main theorem | For large prime `q` with `(a_h,q)=1`, equidistribution of `s_q(P(n))` in AP mod `m`: count = `N/m · Q*(g,d) + O(N^{1−σ})` | **AP yes**; base `q` large prime |
| Monomial remark | Improved lower bounds for `P(x)=x^h`, `h≥3` | Supports density, not LLT |
| Irrational rotation | Uniform distribution of `{α s_q(P(n))}` for `α ∉ ℚ` when `q` large prime | Suggests **fluctuation** of digit sums |

**Pilot `(3,10)`:** base `10` is **composite**; [9] as stated targets large **prime** bases. The paper's Hypothesis LLT treats [9] as the **analytic input** for the monomial family at `b=10` — consistent with applied use in §7.5, but G2 must either:

- (a) cite a composite-base extension (survey / [15]), or  
- (b) prove G2 directly for `b=10`, `k=3` from digit-layer methods.

**Gap G2c (new):** formal citation chain for **composite** `b=10`, not only prime `q` in [9].

---

## 7. Lemma G2-band (band vs interval; draft)

**Lemma G2-band.** For fixed `b ≥ 2`, modulus `m`, and residue `r`, let

`N_D^{(r)} = N_D ∩ (r + mℤ) = { n : b^{D-1} ≤ n < b^D, n ≡ r (mod m) }`.

Then

`|N_D^{(r)}| = (b^D − b^{D-1})/m + O(1)`.

**Corollary (error transfer).** Suppose a counting estimate on `[1, N]` has
form `count = density · N + O(N^{1−σ})` with `σ > 0`. Restricting to
`N_D^{(r)}` with `N = b^D` yields error `O(b^{D(1−σ)}) = o(b^D)`.

*Proof sketch.* Each residue class contributes `(b^D − b^{D-1})/m` integers in
the band, up to `O(1)` boundary correction at `n = b^{D-1}`.

**Use:** Reduces G2a (LLT on `N_D^{(r)}`) to verifying DMR-type bounds on
initial segments `n < b^D` restricted to progressions, not only global `[1,N]`.

**Status:** Combinatorial; ready to promote as numbered input lemma once G2c
(composite base `b=10`) is resolved (§6).

---

## 8. Next actions

1. ~~Locate DMR theorem~~ — Main equidistribution theorem + prime-base caveat (§6).
2. Write band-to-interval lemma (§7) as numbered sidecar lemma.
3. For pilot: either find composite-base LLT in [15] or prove CLT for `s_{10}(n^3)`
   on `N_D^{(r)}` directly (Peter 2002 for summatory function).
4. Only after (2)–(3): promote G2 from sidecar to paper §10 as “Lemma (input)”.
