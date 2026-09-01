# Q-class sidecar (isolated laboratory)

Parallel engine for **$f(n)=S_b(Q(n))$** with positive leading coefficient.
Does **not** write into `data/sweeps/`, `data/mining/`, or `data/split/`.

## Findings (2026-09-01)

1. **Split oscillates for non-monomials.** $Q=1+3x+2x^2$, $b=10$: two $2$-cycles
   $\{6,10\}$ vs $\{15,19\}$ on signature $\{1,6\}$, antiphase ($r=-1$),
   amplitude $\approx 0.27$ on $8\le D\le 64$.

2. **$F_j$ failed on the wrong modular lattice, not on the Gaussian.** Digit-sum
   congruence is $S_b(Q(n))\equiv Q(n)\pmod{b-1}$. Mass must sit on
   $v\equiv Q(r)\pmod m$, not $v\equiv r$. Fixing this drops MAE from $\approx 0.17$
   to $\approx 0.006$ on the quadratic pilot and from $\approx 0.041$ to
   $\approx 0.003$ on $x^3$ (signature $\{0\}$).

3. **Monomial bridge.** For $Q=x^k$, `predict_split_Q` agrees with `predict_split`
   (image lattice $r^k$); see `split/monomial_compare_latest.md`.

4. **Excess identity holds** on the pilot grid; $\Delta\neq$ visible split in general
   ($x+x^2$ splits with $\Delta=0$ in-window; $1+x^3$ has $\Delta=0$, no split).

Results promoted to paper §7.5 and Appendix B.5 (`paper/*/paper.md`).

## Scripts

| Script | Output |
|--------|--------|
| `scripts/qclass_check.py` | `checks/` — OEIS / survey tables |
| `scripts/qclass_pilot.py` | `pilot/` — pilot $Q\times b$ |
| `scripts/qclass_split.py` | `split/` — short-band split / $F_j$ |
| `scripts/qclass_split_refine.py` | `split/refine_latest.*` — long band $D=8..64$ |
| `scripts/qclass_split_twostep.py` | `split/twostep_latest.*` — lattice diagnosis |
| `scripts/qclass_split_monomial_compare.py` | `split/monomial_compare_latest.*` |
| `scripts/qclass_excess.py` | `excess/` — $\Delta$ / digit layers |

Code: `src/dspm/qmaps.py`. Tests: `tests/test_qmaps.py`.

## Retention

Scripts may write both `*_YYYYMMDDTHHMMSSZ.*` and `*_latest.*`. Only `*_latest`
(and static notes like `lemma.md`, `checks/LITERATURE.md`) are kept in git.
Timestamped copies are regenerable and gitignored.
