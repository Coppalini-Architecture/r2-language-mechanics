# EVAL-0001 — J1 Reader Agreement

- **Source** — `BASE.lock`; handoffs 0003–0011; `tools/j1_check.py`, `tools/j1_check2.py`, their fixtures and expected matrices.
- **Reader** — Extension constructor, differential reader, independent replay auditor. Resolution: declared J1 inputs and each reader's complete deterministic output.
- **Claim** — `construction`. This brief tests agreement after a rule is frozen. 0011 T1/T2 remains OPEN.
- **Check** — Construct finite mutations from a declared base fixture. Rebuild linked chain bytes only when the mutation specifies it. Run both readers twice in fresh worktrees. Compare complete outputs after selecting the frozen matrix for each ruled surface.
- **Receipt** — Source/mutation hashes, seed, complete outputs, replay outputs, and minimization trace.
- **Delta** — INITIAL — first J1 adversarial brief at this base.
- **Open** — T1/T2; CHAIN I1 NFC/UTF-8; UTF-8/CR ordering; D4; canonical decimal grammar.

## Target

Every admitted fixture whose semantics are fully ruled at this base gives the
same complete output in both readers.

## Domain

One declared seed; at most 256 fixtures; at most two byte-level mutations per
fixture; fixture size at most 8 KiB; mutation leaves the selected target ruled.

## Flag boundary

An unruled condition yields `OPEN-SEAM`. `DIFFERENTIAL` requires the same ruled
predicate and distinct complete outputs after two fresh replays. This brief
supplies no `exact` target, so it has no `HALT` path.
