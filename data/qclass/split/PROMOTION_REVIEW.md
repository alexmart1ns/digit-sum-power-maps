# Sidecar → paper promotion review (W4.4)

**Date:** 2026-09-01 | **Pilot:** `(k,b)=(3,10)`, signature `{0}`  
**Status:** Tier B empirical patches **MERGED** into `paper/` on 2026-09-01 (`e67692b`).  
**Constraint:** [`PAPER_FROZEN.md`](../PAPER_FROZEN.md) — further `paper/` edits need explicit approval.

This document closes the 4-week execution programme ([`EXECUTION_PLAN.md`](EXECUTION_PLAN.md)).
It classifies sidecar artifacts for paper merge review.

---

## 1. Verdict summary

| Tier | Count | Action |
|------|-------|--------|
| **A — Already in paper** | 6 | None |
| **B — Safe to promote** (empirical / reproducibility) | 4 | **Merged** (v2.2 Tier B, 2026-09-01) |
| **C — Promote as conditional / remark** | 2 | Needs reviewer sign-off |
| **D — Blocked** (no theorem claim) | 8 | Stay sidecar until analytic closure |

**Programme exit:** conditional chain is **documented** in sidecar; **unconditional** bridge
and Conjecture 10.6 proof remain **open** (G2d + analytic LM).

---

## 2. Tier A — Already promoted (no action)

| Sidecar item | Paper location |
|--------------|----------------|
| Image lattice `v ≡ Q(r) (mod m)` | §7.5, Appendix B.5 |
| `F_j` / `predict_split` mechanistic model | §7.5 |
| Hypotheses LLT, LM; Conjecture 10.6 / 10.6′ | §10 (Problem 10.6) |
| Gaussian label sweep `D≤300`, `r≈0.37` | §10.6′ |
| MC split scale amplitude ≈0.18, `D≤90` | §7.5 observation |
| `local_mean.py` as LM diagnostic | §10 pipeline |

---

## 3. Tier B — Merged 2026-09-01

Empirical refinements and reproducibility; theorem status unchanged.

| Item | Sidecar evidence | Paper edit | Status |
|------|------------------|------------|--------|
| **Bridge MAE** | `bridge_check.py`: mean **0.0017**, 87 bands `D=4…90` | §7.5 + abstract | **Merged** |
| **Label sweep D=1000** | `label_sweep_k3_b10_sig0_D1000_latest.md`: amp survives; **r≈0.26** | §10.6′ `amplitude_only` caveat | **Merged** |
| **Landing depth ≤2** | `g4_landing_latest.md`, `first_landing()` API | §7.5 remark | **Merged** |
| **LM scripts** | `lm_stratum.py`, `lm_oscillation.py`, `lm_suffix.py`, `lm_carry_depth.py`, `g4_landing.py` | Appendix A pipeline | **Merged** |

Frozen data paths: `label_sweep_k3_b10_sig0_D300_latest.*` (D≤300, r≈0.37) and
`label_sweep_k3_b10_sig0_D1000_latest.*` (D≤1000, r≈0.26).

---

## 4. Tier C — Conditional / remark (reviewer required)

| Item | Sidecar | Suggested treatment | Blocker |
|------|---------|---------------------|---------|
| **Lemma A (G2-band)** | `llt_bands.md` §7 | Appendix lemma: `\|N_D^{(r)}\| = (b^D-b^{D-1})/m + O(1)` | Short combinatorial proof; cite in CLT reduction |
| **CLT leg for `b=10`** | `clt_citation.md` | Remark: [15] §8.3.13 + Ex. 8.3.15 gives CLT on progression slices; LLT remains Hypothesis | Distinguish CLT vs LLT explicitly in §10 |

Do **not** promote as theorems: Lemma B, C, D, or the conditional chain in `lemma.md`.

---

## 5. Tier D — Blocked (stay sidecar)

| Item | Reason | Re-open when |
|------|--------|--------------|
| **Lemma B** (`w_n → 1/2`) | Combinatorial proof in sidecar; not peer-reviewed as paper lemma | External review of `lemma_b_stratum.md` |
| **Lemma C** (oscillation) | Empirical only; Route C-C refutes convergence models but does not prove `limsup≠liminf` | Route C-A analytic bound or C-B + G2b |
| **Lemma D-depth** (full G4) | Depth ≤2 proven empirically; window identification needs G2d | G2d or conditional LLT + tail bounds |
| **Bridge `δ_j = F_j + o(1)`** | Sketch; gaps G2d, G4-window | G2d closed or explicit Hypothesis + error budget |
| **G2d memo** | Literature blocker documented | New citation or proof |
| **Conditional theorem** (`lemma.md`) | Packaging only; hypotheses not proved | Lemma B+C analytic + G2d or accepted hypothesis |
| **ATTACK_PLAN / EXECUTION_PLAN** | Internal programme tracker | N/A |
| **Route C-C refutation** | Computational; not a limit proof | — |

---

## 6. v2.2 merge package — **MERGED 2026-09-01**

Patches applied to `paper/{en,pt-BR}/paper.{md,tex}`:

1. §7.5: bridge MAE **0.0017** (`bridge_check.py`, 120k samples, 87 bands).
2. §10.6′: D=1000 amplitude survival + **r≈0.26** phase caveat (`amplitude_only`).
3. §7.5: G4 landing depth ≤2 remark.
4. Appendix A: LM sidecar scripts listed.

**Validation:** [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) — checklist B1–B7 **closed**.  
**Historical draft:** [`paper_v22_tier_b_proposed.md`](paper_v22_tier_b_proposed.md) (superseded).

**Do not merge:** Lemmas B–D as theorems, conditional non-convergence chain, G2d claims.

---

## 7. Post-programme — next analytic targets

Execution programme **complete**. Open work ranked:

| Priority | Target | Route |
|----------|--------|-------|
| 1 | Analytic Lemma C | Route C-A (suffix classes, depth ≤2) |
| 2 | G2b covariance | Peter (2002) extraction → Route C-B |
| 3 | G2d | Literature / collaboration ([9] Problem 2) |
| 4 | Paper v2.2 Tier C | Lemma A appendix after external review |

---

## 8. Sign-off checklist

- [x] Tier B text patches merged (`e67692b`)
- [x] `PAPER_FROZEN.md` updated after merge
- [x] No promotion of empirical Lemma C as theorem
- [ ] Author formal sign-off
- [ ] External reviewer confirms Lemma A appendix if included

---

*Tier B merge complete. Author sign-off pending.*
