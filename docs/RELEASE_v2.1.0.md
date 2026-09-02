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
| Proof roadmap | `data/qclass/split/lemma.md`, `checks/LITERATURE.md` |
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

1. Tag `v2.1.0` on commit `6c8b149` (or `v2.1.1` if tag already published at `a535052`)
2. Upload bundle: code, paper (md+tex+pdf), figures, `data/qclass/*_latest`,
   `data/split/*_latest`, `data/mining/*_latest`, sweep `results_*.jsonl.gz`
3. New version at [Zenodo 22181953](https://zenodo.org/records/22181953)
4. Release notes: cite five errata, Q-class sidecar, label_sweep D=300/D=1000,
   Tier B bridge MAE 0.0017, tex figures + appendix sync (`6c8b149`)
