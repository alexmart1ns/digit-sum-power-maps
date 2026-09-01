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

4. **Excess identity holds** on the pilot grid; $\Delta$ and band split are
   **different objects** (see `excess/HYPOTHESES.md`: H2a tautology vs H2b rejected).

5. **Universality grid** (`universality/grid_latest.md` + `THEORY_NOTE.md`): monomials
   $x^2,x^3,x^4$ and quadratics/cubics at bases $8,10,16$ — split presence,
   antiphase $r$, post-lattice $F_j$ MAE. Run `python scripts/qclass_universality_grid.py`.

6. **Excess campaign** (`excess/excess_latest.md`, `excess/HYPOTHESES.md`): 35
   $(Q,b)$ pairs; Spearman (digit layers, $\delta_i$) $\approx 0.89$ — empirical
   only. $\Delta>0$ iff split signature exists (tautology); does not predict
   oscillation amplitude.

7. **Problem B programme** (`split/bridge_lemma.md`, `split/proof_pilot_3_10.md`,
   `checks/LITERATURE.md` LM verdict): bridge $\delta_j=F_j+o(1)$ sketched; LM open.
   Validate bridge: `python scripts/bridge_check.py --k 3 --b 10`.

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
| `scripts/qclass_universality_grid.py` | `universality/` — $Q\times b$ grid |
| `scripts/bridge_check.py` | (stdout) — per-D $\|\delta_j-F_j\|$ on measured curves |
| `scripts/lm_structure.py` | `split/lm_structure_latest.*` — labelling vs digit length |
| `scripts/lm_liminf.py` | `split/lm_liminf_latest.*` — liminf/limsup of Ψ_j |

Code: `src/dspm/qmaps.py`. Tests: `tests/test_qmaps.py`.

## Key sidecar notes (Problem B / C / A)

| Path | Role |
|------|------|
| `split/bridge_lemma.md` | Draft bridge δ_j = F_j + o(1) |
| `split/llt_bands.md` | G2: band-restricted LLT from DMR [9] |
| `split/lm_pilot.md` | LM attack plan (3,10) |
| `split/lm_liminf_latest.md` | liminf/limsup of Ψ_j from local_mean |
| `split/lm_structure_latest.md` | Labelling vs digit length in `[1,M]` |
| `split/proof_pilot_3_10.md` | Checklist for (3,10); LM gap |
| `split/lemma.md` | Conditional LLT + LM ⇒ no limit |
| `checks/LITERATURE.md` | [13]–[15] vs Hypothesis LM |
| `universality/THEORY_NOTE.md` | S_b(Q(n)) synthesis |
| `excess/HYPOTHESES.md` | Pre-registered Δ tests H1–H5 |

## Retention

Scripts may write both `*_YYYYMMDDTHHMMSSZ.*` and `*_latest.*`. Only `*_latest`
(and static notes like `lemma.md`, `checks/LITERATURE.md`) are kept in git.
Timestamped copies are regenerable and gitignored.
