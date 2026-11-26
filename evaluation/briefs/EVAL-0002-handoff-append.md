# EVAL-0002 — Handoff Append Carrier

- **Source** — `tools/check_handoff.py` at the base; handoff records 0001–0011.
- **Reader** — Generator, independent Python reimplementation, replay auditor.
- **Claim** — `construction`; target is the executable H1–H6 carrier.
- **Check** — Generate grammar-preserving and grammar-breaking handoff trees under one seed. Run both readers twice. Retain only fixtures whose tree and history model are declared.
- **Receipt** — Generator hash, seed, manifest, checker outputs, independent output, and reduced witness.
- **Delta** — INITIAL — first append-carrier adversarial brief.
- **Open** — H3 needs a declared full history; a shallow clone is a receipt gap, never a substitute.

## Domain

At most 64 records, ASCII filenames, UTF-8 contents, and a synthetic full git
history in which every commit is explicit. Every result gate parses H1–H5;
process exit alone is insufficient because `H3 UNVERIFIED` exits zero.
