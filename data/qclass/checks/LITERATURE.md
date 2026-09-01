# Isolated literature notes for the Q-class sidecar

Sources live in `C:\Users\Alex Martins\Downloads\estudo` and are **not** copied
into `data/sweeps`, `data/mining`, or `data/split`.

Paper bibliography: [13] Delange 1975; [14] Drmota 2003 (patterns); [15]
Drmota–Grabner 2010 (monograph); [9] DMR 2011 (LLT for `S_b(n^k)`).

---

## Koppelaar–Nasehpour 2020

H. Koppelaar and P. Nasehpour, *On Hardy’s Apology numbers*, Journal of
Algorithms and Computation **52**(2) (2020), 67–83. arXiv:2008.08187.

Finitude of solutions of `n = s_b(P(n))` for suitable polynomials P
(Hardy / Dudeney / Wells types), with explicit search bounds. Transferable
to **fixed points** of `S_b(Q(n))` only — not to cycles, excess, or the split.

## Hare–Laishram–Stoll 2011

K. G. Hare, S. Laishram and T. Stoll, *Stolarsky’s conjecture and the sum of
digits of polynomial values*, Proc. Amer. Math. Soc. **139** (2011), 39–49.
arXiv:1001.4169.

`liminf s_q(P(n))/s_q(n) = 0` for `deg P ≥ 2`. Class-B analytic input for
digital fluctuation of polynomial values, parallel to Mauduit–Rivat for `n^k`.
Does **not** supply LLT on dyadic bands nor LM for labelling indicators.

## Alcântara survey tables

Cycle lists for `T_{10,k}`, `2 ≤ k ≤ 10`, checked in-memory against
`build_system(k, 10)` by `scripts/qclass_check.py`. See `oeis_k2-10.json`.
Do not merge those tables into the 19.5k sweep.

---

## [13] Delange 1975 — digital fluctuation

H. Delange, *Sur la fonction sommatoire de la fonction "somme des chiffres"*,
Enseign. Math. **21** (1975), 31–47.

**What it gives:** Fourier expansions for sums of digital functions; the
summatory function of `s_b(n)` has a main term plus a **log-periodic**
fluctuation term. The periodic factor is continuous and **nowhere differentiable**
in the intended regime.

| Target | Implies LM? | Notes |
|--------|-------------|-------|
| `S_b(n)` / `s_b(n)` fluctuation | No (different object) | Classical log-periodicity of digit sums |
| `h_j(v)=1_{g(v)∈β_j}` window mean `Ψ_j(V)` | **Inconclusive** | No Delange expansion for dynamics-induced labelling |
| Thin-window lemma (retracted, paper §10) | **No** | `C^1` period-1 route false; see Appendix B remark |

**Verdict:** Delange explains why **digit sums** fluctuate log-periodically. It
does **not** automatically imply Hypothesis LM for the **fixed attractor labelling**
`h_j` on the image lattice. The retracted thin-window lemma must not be reused.

---

## [14] Drmota 2003 — patterns in digital expansions

M. Drmota, *The Distribution of Patterns in Digital Expansions*, in
P. Grabner and W. Woess (eds.), *Fractals in Graz 2001*, Birkhäuser, 2003.

**What it gives:** Pattern-counting and Mellin–Perron methods for functions of
digit strings (subword frequencies, etc.).

| Target | Implies LM? | Notes |
|--------|-------------|-------|
| Pattern frequencies in `n^k` expansion | No | Orthogonal to basin labelling |
| Bridge `δ_j = F_j + o(1)` | Partial input | Same toolbox family as [15], not a proof |

**Verdict:** Background for digital analysis; **does not** address LM or split
mass directly.

---

## [15] Drmota–Grabner 2010 — monograph

M. Drmota and P. Grabner, *Analysis of Digital Functions and Applications*,
Encyclopedia of Mathematics and Its Applications, Cambridge University Press, 2010.

**What it gives:** Systematic Mellin–Perron / Delange theory; polynomial digit-sum
asymptotics; connections to [9] for `S_b(n^k)`.

| Target | Implies LM? | Notes |
|--------|-------------|-------|
| LLT for `S_b(n^k)` on progressions | **Yes (input)** | Via DMR [9] restriction to bands |
| Non-convergence of `Ψ_j` for labelling | **Inconclusive** | Book treats digit sums / digital functions, not `h_j∘g` |
| `F_j` Gaussian sweep | Mechanistic only | Numerical Mellin–Perron philosophy, not theorem |

**Verdict:** Supports **Hypothesis LLT** for monomials and the **plausibility** of
log-periodic structure in the driving variable `m_1=S_b(n^k)`. Does **not** close
LM or the bridge lemma without a new statement about the labelling map `g`.

---

## [9] DMR 2011 (cross-reference)

M. Drmota, C. Mauduit, J. Rivat, *The sum-of-digits function of polynomial
sequences*, J. London Math. Soc. **84** (2011), 81–102.

Local limit theorem for `S_b(n^k)` — the analytic input for LLT on the pilot
`(k,b)=(3,10)`. Must be restricted to dyadic bands `N_D` and progressions
`n ≡ r (mod m)` feeding the split signature.

---

## Computational diagnostic: `local_mean` (Hypothesis LM)

Script: `scripts/local_mean.py`. Latest: `data/split/local_mean_latest.md`.

Pilot `(3,10)`, signature `{0}`, `V ∈ [100, 10^7]`:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Pearson `Ψ(V)` vs `Ψ(bV)` | **0.567** | Neither confirms period-1 collapse nor strong LM |
| MAE decade collapse | **0.089** | On order of within-scale amplitude (~0.12 sd) |
| Amplitude base / shifted | 0.668 / 0.521 | Phase drift across decades |

**What compute does NOT establish:**

1. Comparing Fourier vs Gaussian MAE (both at noise floor) — see paper §10.
2. A single Pearson threshold — inconclusive band between Delange and LM.
3. LM as theorem — only motivates **Hypothesis LM** as an explicit gap.

**Extended note (D=1000 Gaussian sweep, sidecar only):** cross-decade phase
Pearson drops to **0.26** for `D ≤ 1000` vs **0.735** for `D ≤ 300` (paper).
Amplitude survives; long-scale phase stability remains open.

---

## Final verdict on Hypothesis LM (B1 exit criterion)

| Option | Status |
|--------|--------|
| (i) LM reducible to [13]–[15] as stated | **No** — literature covers digit sums, not `h_j` |
| (ii) New lemma required | **Yes** — dynamics-induced labelling on image lattice |
| (iii) Remains computational hypothesis | **Yes** — `local_mean` diagnoses, does not prove |

**Recommended formulation:** keep LM as an **explicit hypothesis** (paper §10),
with sidecar notes (`lemma.md`, `bridge_lemma.md`) separating LLT input [9],
bridge `δ_j=F_j+o(1)`, and LM as the unique analytic gap for Conjecture 10.6.
