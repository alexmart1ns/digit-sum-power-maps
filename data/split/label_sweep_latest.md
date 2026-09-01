# Gaussian label sweep -- Conjecture 10.6' diagnostic

- pair: (k, b) = (3, 10)
- signature: [0]
- modular weight p_i = 0.333333
- D in [4, 300]
- attractors: ['[18]', '[27]']
- ceiling V = 4789 (no sampling of n)

## Verdict

SURVIVES: decade amplitude stays up and phase correlates across {log_b D} decades; under LLT, Conjecture 10.6' follows

- primary attractor: [27]
- secondary attractor: [18]
- Pearson(primary, secondary): -1.0000 (algebraic: two attractors sum to p_i)
- mean signature sum: 0.333333 (target 0.333333)

## Amplitude per {log_b D} decade

- D=4..9  amp=0.0738  mean=0.2176  frac_span=0.352  (partial period)
- D=10..99  amp=0.1132  mean=0.2001  frac_span=0.996  (full period)
- D=100..300  amp=0.1148  mean=0.1750  frac_span=0.477  (partial period)

## Cross-decade phase

- decades 10^1 vs 10^2  overlap n=201
- Pearson on {log_b D}: 0.7351
- amplitude on overlap: earlier 0.0718, later 0.1148

## Curve (every 10th D, plus endpoints)

    D   {log_b D}        [18]        [27]     sum
     4     0.6021      0.1623      0.1711    0.3333
    14     0.1461      0.1220      0.2113    0.3333
    24     0.3802      0.0768      0.2565    0.3333
    34     0.5315      0.1137      0.2197    0.3333
    44     0.6435      0.1240      0.2093    0.3333
    54     0.7324      0.1374      0.1960    0.3333
    64     0.8062      0.1672      0.1661    0.3333
    74     0.8692      0.1252      0.2081    0.3333
    84     0.9243      0.1125      0.2209    0.3333
    94     0.9731      0.1836      0.1498    0.3333
   104     0.0170      0.1803      0.1530    0.3333
   114     0.0569      0.1442      0.1892    0.3333
   124     0.0934      0.1687      0.1646    0.3333
   134     0.1271      0.1555      0.1778    0.3333
   144     0.1584      0.2094      0.1239    0.3333
   154     0.1875      0.2106      0.1227    0.3333
   164     0.2148      0.1548      0.1785    0.3333
   174     0.2405      0.1793      0.1540    0.3333
   184     0.2648      0.1647      0.1686    0.3333
   194     0.2878      0.1555      0.1779    0.3333
   204     0.3096      0.1593      0.1740    0.3333
   214     0.3304      0.1294      0.2039    0.3333
   224     0.3502      0.1139      0.2194    0.3333
   234     0.3692      0.1317      0.2016    0.3333
   244     0.3874      0.1614      0.1720    0.3333
   254     0.4048      0.1645      0.1688    0.3333
   264     0.4216      0.1631      0.1702    0.3333
   274     0.4378      0.1526      0.1807    0.3333
   284     0.4533      0.1380      0.1953    0.3333
   294     0.4683      0.1314      0.2019    0.3333
   300     0.4771      0.1373      0.1960    0.3333

