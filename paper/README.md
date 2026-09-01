# Paper source

Bilingual article: English (`en/`) and Brazilian Portuguese (`pt-BR/`), each in Markdown and LaTeX.

## Canonical edit path

1. Edit **`paper/{en,pt-BR}/paper.md`** first (primary working copy).
2. Mirror substantive changes in the other language.
3. Sync **`paper.{tex}`** when preparing a LaTeX/PDF build (keep section structure identical).

Do not edit only `.tex` without updating `.md`, unless the change is purely typographic.

## Version label

- Package release: **`2.1.0`** (`pyproject.toml`, `CITATION.cff`).
- Paper header: **v2.1.0** with Tier B empirical patch (September 2026); errata in Appendix B.
- Merge governance: [`data/qclass/PAPER_FROZEN.md`](../data/qclass/PAPER_FROZEN.md).

## Figures (`figures/`)

Regenerate from measured data (120k samples, `split_scale_k3_b10_latest.json`):

```bash
python scripts/plot_split_figures.py --k 3 --b 10 --d-max 90 --lang en --oscillation
python scripts/plot_split_figures.py --k 3 --b 10 --d-max 90 --lang pt --oscillation  # PT titles
```

Outputs: `split_predict_overlay.svg`, `split_oscillation.svg`.

## §7.5 error metrics (do not conflate)

| Metric | Window | Typical value | Script |
|--------|--------|---------------|--------|
| Short-band MAE | D≤60 (or 8≤D≤64, 12k/band) | ≈0.003 | `split_predict.py` |
| Bridge MAE | D=4…90, 120k/band | ≈0.0017 | `bridge_check.py` |

Figure 2 overlay uses the **bridge** window (D=4…90).
