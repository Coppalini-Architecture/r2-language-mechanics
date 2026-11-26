# EVAL-0001 — J1 Ruled Surfaces

- **Source** — Base `4f7288269e75dcb1e8bd67ae82ddeb754eac7548`; reader A `e2522efd…d8da5eb`; reader B `fd72f9b2…8872a7`; `j1_i8_rows.py` `3b3d4cf…e67231`.
- **Reader** — A, B, and `j1_i8_rows.py` in a fresh temporary workspace.
- **Claim** — `construction`: ruled D1–D3 and 0011 candidate classification.
- **Check** — Rebuilt D3 corpus, replayed the D3 matrix, emitted both 0011 expected readings, and tested D1/D2 controls plus two open-boundary probes.
- **Receipt** — D3 matrix SHA-256 `39ad87e7…3d44083`; T1 `18c3099e…1e11b6`; T2 `6f784f3c…f50ce46`; all exact. Cross-register D1 swap passes in A/B; within-register swap fails I8 in A/B. Re-chained leading BOM yields I1-only in A/B. CHAIN CRLF at line 7 yields I1-only at line 7 in A/B.
- **Delta** — No contradiction against a ruled target. Two typed residuals reproduce: zero-padded `len` gives A PASS/B I8 FAIL, and invalid UTF-8 at line 23 plus CR at line 40 yields distinct I1 coordinates.
- **Open** — Canonical decimal grammar for I8; invalid-UTF-8/CR coordinate order. Both remain outside contradiction scoring.
