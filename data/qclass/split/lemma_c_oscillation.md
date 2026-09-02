# Lemma C — decade oscillation (pilot 3,10)

Sidecar only. Completes **LM §4.2.4** reduction after Lemma B
([`lemma_b_stratum.md`](lemma_b_stratum.md)).

**Compute:** `scripts/lm_oscillation.py` → [`lemma_c_oscillation_latest.md`](lemma_c_oscillation_latest.md)

---

## 1. Reduction from Lemma B

By Lemma B, for `V = 10^n` with `w_n, w_{n+1} → 1/2`:

`Ψ_{18}(10^n) = (ρ_n + ρ_{n+1})/2 + O(b^{-n/2})`

Therefore **LM on `Ψ_{18}`** is equivalent to **non-convergence of the sequence
`(ρ_n)_{n≥2}`** (labelling rate at digit-length stratum `n`).

---

## 2. Empirical oscillation (exact compute, `n=2…14`)

From `lemma_c_oscillation_latest.json`:

| Metric | Value |
|--------|-------|
| `Ψ_{18}(10^n)` min | **0.238** at `n=3` |
| `Ψ_{18}(10^n)` max | **0.562** at `n=8` |
| Gap on subsequence | **≥0.32** |
| `ρ_n` min / max | **0.182** (`n=3`) / **0.582** (`n=8`) |
| `ρ_n` full range | **0.400** |
| Max adjacent `\|ΔΨ\|` | **≥0.18** |
| Late decades | `ρ_{13}=0.348`, `ρ_{14}=0.241` — new downward leg, not settling |

**Antiphase:** `Ψ_{18} + Ψ_{27} = 1` on every decade anchor (Lemma B parity).

---

## 3. Lemma C (draft statement)

**Lemma C (decade oscillation; empirical).** For `(3,10)` and attractor `{18}`,
the sequence `(Ψ_{18}(10^n))_{n≥2}` satisfies

`limsup_{n→∞} Ψ_{18}(10^n) − liminf_{n→∞} Ψ_{18}(10^n) ≥ c`

with empirical **c ≥ 0.32** (computed `n ≤ 14`).

**Equivalent form (Lemma B):**

`limsup ρ_n − liminf ρ_n ≥ 2c`  (approximately, since `Ψ ≈ (ρ_n+ρ_{n+1})/2`).

**Status:** **Empirical** on finite `n`; analytic proof **open**. Route C-C
refutes naive convergence hypotheses (§4.3).

---

## 4. Proof routes (Week 3)

### Route C-A — Alternating `ρ_n` from suffix classes ✓ **closed (empirical)**

Since `g(v)` has landing depth `≤2` ([`g4_landing_latest.md`](g4_landing_latest.md)),
classify `v` by `v mod 10^2` at stratum `L=n` in the window at `V=10^n`.

**Compute:** `scripts/lm_suffix.py` → [`lemma_c_route_ca_latest.md`](lemma_c_route_ca_latest.md)

| Metric | Value (`n=9…14`, mod 100) |
|--------|---------------------------|
| Min per-decade max suffix gap | **≥0.175** (`n=11`) |
| Max per-decade gap | **0.371** (`n=9`, suffixes `1` vs `59`) |
| Best stable pair (all 6 decades) | `[50,55]`, min gap **≥0.12** |
| At `n=14` | gap **0.289** (suffixes `0` vs `49`) |

**Interpretation:** `ρ_n` aggregates suffix classes with **intrinsic** labelling rates
differing by `≥0.12` persistently. Window mix shifts with `n` → aggregate `ρ_n` oscillates.
This explains Lemma C mechanism; **analytic** bound `|ρ(s₁)−ρ(s₂)|≥c` on fixed suffix
classes remains open (finite carry-depth argument).

**Status:** empirical closure; not a `limsup≠liminf` proof.

### Route C-B — Log-periodic inheritance

Peter (2002) log-periodic terms in `s_{10}(n³)` may induce correlated
oscillation in `ρ_n` via first landing — see [`g2d_feasibility.md`](g2d_feasibility.md) G2b notes.

**Status:** open (needs G2b covariance extraction).

### Route C-C — Refutation bound ✓ **closed (empirical)**

**Hypothesis tested:** `ρ_n → L` (constant, `1/n`-decay, linear drift, or
low-period cosine).

**Protocol:** train on `n=2…8`, hold-out `n=9…14`; tolerance `ε=0.05` on
`|ρ_n − ρ̂_n|`.

| Model | Fit on `n≤8` | max hold-out error | at worst `n` |
|-------|--------------|-------------------|--------------|
| Constant `L̂=0.424` | mean | **0.183** | 14 |
| `ρ_n = a + b/n` | OLS | **0.354** | 14 |
| `ρ_n = a + b·n` | OLS | **0.729** | 14 |
| `ρ_n = L + A·cos(2πn/6)` | best period | **0.315** | 14 |

**Additional checks:**

- Running range `max ρ − min ρ` at `n=8`: **0.400**; at `n=14`: **0.400** (no shrink).
- `ρ_{14}=0.241` misses every model by `≥0.18` (constant) or predicts upward drift
  while data falls.

**Verdict:** **`convergence_refuted`** on all tested models. The sequence does not
settle toward a limit or a simple asymptotic law up to `n=14`.

**Compute:** `python scripts/lm_oscillation.py --n-max 14` (also refreshes
`lemma_b_stratum_latest.*`).

**Limitation:** empirical refutation only; does not prove `limsup ρ_n ≠ liminf ρ_n`.
Analytic Lemma C still requires Route C-A or C-B.

---

## 5. Connection to Conjecture 10.6

```text
Lemma B (w_n → 1/2)  +  Lemma C (ρ_n oscillates)  ⟹  LM (Ψ non-convergent)
                              │
                              ▼
              bridge δ_j = F_j + o(1)  +  LM  ⟹  no lim δ_j
```

Lemma C is the **last pilot-specific** gap before conditional 10.6.

---

## 6. Status

| Item | Status |
|------|--------|
| Empirical gap `c ≥ 0.32` | **Done** (`n≤14`) |
| Route C-C convergence refutation | **Done** (`n≤14`, all models fail) |
| Route C-A suffix-class gap | **Done** (`c≥0.12` on `n=9…14`; `c≈0.097` on `n=9…16`) | `lemma_c_route_ca_latest.md` |
| Analytic proof of `limsup ≠ liminf` | **Open** (uniform witness + rate drift control) | `lemma_c_analytic.md` |
| Promotion to paper | **Blocked** on analytic Lemma C |

---

*2026-09-01. Sidecar only.*
