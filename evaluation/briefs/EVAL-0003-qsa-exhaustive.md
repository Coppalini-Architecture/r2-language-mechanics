# EVAL-0003 — Finite q,s,a Address Map

- **Source** — Handoffs 0005–0006; `qsa_check.py`; `qsa_check.js`; schema pin and frozen fixture.
- **Reader** — Independent third runtime plus declared CPython and Node readers.
- **Claim** — `exact` for the finite map `(q,s) ↦ a` on `q ∈ 0..3`, `s ∈ 0..136`; cross-runtime parity is construction evidence.
- **Check** — Exhaust all 548 pairs; verify range, uniqueness, coverage, congruences, inverses, and bound `s_input` rows.
- **Receipt** — Schema, implementation, and output hashes; runtime versions; two fresh replays; independent comparison.
- **Delta** — INITIAL — finite exact target.
- **Open** — U+03C0 adapter, λ adapters, iris-dome bytes, platform diversity.

## Flag boundary

`HALT` requires an admitted pair in the stated 548-pair domain that violates
the law and an independent certificate reproducing it. A format difference
stays `OPEN` until a serialization rule exists.
