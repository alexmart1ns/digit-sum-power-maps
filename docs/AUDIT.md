# Audit of the July 2026 draft

This is the record of an adversarial re-reading of the v1 paper, done before the repository was
assembled. The goal was not to confirm the results but to find the weakest claim and break it. Five
claims broke (four in v1, one lattice fix in v2.1). Three of the v1 errors broke for the same reason: the original verification measured a statistic
that could not have distinguished the claim from its negation.

Each finding has an executable script under `verification/audit/`. They are self-contained and print
their own verdict.

---

## 1. The modular cycle count is not flat in $v_2(k)$

`verification/audit/audit_01_cycle_count.py`

**The v1 claim.** Corollary 6.2 asserted that within a fixed modulus the cycle count of
$\varphi_{k,m}$ drops once at $v_2(k)\colon 0 \to 1$ and is then flat for all $v_2 \ge 1$, "verified
for $m = 16, 17, 32, 37, 41, 64$".

**Two independent defects.**

The mathematical one: Proposition 6.1 counts periodic *points*, and $\#\mathrm{Per}$ genuinely is a
function of $\mathrm{rad}(k)$. The claim was transferred to the number of *cycles*, which is a
different object. A periodic element of order $d$ sits on a cycle of length $\mathrm{ord}_d(k)$, and
that depends on $k$ modulo $d$, not on which primes divide $k$. Direct counterexamples inside the
paper's own list of test moduli:

| $m$ | $k=2$ | $4$ | $8$ | $16$ | $32$ | $\#\mathrm{Per}$ |
|---|---|---|---|---|---|---|
| $37$ | 4 | 6 | 6 | 6 | 4 | 10 |
| $41$ | 3 | 4 | 3 | 6 | 3 | 6 |

The methodological one: the supporting script grouped $k$ by the odd part and $v_2$ of
$\gcd(k,\lambda(m))$ and compared group **means**. Re-running that test while also printing the
spread shows what it hid: for $m = 37$ every $v_2$ group contains $\{4, 6, 10\}$ and for $m = 41$
every group contains $\{3, 4, 6\}$, in the same proportions, so the means agree exactly while nothing
is constant. Worse, four of the six test moduli are degenerate: $\kappa_k$ collapses the unit part,
$\#\mathrm{Per} = 2$, and flatness holds vacuously. Only two of six cases were capable of failing,
and both did.

**Scale.** Across $m \in [2,500)$ there are 421 moduli with $\mathrm{Cyc}(\varphi_{2,m}) \ne
\mathrm{Cyc}(\varphi_{4,m})$, and every single one has identical $\#\mathrm{Per}$. Inside the paper's
own sweep grid ($m = b-1 \le 39$), 21 of 38 moduli behave this way. This was not a rare edge case.

**Replacement.** A closed form for the cycle count (Proposition 6.3 of v2), obtained by combining
local cycle types through the Chinese remainder theorem: the local type at $p^e$ is the multiset of
$\mathrm{ord}_d(k)$ over element orders $d$ in the $k$-coprime subgroup, and a tuple of local cycles
of lengths $\ell_i$ contributes $\prod \ell_i / \mathrm{lcm}(\ell_i)$ global cycles. Implemented as
`dspm.modular.cycle_count_formula` and checked against brute-force graph enumeration for all
$k \in [1,60]$, $m \in [1,259]$: 15,540 pairs, 0 discrepancies.

This is a strict improvement on v1: the count side of the lower bound theorem was previously closed
only for the wrong counting function.

---

## 2. No basin split converges

`verification/audit/audit_02_split_convergence.py`

**The v1 claim.** §7.4 classified the three signatures of $(k,b) = (3,10)$ into two that converge
(signatures $\{1\}$ and $\{8\}$, where a single attractor was said to capture all the mass while the
small fixed points $\{1\},\{8\},\{17\}$ decay to zero) and one that oscillates (signature $\{0\}$).

**The defect.** The measurement script decided convergence from the change in the split across one
step of $D$, declaring stabilization when that change fell below the sampling noise. A quasi-periodic
curve has long flat stretches, so the rule reports convergence whenever the sampled window happens to
lie inside one. The original run stopped at $D = 60$, which is inside such a stretch for two of the
three small fixed points. A local slope cannot establish a limit.

**Re-measurement.** $4 \le D \le 90$, 60,000 samples per band, sampling $\sigma \approx 0.002$. All
three "vanishing" fixed points come back after long silences: $\{17\}$ is numerically zero throughout
$22 \le D \le 70$ and returns to $0.027$ at $D = 79$; $\{8\}$ is zero throughout $13 \le D \le 49$
and peaks at $0.028$ at $D = 58$; $\{1\}$ vanishes over $13 \le D \le 64$ and returns to $0.026$ at
$D = 73$. All seven curves are non-monotone. The returns are two orders of magnitude above the noise
floor.

**Mechanism.** This is what makes the correction credible rather than just a longer run. The
trapping region is a *fixed* window ($M = 57$ here), so the first-passage landing distribution lives
on a fixed finite set and never escapes; it drifts and spreads slowly. The relevant basins are
$\beta_{\{1\}} = \{1,4,7,10,40\}$, $\beta_{\{8\}} = \{2,5,8,11,20,50\}$,
$\beta_{\{17\}} = \{14,17,23,47\}$: each small, and each containing one element well above the
others. Those high elements are what the drifting distribution sweeps back across at large $D$.

This correction strengthens the paper: *every* individual density fails to settle, not just one.

---

## 3. The $(b-1)/M$ bound is not saturated

`verification/audit/audit_03_bound_sharpness.py`

**The v1 claim.** The finite-window error bound $(b-1)/M$ of Theorem 5.3 was described as
"saturated", and §8.2 reported 100.00% of 152,276 measurements within it as the headline evidence.

**The defect.** The proof bounds the deviation of one residue class by $|R_i|$, but the deviations
across all $m$ classes sum to zero, so the sharp constant is $\min(|R_i|,\, m - |R_i|)$; and in a
window $M = qm + s$ only $s$ classes are over-represented, giving $\min(|R_i|, s) \le \min(|R_i|,
b-2)$. Over 295,446 comparisons the worst ratio of actual error to $(b-1)/M$ is **0.25**, while the
sharp bound is approached at **0.95**. A 100% pass rate against a bound that is never approached is
close to automatic.

The paper's own results table already displayed the gap (worst error 0.10 against a bound of 0.40)
without drawing the conclusion.

**Replacement.** Theorem 5.3 of v2 states the sharp bound, and the verification is reframed around
Proposition 5.2, the exact identity between integers: for every $(k,b)$ and every window, the number
of $n \le M$ reaching an attractor of signature $\gamma_i$ equals the number of $n \le M$ with
$n \bmod (b-1) \in R_i$. No floating point, no slack. That is the statement worth reporting a 0
failure count for.

---

## 4. "Prime exponents amplify attractors" is a parity effect

`verification/audit/audit_04_parity_confound.py`

**The v1 claim.** §9.3: prime $k$ gives mean $|C| = 31.82$ against $18.26$ for composite, about 74%
more.

**The defect.** Two is the only even prime, while roughly half of the composites are even, and
$2 \mid k$ collapses the 2-part of every local unit group ($\kappa_k$ strips it), cutting both
$\mathrm{Cyc}$ and $|C|$ sharply. The contrast is a parity contrast wearing a primality label.

**Controlled comparison**, exhaustive over $2 \le k \le 60$, $3 \le b \le 24$ (1,298 pairs):

| class of $k$ | $n$ | mean $|C|$ | sd | mean $\mathrm{Cyc}$ |
|---|---|---|---|---|
| prime (raw) | 374 | 17.27 | 10.03 | 7.97 |
| composite (raw) | 924 | 11.40 | 7.49 | 4.82 |
| odd prime | 352 | 18.09 | 9.76 | 8.25 |
| odd composite | 286 | 17.16 | 9.55 | 7.35 |
| odd (any) | 638 | 17.67 | 9.68 | 7.85 |
| even (any) | 660 | 8.66 | 4.34 | 3.68 |

Odd primes and odd composites differ by 0.93 against a within-class sd near 9.7: indistinguishable.
Odd and even differ by 9.01. The related correlation $R = -0.391$ between the number-of-divisors
function and $\mathrm{Cyc}$ carries the same confound, since even $k$ tends to have more divisors.

This one is a reinterpretation rather than a retraction: the number replicates, the causal reading
does not.

---

## 5. The Gaussian lattice used feeding residues of $n$

`verification/audit/audit_05_lattice.py`

**The v1 / early-v2 claim.** The parameter-free model $F_j$ in §7.5 placed Gaussian mass on
$v \equiv r \pmod m$ for each residue $r$ feeding a signature.

**The defect.** Casting out nines forces $S_b(n^k) \equiv n^k \pmod{b-1}$ exactly. The correct
congruence classes for the first iterate are $v \equiv r^k \pmod m$ (image lattice), not $v \equiv r$.
For general polynomials $Q$, the sidecar uses $v \equiv Q(r) \pmod m$ (`predict_split_Q` in
`dspm.qmaps`).

**Evidence.** On signature $\{0\}$ of $(3,10)$, band $8 \le D \le 64$ against measured Monte Carlo:

| lattice | MAE |
|---|---|
| feeding ($v \equiv r$) | $\approx 0.033$ |
| image ($v \equiv r^k$) | $\approx 0.002$ |

Q-class diagnostics: `data/qclass/split/twostep_latest.md` (lattice diagnosis),
`data/qclass/split/refine_latest.md` (long-band MAE after fix).

**Replacement.** `predict_split` and `predict_split_Q` use the image lattice; Appendix B.5 and
§7.5 document the correction. Reproduce: `python scripts/qclass_split_refine.py` or audit 5 above.

---

## What survived

Everything else. The lower bound theorem, the signature-determinacy lemma, the exact finite-window
mass partition, the aggregate density law, and the periodic-point formula all hold without exception
across the exhaustive grid and under an independent from-scratch reimplementation
(`verification/verify_theorems.py`, which imports nothing from `dspm`).

Two related claims in §9.2 were also re-examined and left in place with a caution attached rather
than removed: the $\gcd$ grouping table and the $\omega(b-1)$ correlations are real features of the
pooled data, but each row of the $\gcd$ table pools many different moduli, so no per-system law can
be read off it. `scripts/analyze_patterns.py` therefore reports the within-group standard deviation
and the number of distinct moduli next to every group mean.

## The pattern

| claim | statistic used | what was at issue | why it could not fail |
|---|---|---|---|
| cycle count flat | group means | constancy | means agree when groups hold the same multiset |
| splits converge | slope over one step | a limit | flat stretches look like convergence |
| bound saturated | pass rate against the bound | sharpness | a loose bound is always passed |
| $F_j$ lattice | MAE vs measured split | congruence class of $m_1$ | wrong lattice still gives a number |

The countermeasure adopted throughout this repository: prefer exact integer identities where they
exist, and where they do not, report amplitude, spread and noise floor next to every verdict. Every
audit script above prints the quantity that the original test omitted.
