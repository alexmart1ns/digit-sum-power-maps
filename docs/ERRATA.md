# Errata: v1 (July 2026) → v2 (August 2026)

Five claims in the July 2026 draft were wrong or incomplete. This file lists what changed and where. The reasoning
that produced each error, and the scripts that break it, are in [`AUDIT.md`](AUDIT.md); a condensed
version is Appendix B of the paper itself.

## The five corrections

**B.1. "The modular cycle count is flat for $v_2(k) \ge 1$."** *Withdrawn.* Corollary 6.2 of v1
transferred a property of the periodic-point count to the cycle count, which does not have it, and
its supporting test compared group means where constancy was at issue. Replaced by Proposition 6.3
(a closed form for $\mathrm{Cyc}(\varphi_{k,m})$) and Corollary 6.4 (the cycle count is not a
function of $\mathrm{rad}(k)$).

**B.2. "Signatures $\{1\}$ and $\{8\}$ have convergent splits."** *Withdrawn.* The convergence
verdict was read off a single-step slope, which reports convergence inside any flat stretch of a
quasi-periodic curve. Re-measured over $4 \le D \le 90$: all seven curves are non-monotone. §7.4 now
reports the whole curve and its amplitude.

**B.3. "The finite-window bound $(b-1)/M$ is saturated."** *Withdrawn.* The worst observed
error-to-bound ratio is 0.25. The sharp constant is $\min(|R_i|,\, m-|R_i|,\, s) \le \min(|R_i|,
b-2)$. Theorem 5.3 now states the sharp form, and the verification is reframed around the exact
integer identity of Proposition 5.2, which has no slack.

**B.4. "Prime exponents amplify attractors by $\approx 74\%$."** *Reinterpreted.* The number
replicates but is confounded with the parity of $k$, which is the actual driver. §9.3 gives the
controlled comparison.

**B.5. "The Gaussian sweep model $F_j$ uses residue classes $v \equiv r \pmod m$."** *Corrected.*
For $f(n)=S_b(n^k)$ the congruence is $v \equiv r^k \pmod m$ (image of the feeding residue under
the power map). For general $Q$, $S_b(Q(n))\equiv Q(n)\pmod{b-1}$, so mass must sit on
$v\equiv Q(r)\pmod m$. Using the wrong lattice inflated MAE by an order of magnitude on the Q-class
pilots; with the image lattice, $F_j$ matches measured splits at the noise floor. See §7.5 and
`data/qclass/split/refine_latest.md`.

## What changed in the paper, section by section

| Section | Change |
|---|---|
| Abstract | claim (II) now states the sharp bound and the integer identity; claim (III) covers both counting functions; an *Erratum* paragraph was added |
| §1.3 Scope and contribution | "saturated" bound replaced by the sharpened bound; the cycle-count formula is now flagged as the one the lower bound needs |
| §5 Theorem 5.3 | sharp bound $\min(|R_i|, m-|R_i|, s)/M$, with the proof rewritten to track over- and under-represented classes; new Remark 5.3a on why the loose bound makes for weak verification |
| §6 | retitled to cover cycles as well as periodic points; Corollary 6.2 restated as radical dependence *of the periodic-point count*; new Proposition 6.3 (cycle count), Corollary 6.4 (counterexamples), Remark 6.5 (scope) |
| §7.4 | tripartite classification replaced by "no signature's split converges", with measured ranges for all seven attractors and the recurrence of the three small fixed points; methodological note added |
| §7.5 | image-lattice correction for $F_j$; Q-class pilots ($x^3$, $1+3x+2x^2$); caveat on how much an MAE at the noise floor can prove |
| §7.6 | "Result" downgraded to "Observation", with an explicit statement of what finitely many bands can and cannot establish |
| §8.2 | table reordered to put the exact integer statements first; new paragraph on which rows carry evidence |
| §9.2 | "Correction (important)" replaced by a caution about cross-modulus aggregation; both earlier readings withdrawn |
| §9.3 | retitled to parity rather than primality, with a controlled table |
| §10 | Problem 10.7 updated (modular count side now closed); new Problem 10.8 on the complexity of evaluating the cycle count |
| §11 Conclusion | rewritten to match all of the above |
| Appendix A | file paths updated to the `dspm` package; the independent verification now covers Lemma 5.1, Proposition 5.2 and both bounds |
| Appendix B | the errata, with the reasoning behind each error (now five items, incl. B.5 lattice) |

All four language/format variants were updated in parallel: `paper/en/paper.md`, `paper/en/paper.tex`,
`paper/pt-BR/paper.md`, `paper/pt-BR/paper.tex`.

## What changed in the code

The v1 scripts lived flat in a `miner/` directory and imported each other by `sys.path` insertion.
They are now the `dspm` package plus thin command-line wrappers in `scripts/`. Two of the original
scripts contained the defective verifications described above and were replaced rather than moved:

| v1 | v2 | why |
|---|---|---|
| `miner/cycle_collapse.py` | `scripts/cycle_structure.py` | tested flatness by comparing group means; now verifies both closed forms against brute force and prints within-group spread |
| `miner/split_scale.py` | `scripts/split_scale.py` | inferred convergence from a single-step slope; now reports the full curve, amplitude, monotonicity and noise floor |
| `miner/split_predict.py` | `scripts/split_predict.py` | ported unchanged in substance |
| `miner/miner.py` | `scripts/sweep.py` | ported; now also records failures of the exact integer identity |
| `verify_papers.py` | `verification/verify_theorems.py` | extended to cover Lemma 5.1, Proposition 5.2 and the sharp bound |

New in v2: `dspm.modular.cycle_count_formula` (Proposition 6.3), `dspm.numtheory` (exact integer
helpers extracted from the old scripts), `dspm.split` and `dspm.predict` (the measurement and model,
importable rather than script-only), `dspm.patterns` (the §9 statistics, with spread reported next to
each group mean), the `tests/` suite, and the five `verification/audit/` scripts.

New in v2.1 (Q-class, 2026-09): `dspm.qmaps` (sidecar for $S_b(Q(n))$), `scripts/qclass_*.py`,
`tests/test_qmaps.py`, and `data/qclass/` (isolated laboratory outputs).

## Reproducing each correction

```bash
python verification/audit/audit_01_cycle_count.py                        # B.1
python verification/audit/audit_02_split_convergence.py --samples 120000  # B.2 (paper uses 120k; 60k was original errata run)
python verification/audit/audit_03_bound_sharpness.py                    # B.3
python verification/audit/audit_04_parity_confound.py                    # B.4
python verification/audit/audit_05_lattice.py                            # B.5
python scripts/qclass_split_refine.py                                    # B.5 (image lattice)
```

Each audit prints its own verdict and exits 0. Audit 2 takes about half a minute; the others are quick.
