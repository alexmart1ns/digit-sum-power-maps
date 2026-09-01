# LM attack plan: pilot (3,10), signature {0}

Sidecar only. Next analytic step after [`proof_pilot_3_10.md`](proof_pilot_3_10.md).
Hypothesis LM is the **unique open gap** for Conjecture 10.6.

---

## 1. Objects (explicit)

Fix `(k,b)=(3,10)`, `m=9`, `M=57`. Signature `γ={0}`; physical attractors
`A_{18}=(18)`, `A_{27}=(27)` (Example 4.4).

- `g(v)` — first iterate `f_{3,10}(v)` inside `[1,M]` (composition of digit-sum
  map on values `> M`).
- `β_j` — basin of attractor `A_j` inside the trapping region.
- `h_j(v) = 1_{g(v) ∈ β_j}` for `v ∈ ℤ⁺`.
- `Ψ_j(V)` — mean of `h_j` on `[V−√V, V+√V]` ∩ image lattice
  `{ v : v ≡ 0 (mod 9) }` (feeding residues `{0,3,6}`).

**LM claim:** `lim_{V→∞} Ψ_j(V)` does **not** exist for `j ∈ {18,27}`.

---

## 2. What compute shows

| Diagnostic | Result | File |
|------------|--------|------|
| Decade collapse `Ψ(V)` vs `Ψ(bV)` | Pearson **0.57**, MAE **0.09** | `local_mean_latest.md` |
| Amplitude `Ψ_{18}` at V≤10⁷ | ≈ **0.67** | same |
| Labelling vs digit length `L` | Amplitude across `L` in `[1,M]` | `lm_structure_latest.md` |
| Delange [13] for `s_b` | Log-periodic; **not** for `h_j` | `LITERATURE.md` |

**Interpretation:** Neither confirms a period-1 factor in `log_b V`, nor proves LM.
Pearson 0.57 is **inconclusive** — between “collapse” and “random”.

---

## 3. Three proof routes (ranked)

### Route A — Direct non-convergence of `Ψ_j` (target)

Show `liminf Ψ_j(V) < limsup Ψ_j(V)` along `V → ∞`, e.g. by exhibiting two
infinite sequences `V_n, V'_n` with `Ψ_j(V_n) − Ψ_j(V'_n) ≥ c > 0`.

**Subtasks:**

1. Run `python scripts/lm_structure.py --k 3 --b 10` — finite-window label
   variation by digit length.
2. Extend `local_mean` analysis: extract `liminf`/`limsup` along log-spaced
   `V` (no new sampling).
3. Relate window `[V±√V]` to digit-length layers crossed as `V` grows.

### Route B — Contrapositive via bridge

If `δ_j(D) = F_j(D) + o(1)` and `F_j` is non-convergent (Gaussian sweep), then
`δ_j` is non-convergent **without** LM — but non-convergence of `F_j` still
needs LM or direct oscillation proof on the labelling.

### Route C — Refute LM (would weaken 10.6)

If `Ψ_j(V) → L_j` exists, Conjecture 10.6 needs revision. Current data do
**not** support convergence.

---

## 4. Candidate lemma (to prove or disprove)

**Lemma LM-pilot (draft).** For `(3,10)` and `j ∈ {18,27}`, the sequence
`(Ψ_j(b^n))_{n≥2}` does not converge, and

`limsup_{n→∞} Ψ_j(b^n) − liminf_{n→∞} Ψ_j(b^n) ≥ c_j > 0`

for some explicit `c_j`.

**Evidence needed:** deterministic bounds from `g` on `[b^{n−1}, b^n)` —
not Monte Carlo.

---

## 5. Scripts

```bash
python scripts/local_mean.py --k 3 --b 10 --v-max 10000000
python scripts/lm_structure.py --k 3 --b 10 --signature 0
```

---

## 6. Dependency

```text
llt_bands.md (G2)  ──►  bridge_lemma  ──►  δ_j = F_j + o(1)
                              │
lm_pilot.md (LM)   ──►  Ψ_j non-convergence  ──►  Conjecture 10.6
```

G2 and LM are **independent hypotheses**; both needed for the conditional chain.
