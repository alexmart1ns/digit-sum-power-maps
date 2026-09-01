# Proposed paper v2.2 — Tier B patches (draft)

**Not merged.** Author approval required per [`PAPER_FROZEN.md`](../PAPER_FROZEN.md)
and [`PROMOTION_REVIEW.md`](PROMOTION_REVIEW.md) §8.

Apply to `paper/en/paper.md` and `paper/pt-BR/paper.md` (and `.tex` if kept in sync).

---

## Patch 1 — §7.5 bridge MAE (EN)

**Find (approx):** MAE ≈ 0.002 or similar bridge error citation.

**Replace with:**

> On the `(3,10)` pilot signature `{0}`, the mean per-band absolute error
> `|δ_j(D) − F_j(D)|` over attractors and `D=4…90` (87 bands, 120k samples/band)
> is **≈0.0017** (`scripts/bridge_check.py`).

---

## Patch 2 — §10.6′ label sweep extension (EN)

**After** the `D≤300` Gaussian diagnostic paragraph, **add:**

> A follow-up sweep to `D=1000` (`scripts/sweep_label.py`;
> `data/split/label_sweep_latest.md`) shows **amplitude survival** on the pilot,
> but cross-decade phase correlation weakens to Pearson `r≈0.26` (vs `r≈0.735` for
> `D≤300`). Amplitude persistence supports Conjecture 10.6′ under Hypothesis LLT;
> long-scale phase stability is **not** claimed.

---

## Patch 3 — §7.5 or Appendix B landing depth (EN)

**Add remark:**

> For `(k,b)=(3,10)`, every `v≥1` on the feeding lattice reaches `[1,M]` under at
> most **two** applications of `f_{3,10}` (`first_landing` in `src/dspm/predict.py`;
> scan `v≤10^6` in `scripts/g4_landing.py`). This finite-depth property is used in
> the sidecar bridge programme; a proof for all `v` is open.

---

## Patch 4 — §10 reproducibility pipeline (EN)

**Extend script list with:**

> Sidecar LM diagnostics: `scripts/lm_stratum.py`, `scripts/lm_oscillation.py`,
> `scripts/lm_suffix.py`, `scripts/lm_carry_depth.py`, `scripts/g4_landing.py`
> (outputs under `data/qclass/split/`).

---

## Patch 5 — PT-BR

Mirror patches 1–4 in `paper/pt-BR/paper.md` with equivalent Portuguese prose.

---

## Not included (Tier C/D — blocked)

- Lemma A appendix
- CLT vs LLT remark
- Lemma B/C/D as theorems
- Conditional non-convergence chain

---

*Draft 2026-09-01. Sidecar only until sign-off.*

---

## REVISED patches (post 3-reviewer validation)

See [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md). **Conditional NO-GO** until B1–B7 closed.

### Patch 1 (revised) — §7.5 bridge MAE

> Comparing Monte-Carlo measured splits to the parameter-free prediction
> (`scripts/bridge_check.py`; `split_scale_k3_b10_latest.json`, 120 000 samples per band)
> gives mean per-attractor absolute error `|δ_j(D) − F_j(D)|` over D=4…90 (87 bands) of
> **≈0.0017**, at the measurement noise floor (≈0.0014).

Harmonize abstract/§7.5 prior **0.003** references; update noise-floor paragraph to 120k samples.

### Patch 2 (revised) — §10.6′ D=1000

> Extending the Gaussian-window diagnostic to D=1000
> (`data/split/label_sweep_k3_b10_sig0_D1000_*.md`) shows **amplitude survival**
> (0.19 on 10≤D≤99; 0.13 on 100≤D≤1000), but cross-decade phase correlation on the
> overlapping 10¹–10² interval weakens to Pearson **r≈0.26** (cf. **r≈0.735** for D≤300).
> Antiphase and sum 1/3 persist at every D. Tagged **amplitude_only** — do **not** claim
> Conjecture 10.6′ phase stability at D=1000.

**B1:** freeze D≤300 citation path separately from `label_sweep_latest` (currently D=1000).

### Patch 3 (revised) — landing depth

> For `(k,b)=(3,10)`, every sampled `v` on the feeding lattice reaches `[1,M]` under at most
> **two** applications of `f_{3,10}` (`first_landing`; scan to **v≤10⁶** in `g4_landing.py`).
> Proof for all `v` open.

### Patches 4–5: **APPROVED** (unchanged)
