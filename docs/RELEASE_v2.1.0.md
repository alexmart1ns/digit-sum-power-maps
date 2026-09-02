# Release v2.1.0

## Summary

Second major bundle after the five errata (Appendix B). Adds reproducible split
prediction, Gaussian label-sweep diagnostics to D=300 (paper) and D=1000
(extended), Q-class universality grid, mining scripts for §10, image-lattice
fix for F_j, and audit B.5.

## Errata incorporated (B.1–B.5)

1. Cycle-count flatness claim → closed form `cycle_count_formula`
2. §7.4 tripartite convergence → strengthened non-existence (Result 7.6)
3. Bound saturation → sharp `min(|R_i|, b-2)/M`
4. Prime-k effect → parity confound
5. **New:** F_j lattice must use `v ≡ Q(r) (mod m)`, not `v ≡ r`

## New / updated artifacts

| Area | Path |
|------|------|
| Split loader v1→v2 | `src/dspm/split.py`, `tests/test_split_predict.py` |
| Figures | `scripts/plot_split_figures.py`, `paper/figures/*.svg` |
| Label sweep | `data/split/label_sweep_k3_b10_sig0_D300_latest.*` (paper); `_D1000_latest.*` (extended) |
| Local mean LM | `data/split/local_mean_latest.*` (V≤10⁷) |
| MC split scale | `data/split/split_scale_k3_b10_latest.json` (120k samples) |
| Q-class grid | `data/qclass/universality/grid_latest.*` |
| Excess campaign | `data/qclass/excess/excess_latest.*` |
| Proof roadmap | `data/qclass/split/lemma.md`, `data/qclass/checks/LITERATURE.md` |
| Mining | `data/mining/`, `scripts/mine_topic10.py`, `analyze_topic10.py` |

## Verification (all pass)

```bash
pytest
python verification/verify_theorems.py
python verification/audit/audit_01_cycle_count.py
python verification/audit/audit_02_split_convergence.py
python verification/audit/audit_03_bound_sharpness.py
python verification/audit/audit_04_parity_confound.py
python verification/audit/audit_05_lattice.py
```

## Zenodo upload checklist

**Recommended tag:** `v2.1.1` at commit `25eb4b2` (supersedes `v2.1.0` at `a535052`).

1. `git tag -a v2.1.1 25eb4b2 -m "v2.1.1: Tier B paper production + Route C-A/C-B pilots"`
2. `git push origin v2.1.1`
3. Upload bundle: code, paper (md+tex+pdf), figures, `data/qclass/*_latest`,
   `data/split/*_latest`, `data/mining/*_latest`, sweep `results_*.jsonl.gz`
4. New version at [Zenodo 22181953](https://zenodo.org/records/22181953)
5. Release notes: five errata; Tier B bridge MAE 0.0017; label_sweep D300/D1000;
   tex figures; post-programme pilots (`g2b_layer_cov`, `g2b_suffix_phase`, `n≤16`)

## Post-v2.1.0 patches (included in `v2.1.1`)

| Commit | Summary |
|--------|---------|
| `6c8b149` | Tex figures, appendix commands, B.2 footnote |
| `ec82044`–`3985981` | Route C-A witness `n≤16`; G2b layer/suffix pilots |
| `25eb4b2` | Paper prose (rad(k), b-adic band); dspm input guards |
