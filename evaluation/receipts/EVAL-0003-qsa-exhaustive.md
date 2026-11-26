# EVAL-0003 — q,s,a Exhaustive Check

- **Source** — Base `4f7288269e75dcb1e8bd67ae82ddeb754eac7548`; 0005–0006; schema SHA-256 `c85c2f34…59675caad`; frozen fixture SHA-256 `a6afee74…62ffa9`.
- **Reader** — Independent Python 3.12.14 and Node v24.22.3 enumerators, then pinned Python and Node checkers.
- **Claim** — `exact` for `a=s+137((q-s) mod 4)` over all 548 declared pairs.
- **Check** — Exhaustive range, uniqueness, coverage, two congruences, forward inverse, reverse inverse, row-bound fixture parsing, and a negative `s_input=-1` control.
- **Receipt** — Both independent enumerators report 548 distinct values exactly `0..547`; all predicates pass. Pinned Python/Node outputs match byte-for-byte at `a7bdeb1e…efe0a0c`. The negative control fails in both readers at `s_input -1`.
- **Delta** — Additional independent exhaustive replay and current Node parity receipt; no finite-law counterexample.
- **Open** — U+03C0 adapter, λ adapters, dome bytes, and broader platform/engine diversity.
