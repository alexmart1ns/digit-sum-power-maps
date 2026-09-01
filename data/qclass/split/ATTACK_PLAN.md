# Attack plan: pilot (k,b)=(3,10), signature {0}

Sidecar only. Consolidates open gaps from [`proof_pilot_3_10.md`](proof_pilot_3_10.md),
[`llt_bands.md`](llt_bands.md), [`lm_pilot.md`](lm_pilot.md), [`bridge_lemma.md`](bridge_lemma.md),
[`lemma.md`](lemma.md), [`lm_deterministic_latest.md`](lm_deterministic_latest.md), and
[`checks/LITERATURE.md`](../checks/LITERATURE.md).

**Pilot objects.** `f_{3,10}(n)=s_{10}(n^3)`, `M=57`, trapping region `[1,M]`, attractors
`A_{18}=(18)`, `A_{27}=(27)`, modular weight `p_i=1/3`. Signature `{0}` feeds residues
`r∈{0,3,6}`; image lattice `v≡0 (mod 9)`.

**Proven (finite / empirical).**

| Item | Result |
|------|--------|
| `F_j` vs MC | MAE ≈ 0.002 (`predict_split`, audit_05) |
| Trap labelling `ρ_L` | `ρ_1=1.0`, `ρ_2=0.4`, amplitude **0.6** on `[1,M]` |
| Exact `Ψ_j(10^n)` | gap **≥ 0.315** for `n=2…7`; antiphase `Ψ_{18}+Ψ_{27}=1` |
| `β_{18}`, `β_{27}`, `g(v)` | Explicit finite partition (`lm_deterministic.py`) |

**Open (blocks Conjecture 10.6).** G2d (pointwise LLT), G4 (first landing ≡ labelling),
LM §4.2.3–4 (`w_L` oscillation / `liminf≠limsup`).

---

## 1. Executive summary — gaps ranked by feasibility × impact

Score: **F** (feasibility 1–5) × **I** (impact 1–5) = **F×I**. Higher = attack first.

| Rank | Gap | F | I | F×I | One-line status |
|------|-----|---|---|-----|-----------------|
| **1** | **LM 4.2.3** — mixture weights `w_L(V)` at `V=b^n` | 4 | 5 | **20** | Trap `ρ_L` proven; need large-`L` stratum → trap amplitude transfer |
| **2** | **G4** — first landing mass ≡ `a(v)` on Gaussian window | 4 | 4 | **16** | Fixed `M=57`; likely a finite-dynamics + tail bound lemma |
| **3** | **LM 4.2.4** — `liminf Ψ_j < limsup Ψ_j` along `V→∞` | 3 | 5 | **15** | Decade gap ≥0.315 exact to `n=7`; limit argument missing |
| **4** | **G2a** — uniform LLT on dyadic band index `D` | 3 | 4 | **12** | Combinatorial **G2-band** ready; error transfer from `[1,b^D]` |
| **5** | **G2b** — digit-layer covariance / Gaussian mixture | 2 | 4 | **8** | Mechanistic in `predict.py`; Peter (2002) summatory input |
| **6** | **G2d** — pointwise LLT for `s_{10}(n³)`, `k≥3` | 1 | 5 | **5** | [9] Problem 2 open; no citation in [15]; blocks bridge rigorously |

**Strategic read.**

- **LM 4.2.3–4** is the highest-leverage *pilot-specific* work: finite trap data are complete;
  the remaining step is analytic geometry of the window `[V±√V]` on the image lattice, not
  a global open problem in digit-sum theory.
- **G4** is a *local* finite-dynamics identification; should close in parallel with LM once
  the Gaussian window scale is fixed relative to `M`.
- **G2d** is the deepest gap (literature-level). For the pilot, a **weaker band-CLT + lattice
  discretization** route may suffice for a *conditional* bridge if LM is proved independently;
  pointwise LLT remains mandatory for an unconditional `δ_j=F_j+o(1)` theorem.

**Recommended order:** LM 4.2.3 → G4 → LM 4.2.4 → G2a/G2-band → G2d (parallel literature
track). Promote bridge + conditional lemma only after (LM + G4) or full G2d.

---

## 2. G2d attack routes (pointwise LLT for `s_{10}(n³)`)

[9] Problem 2: local counts for `deg P≥3` open even for large prime `q`. [15] Thm 8.3.17
covers completely additive `f` on full intervals, not `n↦n^k`. CLT for composite `b=10` is
**citable** via [15] §8.3.13 + Ex. 8.3.15; LLT is not.

### Route G2d-A — Sharpen DMR Fourier/saddle bounds for `P(n)=n³`, `q=10`

**Idea.** Extend [9] Thm 2 AP machinery from prime large `q` to `q=10` (Remark 2: hypotheses
not essential, but small `q` excluded). Target

`#{n ∈ N_D^{(r)} : s_{10}(n³)=v} = |N_D^{(r)}| · φ((v−μ_D)/σ_D)/σ_D + E_{D,v}`

with `sup_{|v−μ_D|≤Cσ_D} |E_{D,v}| = O(D^{-1/2} log D)`.

**Steps.**

1. Verify BK-Property 8.3.11 on progression slices `N_D^{(r)}` (same exponential-sum input as
   Ex. 8.3.15).
2. Adapt DMR §3–4 digit-layer generating functions at `q=10`; track non-coprime leading
   coefficient issues via CRT over `{2,5}`.
3. Use **Lemma G2-band** to transfer interval bounds to `N_D^{(r)}`.

**Risk.** Problem 2 is explicitly open for `deg≥3`; cubic may need new uniform-in-`α` estimate.

### Route G2d-B — Digit-layer covariance (Peter / Delange → local)

**Idea.** [15] §8.2 + Peter (2002): summatory asymptotics for `s_q(⌊αn^k⌋)` at any `q≥2`.
Extract **covariance structure** of digit layers for `s_{10}(n³)`; prove multivariate CLT
then **Cramér-type** local limit via Edgeworth with bounded third cumulants per layer.

**Steps.**

1. Write `s_{10}(n³)` as sum of dependent digit contributions per length layer `L`.
2. Bound cross-layer covariances `O(D^{-1/2})` (G2b).
3. Apply Berry–Esseen on lattice with modulus-9 constraint (image lattice exact).

**Risk.** Dependence across layers for `n³` is strong; may yield CLT only, not pointwise LLT.

### Route G2d-C — Saddle-point / large deviations on carry chains

**Idea.** Model base-10 expansion of `n³` via carry propagation (Mauduit–Rivat philosophy for
`n²`). Large-deviation rate function for digit-sum of `n³` near `μ_D`; local limit from
quadratic approximation of rate function at minimum.

**Steps.**

1. Build finite-state transducer or carry Markov chain for cubing mod `10^L`.
2. Prove LDP for `S_{10}(n³)/D` on `N_D^{(r)}` (cf. [14] pattern methods).
3. Integrate local CLT from [15] Thm 8.3.17 as **template** for one layer; patch layers.

**Risk.** High technical overhead; composite base carries are messy.

### Route G2d-D — Conditional bridge (weaken G2d)

**Idea.** If **LM** is proved, Conjecture 10.6 needs only that `F_j` captures oscillation,
not a sharp LLT. Use **band CLT** + discretization error `O(σ_D^{-1})` on the image lattice;
accept `δ_j=F_j+O(D^{-1/2})` if bridge error swamps lattice discretization.

**Use.** Interim sidecar proposition; not a substitute for Hypothesis LLT in the paper.

---

## 3. G4 attack routes (first landing ≡ labelling)

Bridge step 3–4 ([`bridge_lemma.md`](bridge_lemma.md)): identify mass of first iterate
`g(v)` with attractor label `a(v)` for `v` in the LLT window.

### Route G4-A — Fixed-`M` threshold lemma (pilot)

**Idea.** For `M=57` fixed, `g(v)` depends only on `v mod M'` for explicit `M'`. For
`v ≥ v_0(M,k,b)`, one step of `f_{3,10}` on values `>M` lands in `[1,M]` with the same
basin as `a(v)`.

**Steps.**

1. Enumerate preimages of `β_{18}`, `β_{27}` under `g` on `{v : v≡0 (mod 9)}` (done to `M`).
2. Prove: if `v ≥ C·M` and `|v−μ_D| ≤ 6σ_D`, then `g(v)∈β_j ⟺ a(v)=j`.
3. Bound `μ_D` and `σ_D` for `D` large so window lies in `v ≥ v_0`.

**Feasibility.** High for pilot; `v_0` likely `≪ 10^2`.

### Route G4-B — Tail exclusion

**Idea.** Values with `g(v)∉[1,M]` or multiple pre-landing steps have exponentially small
mass under LLT. Truncation at `μ±6σ` in `predict_split` is already coded (G3).

**Steps.**

1. Show `P(v > M·10) → 0` faster than Gaussian tail on `N_D^{(r)}`.
2. Show second-iterate correction is `o(1)` on band mass.

### Route G4-C — Exact finite dynamics on trap lattice

**Idea.** Restrict to `v` whose base-10 length is `L` with `b^{L-1}≤v < b^L`; for
`L≥2`, values in `[V±√V]` at `V=10^n` have `L=n` or `n+1`. Combine with trap
`ρ_1,ρ_2` and **G4-A** on each stratum.

**Coupling.** Aligns with LM 4.2.3 (same partition).

---

## 4. LM attack routes (§4.2.3–4)

**Target.** Hypothesis LM: `Ψ_j(V)` does not converge. Proven on trap: `ρ_1−ρ_2=0.6`.
Exact decade anchors: `Ψ_{18}(10^n)∈[0.238,0.553]`, gap ≥0.315 (`n≤7`).

### Route LM-1 — Stratum weights `w_L(V)` (§4.2.3)

**Idea.** At `V=b^n`, window width `Θ(b^{n/2})`. Partition
`[V−√V,V+√V]∩(0+9ℤ)` by digit length `L`. Dominant strata `L=n`, `L=n+1` with
weights `w_n(V), w_{n+1}(V) ≈ 1/2` (empirical). Labelling fraction on stratum `L` is
`ρ_L` **only if** `g(v)` sees trap geometry — for `L≥3`, reduce to trap via **`g` stability**
on long integers (same as G4-A).

**Steps.**

1. Exact count `N_L(V) = #{v ∈ window : L(v)=L, v≡0 (mod 9)}` — combinatorics of
   `⌊log_{10} v⌋` in `[b^n−b^{n/2}, b^n+b^{n/2}]`.
2. Prove `w_n(V)+w_{n+1}(V)=1−o(1)` and `w_n(V)` alternates about `1/2` along even/odd `n`
   (log-periodic digit-boundary effect).
3. Show effective label rate on stratum `L` equals `ρ_{L mod 2}` or `ρ_1,ρ_2` after
   projecting `v` through `g` (link to trap table).

**Deliverable.** Explicit formula `Ψ_j(b^n) = w_n ρ^{(n)} + w_{n+1} ρ^{(n+1)} + o(1)` with
`ρ^{(n)}∈{ρ_1,ρ_2}`.

### Route LM-2 — Antiphase decade subsequence (§4.2.4)

**Idea.** Exhibit infinite sequences `n_k`, `m_k` with `Ψ_{18}(b^{n_k}) ≤ 0.25`,
`Ψ_{18}(b^{m_k}) ≥ 0.55`. Data: min at `n=3`, max at `n=6`; antiphase with `Ψ_{27}`.

**Steps.**

1. Extend exact computation to `n≤12` via `lm_deterministic.py` (verify gap persists).
2. Prove **lower bound** on window lattice size `|window ∩ (0+9ℤ)| ≍ b^{n/2}`.
3. Combine LM-1 with alternating `w_n` to force oscillation of convex combination of
   `ρ_1=1.0` and `ρ_2=0.4` → amplitude ≥ `0.6·|w_n−w_{n+1}| ≥ c > 0` infinitely often.

### Route LM-3 — Delange-type forbidden convergence

**Idea.** If `Ψ_j(V)→L_j`, then decade scaling `Ψ(bV)−Ψ(V)→0`. Compute shows Pearson
0.57, MAE 0.09 — not proof. Seek **deterministic** bound `|Ψ_j(b^n)−Ψ_j(b^{n+1})| ≥ c_j`
from LM-1.

**Contrast.** Delange [13] applies to `s_b`, not `h_j`; do not cite directly.

### Route LM-4 — Refutation track (low priority)

If `Ψ_j` converges, revise Conjecture 10.6. Current data and trap amplitude **oppose**
convergence; keep as sanity check only.

---

## 5. Candidate lemma statements

### Lemma A (G2-band; promote from `llt_bands.md` §7)

For fixed `b≥2`, `m`, `r`: `|N_D^{(r)}| = (b^D−b^{D−1})/m + O(1)`. Corollary: counting
errors `O(N^{1−σ})` on `[1,N]` restrict to `o(b^D)` on `N_D^{(r)}`.

*Status:* Proof combinatorial; ready to number.

### Lemma B (LM-stratum; pilot)

Let `(k,b)=(3,10)`, `j∈{18,27}`. For `V=b^n` with `n≥2`, let `w_L(V)` be the fraction of
`v∈[V−√V,V+√V]∩(0+9ℤ)` with `⌊log_{10}v⌋+1=L`. Then

`Ψ_j(V) = w_n(V)·ρ_n^{*} + w_{n+1}(V)·ρ_{n+1}^{*} + O(b^{-n/2})`,

where `ρ_L^{*}∈{ρ_1,ρ_2}` are the trap labelling rates (§4.2.2) and `ρ_1−ρ_2=0.6`.

*Opens:* Definition of `ρ_L^{*}` for `L>2` (reduction to trap via `g`); proof of weight
asymptotics.

### Lemma C (LM-decade oscillation; pilot)

`limsup_{n→∞} Ψ_{18}(10^n) − liminf_{n→∞} Ψ_{18}(10^n) ≥ 0.3`.

*Evidence:* Exact `n=2…7` gap 0.315. *Needs:* Lemma B + alternating `w_n`.

### Lemma D (G4 landing; pilot)

There exists `D_0` such that for all `D≥D_0`, all `v` in the LLT window
`|v−μ_D|≤6σ_D` with `v≡0 (mod 9)`, first landing satisfies `g(v)∈β_j ⟺ a(v)=j`.

*Needs:* Explicit `v_0(M)` and LLT/CLT centering bounds.

---

## 6. Literature to read next

| Priority | Reference | Why |
|----------|-----------|-----|
| **P1** | [15] Drmota–Grabner 2010, §8.3.2–8.3.3 | BK-Property, Thm 8.3.13, Ex. 8.3.15 — **close CLT citation** for pilot |
| **P1** | [9] DMR 2011, §2 Problem 2, Thm 2 proof | Understand what blocks `deg≥3` pointwise LLT |
| **P1** | Peter 2002, *Acta Arith.* **104**, 85–96 | Summatory `s_q(⌊αn^k⌋)`; covariance / log-periodic (G2b) |
| **P2** | Mauduit–Rivat 2009 (`n²` local limit) | Template for carry/saddle approach (G2d-C) |
| **P2** | Bassily–Kátai 1995 (via [15]) | CLT backbone for polynomial sequences |
| **P2** | Dartyge–Tenenbaum (digit sums in AP) | Weak AP bounds at `b=10` if DMR prime restriction bites |
| **P3** | [14] Drmota 2003 (patterns) | Mellin–Perron for carry chains |
| **P3** | Füredi–Turán / digital LLL surveys | Alternative local-limit technology |
| **P3** | Hare–Laishram–Stoll 2011 | Polynomial digit-sum size; Q-class extension, not pilot LLT |

**Not useful for LM:** Delange [13] for `s_b` alone — dynamics labelling `h_j` requires
Lemma B, not a classical digit-sum theorem.

---

## 7. Four-week programme

### Week 1 — Finite closure and CLT leg

| Day | Task | Output |
|-----|------|--------|
| 1–2 | Promote **Lemma A (G2-band)**; draft CLT citation note `[15] Thm 8.3.13 + Ex. 8.3.15` on `N_D^{(r)}` | `llt_bands.md` update |
| 2–3 | Extend `lm_deterministic.py` to `n≤12`; tabulate `w_L(V)`, `Ψ_j(b^n)` | `lm_deterministic_*.md` |
| 4–5 | **G4-A:** prove landing ≡ label for `v≥v_0(57)` on image lattice | Lemma D draft |
| 5 | Read [15] §8.3.2 + verify BK on progression slice | Citation checklist |

### Week 2 — LM 4.2.3 (stratum weights)

| Day | Task | Output |
|-----|------|--------|
| 1–2 | Exact combinatorics of `N_L(b^n)` for `L∈{n,n+1}` | Lemma B §weight |
| 3–4 | Define `ρ_L^{*}` for `L≥3` via `g`-stability; link to `ρ_1,ρ_2` | Lemma B complete draft |
| 5 | Numerical parity: `Ψ_j` from Lemma B vs `local_mean` / deterministic | Error table |

### Week 3 — LM 4.2.4 + bridge coupling

| Day | Task | Output |
|-----|------|--------|
| 1–2 | Prove alternating lower bound on `|w_n−w_{n+1}|` or `Ψ_j(b^n)−Ψ_j(b^{n+1})` | Lemma C draft |
| 3 | Integrate **Lemma D (G4)** into bridge sketch | `bridge_lemma.md` §G4 closed |
| 4–5 | Peter (2002) pass for G2b covariance bounds | G2d-B notes |
| 5 | Read [9] Problem 2 proof line-by-line | G2d feasibility memo |

### Week 4 — G2d literature attack + conditional packaging

| Day | Task | Output |
|-----|------|--------|
| 1–2 | Attempt G2d-A at `q=10` CRT split, or document blocker | `llt_bands.md` §G2d |
| 3 | **Conditional theorem:** LLT (hypothesis) + Lemma C + Lemma D ⇒ no `lim δ_j` | `lemma.md` tighten |
| 4 | `bridge_check.py` at larger `D`; document `o(1)` budget | `proof_pilot_3_10.md` |
| 5 | Sidecar review: what can promote to paper §10 vs stay conditional | This file §status |

---

## Dependency graph (updated)

```text
Lemma A (G2-band) ──► [15] CLT on N_D^(r)          ──► G2a closed
                              │
Peter / G2b ──────────────────┼──► G2d (open) ──► Hypothesis LLT
                              │
Lemma B (w_L) ──► Lemma C (oscillation) ──► LM ──► Conj. 10.6
       │                                        ▲
Lemma D (G4) ──► bridge δ_j = F_j + o(1) ──────┘
```

**Exit criterion (pilot).** Publishable conditional chain when **Lemma B + C + D** are proved
and CLT leg is cited; unconditional bridge waits on **G2d**.

---

## Scripts

```bash
python scripts/lm_deterministic.py --k 3 --b 10 --signature 0
python scripts/local_mean.py --k 3 --b 10 --v-max 100000000
python scripts/bridge_check.py --k 3 --b 10
python scripts/split_predict.py --k 3 --b 10 --d-max 90
```

---

*Generated 2026-09-01. Sidecar only — no paper edits.*
