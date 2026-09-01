# Proof checklist: pilot (k,b) = (3,10), signature {0}

Sidecar only. Tracks progress toward Conjecture 10.6 / 10.6′ without claiming
a completed proof.

| Artifact | Role |
|----------|------|
| [`bridge_lemma.md`](bridge_lemma.md) | Draft bridge δ_j = F_j + o(1) |
| [`llt_bands.md`](llt_bands.md) | G2: LLT on dyadic bands (DMR reduction) |
| [`lm_pilot.md`](lm_pilot.md) | LM attack plan for (3,10) |
| [`ATTACK_PLAN.md`](ATTACK_PLAN.md) | PhD roadmap for G2d, G4, LM |
| [`checks/LITERATURE.md`](../checks/LITERATURE.md) | LM verdict (option ii+iii) |
| `scripts/bridge_check.py` | Per-D \|δ_j − F_j\| on measured MC curve |

---

## Checklist

| # | Step | Status | Evidence |
|---|------|--------|----------|
| 1 | **LLT** for `S_b(n^3)` on `N_D ∩ (r+9ℤ)` feeding `{0}` | **Open** (G2d) | CLT: [15] §8.3.2; LLT: no citation — `llt_bands.md` §6.3 |
| 2 | **Image lattice** `v ≡ r^3 (mod 9)` | Done | Errata B.5; audit_05 MAE 0.002 vs 0.033 |
| 3 | **F_j** = `predict_split` (parameter-free) | Done | `split_predict.py`; MAE ≈ 0.002 |
| 4 | **Bridge** δ_j(D) = F_j(D) + o(1) | Open (sketch) | Gaps G2, G4 in `bridge_lemma.md` |
| 5 | **LM** for Ψ_{18}, Ψ_{27} | Open — trap ρ_L **proven** (amp 0.6); decade Ψ **exact** (gap ≥0.315, n≤7); limit **open** | `lm_pilot.md` §4.2, `lm_deterministic_latest.md` |
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
| Local mean LM | gap ≥0.315 on `V=10^n`; global range 0.67 | `lm_liminf_latest.md` |
| Deterministic trap + decade Ψ | gap **0.323** for `n=2…8`; `w_n→0.5` | `lm_deterministic_latest.md` |
| G4 landing depth | max **2** steps; no simple `b^T` period | `g4_landing_latest.md` |

**Nuance (D=1000):** amplitude does not collapse, but **phase correlation**
between decades weakens (0.26 vs 0.735). Do not overclaim long-scale phase
stability; amplitude survival alone supports 10.6′ under LLT, not full LM.

---

## Proof dependency graph

```text
[15] §8.3.2 CLT (composite b=10) ──► partial
[9]  AP equidist. (prime q only; no LLT k≥3)
        │
        ▼
  bridge_lemma (δ_j = F_j + o(1))  ◄── gaps G2a–G2d, G4
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

See [`ATTACK_PLAN.md`](ATTACK_PLAN.md) for the full PhD roadmap. Summary:

1. **LM-shadow lemma** (carry periodicity of `g(v)`) — highest feasibility
2. **G4-finite** (first-landing depends on `v mod b^T`) — in-house
3. **G2d** (pointwise LLT) — literature gap; external collaboration likely
4. Promote bridge + conditional lemma only after (1)–(2) or explicit G2d hypothesis

---

## Commands

```bash
python scripts/bridge_check.py --k 3 --b 10
python scripts/split_predict.py --k 3 --b 10 --d-max 90 --samples-hint 120000
python scripts/local_mean.py --k 3 --b 10 --v-max 10000000
python scripts/lm_deterministic.py --k 3 --b 10 --signature 0
python verification/audit/audit_05_lattice.py
```
