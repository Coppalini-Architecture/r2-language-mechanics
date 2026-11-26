# EVAL-0004 — Receipt-Gate Audit

- **Source** — Base `4f7288269e75dcb1e8bd67ae82ddeb754eac7548`; `tools/check_handoff.py` blob `7bd573cc9e4c7ba9cfabbb081138253bdd992bd8`.
- **Reader** — Exact checker in fresh full-history temporary repositories.
- **Claim** — `construction`: H1–H6 bind the handoff directory/history and first matching protocol fields.
- **Check** — Commit a changed receipt artifact named by a handoff SHA; add duplicate `Claim`/`Delta`; use trailing-text `Corrects:`; dirty a handoff receipt; commit an historic handoff modification.
- **Receipt** — Changed artifact, duplicate fields, trailing-text `Corrects:`, and dirty receipt all return RESULT PASS. A committed historic handoff modification returns H3 FAIL.
- **Delta** — Artifact binding, field cardinality, and worktree-binding requirements are independently exposed as residuals.
- **Open** — A future desk gate may require a clean HEAD, exactly-once protocol fields, and bytewise verification of every named artifact path. H1–H6 do not presently state those predicates.
