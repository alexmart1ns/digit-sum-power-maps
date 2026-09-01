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
| 3 | CLT on polynomial subsequence; LLT per layer `L` | CLT: [15] §8.3.2; LLT: **G2d** (direct) |
| 4 | Combine layers with weights `w_L(D)` | Convolution of Gaussians → mixture |
| 5 | Restrict to `v ≡ r^k (mod m)` | Exact congruence, not approximate |

**Gap G2a:** DMR does not literally state “uniform in dyadic band index `D`”;
need to track error terms when `x` runs through `b^D` with `D → ∞`.

**Gap G2b:** Independence of digit layers in the Gaussian model is the
mechanistic approximation of §7.5; rigorous proof may need covariance bounds
from Peter (2002) or digit-layer methods in [15] §8.2.

**Gap G2c / G2d:** see §6.3 and gap table in §8.

---

## 4. Pilot (3,10)

- Feeding residues for `{0}`: `r ∈ {0,3,6}` (all `≡ 0 mod 3`).
- Image lattice: `v ≡ 0 (mod 9)`.
- CLT for `S_{10}(n³)`: [15] Thm 8.3.13 + Ex. 8.3.15 (composite base OK).
- LLT (Hypothesis LLT): **no citation** — G2d; paper §7.5 uses mechanistic Gaussian.

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

## 6. What [9] and [15] actually prove (scope check)

### 6.1 [9] DMR 2011 — prime base, degree ≥ 3

Drmota–Mauduit–Rivat, *J. London Math. Soc.* **84**(1) (2011), 81–102
([arXiv:1001.4169](https://arxiv.org/abs/1001.4169)):

| Result in [9] | Statement (paraphrase) | Usable for G2? |
|---------------|------------------------|----------------|
| **Thm 1** | Uniform distribution mod 1 of `{α s_q(P(n))}` for irrational `α`, large prime `q`, `(a_d,q)=1` | Fluctuation input only |
| **Thm 2** | AP equidistribution: `#{n≤x : s_q(P(n))≡a mod m} = x/m·Q(a,D) + O(x^{1−σ})` for large prime `q` | **AP yes**; not pointwise LLT |
| **Thm 3** | Irrational rotation criterion (same prime-base regime) | Not LLT |
| **Remark 2** | Prime/`(a_d,q)=1` hypotheses are **not essential**; proof extends to general `q ≥ q₀(d)` but is more technical | Does **not** cover small `q` like `10` |
| **Problem 2** | Pointwise count `#{n≤x : s_q(P(n))=k}` with `k` near mean: solved for `deg P=2`; **open for `deg P≥3`** even when `q` is large prime | **Blocks LLT citation at `k=3`** |

DMR explicitly state (Problem 2, §2) that estimate (2.1) is **not uniform in `α`**, so their Fourier bounds do not yield a local limit for cubic monomials in any base. The paper's Hypothesis LLT cites [9] as mechanistic philosophy; a literal citation chain for `S_{10}(n³)` does **not** exist in [9].

### 6.2 [15] Drmota–Grabner 2010 — composite base, but CLT not LLT

Chapter 9, *Analysis of Digital Functions and Applications*, in Berthé–Rigo
(eds.), *Combinatorics, Automata and Number Theory*, Cambridge Univ. Press
2010 (Encycl. Math. Appl. **135**), pp. 452–504:

| Result in [15] | Location | Statement (paraphrase) | Usable for G2? |
|----------------|----------|------------------------|----------------|
| **Thm 8.3.10** | §8.3.2 | CLT for `f(P(n))` on initial segments, **any `q≥2`**, via Bassily–Kátai (1995) | **CLT yes** for `S_{10}(n³)` |
| **Thm 8.3.13** | §8.3.2 | CLT for any subsequence `Ω_N` satisfying BK-Property 8.3.11 | Band/progression CLT after BK check |
| **Lemma 8.3.14 + Ex. 8.3.15** | §8.3.2 | Polynomial sets `Ω_N={P(n): n<N}` satisfy BK-Property | **Pilot CLT chain** for composite `b=10` |
| **Thm 8.3.17 / (8.66)** | §8.3.3 | **Local** Gaussian limit for completely `q`-additive `f` on `{0,…,N−1}` | **No** — full range only, not `n↦n^k` |
| **§8.4.1 closing remark** | §8.4.1 | After `s_q(n²)` (Mauduit–Rivat), main open problem is to generalise (8.71) to **`deg P≥3`**; cites DMR [9] extensions | Confirms **no LLT** in survey |
| Bassily–Kátai (1995) | cited §8.3.2 | CLT backbone; no prime-base restriction | Composite `q` included |

Peter (2002, Acta Arith. **104**, 85–96) — cited in both [9] and [15] — gives Delange-type
**summatory** asymptotics for `s_q(⌊αn^k⌋)` at **any** `q≥2` (CRT over prime powers).
Useful for mean/variance and log-periodic structure (G2b), **not** for pointwise
`P(S_q(n^k)=v)`.

### 6.3 G2c resolution (composite `b=10`)

**Verdict:** G2c splits into a **closed CLT leg** and an **open LLT leg**.

| Target | Citation path | Status |
|--------|---------------|--------|
| CLT on `N_D^{(r)}` for `S_{10}(n³)` | [15] Thm 8.3.13 + Lemma 8.3.14 + Ex. 8.3.15 (BK-Property for `P(n)=n³`); restrict to dyadic band via §7 | **Citable** (verify BK on AP slice — likely same exponential-sum input as Ex. 8.3.15) |
| AP equidistribution mod `m=9` | [9] Thm 2 **not** at `q=10`; Dartyge–Tenenbaum lower bounds only; Mauduit–Rivat covers `k=2` only | **Weak** — density, not Gaussian |
| **Local** limit (Hypothesis LLT) | Neither [9] (Problem 2 open, prime-only) nor [15] (Thm 8.3.17 is wrong subsequence) | **Must prove directly** |

**Precise resolution path for pilot `(3,10)`:**

1. **CLT (composite base):** cite [15] §8.3.2, Theorem 8.3.13 + Example 8.3.15, with
   `f=s_{10}`, `P(n)=n³`, `Ω_N = N_D^{(r)} ∩ [1,b^D)` (band + progression); combine
   with Lemma G2-band (§7) for cardinality errors.
2. **LLT (pointwise Gaussian):** **no theorem in [9] or [15]** — prove Lemma G2
   directly (digit-layer covariance bounds, or sharpen Problem 2 methods for
   `b=10`, `k=3`). Peter (2002) supplies summatory/log-periodic input only.
3. Do **not** cite [9] Thm 2 as “LLT for `b=10`”; it is AP equidistribution for
   `q ≥ exp(67·3³(log 3)²)` prime.

**Gap G2c (composite base):** **partially resolved** — CLT chain via [15] §8.3.2;
LLT still requires direct proof (feeds **G2d**).

**Gap G2d (new — local limit for `k≥3`):** Hypothesis LLT needs pointwise
`P(S_b(n^k)=v) ≈ φ(...)`. [9] Problem 2 is open for `deg≥3`; [15] Thm 8.3.17
applies only to completely additive `f` on full intervals. Bridging CLT→LLT for
polynomial subsequences at composite `b` is **not** a known citation. Empirical
Gaussian sweep in `predict_split` is mechanistic until G2d closes.

---

## 7. Lemma A (G2-band) — promoted

**Lemma A (band vs interval).** For fixed `b ≥ 2`, modulus `m`, and residue `r`, let

`N_D^{(r)} = N_D ∩ (r + mℤ) = { n : b^{D-1} ≤ n < b^D, n ≡ r (mod m) }`.

Then

`|N_D^{(r)}| = (b^D − b^{D-1})/m + O(1)`.

**Corollary A.1 (error transfer).** Suppose a counting estimate on `[1, N]` has
form `count = density · N + O(N^{1−σ})` with `σ > 0`. Restricting to
`N_D^{(r)}` with `N = b^D` yields error `O(b^{D(1−σ)}) = o(b^D)`.

*Proof.* Each residue class contributes `(b^D − b^{D-1})/m` integers in the
band, up to `O(1)` boundary correction at `n = b^{D-1}`.

**Use:** Reduces G2a to verifying bounds on initial segments `n < b^D`
restricted to progressions. CLT citation: [`clt_citation.md`](clt_citation.md).

**Status:** Combinatorial; **promoted** 2026-09-01. CLT leg cites Lemma A + [15]
§8.3.2; LLT leg still blocked on G2d.

---

## 8. Next actions

1. ~~Locate DMR theorem~~ — Thm 2 (AP), Problem 2 open for `k≥3`; prime-base
   regime (§6.1).
2. ~~Composite-base survey~~ — [15] §8.3.2 closes **CLT** for `b=10`; no LLT
   theorem (§6.2–6.3).
3. ~~Promote §7 to Lemma A~~ — done 2026-09-01; see [`clt_citation.md`](clt_citation.md).
4. **Pilot CLT:** citation note in progress — verify BK on progression slices (`clt_citation.md` checklist).
5. **Pilot LLT (G2d):** prove pointwise local limit for `s_{10}(n³)` on bands
   directly, or document why CLT + lattice discretization is insufficient for
   bridge error budget (G4 coupling).
6. Only after (3)–(5): promote G2 from sidecar to paper §10 as “Lemma (input)”.

### Gap status summary

| Gap | Description | Status |
|-----|-------------|--------|
| G2a | Uniform LLT on dyadic band index `D` | Open |
| G2b | Digit-layer covariance / Gaussian mixture | Open (mechanistic in `predict.py`) |
| G2c | Composite-base citation for `b=10` | **Partial** — CLT via [15] §8.3.2; LLT → G2d |
| G2d | Pointwise LLT for `S_b(n^k)`, `k≥3` | **Open** — not in [9] or [15]; must prove |
