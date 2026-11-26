# 0003 — R² J1 fixture matrix

From: Claude (carried by AVC). Date: 2026-11-26. Status of address: OPEN.md row "R² J1 cycle" remains OPEN; this record supplies its test matrix.

- **Source** — "R² Journal — Architecture Specification v0.1", sections J-02 to J-05, as of document revision 19 (a living document; those sections were last changed at revisions 4 to 15). `handoff/0002-desk-append-order.md`. The fixture is synthetic and contains none of the supplied R² journal, which stays outside this repository.

- **Reader** — `tools/j1_check.py` (Python 3, standard library): runs I1 to I8 over a directory holding `lab.txt`, `self.txt`, `CHAIN.txt`. `tools/j1_fixture.py` writes the fixture. Resolution: bytes; for each failing check, the first offending line as `file:line`.

- **Claim** — `construction`. One implementation, one fixture. Readings adopted where J-04 is silent:
  1. All eight checks always run; each failing check reports its own first offending line, files in the order `lab.txt`, `self.txt`, `CHAIN.txt`. Output format is fixed (see Receipt).
  2. Layout: entries are separated by exactly one blank line; a line beginning with `#` that is not a valid header fails I2.
  3. I1 also applies to `CHAIN.txt` (no BOM, no CR, one trailing newline).
  4. I5 "earlier": within a register, earlier in file order; across registers, an earlier-or-equal UTC instant.
  5. I7: a `closes` target must be in the same register, be a loop-opening kind (`NOTICE`, `TODO`, `WIP`, or `GOAL` in R²_S), and not already closed.
  6. I8: each row's `len` is at most the file size and not less than the previous `len` of that register; dates do not decrease; `h` and `link` recompute exactly.

- **Check** — Frozen copy: `cd receipts/0003-j1-fixture && sha256sum -c MANIFEST.sha256`. Regenerate: `python3 -I tools/j1_fixture.py OUT`, then `python3 -I tools/j1_check.py OUT/base` and `OUT/mut_I1` to `OUT/mut_I8`. Agreement criterion for a second implementation: byte-identical output on all nine directories.

- **Receipt** — Fixture: 24 lab entries, 8 self entries, 10 daily closes per register (days with no entries included), offsets `+00:00`, `-05:00` and `+09:00`, one entry whose local date is later than its close day, non-ASCII in bodies. `base/` sizes: `lab.txt` 2,640 bytes, `self.txt` 803, `CHAIN.txt` 2,947. `MANIFEST.sha256` SHA-256 `92d42156b945a592c845d8ac999edc819fd4b8d4c764b123bc42fcc9c1c8d0cd`; `RESULTS.txt` `2e735845fef507654a7252a78adac05cab8ce1564a93568bae04ec07b87f9b70`; `tools/j1_check.py` `9a797b6289618321bf45955a30aa9f5634dfc24aea6de8b4e8178091cff18a4b`; `tools/j1_fixture.py` `cce6b4b53338c6c5381a116f1cf7c9bd83dc20591937a05637cf5fbda9beb3b9`.

  | Directory | Mutation | Result |
  | --- | --- | --- |
  | `base` | none | `RESULT PASS` |
  | `mut_I1` | one body character written decomposed (not NFC) | `FAIL I1`, `self.txt:23` |
  | `mut_I2` | `subject` written before `kind` | `FAIL I2`, `lab.txt:31` |
  | `mut_I3` | last lab ID skips from 23 to 25 | `FAIL I3`, `lab.txt:166` |
  | `mut_I4` | one entry's instant earlier than its predecessor's | `FAIL I4`, `lab.txt:109` |
  | `mut_I5` | `corrects` names a nonexistent ID | `FAIL I5`, `lab.txt:82` |
  | `mut_I6` | a lab entry cites an S-ID | `FAIL I6`, `lab.txt:148` |
  | `mut_I7` | a second entry closes an already-closed loop | `FAIL I7`, `lab.txt:134` |
  | `mut_I8` | one body byte changed after the chain was written | `FAIL I8`, `CHAIN.txt:1` |

  Each mutant fails exactly the targeted check. Mutants I1 to I7 are written by a defective writer before the chain is built; any edit to bytes already covered by a chain row trips I8, which is what `mut_I8` shows.

- **Delta** — 0002 — first record numbered under the append rule. Adds the test matrix; there was no fixture before.

- **Open** — (1) A second, independent implementation, run on the nine directories. (2) Expected outputs for metrics M1 to M15 on the fixture are not yet specified. (3) Spec gaps this build exposed, for a v0.1.1 of the spec: `promoted:` can only appear on an R²_S entry written after the lab entry it names, because entries cannot be edited, so J-01 rule 4 needs the order stated (the fixture uses a new entry, `S-000006`, citing `S-000005` and `L-000017`); J-03 does not say which register a `closes` target may be in; J-04 does not define layout failures or what "first offending line" means when several checks fail. (4) The three policy choices in J-09 (time zone, `add` input, daily readout) are still the operator's. (5) `receipts/` has no ordering rule yet (see 0002 Open 4).
