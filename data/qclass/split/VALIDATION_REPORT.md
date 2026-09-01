# Multi-reviewer validation report (pre-paper merge)

**Date:** 2026-09-01 | **Pilot:** `(k,b)=(3,10)`, signature `{0}`  
**Reviewers:** 3 independent PhD panels (mathematics, algorithms, paper audit)  
**Constraint:** No `paper/` edits until this checklist is closed.

---

## 1. Executive verdict

| Layer | Verdict | Summary |
|-------|---------|---------|
| **Mathematics** | **Conditional scaffold OK** | Lemma A + Proposition B-weight sound; G2d blocker honest; “Lemma C/D” over-labelled |
| **Algorithms** | **Reproducible with fixes** | Core numbers bit-exact; n=6 suffix gap spurious; G4 T≥6 vacuous |
| **Paper Tier B** | **Conditional NO-GO** | 4 revisions required before merge; Patch 4 approved |

**Overall:** **DO NOT MERGE** `paper_v22_tier_b_proposed.md` until §2 blockers cleared.  
Sidecar data is **fit for conditional documentation**; not fit for **unconditional theorems**.

---

## 2. Blockers before paper merge

| ID | Issue | Owner | Status |
|----|-------|-------|--------|
| B1 | `label_sweep_latest` now D=1000; paper cites D≤300 r=0.735 | data + paper | **open** |
| B2 | Patch 2 overclaims 10.6′ at D=1000 (verdict `amplitude_only`) | paper draft | **open** |
| B3 | Patch 1 find string wrong (0.003 not 0.002); sample counts stale | paper draft | **open** |
| B4 | Patch 3 says v≤10⁶; depth scan caps at 5×10⁵ | paper draft | **open** |
| B5 | `lm_suffix` n=6 gap 1.0 artifact; summary field misleading | scripts | **fix in progress** |
| B6 | `g4_landing` T≥6 periodicity vacuous at default v_max | scripts | **fix in progress** |
| B7 | `bridge_lemma.md` §1 cites [9] for LLT (contradicts audit) | sidecar | **open** |

---

## 3. Claims safe to cite (post-fix)

| Claim | Type | n-range | Evidence |
|-------|------|---------|----------|
| Two-stratum Ψ = wₙρₙ + wₙ₊₁ρₙ₊₁ exact | **Proven** (finite) | n≥2 | `lemma_b_stratum_latest` |
| wₙ, wₙ₊₁ → ½ | **Proven** (asymptotic) | n≥7 exact | combinatorial counts |
| Ψ₁₈ gap ≥ 0.32 | **Empirical** | n=2…14 subseq. | `lemma_c_oscillation_latest` |
| Route C-C refutes 4 model families | **Empirical** | hold-out n=9…14 | `lemma_c_oscillation` route_cc |
| Suffix witness [50,55] gap ≥ 0.12 | **Empirical** | n=9…14 | `lemma_c_analytic_latest` |
| ρₙ = Σαₙ(s)ρₙ(s) exact | **Identity** | n≥9 | `lemma_c_analytic_latest` |
| Landing depth ≤ 2 | **Empirical** | v≤5×10⁵ lattice | `g4_landing_latest` |
| Bridge MAE ≈ 0.0017 | **MC empirical** | D=4…90 | `bridge_check.py` |
| G2d open | **Literature** | — | `g2d_feasibility.md` |

---

## 4. Claims NOT safe for paper theorems

| Claim | Issue |
|-------|-------|
| Lemma C: limsup Ψ − liminf Ψ ≥ 0.32 | Finite n only; not limit proof |
| Lemma D-depth for all v | Scan bounded; no carry proof |
| ρₙ → L refuted | Only 4 model families tested |
| Conjecture 10.6′ at D=1000 | `amplitude_only`; r≈0.26 not 0.735 |
| δ_j = F_j + o(1) | Conditional on G2d |

---

## 5. Nomenclature recommendations (math panel)

| Current label | Recommended paper status |
|---------------|-------------------------|
| Lemma A | **Lemma** (band cardinality) |
| Lemma B (full) | **Proposition** (reduction) + empirical gap |
| Lemma C | **Empirical observation** |
| Lemma D-depth | **Computational evidence** |
| Conditional chain | **Theorem (conditional)** with explicit hypotheses |

---

## 6. Reviewer panels

| Panel | Agent | Focus |
|-------|-------|-------|
| Mathematics | [PhD math review](7482b78d-531d-466f-bc3e-456967afa3cd) | 41 claims table; logical gaps |
| Algorithms | [PhD algorithms review](9a0e25d6-0ced-4835-af59-8193d706bed7) | Reproducibility; min_count; MC vs exact |
| Paper audit | [Tier B audit](a170093e-2f3a-40a4-833e-b82652ede7b2) | Per-patch GO/NO-GO |

---

## 7. Merge checklist (GO criteria)

- [ ] B1: freeze `label_sweep_D300` archive path in paper citations
- [ ] B2–B4: apply revised wording in `paper_v22_tier_b_proposed.md` §revised
- [ ] B5–B6: script fixes merged; re-run `lm_suffix`, `g4_landing`
- [ ] B7: fix `bridge_lemma.md` §1 LLT citation
- [ ] Author sign-off (`PROMOTION_REVIEW.md` §8)
- [ ] Update `PAPER_FROZEN.md` after merge

---

*Sidecar only until checklist complete.*
