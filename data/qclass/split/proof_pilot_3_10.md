# Proof checklist: pilot (k,b) = (3,10), signature {0}

Sidecar only. Tracks progress toward Conjecture 10.6 / 10.6′ without claiming
a completed proof.

| Artifact | Role |
|----------|------|
| [`bridge_lemma.md`](bridge_lemma.md) | Draft bridge δ_j = F_j + o(1) |
| [`lemma.md`](lemma.md) | Conditional LLT + LM ⇒ no limit |
| [`checks/LITERATURE.md`](../checks/LITERATURE.md) | LM verdict (option ii+iii) |
| `scripts/bridge_check.py` | Per-D \|δ_j − F_j\| on measured MC curve |

---

## Checklist

| # | Step | Status | Evidence |
|---|------|--------|----------|
| 1 | **LLT** for `S_b(n^3)` on `N_D ∩ (r+9ℤ)` feeding `{0}` | Input [9] | Paper §10 Hypothesis LLT; DMR 2011 |
| 2 | **Image lattice** `v ≡ r^3 (mod 9)` | Done | Errata B.5; audit_05 MAE 0.002 vs 0.033 |
| 3 | **F_j** = `predict_split` (parameter-free) | Done | `split_predict.py`; MAE ≈ 0.002 |
| 4 | **Bridge** δ_j(D) = F_j(D) + o(1) | Open (sketch) | Gaps G2, G4 in `bridge_lemma.md` |
| 5 | **LM** for Ψ_{18}, Ψ_{27} | Open | `local_mean_latest.md`: Pearson 0.57 @ V≤10⁷ |
| 6 | **Non-convergence** of δ_j | Conditional | Conjecture 10.6; needs (4)+(5) |
| 7 | **10.6′ pilot** antiphase, sum 1/3 | Empirical | MC + Gaussian sweep SURVIVES |

---

## Empirical anchors (3,10), signature {0}

**Attractors:** `{18}`, `{27}`; modular weight `p_i = 1/3`.

| Diagnostic | Key numbers | File |
|------------|-------------|------|
| MC split scale | amp ≈ 0.19, 120k samples/band, D≤90 | `data/split/split_scale_k3_b10_latest.json` |
| Gaussian label sweep D≤300 | amp 0.11–0.19, cross-decade r=0.735 | paper §10.6′ |
| Gaussian label sweep D≤1000 | amp survives; cross-decade r=**0.26** | `label_sweep_latest.md` |
| Bridge MAE | ≈ 0.002 (F_j vs MC) | `audit_05_lattice.py`, `bridge_check.py` |
| Local mean LM | inconclusive | `local_mean_latest.md` |

**Nuance (D=1000):** amplitude does not collapse, but **phase correlation**
between decades weakens (0.26 vs 0.735). Do not overclaim long-scale phase
stability; amplitude survival alone supports 10.6′ under LLT, not full LM.

---

## Proof dependency graph

```text
[9] DMR LLT on progressions
        │
        ▼
  bridge_lemma (δ_j = F_j + o(1))  ◄── gaps G2, G4
        │
        ├──► F_j explicit (predict_split)     ✓ empirical
        │
        └──► LM (Ψ_j non-convergence)         ✗ open
                    │
                    ▼
           Conjecture 10.6 (no limit for δ_j)
```

---

## Suggested order of attack

1. Formalize **G2**: uniform LLT remainder on dyadic bands `N_D` for `n^3`.
2. Prove **LM** for `h_{18}, h_{27}` OR find a counterexample (would refute 10.6).
3. Only then promote bridge + conditional lemma to the main paper.

---

## Commands

```bash
python scripts/bridge_check.py --k 3 --b 10
python scripts/split_predict.py --k 3 --b 10 --d-max 90 --samples-hint 120000
python scripts/local_mean.py --k 3 --b 10 --v-max 10000000
python verification/audit/audit_05_lattice.py
```
