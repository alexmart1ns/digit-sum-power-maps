# Conditional lemma for Conjecture 10.6 (sidecar note)

The paper is frozen in this sequence. This note records the target statement
that `predict_split_Q` already implements as the candidate `F_j`. It is not a
peer-reviewed proof and does not modify `paper/en/paper.md`.

## Setup

Fix `Q ∈ ℤ[x]` of degree `≥ 1` with positive leading coefficient, base `b ≥ 2`,
`m = b − 1`. Let `f(n) = S_b(Q(n))`, `N_D` the D-digit band, `δ_j(D)` the
fraction of `N_D` whose first landing in `[1, M]` lies in the finite basin of
attractor `A_j`. Theorem 5.3 / the window identity give

`Σ_{A_j ⊂ γ_i} δ_j(D) → p_i`.

## Hypotheses

**LLT(Q, b, r).** On each residue class feeding a split signature, `S_b(Q(n))`
for `n` uniform in `N_D ∩ (r + mℤ)` admits a local Gaussian limit with mean
`Θ(D)` and standard deviation `Θ(√D)` (Drmota–Mauduit–Rivat [9] for monomials;
Hare–Laishram–Stoll supplies polynomial digit-sum size, not the full LLT).

**LM(Q, b, j).** The labelling mean `Ψ_j(V)` of `h_j(v) = 1_{g(v) ∈ β_j}` on
the window `[V − √V, V + √V]` restricted to residues in the image
`{Q(r) mod m : r feeds γ_i}` does not converge as `V → ∞`.

## Lemma (conditional; target of Conjecture 10.6)

Assume LLT for every residue feeding a split signature `γ_i` (`a_i ≥ 2`) and
LM for each attractor `A_j` of that signature. Then `lim_{D→∞} δ_j(D)` does
not exist. The same non-existence passes to the cumulative density on `[1, b^D]`
because band `D` has geometric weight `1 − 1/b`.

No identity `δ_j(D) = P_j({log_b D}) + o(1)` is claimed: decade collapse already
fails for the (3, 10) pilot.

## Characterisation of F_j (Salto 2)

Define `F_j(D)` by the Gaussian-sweep functional coded as `predict_split_Q`:
digit-count mixture of `Q(n)` on the D-band, independent-digit Gaussian for
`S_b`, lattice `v ≡ Q(r) (mod m)` for each residue `r` feeding the signature
(not `v ≡ r`; digit-sum congruence is `S_b(Q(n)) ≡ Q(n)`), convolution with
the exact labelling `a(v)`, scaled by `p_i`. Sidecar check
`data/qclass/split/twostep_latest.md`: this lattice drops MAE from 0.18 to
0.007 on `1+3x+2x^2` and from 0.041 to 0.002 on `x^3` at `b=10`.

For monomials `Q(r)=r^k`, matching `predict_split` in `src/dspm/predict.py`
(`v ≡ r^k mod m`). Monomial bridge: `monomial_compare_latest.md`.

Under LLT on the image lattice, `δ_j(D) = F_j(D) + o(1)` is the natural remainder
statement. `F_j` is explicit and parameter-free. Delange's period-1 factor remains
the wrong shape for this labelling. Long-band refine (`refine_latest.md`): MAE
≈ 0.006 on `1+3x+2x^2`, ≈ 0.003 on `x^3` at `b=10` (12k samples/band, D=8..64).

Gaussian-window diagnostic (`data/split/label_sweep_latest.md`): model oscillation
survives to `D=300` (Pearson phase 0.735 across decades); under LLT, Conjecture
10.6′ follows computationally.

## Proof roadmap (open)

```text
LLT(Q,b,r) on bands N_D          ──┐
                                   ├──► δ_j(D) = F_j(D) + o(1)  ──► no limit for δ_j
LM(Q,b,j) for labelling Ψ_j(V)  ──┘         (bridge)              (§7.5 weight 1-1/b)
```

| Step | Status | Action |
|------|--------|--------|
| 1. LLT on dyadic bands + progressions | Input for monomials [9]; open for general `Q` | Restrict DMR to `N_D^(r)`; cite Hare–Laishram–Stoll for size only |
| 2. Bridge LLT → `F_j` | Open (mechanistic §7.5) | Formalize Gaussian mixture + exact labelling as theorem |
| 3. LM for dynamics-induced `h_j` | Open; diagnosed by `local_mean.py` | Literature [13–15]; see `checks/LITERATURE.md` |
| 4. Cumulative density | Elementary given (2)+(3) | §7.5 Remark after Observation 7.6 |

**Retracted route:** thin-window Delange lemma with `C^1` period-1 factor (Appendix
B, Remark after LM). Do not use.

**Pilot:** `(k,b)=(3,10)`, signature `{0}`. DMR covers LLT for `n^3`; LM remains
the analytic gap. See also [`bridge_lemma.md`](bridge_lemma.md) and
[`proof_pilot_3_10.md`](proof_pilot_3_10.md).
