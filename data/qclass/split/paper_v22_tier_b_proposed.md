# Paper v2.2 — Tier B patches

**Status: MERGED 2026-09-01** into `paper/{en,pt-BR}/paper.{md,tex}` (commit `e67692b`).

This file is retained as a historical record of the patch set. For current merge
status see [`PAPER_FROZEN.md`](../PAPER_FROZEN.md) and [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md).

---

## Applied patches (summary)

### Patch 1 — §7.5 bridge MAE

Mean per-attractor absolute error `|δ_j(D) − F_j(D)|` over D=4…90 (87 bands,
120k samples/band): **≈0.0017**, at measurement noise floor (≈0.0014).
Short-band MAE on D≤60/64 remains **0.003** (different window).

### Patch 2 — §10.6′ label sweep extension

- D≤300: `label_sweep_k3_b10_sig0_D300_latest.md` — r≈**0.37**, amplitudes 0.192/0.132
- D≤1000: `label_sweep_k3_b10_sig0_D1000_latest.md` — amplitude survival; r≈**0.26**
  (`amplitude_only` — long-scale phase lock **not** claimed)

### Patch 3 — G4 landing depth

For `(k,b)=(3,10)`, sampled `v` reaches `[1,M]` in ≤2 steps (`g4_landing.py`;
scan to v≤10⁶). Proof for all `v` open.

### Patch 4 — Appendix A pipeline

Added: `bridge_check.py`, `lm_stratum.py`, `lm_oscillation.py`, `lm_suffix.py`,
`lm_carry_depth.py`, `g4_landing.py`.

### Patch 5 — PT-BR

Mirrored patches 1–4 in `paper/pt-BR/paper.{md,tex}`.

---

## Not included (Tier C/D — blocked)

- Lemma A appendix
- CLT vs LLT remark
- Lemma B/C/D as theorems
- Conditional non-convergence chain

---

*Merged 2026-09-01. Superseded by live paper.*
