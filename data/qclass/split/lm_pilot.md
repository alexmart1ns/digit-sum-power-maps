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
| Global `liminf` / `limsup` on Ψ_{18} | **0.09** / **0.76** (range **0.67**) | `lm_liminf_latest.md` |
| Subsequence `V ≈ 10^n` range Ψ_{18} | **0.24**–**0.64** (range **0.40**) | `lm_liminf_latest.md` |
| Labelling vs digit length `L` in `[1,M]` | amplitude **0.6** across L | `lm_structure_latest.md` |
| Delange [13] for `s_b` | Log-periodic; **not** for `h_j` | `LITERATURE.md` |

**Verdict (computational):** `suggests_non_convergence` — Ψ_j has range 0.67 on
`V ≤ 10^7` and 0.40 on decade anchors alone. This **supports** LM but is **not**
a proof (`lim inf ≠ lim sup` along a specific infinite sequence remains to be shown).

---

## 3. Three proof routes (ranked)

### Route A — Direct non-convergence of `Ψ_j` (target)

Show `liminf Ψ_j(V) < limsup Ψ_j(V)` along `V → ∞`, e.g. by exhibiting two
infinite sequences `V_n, V'_n` with `Ψ_j(V_n) − Ψ_j(V'_n) ≥ c > 0`.

**Subtasks:**

1. ~~Run `lm_structure.py`~~ — done; amplitude **0.6** across `L=1,2` in `[1,M]`.
2. ~~Extract `liminf`/`limsup` via `lm_liminf.py`~~ — done; see §2.
3. **Open:** relate window `[V±√V]` to digit-length layers as `V` grows (§4.1).

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

### 4.1 Empirical lower bounds (compute, not proof)

From `lm_liminf_latest.md` on the decade subsequence `V = 10^n`, `n = 2…7`:

| attractor | min Ψ_j(b^n) | max Ψ_j(b^n) | empirical gap |
|-----------|--------------|--------------|---------------|
| [18] | **0.238** at `n=3` (`V=10³`) | **0.553** at `n=6` (`V=10⁶`) | **≥ 0.315** |
| [27] | **0.447** at `n=6` | **0.762** at `n=3` | **≥ 0.315** |

Antiphase: when Ψ_{18} is low, Ψ_{27} is high (sum ≈ 1 on anchors).

**Mechanism hypothesis:** at `V = b^n`, the window `[V−√V, V+√V]` has width
`Θ(b^{n/2})` and samples values whose base-`b` digit length is predominantly
`L = n` or `n±1`. Finite-window labelling (`lm_structure`) shows
`frac_primary` swings **1.0 → 0.4** between `L=1` and `L=2` (amplitude **0.6**).
If the mixture weights `w_L` in the bridge (§2 of `bridge_lemma.md`) inherit
this log-periodic variation, Ψ_j cannot settle to a constant.

**Evidence still needed:** deterministic bounds on `g(v)` and basin membership
on each digit-length stratum inside `[V±√V]`, not Monte Carlo local means.
Target: show two residue/digit-length regimes with `Ψ_j` differing by ≥ `c_j`.

### 4.2 Proof strategy (deterministic)

1. Fix `n` large. Partition `[V−√V, V+√V] ∩ (0+9ℤ)` by digit length `L`.
2. Bound `|{ v : L(v)=ℓ, g(v)∈β_{18} }| / |{ v : L(v)=ℓ }|` using explicit
   preimages of `β_{18}` under one step of `f_{3,10}` on `[1,M]`.
3. Show weights `w_ℓ(V)` alternate or oscillate along `V = b^n` (Delange-type
   log-periodicity pushed to `h_j`, not just `s_b`).
4. Conclude `Ψ_{18}(b^n) − Ψ_{18}(b^{n'}) ≥ c` for infinitely many pairs `(n,n')`.

**Status:** steps 1–2 are finite combinatorics on `[1,M]`; step 3 is the hard
analytic gap (no Delange theorem for `h_j`).

---

## 5. Scripts

```bash
python scripts/local_mean.py --k 3 --b 10 --v-max 10000000
python scripts/lm_structure.py --k 3 --b 10 --signature 0
python scripts/lm_liminf.py
```

---

## 6. Dependency

```text
llt_bands.md (G2)  ──►  bridge_lemma  ──►  δ_j = F_j + o(1)
                              │
lm_pilot.md (LM)   ──►  Ψ_j non-convergence  ──►  Conjecture 10.6
```

G2 and LM are **independent hypotheses**; both needed for the conditional chain.
