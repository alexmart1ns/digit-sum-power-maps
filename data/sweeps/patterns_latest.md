# Padrões Usáveis — Análise do Dataset do Minerador

**Fonte:** `results_k1-500_b2-40_20260717T191848Z.jsonl`  
**Gerado:** 20260717T210510Z  
**Pares analisados (status ok):** 19500

## 0. Sanidade do Teorema 3.1
- Violações de |C| ≥ Cyc: **0** (teorema válido)
- Δ máximo observado: **98**
- k máximo / b máximo no dataset: 500 / 40

## 1. Matriz de correlação (R de Pearson)
_Preditor teórico-numérico × métrica observada. |R| alto = padrão explorável._

| preditor \ alvo | cyc_modular | num_attractors | delta | max_tail_depth_overall |
|---|---|---|---|---|
| `gcd_k_m` | -0.054 | -0.053 | -0.051 | -0.100 |
| `k_prime` | +0.338 | +0.314 | +0.285 | +0.080 |
| `k_ndiv` | -0.391 | -0.361 | -0.326 | -0.046 |
| `omega_m` | +0.436 | +0.419 | +0.391 | -0.237 |
| `k` | -0.004 | +0.101 | +0.163 | +0.540 |
| `b` | +0.487 | +0.420 | +0.360 | -0.123 |
| `m` | +0.487 | +0.420 | +0.360 | -0.123 |
| `k_mod_m` | +0.330 | +0.293 | +0.257 | -0.058 |
| `v2_gcd` | -0.259 | -0.255 | -0.241 | -0.207 |
| `gcd_power2` | -0.244 | -0.240 | -0.227 | -0.182 |
| `gcd_odd` | +0.268 | +0.263 | +0.249 | +0.216 |

## 2. H1 — Δ e |C| vs gcd(k, b−1)
| gcd(k, b-1) | n pares | Δ médio | Δ máx | |C| médio |
|---|---|---|---|---|
| 1 | 12011 | 14.46 | 98 | 23.29 |
| 2 | 3020 | 8.79 | 39 | 13.74 |
| 3 | 1394 | 14.15 | 70 | 22.35 |
| 4 | 732 | 6.90 | 20 | 10.68 |
| 5 | 466 | 16.55 | 69 | 26.03 |
| 6 | 318 | 8.91 | 23 | 13.75 |
| 7 | 248 | 17.70 | 66 | 28.25 |
| 8 | 166 | 5.16 | 18 | 7.67 |
| 9 | 148 | 7.55 | 20 | 11.95 |
| 10 | 109 | 8.86 | 20 | 14.11 |
| 11 | 98 | 13.95 | 70 | 23.16 |
| 12 | 90 | 7.17 | 13 | 11.17 |
| 13 | 83 | 19.86 | 73 | 32.22 |
| 14 | 53 | 10.23 | 20 | 16.26 |
| 15 | 50 | 26.88 | 64 | 41.84 |
| 16 | 47 | 4.06 | 9 | 6.06 |
| 17 | 44 | 16.93 | 53 | 28.34 |
| 18 | 41 | 7.44 | 13 | 11.44 |
| 19 | 39 | 14.67 | 63 | 25.05 |
| 20 | 25 | 7.52 | 10 | 11.52 |
| 21 | 23 | 12.52 | 22 | 19.13 |
| 22 | 22 | 11.77 | 26 | 18.95 |
| 23 | 21 | 10.05 | 33 | 16.43 |
| 24 | 20 | 7.35 | 11 | 11.35 |
| 25 | 20 | 5.85 | 14 | 9.10 |
| 26 | 19 | 12.89 | 22 | 18.89 |
| 27 | 18 | 5.28 | 10 | 7.78 |
| 28 | 17 | 10.06 | 19 | 16.18 |
| 29 | 17 | 11.41 | 35 | 20.47 |
| 30 | 16 | 13.31 | 22 | 21.31 |
| 31 | 16 | 20.50 | 43 | 30.38 |
| 32 | 15 | 3.73 | 8 | 5.73 |
| 33 | 15 | 20.13 | 54 | 32.93 |
| 34 | 14 | 6.43 | 14 | 10.43 |
| 35 | 14 | 23.29 | 63 | 37.79 |
| 36 | 13 | 7.00 | 12 | 11.00 |
| 37 | 13 | 14.69 | 44 | 25.31 |
| 38 | 13 | 12.77 | 35 | 22.00 |
| 39 | 12 | 13.58 | 27 | 22.33 |

### Estrutura 2-ádica de gcd(k, b−1)

| classe | n | Δ médio | Δ máx | |C| médio |
|---|---|---|---|---|
| potência de 2 | 3980 | 8.22 | 39 | 12.81 |
| ímpar (gcd ímpar) | 14750 | 14.54 | 98 | 23.36 |
| par composto (não 2^e) | 770 | 8.91 | 35 | 13.93 |

| v₂(gcd) | n | Δ médio | Δ máx |
|---|---|---|---|
| 0 | 14750 | 14.54 | 98 |
| 1 | 3625 | 8.87 | 39 |
| 2 | 877 | 7.01 | 20 |
| 3 | 186 | 5.40 | 18 |
| 4 | 47 | 4.06 | 9 |
| 5 | 15 | 3.73 | 8 |

- Entre potências de 2: correlação v₂(gcd)×Δ: R=-0.227, R²=0.052 (desprezível, n=3980)
- Esperado pelo density law: R **negativo** (maior v₂ ⇒ excesso colapsa).

## 3. H2 — k primo vs composto
| classe de k | n | Cyc médio | Δ médio | |C| médio |
|---|---|---|---|---|
| k primo | 3705 | 12.47 | 19.35 | 31.82 |
| k composto | 15756 | 6.68 | 11.57 | 18.26 |

Correlação nº-de-divisores(k) × Cyc(φ): R=-0.391, R²=0.153 (fraca)

## 4. H3 — Lei de densidade das bacias (generalização do 22/33/44%)
- Pontos comparados (ciclo modular × densidade física agregada): **152276**
- Correlação proporção-modular × densidade-física: **R=+1.000, R²=1.000** (muito forte)
- Erro absoluto médio |p_modular − q_física|: **0.0001** (quanto menor, mais a lei de densidade se generaliza)
- Dentro da cota teórica |q̂−p| ≤ (b−1)/M: **152276/152276 (100.00%)**
- Veredito: a densidade física segue a proporção residual modular? **CONFIRMADA**

## 5. Caracterização do match exato (Δ=0) — Problema 6.2
- Pares com match exato (Δ=0): **69** de 19500 (0.35%)
- Distribuição por base (top): b=2:5, b=26:4, b=3:3, b=18:3, b=33:3, b=4:2, b=8:2, b=9:2
- Match exato onde b-1 é primo: 25/69
- Maior k com match exato: 381

## 6. Envelope de Δ por base — Problema 6.1
| base b | Δ máximo |
|---|---|
| 2 | 8 |
| 3 | 13 |
| 4 | 17 |
| 5 | 19 |
| 6 | 21 |
| 7 | 20 |
| 8 | 28 |
| 9 | 22 |
| 10 | 24 |
| 11 | 30 |
| 12 | 34 |
| 13 | 29 |
| 14 | 35 |
| 15 | 37 |
| 16 | 51 |
| 17 | 30 |
| 18 | 38 |
| 19 | 37 |
| 20 | 41 |
| 21 | 37 |
| 22 | 52 |
| 23 | 54 |
| 24 | 58 |
| 25 | 44 |
| 26 | 43 |
| 27 | 66 |
| 28 | 44 |
| 29 | 50 |
| 30 | 57 |
| 31 | 70 |
| 32 | 98 |
| 33 | 37 |
| 34 | 70 |
| 35 | 66 |
| 36 | 86 |
| 37 | 47 |
| 38 | 67 |
| 39 | 86 |
| 40 | 85 |

Tendência base × Δ-máximo: R=+0.876, R²=0.768 (forte)
