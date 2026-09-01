# Execution plan — pilot (3,10) proof programme

Sidecar tracker for [`ATTACK_PLAN.md`](ATTACK_PLAN.md). Paper frozen.

**Start:** 2026-09-01 | **Status:** programme **complete** (W4.4 done 2026-09-01)

---

## Overview

| Week | Theme | Exit criterion |
|------|-------|----------------|
| **1** | Finite closure + CLT leg | Lemma A promoted; CLT note; G4 draft; `first_landing` API |
| **2** | LM stratum weights (Lemma B) | `ρ_L^*` defined; `w_L(V)` asymptotics at `V=10^n` |
| **3** | LM oscillation (Lemma C) + bridge G4 | Lemma C draft; `bridge_lemma.md` G4 closed |
| **4** | G2d literature + conditional packaging | G2d memo; conditional theorem in `lemma.md` |

---

## Week 1 — Finite closure and CLT leg

| ID | Task | Output | Status |
|----|------|--------|--------|
| W1.1 | Promote **Lemma A (G2-band)** | `llt_bands.md` §7 numbered | **done** |
| W1.2 | CLT citation note [15] Thm 8.3.13 + Ex. 8.3.15 | `clt_citation.md` | **done** |
| W1.3 | Export `first_landing(v)` in `predict.py` | code + test | **done** |
| W1.4 | G4 periodicity analysis script | `g4_landing_latest.*` | **done** (no simple T; depth ≤2) |
| W1.5 | Draft **Lemma D (G4 landing)** | `lemma_d_g4.md` | **done** (revised) |
| W1.6 | Extend `lm_deterministic.py` (`n≤8`, `w_L`) | `lm_deterministic_latest.*` | **done** |

---

## Week 2 — LM 4.2.3 (Lemma B)

| ID | Task | Output | Status |
|----|------|--------|--------|
| W2.1 | Exact `N_L(b^n)` for `L∈{n,n+1}` | `lemma_b_stratum.md` | **done** |
| W2.2 | Define `ρ_L^*` via window rates | same + `lemma_b_stratum_latest.*` | **done** |
| W2.3 | Parity: Lemma B vs deterministic Ψ | error table (parity=0) | **done** |

---

## Week 3 — LM 4.2.4 + bridge

| ID | Task | Output | Status |
|----|------|--------|--------|
| W3.1 | Alternating bound on `Ψ_j(b^n)` | `lemma_c_oscillation.md` | **done** (empirical `c≥0.32`) |
| W3.2 | Close G4 in `bridge_lemma.md` | §7 Lemma D-depth | **done** |
| W3.3 | Peter (2002) covariance notes | `bridge_lemma.md` §9, `g2d_feasibility.md` | **done** |
| W3.4 | [9] Problem 2 feasibility memo | `g2d_feasibility.md` | **done** |

---

## Week 4 — G2d + conditional packaging

| ID | Task | Output | Status |
|----|------|--------|--------|
| W4.1 | G2d-A at `q=10` or blocker doc | `g2d_feasibility.md`, `llt_bands.md` | **done** (blocker memo) |
| W4.2 | Conditional theorem (LLT hyp + C + D) | `lemma.md` | **done** (sidecar packaging) |
| W4.3 | Bridge `o(1)` budget at larger D | `proof_pilot_3_10.md` | **done** (MAE 0.0017, D≤90) |
| W4.4 | Sidecar → paper promotion review | `PROMOTION_REVIEW.md` | **done** |

---

## Post-programme

| Priority | Target | Doc |
|----------|--------|-----|
| 1 | Uniform witness gap + Route C-B (G2b) | `lemma_c_analytic.md`, `g2b_peter_notes.md` |
| 2 | G2b / Route C-B programme | `g2b_peter_notes.md` |
| 3 | G2d literature | `llt_bands.md` §6.3 |
| 4 | Paper v2.2 (Tier B footnotes) | `paper_v22_tier_b_proposed.md` |

---

## Dependency graph (execution)

```text
W1.1–W1.2 (Lemma A + CLT) ──► G2a citation closed
W1.3–W1.5 (first_landing + Lemma D) ──► G4 draft
W1.6 (w_L table) ──► Week 2 Lemma B
W2.* ──► W3.1 Lemma C
W3.2 + W1.5 ──► bridge G4 closed
W4.* ──► conditional packaging
```

---

## Commands (reproduce Week 1)

```bash
python scripts/lm_stratum.py --k 3 --b 10 --n-max 14
python scripts/lm_oscillation.py --k 3 --b 10 --n-max 14
python scripts/g4_landing.py --k 3 --b 10
python scripts/bridge_check.py --k 3 --b 10
pytest tests/test_predict_landing.py -q
```

---

*Update status column as tasks complete.*
