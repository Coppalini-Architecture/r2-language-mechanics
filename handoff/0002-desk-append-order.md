# 0002 — Desk append order

From: Claude (carried by AVC). Date: 2026-11-26. Status of address: new rule set; no OPEN.md row closed.

- **Source** — `PROTOCOL.md@44f499efe61b87885c445f0890a335d23044e678` (defines Delta as the "witnessed change from the preceding record" and defines no numbering); `handoff/0001-h2-numeric-serializer.md`; the five rules below as supplied by AVC on 2026-11-26.

- **Reader** — `tools/check_handoff.py` (Python 3, standard library), reading the `handoff/` directory and its git history. Resolution: filename, field presence and order, Delta token, add-only history.

- **Claim** — `construction`. The rules are declared and the checker was run on two records. Immutability (H3) is unverified on a shallow clone. Rules:
  1. Filenames are `NNNN-slug.md`: four digits from `0001`, contiguous, never reused; slug is lowercase `a-z0-9` joined by `-`. (H1, H2)
  2. Records are immutable: a record is added once and never modified, renamed or deleted. (H3)
  3. A correction is a later numbered record carrying a header line `Corrects: NNNN` that names an earlier record. (H6)
  4. Delta names the immediately preceding numbered record, written as its four digits, then ` — `, then the change. Numbering is by file number, so a correction's Delta names the previous number, not the record it corrects. (H5)
  5. `0001` carries `Delta: INITIAL — no predecessor`. (H5)
  Every record keeps the seven PROTOCOL.md fields in order, with Claim one of `exact`, `construction`, `open`. (H4)

- **Check** — `python3 -I tools/check_handoff.py .` from the repository root. Run it on a full-history clone to settle H3.

- **Receipt** — Run on the working tree holding 0001 and 0002, shallow clone, 2026-11-26:
  ```
  HANDOFF CHECK
  H1 PASS
  H2 PASS
  H3 UNVERIFIED (shallow clone; run on a full clone)
  H4 PASS
  H5 PASS
  H6 N/A
  RESULT PASS
  ```

- **Delta** — 0001 — adds the numbering and immutability rules that PROTOCOL.md's "preceding record" assumed. It also gives 0001 the Delta `INITIAL`. That field was edited once, before 0001 was committed, so 0001 was not yet immutable under these rules.

- **Open** — (1) Amend `PROTOCOL.md` to carry rules 1 to 5 and the `Corrects:` line; PROTOCOL.md is not a numbered record, so its history is git only. (2) Run H3 on a full clone. (3) Numbers are issued by the carrier at commit time, so two drafts written in parallel cannot both take the same number; the carrier renumbers the later one before commit. (4) `receipts/` and `tools/` files have no ordering rule yet.
