# Code map: (3,10) pilot proof dependencies

Sidecar only. Links paper symbols to implementation. Pilot: `(k,b)=(3,10)`, `m=9`, signature `{0}`, attractors `{18}` (idx 2) and `{27}` (idx 6), modular weight `p_i=1/3`.

---

## 1. Core objects

| Symbol | Meaning | Where defined / computed |
|--------|---------|--------------------------|
| `M = M(3,10) = 57` | Contraction / trapping bound; forward-invariant `[1,M]` | `contraction_bound(k,b)` → `src/dspm/core.py` (L121–143). Consumed by `build_system` → `src/dspm/dynamics.py` (L113–120). Verified: `tests/test_core.py::test_contraction_bound_is_forward_invariant`. |
| `f_{k,b}(n) = S_b(n^k)` | Digit-sum power map | `f_kb` → `src/dspm/core.py`. |
| `FiniteSystem` | Exhaustive graph on `[1,M]`: attractors, `label[n]`, basins, signatures | `build_system` → `src/dspm/dynamics.py` (L28–180). |
| `β_j = B(A_j) ∩ [1,M]` | Basin of attractor `j` inside trapping window | Implicit: `{ n ∈ [1,M] : label[n] == j }`. Sizes: `system.basin_sizes[j]`. Pilot: `β_18` size 12 (idx 2), `β_27` size 7 (idx 6). |
| `g(v)` | First iterate of `f_{3,10}` landing in `[1,M]` | **No named function.** Implemented inline in `attractor_labels_upto`: loop `while w > M: w = f_kb(w,…)` → `src/dspm/predict.py` (L27–35). |
| `a(v)` | Attractor index reached by `v` | `attractor_labels_upto(V, system)[v]` = `system.label[g(v)]` → `src/dspm/predict.py` (L27–35). Also `FiniteSystem.attractor_of(n)` for sampled `n` → `src/dspm/dynamics.py` (L81–91). |
| `h_j(v) = 1_{g(v)∈β_j}` | Labelling indicator | **No named function.** Equivalent to `1_{a(v)=j}` on the pilot. Used implicitly in `scripts/local_mean.py::psi_sharp` via `labels[v]` (L42–65). |
| `Ψ_j(V)` | Mean of `h_j` on sharp window `[V±√V]` ∩ image lattice | `scripts/local_mean.py::psi_sharp` + `run_psi` (L42–153). Output → `data/split/local_mean_latest.json`. |
| Image lattice `v ≡ r^k (mod m)` | Residue classes for first iterate | `predict_split`: `images = [pow(r,k,m) for r in feeding]` → `src/dspm/predict.py` (L83–86). For sig `{0}` on (3,10): feeding `{0,3,6}` all map to `0 mod 9` — image = `{0+9ℤ}`. |
| Modular skeleton | Cycles, signatures, weights `p_i` | `structure(k,m)` → `src/dspm/modular.py`. `ModularStructure.weights`, `.signature_of_residue`, `.owner`. |

### Pilot attractor lookup (3,10)

```
M=57  attractors: [1] idx0  [8] idx1  [18] idx2  [19,28] idx3  [17] idx4  [26] idx5  [27] idx6
signature {0}: idx 2 → {18}, basin 12; idx 6 → {27}, basin 7
```

---

## 2. Pipeline: `predict_split` ↔ `local_mean` ↔ `bridge_check`

```text
                    build_system(3,10)
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
  attractor_labels_upto   split_curves     structure(3,9)
  (a(v) on [1,V])         (MC δ_j(D))      (sig, weight)
         │                 │                 │
         │                 │                 │
         ▼                 ▼                 ▼
  predict_split ──────────┼────────► F_j(D) = bridge target
  (Gaussian × labels      │           scripts/split_predict.py
   on image lattice)     │           scripts/bridge_check.py
         │                 │                 │
         │                 ▼                 │
         │         split_scale_k3_b10        │
         │         _latest.json (δ_j MC)     │
         │                 │                 │
         └──── bridge_check: |δ_j − F_j| per D ────┘

  local_mean (parallel track, v-space LM):
  attractor_labels_upto → psi_sharp → Ψ_j(V) → data/split/local_mean_latest.json
       → lm_liminf.py → liminf/limsup → data/qclass/split/lm_liminf_latest.*
       → lm_structure.py → labelling vs digit length L in [1,M]
       → lm_deterministic.py → trap ρ_L + exact decade Ψ (psi_sharp parity)
```

### `predict_split` — model `F_j(D)`

| Layer | Symbol | File / symbol |
|-------|--------|---------------|
| Digit-count mixture | `w_L(D)` | `digit_count_mixture` → `src/dspm/predict.py` (L38–58) |
| Gaussian LLT | `φ_L(v; μ_L, σ_L)` | `_gaussian`, loop in `predict_split` → `src/dspm/predict.py` (L61–110) |
| Labelling convolution | `a(v)` | `labels` from `attractor_labels_upto` |
| Modular scale | `p_i` | `modular_weight` argument |
| CLI wrapper | — | `scripts/split_predict.py` |
| Conjecture 10.6′ sweep | `P_j({log_b D})` | `scripts/sweep_label.py` (reuses `predict_split`) |

### `local_mean` — diagnostic `Ψ_j(V)`

| Layer | File / symbol |
|-------|---------------|
| Window mean | `scripts/local_mean.py::psi_sharp` |
| Feeding residues | `feeding_residues` → uses `v ≡ r (mod m)`; **coincides with image lattice** for sig `{0}` on (3,10) |
| Post-process | `scripts/lm_liminf.py` (liminf/limsup, decade anchors `V=10^n`) |
| Finite-window structure | `scripts/lm_structure.py` (label fractions by digit length `L` in `[1,M]`) |
| Deterministic bounds | `scripts/lm_deterministic.py` (trap `β_j`, `ρ_L`, exact decade `Ψ_j(b^n)`) |

### `bridge_check` — empirical bridge `δ_j ≈ F_j`

| Input | Source |
|-------|--------|
| Measured `δ_j(D)` | `data/split/split_scale_k3_b10_latest.json` via `load_split_scale_file` → `src/dspm/split.py` |
| Predicted `F_j(D)` | `predict_split` → `src/dspm/predict.py` |
| Script | `scripts/bridge_check.py` (stdout only; MAE over attractors × D bands) |

Bridge **theorem** (draft, gaps G2/G4): `data/qclass/split/bridge_lemma.md`. Conditional non-convergence: `data/qclass/split/lemma.md`.

---

## 3. Verification / audit for lattice B.5

Appendix **B.5**: Gaussian sweep must use **image lattice** `v ≡ r^k (mod m)`, not feeding `v ≡ r (mod m)`.

| Script | Role | Verdict criterion |
|--------|------|-------------------|
| `verification/audit/audit_05_lattice.py` | Primary B.5 audit: compares MAE of correct vs wrong lattice on (3,10), D∈[8,64] | PASS if image MAE < 0.01 and wrong > 3× correct |
| `scripts/bridge_check.py` | Per-D `\|δ_j − F_j\|` with **correct** lattice | Empirical bridge; MAE ≈ 0.002 |
| `scripts/split_predict.py` | Full-band F_j vs MC with MAE + noise floor | Same model as audit |
| `scripts/qclass_split_refine.py` | Q-class long-band refine; uses `predict_split_Q` (image lattice generalized) | Sidecar `data/qclass/split/refine_latest.*` |
| `scripts/qclass_split_twostep.py` | Two-step law vs `predict_split_Q` | `data/qclass/split/twostep_latest.*` |
| `scripts/qclass_split_monomial_compare.py` | Classic `predict_split` ≡ sidecar for monomials | `data/qclass/split/monomial_compare_latest.*` |
| `tests/test_split.py` | `predict_split` sums to modular weight | Unit test |
| `tests/test_qmaps.py` | Q-sidecar lattice + contraction | Unit test |
| `docs/AUDIT.md` (§ B.5) | Narrative + MAE table | Documentation |
| `docs/ERRATA.md` (B.5) | Repro commands | Documentation |

Other audits (not B.5): `audit_01`–`audit_04` in `verification/audit/` (cycle count, split convergence, bound sharpness, parity confound).

---

## 4. Sidecar proof artifacts (3,10)

| File | Content |
|------|---------|
| `data/qclass/split/proof_pilot_3_10.md` | Checklist + dependency graph |
| `data/qclass/split/ATTACK_PLAN.md` | PhD roadmap: G2d, G4, LM (Lemmas A–D) |
| `data/qclass/split/lm_pilot.md` | LM attack plan, empirical gaps |
| `data/qclass/split/bridge_lemma.md` | Bridge sketch (G1–G4) |
| `data/qclass/split/llt_bands.md` | G2: LLT on dyadic bands |
| `data/qclass/split/lm_deterministic_latest.md` | Trap ρ_L + exact decade Ψ |
| `data/qclass/split/CODE_MAP.md` | This file |
| `data/qclass/checks/LITERATURE.md` | LM literature verdict |

---

## 5. Gaps for LM deterministic proof

What **exists** (proven finite / exact compute):

- Trap partition `β_{18}`, `β_{27}` and `ρ_L` on `[1,M]`: amplitude **0.6** (`lm_deterministic_latest.md`)
- Exact decade `Ψ_j(10^n)` for `n=2…7`: gap **≥ 0.315**, antiphase (`lm_deterministic.py`, confirms `lm_liminf`)
- `Ψ_j(V)` range 0.67 on `V ≤ 10^7` (`lm_liminf_latest.md`)
- Labelling amplitude 0.6 across `L` in `[1,M]` (`lm_structure_latest.md`)
- Bridge MAE ≈ 0.002; image lattice fixed (B.5)

What **does not exist** (analytic / proof blockers):

| Gap | Description | Status |
|-----|-------------|--------|
| **No `g(v)` API** | First-landing map not exported | Workaround: `lm_deterministic.py` enumerates trap + window counts |
| **No Delange for `h_j`** | Literature [13–15] covers digit sums only | `checks/LITERATURE.md` |
| **Step 4.2.3** (`lm_pilot`) | Large-`L` window strata vs trap `ρ_L` along `V=b^n` | **Open** — weights `w_L(V)` not proven oscillatory |
| **LM formal lemma** | `liminf Ψ_j < limsup Ψ_j` along infinite sequence | **Open** — exact finite gap only |
| **Bridge G2d** | Pointwise LLT for `S_b(n^k)`, `k≥3` | **Open** — CLT via [15] §8.3.2; see `llt_bands.md` §6.3 |
| **Bridge G4** | First-landing mass ≡ labelling `a(v)` on Gaussian window | Sketch only |
| **`local_mean` lattice** | Feeding vs image lattice for general signatures | For (3,10) sig `{0}` they coincide |

---

## 6. Reproduce commands

```bash
python scripts/bridge_check.py --k 3 --b 10
python scripts/split_predict.py --k 3 --b 10 --d-max 90 --samples-hint 120000
python scripts/local_mean.py --k 3 --b 10 --v-max 10000000
python scripts/lm_liminf.py
python scripts/lm_structure.py --k 3 --b 10 --signature 0
python scripts/lm_deterministic.py --k 3 --b 10 --signature 0
python verification/audit/audit_05_lattice.py
```
