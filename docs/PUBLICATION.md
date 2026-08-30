# Publication bundle

Minimum repository layout for the v2 article, reference implementation,
independent verification, tests, reproduction scripts, and primary datasets.

## Contents

| Path | Role |
|------|------|
| `paper/en/`, `paper/pt-BR/` | Article in Markdown and LaTeX |
| `paper/figures/` | Figures for §7 |
| `src/dspm/` | Reference implementation |
| `verification/` | Independent re-derivation of the theorems |
| `verification/audit/` | Scripts documenting each v1 error |
| `tests/` | Pytest suite |
| `scripts/` | CLI entry points for §6–§9 |
| `data/sweeps/` | Primary sweep archive (k ≤ 500, b ≤ 40) |
| `data/split/` | Split-curve measurements for §7 |
| `docs/AUDIT.md`, `docs/ERRATA.md` | Correction provenance (Appendix B) |

## Reproducibility

After `pip install -e ".[fast,stats,dev]"`:

```bash
pytest
python verification/verify_theorems.py
python scripts/cycle_structure.py
python scripts/analyze_patterns.py
ruff check src scripts tests verification
```

## PDF build

```bash
cd paper/en && pdflatex paper.tex
cd paper/pt-BR && pdflatex paper.tex
```

## Citation

See [`CITATION.cff`](../CITATION.cff). Code: MIT. Paper and docs: CC BY 4.0.
