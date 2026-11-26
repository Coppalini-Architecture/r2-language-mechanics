# OPEN-0002 — J1 Grammar and Coordinate Seams

- **Source** — EVAL-0001 and handoff 0011.
- **Reader** — J1 A/B readers at `BASE.lock`.
- **Claim** — `open`.
- **Check** — Zero-padded `len`; invalid UTF-8 at line 23 with CR at line 40.
- **Receipt** — A/B differ on both probes.
- **Delta** — The probes are minimized rule-choice seams rather than failures of ruled D1–D3.
- **Open** — Canonical decimal grammar; invalid-UTF-8/CR ordering; D4 after the T1/T2 row-boundary ruling.
