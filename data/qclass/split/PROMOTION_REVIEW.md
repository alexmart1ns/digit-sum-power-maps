# Sidecar → paper promotion review (W4.4)

**Date:** 2026-09-01 | **Pilot:** `(k,b)=(3,10)`, signature `{0}`  
**Constraint:** [`PAPER_FROZEN.md`](../PAPER_FROZEN.md) — no `paper/` edits without explicit approval.

This document closes the 4-week execution programme ([`EXECUTION_PLAN.md`](EXECUTION_PLAN.md)).
It classifies sidecar artifacts for a future paper merge review.

---

## 1. Verdict summary

| Tier | Count | Action |
|------|-------|--------|
| **A — Already in paper** | 6 | None |
| **B — Safe to promote** (empirical / reproducibility) | 4 | Optional v2.2 footnotes |
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
| Gaussian label sweep `D≤300`, `r=0.735` | §10.6′ |
| MC split scale amplitude ≈0.18, `D≤90` | §7.5 observation |
| `local_mean.py` as LM diagnostic | §10 pipeline |

---

## 3. Tier B — Safe to promote (low risk)

Empirical refinements and reproducibility; do not change theorem status.

| Item | Sidecar evidence | Suggested paper edit | Caveat |
|------|------------------|----------------------|--------|
| **Bridge MAE** | `bridge_check.py`: mean **0.0017**, 87 bands `D=4…90` | Footnote in §7.5: refine “≈0.002” → “≈0.0017” | Still MC noise floor ~0.0025 |
| **Label sweep D=1000** | `label_sweep_latest.md`: amplitude survives; cross-decade **r=0.26** | Add sentence to §10.6′ after D=300 paragraph | Phase correlation weakens; do not claim long-scale phase lock |
| **Landing depth ≤2** | `g4_landing_latest.md`, `first_landing()` API | One-line remark in §7.5 or Appendix B: “every `v≥1` reaches `[1,M]` in ≤2 digit-sum steps for `(3,10)`” | Finite `v` scan to `10^6`; not a proof for all `v` |
| **New scripts** | `lm_stratum.py`, `lm_oscillation.py`, `g4_landing.py`, `lm_deterministic.py` | Add to §10 reproducibility pipeline paragraph | Sidecar paths `data/qclass/split/` |

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

## 6. Recommended v2.2 merge package (minimal)

If approving a **documentation-only** paper patch (no new theorems):

1. §7.5 footnote: bridge MAE **0.0017** (`bridge_check.py`, 87 bands).
2. §10.6′: one sentence on **D=1000** amplitude survival + **r=0.26** phase caveat.
3. §10 pipeline: list `lm_stratum.py`, `lm_oscillation.py`, `g4_landing.py`.
4. Optional Appendix: **Lemma (band cardinality)** from Tier C.

**Draft patches:** [`paper_v22_tier_b_proposed.md`](paper_v22_tier_b_proposed.md) (revised §post-validation).  
**Validation:** [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) — **conditional NO-GO** until checklist §7.

**Do not merge:** Lemmas B–D as theorems, conditional non-convergence chain, G2d claims.

---

## 7. Post-programme — next analytic targets

Execution programme **complete**. Open work ranked:

| Priority | Target | Route |
|----------|--------|-------|
| 1 | Analytic Lemma C | Route C-A (suffix classes, depth ≤2) |
| 2 | G2b covariance | Peter (2002) extraction → Route C-B |
| 3 | G2d | Literature / collaboration ([9] Problem 2) |
| 4 | Paper v2.2 | Tier B footnotes after reviewer approval |

---

## 8. Sign-off checklist

- [ ] Author approves Tier B text patches
- [ ] External reviewer confirms Lemma A appendix if included
- [ ] No promotion of empirical Lemma C as theorem
- [ ] `PAPER_FROZEN.md` updated after merge

---

*Sidecar only until checklist complete.*
