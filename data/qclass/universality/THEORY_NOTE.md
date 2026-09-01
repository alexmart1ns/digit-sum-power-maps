# Universalité note: S_b(Q(n)) sidecar synthesis

Sidecar only — not merged into `paper/en/paper.md` until external review.

Sources: [`grid_latest.md`](grid_latest.md), [`../split/monomial_compare_latest.md`](../split/monomial_compare_latest.md), [`../pilot/pilot_latest.jsonl`](../pilot/pilot_latest.jsonl).

---

## Thesis

The architecture developed for `f_{k,b}(n) = S_b(n^k)` — modular skeleton +
digital fluctuation — **survives** for a small class of polynomials `Q` with
positive leading coefficient. What is closed is **structural** (bounds, window
identity, excess decomposition); what remains open is **analytic** (LLT for
general `Q`, LM for labelling, bridge theorem).

---

## What transfers (Problem C)

| Component | Monomial `x^k` | General `Q` | Status |
|-----------|--------------|-------------|--------|
| Lower bound `\|C\| ≥ Cyc` | Yes | Yes | Theorem 4.1 / Q analogue |
| Window mass identity | Yes | Yes | 0 failures in pilot |
| Excess `Δ = Σ(a_i−1)` | Yes | Yes | `excess_identity_holds_Q` |
| Split oscillation (band D) | Yes | Yes (examples below) | Empirical |
| `F_j` Gaussian sweep | `predict_split` | `predict_split_Q` | Image lattice `v≡Q(r)` |
| LLT on driving sum | DMR [9] | **Open** | HLS size bounds only |

**Monomial bridge:** for `k=3,4`, `b=10`, classic and sidecar engines agree
(MAE identical; image lattice match). See `monomial_compare_latest.md`.

---

## Grid summary (D ∈ [8,64], 8k samples/band)

| Q | b | Split? | Δ | amp max | antiphase r | F_j MAE |
|---|---|--------|---|---------|-------------|---------|
| x² | 10 | No | 0 | — | — | — |
| x² | 16 | Yes | 1 | 0.12 | −0.99 | 0.005 |
| x³ | 10 | Yes | 4 | 0.18 | −1.00 | 0.005 |
| x⁴ | 10 | Yes | 3 | 0.05 | −0.97 | 0.002 |
| x+x² | 10 | Yes | 1 | 0.01 | — | 0.002 |
| 1+3x+2x² | 10 | Yes | 1 | 0.26 | −1.00 | 0.008 |
| 1+x³ | 10 | No | 0 | — | — | — |
| 1+x³ | 8 | Yes | 1 | 0.16 | −1.00 | 0.004 |

Post-lattice `F_j` MAE is typically **0.002–0.008** wherever split is visible.

---

## Counterexamples and scope limits

1. **Δ vs split (count vs distribution).** Global `Δ>0` iff some signature has
   `a_i ≥ 2` in the trapping window (tautology from `Δ = Σ(a_i−1)`). This is
   **not** the same object as band oscillation of `δ_j(D)`; see
   [`excess/HYPOTHESES.md`](../excess/HYPOTHESES.md).

2. **Δ=0, no split in window:** `1+x³`, `b=10` — tight modular match, no
   intra-signature bifurcation visible on the grid band.

3. **Split without strong antiphase:** `x+x²`, `b=10` — small amplitude
   (0.01); only one split signature in grid.

4. **LLT for general Q:** not established; universality is **empirical** on the
   grid, not a theorem for all `Q ∈ ℤ[x]`.

---

## Relation to Problem B

- **Same mechanism:** Gaussian mixture + image lattice + exact labelling.
- **Same gap:** LM for dynamics-induced `h_j` (see `proof_pilot_3_10.md`).
- **Pilot for proofs:** monomial `(3,10)` remains the analytic entry point;
  Q-class validates portability of code and phenomenology.

---

## Recommended paper cross-ref (one line, when ready)

> Sidecar checks in `data/qclass/` confirm the §7.5 mechanism for several
> `S_b(Q(n))` instances; LLT for general `Q` and Hypothesis LM remain open.

Do **not** merge extended tables into §7.5 without review.
