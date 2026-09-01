# Publication bundle

Minimum repository layout for the v2.1 article, reference implementation,
independent verification, tests, reproduction scripts, and primary datasets.

## Contents

| Path | Role |
|------|------|
| `paper/en/`, `paper/pt-BR/` | Article in Markdown and LaTeX |
| `paper/figures/` | Figures for §7 (`plot_split_figures.py`) |
| `src/dspm/` | Reference implementation |
| `src/dspm/qmaps.py`, `src/dspm/mining/` | Q-class sidecar and §10 mining (v2.1) |
| `verification/` | Independent re-derivation of the theorems |
| `verification/audit/` | Five audit scripts (B.1–B.5) |
| `tests/` | Pytest suite (`test_qmaps`, `test_mining`, `test_split_predict`, …) |
| `scripts/` | CLI entry points for §6–§10 |
| `data/sweeps/` | Primary sweep archive (k ≤ 500, b ≤ 40) |
| `data/split/` | Split-curve measurements and diagnostics for §7 |
| `data/qclass/` | Isolated Q-class laboratory outputs |
| `data/mining/` | Topic-10 mining summaries (`results_*.jsonl` regenerable) |
| `docs/AUDIT.md`, `docs/ERRATA.md` | Correction provenance (Appendix B) |

## Reproducibility

After `pip install -e ".[fast,stats,dev]"`:

```bash
pytest
python verification/verify_theorems.py
python verification/audit/audit_01_cycle_count.py
python verification/audit/audit_02_split_convergence.py --samples 120000
python verification/audit/audit_03_bound_sharpness.py
python verification/audit/audit_04_parity_confound.py
python verification/audit/audit_05_lattice.py
python scripts/cycle_structure.py
python scripts/split_scale.py --k 3 --b 10 --d-max 90 --samples 120000
python scripts/sweep_label.py --k 3 --b 10 --d-max 300
python scripts/sweep_label.py --k 3 --b 10 --d-max 1000   # extended diagnostic
python scripts/local_mean.py --k 3 --b 10 --v-max 10000000
python scripts/plot_split_figures.py --k 3 --b 10 --oscillation
python scripts/qclass_universality_grid.py
python scripts/qclass_split_monomial_compare.py
python scripts/qclass_excess.py
python scripts/bridge_check.py --k 3 --b 10
python scripts/mine_topic10.py --quick
python scripts/analyze_topic10.py --skip-tightness --skip-deep
ruff check src scripts tests verification
```

Regenerate the exhaustive sweep (hours):

```bash
python scripts/sweep.py --k-max 500 --b-max 40
```

## PDF build

```bash
cd paper/en && pdflatex paper.tex
cd paper/pt-BR && pdflatex paper.tex
```

## Citation

Article (Zenodo): [https://zenodo.org/records/22181953](https://zenodo.org/records/22181953) ·
DOI [10.5281/zenodo.22181953](https://doi.org/10.5281/zenodo.22181953)

See also [`CITATION.cff`](../CITATION.cff). Code: MIT. Paper and docs: CC BY 4.0.
