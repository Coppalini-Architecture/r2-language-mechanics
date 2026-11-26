# Invariant Register

All entries are scoped to `BASE.lock`. An unruled boundary stays `OPEN`.

| ID | Strength | Predicate / scope | Flag boundary |
| --- | --- | --- | --- |
| `H2-9D` | construction | 28 `ω` values agree after 9-decimal serialization on the declared 0001 slice. | One archived tuple differs at the stated serialization. |
| `HND-H1…H6` | construction | `check_handoff.py`, full git history, H1–H6. | A one-rule synthetic history returns `RESULT PASS`. |
| `J1-I1…I8` | construction | Base plus frozen 0003 mutants at their listed coordinates. | Base fails; target mutant passes; or target coordinate differs. |
| `J1-D1` | construction | Per-register subsequence order; cross-register interleaving presentation order. | Allowed interleaving fails or within-register inversion passes. |
| `J1-D2` | construction | `V(F)=CRLF→LF(stripOneLeadingBOM(B_F))`; raw I1/hashes, recovered I2–I7/CHAIN parse. | Reader or expected output differs in 0008 scope. |
| `J1-D3` | construction | Valid-UTF-8 I1 coordinate = earliest raw coordinate. | Reader differs from 0010 expected matrix. |
| `J1-I8-row` | construction | A implements T2, B implements T1 on 0011's 16 blocks. | Reader differs from its candidate expected matrix. |
| `QSA-S0…S2` | construction | Schema bytes, law text, declared domains. | Altered source/domain/law reaches PASS. |
| `QSA-A1…A7` | exact | `(q,s) ↦ s + 137*((q-s) mod 4)` for all 548 pairs. | One pair violates range, uniqueness, coverage, congruence, or inverse. |
| `QSA-F1` | construction | Complete canonical 14-row non-negative-residue fixture. | Altered/missing/extra/noncanonical row reaches PASS. |
| `QSA-2R` | construction | CPython and Node byte agreement on pinned fixture and variants. | Reader output differs or damaged fixture passes. |

## Open boundaries

- H² tie bounds, signed zero, other transcendental functions, third engine.
- `U+03C0 → (q,s,a)`, the three `λ` adapters, dome bytes, additional platform coverage.
- J1 invalid UTF-8 ordering, CHAIN NFC/UTF-8 I1 coverage, zero-padded I8 `len`, D4 layout coordinates, and final-row T1/T2 selection.
- Pre-ruling A/B differences in 0007 and 0009 remain historical evidence, not flags.
