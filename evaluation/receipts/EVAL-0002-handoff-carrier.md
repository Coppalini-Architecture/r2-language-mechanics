# EVAL-0002 — Handoff Carrier

- **Source** — Base `4f7288269e75dcb1e8bd67ae82ddeb754eac7548`; `tools/check_handoff.py` blob `7bd573cc9e4c7ba9cfabbb081138253bdd992bd8`.
- **Reader** — Exact checker in isolated Python execution over synthetic full-history Git repositories.
- **Claim** — `construction`: H1–H6 as implemented.
- **Check** — Baseline, committed historic edit, duplicate protocol fields, malformed `Corrects:`, and dirty-worktree fixtures.
- **Receipt** — Baseline H1–H5 PASS; H6 N/A; RESULT PASS. A committed historic edit causes H3 FAIL. A duplicate trailing `Claim` returns PASS; a malformed trailing-text `Corrects:` returns H6 N/A/PASS; an uncommitted historic edit returns H3 PASS. The duplicate and dirty outcomes were independently reproduced by a second receipt-gate evaluator.
- **Delta** — H3’s committed-history read holds. Protocol-field cardinality, `Corrects:` grammar coverage, and current-worktree cleanliness are three bounded seams.
- **Open** — H4 currently asserts ordered presence rather than exactly-once fields; H6 recognizes only exact `Corrects: NNNN`; H3 reads committed history rather than current worktree state. Each needs an explicit extension before it becomes a defect against this checker.
