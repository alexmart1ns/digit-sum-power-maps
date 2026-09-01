# Lemma D (draft) — G4 first landing ≡ labelling

Sidecar only. Companion to [`bridge_lemma.md`](bridge_lemma.md) gap G4 and
[`g4_landing_latest.md`](g4_landing_latest.md).

---

## Setup

Fix `(k,b)=(3,10)`, `M=57`, `f(n)=s_{10}(n³)`. For `v ≥ 1`, let `g(v)` be the
first landing in `[1,M]` under iteration of `f`, and `a(v) = label[g(v)]` the
attractor index. Basins `β_j = { w ∈ [1,M] : label[w]=j }`.

**Implementation:** `first_landing(v, system)` in `src/dspm/predict.py`.

---

## Lemma D-finite (periodicity; draft)

There exists `T = T(k,b,M) ∈ ℕ` such that for all `v ≥ b^T` on the feeding
progressions `v ≡ r (mod 9)`, `r ∈ {0,3,6}`:

`g(v) = g(v + 9 · b^T)`  and hence  `a(v) = a(v + 9 · b^T)`.

*Proof sketch.* The map `f_{3,10}` on integers acts on base-10 digits with
carry propagation of bounded depth `d(k,b,M)` determined by the contraction
bound. For `v` large enough, only the lowest `T` digits of `v` affect the
first landing; high digits are erased before entering `[1,M]`. Finite
enumeration on `[1, b^T · 9]` establishes the period.

**Computational evidence:** `scripts/g4_landing.py` (2026-09-01):

| Finding | Value |
|---------|-------|
| Max landing steps for `v ≤ 10^6` | **2** |
| Mean landing steps | **1.83** |
| Simple periodicity `a(v)=a(v+9·b^T)` for `T≤8` | **Not found** (~47% mismatch at `T=1`) |

**Revision.** The naive periodicity Lemma D-finite as stated is **falsified** by scan.
A revised route: use **bounded depth** (`≤2` steps for pilot range) + explicit
digit-layer analysis rather than a single modulus `b^T`.

---

## Lemma D-window (bridge coupling; draft)

Let `μ_D = 9(D−1)/2`, `σ_D = √(10²−1)D/12` (Gaussian LLT center for `s_{10}(n³)`).
There exists `D_0` such that for `D ≥ D_0`, every integer `v` in the LLT window
`|v − μ_D| ≤ 6σ_D` with `v ≡ 0 (mod 9)` satisfies `v ≥ b^T` and

`#{ n ∈ Ω_{D,r} : s_{10}(n³) = v }` is proportional to `1_{a(v)=j}` on each
attractor basin `β_j` of signature `{0}`.

*Needs:* Lemma D-finite + LLT or CLT mass concentration in the window + tail bound G3.

---

## Status

| Component | Status |
|-----------|--------|
| `first_landing` API | **Done** (`predict.py`) |
| Basin enumeration | **Done** (`g4_landing.py`, `lm_deterministic`) |
| Periodicity `T` | **Computational** — scan in `g4_landing_latest` |
| Formal proof D-finite | **Open** — carry-depth bound |
| D-window for bridge | **Open** — needs G2d or CLT sandwich |

---

## Next step

Prove carry-depth bound `d(3,10,57)` explicitly from digit-length contraction
(Lemma 3.2 in paper), then set `T = d + 1`.
