# Topic 10 follow-up (intra-modulus, tightness, bounds)

**Generated:** 20260831T023906Z  
**Source JSONL:** `data\mining\results_full_20260831T020654Z.jsonl`  
**gmpy2:** True

## 10.1 / 10.7 Intra-modulus local excess

- Ok pairs with local_excess: **7470** across **60** moduli
- Split signatures at one digit layer: **39251**
- Split signatures at two or more layers: **11861**
- Moduli with Spearman(delta_local, n_digit_layers) defined: 60
- Of those, Spearman > 0: **60**
- Moduli with mean Delta (k odd) > mean Delta (k even): 60 / 60

Correlations are computed inside each m=b-1 separately. Do not pool rows across moduli. Same-layer splits (delta_local>0 and n_digit_layers=1) are the obstruction to 'layers cause excess'.

Same-layer splits are physical attractors sharing a residue cycle but sitting at a single digit length. They block the working hypothesis that excess is just 'more digit layers'.

### Highlighted moduli

| m | b | pairs | mean Delta | mean Delta odd | mean Delta even | rho layers (local) | same-layer splits | multi-layer splits |
|---|---|------:|-----------:|---------------:|----------------:|--------------------:|------------------:|-------------------:|
| 1 | 2 | 400 | 3.49 | 3.5 | 3.48 | 0.401 | 0 | 395 |
| 2 | 3 | 400 | 5.405 | 5.47 | 5.34 | 0.479 | 183 | 578 |
| 9 | 10 | 400 | 7.3425 | 8.9 | 5.785 | 0.379 | 879 | 476 |
| 15 | 16 | 86 | 18.755814 | 23.9 | 6.884615 | 0.361 | 451 | 313 |
| 31 | 32 | 173 | 18.83237 | 22.342857 | 13.411765 | 0.353 | 971 | 491 |
| 79 | 80 | 58 | 17.551724 | 20.234043 | 6.090909 | 0.342 | 532 | 124 |

## 10.5 Upper-bound candidates (existing records)

- Scored pairs: **7470**
- Always holds: ['N_star', 'sum_signature_windows']
- Never holds: []
- Tightest surviving: {'name': 'sum_signature_windows', 'mean_slack': 6853.704, 'min_slack': 2, 'min_slack_at': {'k': 1, 'b': 2, 'C': 1, 'M': 3, 'bound': 3, 'slack': 2}}

Min slack 2 on both survivors is the tiny pair (k,b)=(1,2) (M=3, |C|=1). It is not a near-sharp bound on large systems. Mean slack stays O(M).

| candidate | hold rate | mean slack | min slack |
|-----------|----------:|-----------:|----------:|
| N_star | 1.0 | 10966.2525 | 2 |
| Cyc | 0.013788 | -12.8754 | -122 |
| Per | 0.18755 | -6.0918 | -122 |
| digit_layers | 0.013788 | -20.3723 | -198 |
| Cyc_times_layers | 0.387282 | -0.9202 | -67 |
| sum_signature_windows | 1.0 | 6853.704 | 2 |

A surviving upper bound must hold on every scored pair. N* always holds and is useless (slack ~ M). Cyc is a lower bound.

### Worst counterexamples (most negative slack)

- `digit_layers` fails at (k,b)=(157,80): |C|=201 bound=3 slack=-198
- `Cyc` fails at (k,b)=(157,80): |C|=201 bound=79 slack=-122
- `Per` fails at (k,b)=(157,80): |C|=201 bound=79 slack=-122
- `Cyc_times_layers` fails at (k,b)=(451,32): |C|=129 bound=62 slack=-67

## 10.2 Tightness census (b=2,3)

- k_max: **1500**
- Pairs in census (including reused full-run cells): **3000**
- Newly mined: 2200
- Exact Delta=0: **8**
- Exact k for b=2: [1, 2, 3, 7, 381]
- Exact k for b=3: [1, 6, 10]
- Max k with Delta=0: 381

This is a complete list on the rectangle {1..k_max} x {2,3}, not a rate.

## 10.3 / 10.4 Orbit and predecessors

- Prior E cells in the full run: **16** (bands<=2+tail: True; any CSN-plausible: False)
- Extra large-M cells this run: **3**
- (k,b)=(157,80) M=29180 Delta=122 L_window=15 bands<=2+tail=True CSN_plausible=False alpha=7.6328
- (k,b)=(493,38) M=54749 Delta=37 L_window=36 bands<=2+tail=True CSN_plausible=False alpha=8.0
- (k,b)=(499,37) M=54272 Delta=47 L_window=19 bands<=2+tail=True CSN_plausible=False alpha=3.6619

- All new bands bounded by 2 + max tail: **True**
- Any CSN-plausible power law: **False**

## Stopped

- 10.6 Fourier vs Gaussian: MAE already matches noise; no more cells.
- 10.8 Folded Cyc formula: already tested equal to the graph.
