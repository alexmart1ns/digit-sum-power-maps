# G4 landing analysis (pilot)

M=57  minimal consistent T: **None**
Landing depth (samples): max **2**, mean **1.8307**

## Basins in [1,M]

- **[18]**: `[3, 6, 9, 12, 15, 18, 21, 24, 30, 45, 48, 51]` (12 points)
- **[27]**: `[27, 33, 36, 39, 42, 54, 57]` (7 points)

## Periodicity scan (a(v) vs a(v + m·b^T))

| T | modulus | pairs | mismatches | consistent |
|---|---------|-------|------------|------------|
| 1 | 90 | 333303 | 158333 | False |
| 2 | 900 | 333033 | 158401 | False |
| 3 | 9000 | 330333 | 157288 | False |
| 4 | 90000 | 303333 | 143771 | False |
| 5 | 900000 | 33333 | 16722 | False |
| 6 | 9000000 | 0 | 0 | False |
| 7 | 90000000 | 0 | 0 | False |
| 8 | 900000000 | 0 | 0 | False |

**Verdict:** no_T_found_in_range

Consistent T means a(v)==a(v+m*b^T) for all checked pairs on feeding lattice; supports Lemma D (G4-finite). Not a proof for all v.
