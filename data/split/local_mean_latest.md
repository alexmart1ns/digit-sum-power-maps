# v-space local means -- Hypothesis LM diagnostic

- pair: (k, b) = (3, 10)
- signature: [0]
- V in [100, 10000000], 201 scales, ceiling 10003164
- window: [V - sqrt(V), V + sqrt(V)] on feeding residues
- attractors: ['[18]', '[27]']
- amplitudes: {'[18]': 0.6677115987460814, '[27]': 0.6677115987460814}

## Decade collapse Psi(V) vs Psi(b V)

- n pairs: 161
- Pearson: 0.5671
- MAE: 0.0885  (sd base 0.1212, shifted 0.0806)
- amp base / shifted: 0.6677 / 0.5205

Pearson near 1 with MAE below the within-scale sd would support a period-1 factor in log_b V. A small Pearson with MAE on the order of the amplitude supports Hypothesis LM without that form.

