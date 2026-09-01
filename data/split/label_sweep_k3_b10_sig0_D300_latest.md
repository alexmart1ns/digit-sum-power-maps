# Gaussian label sweep -- Conjecture 10.6' diagnostic

- pair: (k, b) = (3, 10)
- signature: [0]
- modular weight p_i = 0.333333
- D in [4, 300]
- attractors: ['[18]', '[27]']
- ceiling V = 4789 (no sampling of n)

## Verdict

AMPLITUDE SURVIVES across decades but cross-decade phase is weak; extend D through another full decade

- primary attractor: [18]
- secondary attractor: [27]
- Pearson(primary, secondary): -1.0000 (algebraic: two attractors sum to p_i)
- mean signature sum: 0.333333 (target 0.333333)

## Amplitude per {log_b D} decade

- D=4..9  amp=0.0451  mean=0.1776  frac_span=0.352  (partial period)
- D=10..99  amp=0.1921  mean=0.1460  frac_span=0.996  (full period)
- D=100..300  amp=0.1315  mean=0.1555  frac_span=0.477  (partial period)

## Cross-decade phase

- decades 10^1 vs 10^2  overlap n=201
- Pearson on {log_b D}: 0.3738
- amplitude on overlap: earlier 0.1229, later 0.1315

## Curve (every 10th D, plus endpoints)

    D   {log_b D}        [18]        [27]     sum
     4     0.6021      0.1607      0.1726    0.3333
    14     0.1461      0.1459      0.1875    0.3333
    24     0.3802      0.0743      0.2590    0.3333
    34     0.5315      0.1346      0.1988    0.3333
    44     0.6435      0.1247      0.2086    0.3333
    54     0.7324      0.1535      0.1798    0.3333
    64     0.8062      0.2421      0.0912    0.3333
    74     0.8692      0.1096      0.2238    0.3333
    84     0.9243      0.1224      0.2109    0.3333
    94     0.9731      0.2064      0.1270    0.3333
   104     0.0170      0.2066      0.1268    0.3333
   114     0.0569      0.1658      0.1675    0.3333
   124     0.0934      0.2032      0.1301    0.3333
   134     0.1271      0.1536      0.1798    0.3333
   144     0.1584      0.2075      0.1258    0.3333
   154     0.1875      0.1885      0.1448    0.3333
   164     0.2148      0.1032      0.2302    0.3333
   174     0.2405      0.1597      0.1737    0.3333
   184     0.2648      0.1713      0.1621    0.3333
   194     0.2878      0.1553      0.1780    0.3333
   204     0.3096      0.1343      0.1990    0.3333
   214     0.3304      0.0993      0.2340    0.3333
   224     0.3502      0.1017      0.2317    0.3333
   234     0.3692      0.1441      0.1892    0.3333
   244     0.3874      0.1913      0.1420    0.3333
   254     0.4048      0.1761      0.1572    0.3333
   264     0.4216      0.1569      0.1765    0.3333
   274     0.4378      0.1452      0.1882    0.3333
   284     0.4533      0.1427      0.1906    0.3333
   294     0.4683      0.1061      0.2273    0.3333
   300     0.4771      0.1058      0.2276    0.3333

