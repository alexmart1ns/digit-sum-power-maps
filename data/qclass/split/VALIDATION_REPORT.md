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
| **Paper Tier B** | **GO (Tier B empirical)** | Revisions B1–B4 applied to `paper/{en,pt-BR}/paper.{md,tex}` |

**Overall:** Tier B empirical updates merged into `paper/` on 2026-09-01.  
Sidecar data is **fit for conditional documentation**; not fit for **unconditional theorems**.

---

## 2. Blockers before paper merge

| ID | Issue | Owner | Status |
|----|-------|-------|--------|
| B1 | `label_sweep_latest` now D=1000; paper cites D≤300 r=0.735 | data + paper | **done** — `_D300_latest` and `_D1000_latest` frozen; paper cites both |
| B2 | Patch 2 overclaims 10.6′ at D=1000 (verdict `amplitude_only`) | paper draft | **done** — amplitude_only language; r≈0.26 at D=1000 |
| B3 | Patch 1 find string wrong (0.003 not 0.002); sample counts stale | paper draft | **done** — bridge MAE 0.0017; 120k samples; σ≈0.0014 |
| B4 | Patch 3 says v≤10⁶; depth scan caps at 5×10⁵ | paper draft | **done** — scan to v≤10⁶ stated; lattice scan in g4_landing |
| B5 | `lm_suffix` n=6 gap 1.0 artifact; summary field misleading | scripts | **done** (commit `8a8953b`) |
| B6 | `g4_landing` T≥6 periodicity vacuous at default v_max | scripts | **done** (commit `8a8953b`) |
| B7 | `bridge_lemma.md` §1 cites [9] for LLT (contradicts audit) | sidecar | **done** |

---

## 3. Claims safe to cite (post-fix)

| Claim | Type | n-range | Evidence |
|-------|------|---------|----------|
| Two-stratum Ψ = wₙρₙ + wₙ₊₁ρₙ₊₁ exact | **Proven** (finite) | n≥2 | `lemma_b_stratum_latest` |
| wₙ, wₙ₊₁ → ½ | **Proven** (asymptotic) | n≥7 exact | combinatorial counts |
| Ψ₁₈ gap ≥ 0.32 | **Empirical** | n=2…14 subseq. | `lemma_c_oscillation_latest` |
| Route C-C refutes 4 model families | **Empirical** | hold-out n=9…16 | `lemma_c_oscillation` route_cc |
| Suffix witness [50,55] gap ≥ 0.12 | **Empirical** | n=9…14 | `lemma_c_analytic_latest` |
| Suffix witness [50,95] gap ≥ 0.097 | **Empirical** | n=9…16 | `lemma_c_route_ca_latest` |
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

- [x] B1: freeze `label_sweep_D300` archive path in paper citations
- [x] B2–B4: apply revised wording in `paper_v22_tier_b_proposed.md` §revised
- [x] B5–B6: script fixes merged; re-run `lm_suffix`, `g4_landing`
- [x] B7: fix `bridge_lemma.md` §1 LLT citation
- [ ] Author sign-off (`PROMOTION_REVIEW.md` §8)
- [x] Update `PAPER_FROZEN.md` after merge

---

*Tier B empirical merge complete 2026-09-01. Author sign-off pending.*
