# Paper merge status

§7.5 image-lattice correction and Q-class numbers were promoted on 2026-09-01
into `paper/en/paper.md`, `paper/pt-BR/paper.md`, and the matching `.tex`
files. Appendix B.5 documents the lattice fix.

**v2.2 Tier B (2026-09-01):** PhD validation checklist B1–B7 closed. Paper
updated with reproducible bridge MAE ≈0.0017 (120k samples), corrected label
sweep paths (`label_sweep_k3_b10_sig0_D300_latest`, `_D1000_latest`), amplitude
survival language (r≈0.37 at D≤300; r≈0.26 at D≤1000; `amplitude_only`), G4
landing depth ≤2 remark, and LM sidecar script references. Lemma B/C/D remain
sidecar-only — not promoted as theorems.

**Production polish (2026-09-02, `25eb4b2`):** tex figures + appendix commands
(`6c8b149`), prose fixes (rad(k), b-adic band, σ-sum notation), post-programme
Route C-A/C-B empirical pilots (`g2b_*_latest`, `n≤16`). **Author sign-off §8
recorded** 2026-09-02 in [`split/PROMOTION_REVIEW.md`](split/PROMOTION_REVIEW.md).
Tag `v2.1.1` at `25eb4b2`; Zenodo upload pending.

The isolated laboratory (`data/qclass/`, `src/dspm/qmaps.py`) remains separate
from `data/sweeps/`, `data/mining/`, and `data/split/`.

Conditional proof notes stay in the sidecar until external review.
Promotion tier review: [`split/PROMOTION_REVIEW.md`](split/PROMOTION_REVIEW.md).
Pre-merge validation: [`split/VALIDATION_REPORT.md`](split/VALIDATION_REPORT.md).
