# Lemma C analytic — suffix mixture route (Route C-A)

Sidecar only. Formalises the **mixture mechanism** behind decade oscillation,
building on bounded landing depth (Lemma D-depth) and empirical Route C-A.

**Compute:** `scripts/lm_carry_depth.py` → [`lemma_c_analytic_latest.md`](lemma_c_analytic_latest.md)

---

## 1. Setup

Fix `(k,b)=(3,10)`, signature `{0}`, attractor `{18}`. At decade anchor `V=b^n`,
stratum `L=n` means `v` has exactly `n` base-10 digits. Write

`ρ_n = #{v in W(V), |v|=n, label=18} / #{v in W(V), |v|=n}`

on the feeding lattice (`v ≡ 0,3,6 mod 9`). Partition by suffix `s = v mod 100`:

`ρ_n = Σ_{s=0}^{99} α_n(s) · ρ_n(s)`,  `α_n(s) =` stratum mass fraction at suffix `s`.

This decomposition is **exact** (finite counting).

---

## 2. Lemma C-A-mix (draft; pilot)

**Lemma C-A-mix (suffix mixture).** For `n ≥ 9` on the pilot:

1. **Witness pair:** suffixes `s₁, s₂` with `|ρ_n(s₁) − ρ_n(s₂)| ≥ c` for all
   `n ∈ {9,…,16}` with **c ≥ 0.097** on the best stable pair `[50,95]` across
   eight decades (`lemma_c_route_ca_latest.md`; per-decade max gap remains
   **≥ 0.17** at every `n ≥ 9`). On `n ∈ {9,…,14}` alone, witness `[50,55]`
   still has **c ≥ 0.12**.
2. **Mixture drift:** suffix rates `ρ_n(s)` vary with `n` (max adjacent drift
   **≈0.27** on some classes); mixture weights `α_n(s)` are stable (max drift **≈7×10⁻⁵**).
3. **Consequence (conditional):** If `α_n(s)` is stable in `n` on the witness
   suffixes and `|ρ_n(s₁) − ρ_n(s₂)| ≥ c` for all `n ≥ n₀`, then `(ρ_n)` cannot
   converge to a constant.

   *Sketch.* Suppose `ρ_n → L`. Stability of `α_n(s₁)` and `α_n(s₂)` on a set
   with fixed positive mass forces both class rates toward limits
   `L_{s₁}, L_{s₂}` with `|L_{s₁} − L_{s₂}| ≥ c`. Then
   `ρ_n = α_n(s₁)ρ_n(s₁) + α_n(s₂)ρ_n(s₂) + (remainder)` cannot satisfy
   `ρ_n → L` unless the witness gap vanishes — contradiction. A fully rigorous
   version must quantify the remainder when `α_n(s₁)+α_n(s₂) < 1`; the pilot
   witness `[50,55]` has `min_gap ≥ 0.12` on common buckets for `n=9…14`; on
   `n=9…16` the best stable pair is `[50,95]` with `min_gap ≈ 0.097`.

*Status:* (1)–(2) **verified computationally** `n=9…16`; step (3) **drafted**
(limit sketch; remainder bound still open).

---

## 3. Carry-depth input (Lemma D-depth)

From [`g4_landing_latest.md`](g4_landing_latest.md): `first_landing` depth `≤ 2`
for all `v ≤ 10^6` on the feeding lattice.

**Tail-digit scan** (`lm_carry_depth.py`): label is **not** determined by
`v mod b^d` alone for `d ≤ 4` (high-digit perturbations change label).

**Implication:** Route C-A cannot reduce to a **single** finite suffix modulus
for `g(v)`; the analytic route is **mixture-level** (weights `α_n(s)` plus
class rates `ρ_n(s)`), not a 2-digit carry lemma alone.

---

## 4. Proof roadmap (analytic closure)

| Step | Statement | Status |
|------|-----------|--------|
| A1 | Exact mixture `ρ_n = Σ α_n(s) ρ_n(s)` | **Proven** (definition) |
| A2 | ∃ witness pair with uniform gap `c ≥ 0.12` for `n ≥ n₀` | **Empirical** `n₀=9`, `n≤14` (`[50,55]`); `n≤16` gives `c≈0.097` (`[50,95]`) |
| A3 | `ρ_n(s)` varies with `n` (suffix rate drift) | **Empirical** (drift ≈0.27) |
| A4 | `α_n(s)` stable in `n` | **Empirical** (drift ≈7×10⁻⁵) |
| A5 | `limsup ρ_n − liminf ρ_n ≥ c'` | **Open** — per-decade max suffix gap `≥0.17` for `n=9…16`; uniform pair gap weakens past `n=14` |

**Honest gap:** empirical witness + mixture drift explain oscillation
mechanistically; a **theorem** still requires controlling `ρ_n(s)` as `n→∞`
(Route C-B / G2b) or a finite carry certificate for two suffix classes.

**Compute note:** `lm_suffix.py --n-max 16` completes in ~5–8 min on the pilot;
`lm_carry_depth.py --n-max 16` ~5 min. Extending further scales as `√(10^n)`.

---

## 5. Connection to Route C-B (G2b)

Peter (2002) log-periodic terms in `s_{10}(n³)` may drive **both** `α_n(s)`
(digit-layer geometry) and `ρ_n(s)` (landing via digit-sum layers). See
[`g2b_peter_notes.md`](g2b_peter_notes.md).

---

*2026-09-01. Sidecar only.*
