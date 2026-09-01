# Iterated Digit-Sum Power Maps

Reference implementation, datasets and paper for the family of discrete dynamical systems

$$f_{k,b}(n) = S_b(n^k),$$

where $S_b$ is the base-$b$ digit sum and $k \ge 1$ a fixed exponent. Every orbit is eventually
periodic, and the system is organized by the modular power map $\varphi_{k,b-1}(x) = x^k \bmod (b-1)$.

Three exact results, all verified computationally:

| | Statement | Where |
|---|---|---|
| **Lower Bound Theorem** | $\lvert C(k,b)\rvert \ge \mathrm{Cyc}(\varphi_{k,b-1})$ | paper §4 |
| **Basin Density Law** | the aggregate basin of each residue signature has natural density exactly $\lvert R_i\rvert/(b-1)$, and the finite-window form is an exact identity between integers | paper §5 |
| **Closed forms for the count side** | both $\#\mathrm{Per}(k,m)$ and $\mathrm{Cyc}(\varphi_{k,m})$ are computable without building a graph | paper §6 |

When several attractors share a residue signature, the individual basin densities do not appear to
exist. Along fixed digit-length they oscillate quasi-periodically, in antiphase, always summing to
the exact aggregate. That is the subject of §7, and it is an instance of the classical log-periodic
fluctuation of digital functions.

The current paper is **v2**. It corrects five errors in the July 2026 draft; see
[`docs/ERRATA.md`](docs/ERRATA.md) and [`docs/AUDIT.md`](docs/AUDIT.md).

**Q-class sidecar** (2026-09): `src/dspm/qmaps.py` and `data/qclass/` study
$S_b(Q(n))$ for general polynomials $Q$ with positive leading coefficient, isolated from the main
`data/split/` records. Post-v2.1 **Problem B** proof notes (bridge lemma, LM verdict) live in
`data/qclass/split/` — sidecar only until external review. See [`data/qclass/README.md`](data/qclass/README.md).

**Zenodo:** [https://zenodo.org/records/22181953](https://zenodo.org/records/22181953) · DOI [10.5281/zenodo.22181953](https://doi.org/10.5281/zenodo.22181953)

## Install

```bash
git clone https://github.com/alexmart1ns/digit-sum-power-maps.git
cd digit-sum-power-maps
pip install -e ".[fast,dev]"
```

Python 3.10+. There are no required dependencies: `gmpy2` (extra `fast`) is a pure speedup and every
code path has a stdlib fallback; `numpy` (extra `stats`) is used only by the pattern report.

## Use

```python
from dspm import build_system, cycle_count, cycle_count_formula

system = build_system(3, 10)          # exhaustive dynamics on the trapping region [1, M]
sorted(system.attractors)             # [(1,), (8,), (17,), (18,), (19, 28), (26,), (27,)]
system.M                              # the trapping bound; every attractor provably lies below it
system.basin_by_signature()           # aggregate basin size per residue signature

cycle_count(3, 9)                     # 3, by explicit graph construction
cycle_count_formula(3, 9)             # 3, by the closed form of Proposition 6.3
```

## Reproduce the paper

```bash
pytest                                          # theorem-level test suite
python verification/verify_theorems.py          # independent re-derivation, imports nothing from dspm
python scripts/cycle_structure.py               # both closed forms vs. brute force
python scripts/sweep.py --k-max 500 --b-max 40  # the exhaustive sweep behind §8 (hours; 28 workers)
python scripts/split_scale.py --k 3 --b 10 --d-max 90 --samples 60000
python scripts/split_predict.py --k 3 --b 10
python scripts/sweep_label.py --k 3 --b 10 --d-max 300
python scripts/local_mean.py --k 3 --b 10 --v-max 1000000
python scripts/plot_split_figures.py --k 3 --b 10 --oscillation
python scripts/bridge_check.py --k 3 --b 10      # |delta_j - F_j| per D (Problem B pilot)
python scripts/analyze_patterns.py              # the correlation tables of §9
python scripts/qclass_split_refine.py           # Q-class split / F_j (writes data/qclass/)
python scripts/mine_topic10.py --quick          # §10 stratified grid (writes data/mining/)
python scripts/analyze_topic10.py --skip-tightness --skip-deep
```

`verification/verify_theorems.py` shares no code with the package: it reimplements the
digit sum, the trapping region, both functional graphs and the modular structure from scratch, so a
bug in `dspm` cannot make a theorem appear to hold.

## Layout

```
paper/en, paper/pt-BR   the article, Markdown and LaTeX, English and Brazilian Portuguese
paper/figures           split_oscillation.svg, split_predict_overlay.svg
src/dspm/               the package (see below)
scripts/                command-line entry points; each writes JSON to data/
verification/           independent re-derivation of the theorems
verification/audit/     five audit scripts (B.1–B.5)
tests/                  pytest suite
data/sweeps/            sweep datasets (19,500 records for k ≤ 500, b ≤ 40)
data/split/             measured split curves and diagnostics (label_sweep, local_mean)
data/mining/            Topic-10 mining summaries (JSONL regenerable)
data/qclass/            Q-class laboratory (isolated from data/split/)
docs/AUDIT.md           how the v1 errors were found
docs/ERRATA.md          what changed between v1 and v2 (incl. B.5 lattice fix)
docs/PUBLICATION.md     publication bundle layout and Zenodo link
```

Inside the package:

| Module | Contents |
|---|---|
| `core` | the map, the digit sum, the rigorous trapping region $[1,M]$ |
| `numtheory` | elementary integer helpers, exact and floating-point free |
| `modular` | the modular power map: graph, cycles, and the two closed forms |
| `dynamics` | exhaustive physical dynamics on $[1,M]$: attractors and basins |
| `analysis` | one JSON record per $(k,b)$ pair, consumed by the sweep |
| `split` | Monte-Carlo measurement of the intra-signature split |
| `predict` | the parameter-free Gaussian-sweep model |
| `mining` | §10 stratified grid, excess, orbit/predecessor extras |
| `qmaps` | Q-class engine for $S_b(Q(n))$ (sidecar; see `data/qclass/`) |
| `patterns` | statistics over a sweep dataset |

## Verification

Three of the v1 errors survived because a claim was tested against a statistic that could not
distinguish it from its negation: a comparison of group means where constancy was at issue, a local
slope where a limit was at issue, and a loose inequality where sharpness was at issue. The code here
prefers exact integer identities where they exist, and reports amplitude, spread and noise floor next
to every numerical verdict where they do not. `docs/AUDIT.md` has the details.

## Publication

The article is published on Zenodo ([record](https://zenodo.org/records/22181953),
[DOI 10.5281/zenodo.22181953](https://doi.org/10.5281/zenodo.22181953)) with PDFs in English and Brazilian Portuguese.
Source versions: [`paper/en/paper.md`](paper/en/paper.md) and [`paper/pt-BR/paper.md`](paper/pt-BR/paper.md).
To build a PDF from LaTeX locally:

```bash
cd paper/en && pdflatex paper.tex    # English
cd paper/pt-BR && pdflatex paper.tex # Brazilian Portuguese
```

**Data availability.** The exhaustive sweep behind §8–§9 is archived under
[`data/sweeps/`](data/sweeps/) (`results_k1-500_b2-40_*.jsonl.gz`, 19,500 records). Split
measurements for §7 are in [`data/split/`](data/split/). Both are regenerable via the scripts above.

See [`docs/PUBLICATION.md`](docs/PUBLICATION.md) for the publication bundle layout.

## Citation

See [`CITATION.cff`](CITATION.cff). Article DOI: [10.5281/zenodo.22181953](https://doi.org/10.5281/zenodo.22181953).
MIT licensed; see [`LICENSE`](LICENSE).
