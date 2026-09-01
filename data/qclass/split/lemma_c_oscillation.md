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

## 2. Empirical oscillation (exact compute, `n=2…12`)

From `lemma_c_oscillation_latest.json`:

| Metric | Value |
|--------|-------|
| `Ψ_{18}(10^n)` min | **0.238** at `n=3` |
| `Ψ_{18}(10^n)` max | **≥0.562** (see latest run) |
| Gap on subsequence | **≥0.32** |
| `ρ_n` range | **≈0.18–0.59** (amplitude ~0.16–0.35) |
| Max adjacent `\|ΔΨ\|` | **≥0.17** |

**Antiphase:** `Ψ_{18} + Ψ_{27} = 1` on every decade anchor (Lemma B parity).

---

## 3. Lemma C (draft statement)

**Lemma C (decade oscillation; empirical).** For `(3,10)` and attractor `{18}`,
the sequence `(Ψ_{18}(10^n))_{n≥2}` satisfies

`limsup_{n→∞} Ψ_{18}(10^n) − liminf_{n→∞} Ψ_{18}(10^n) ≥ c`

with empirical **c ≥ 0.32** (computed `n ≤ 12`).

**Equivalent form (Lemma B):**

`limsup ρ_n − liminf ρ_n ≥ 2c`  (approximately, since `Ψ ≈ (ρ_n+ρ_{n+1})/2`).

**Status:** **Empirical** on finite `n`; analytic proof **open**.

---

## 4. Proof routes (Week 3)

### Route C-A — Alternating `ρ_n` from suffix classes

Since `g(v)` has landing depth `≤2` ([`g4_landing_latest.md`](g4_landing_latest.md)),
classify `v` by `(v mod 10^2, v mod 10^3)` and show two suffix classes yield
`ρ` differing by `≥ c`. No simple `b^T` periodicity; use **2-step** digit suffix.

### Route C-B — Log-periodic inheritance

Peter (2002) log-periodic terms in `s_{10}(n³)` may induce correlated
oscillation in `ρ_n` via first landing — see [`g2d_feasibility.md`](g2d_feasibility.md) G2b notes.

### Route C-C — Refutation bound

If `ρ_n → L`, predict `L` from regression; extend compute to `n=14` to test.

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
| Empirical gap `c ≥ 0.32` | **Done** (`n≤12`) |
| Analytic proof of `limsup ≠ liminf` | **Open** |
| Promotion to paper | **Blocked** on analytic Lemma C |

---

*2026-09-01. Sidecar only.*
