# R² Adversarial Evaluation Charter — AEC-1

## Purpose

This laboratory tests declared finite claims at the pinned base in `BASE.lock`.
Its unit is a bounded evaluation case. Its output is a receipt.

The carrier remains fixed. Each evaluator works in an isolated worktree. A
candidate changes a target status only through an independently replayed
witness.

## Case type

\[
E=(id,B,T,D,I,W,\rho,\beta,C)
\]

| Field | Carrier |
| --- | --- |
| `id` | Unique `EVAL-NNNN` address. |
| `B` | Pinned commit, source hashes, runtime lock. |
| `T` | Named claim and invariant ID. |
| `D` | Finite domain or seed-bounded generator. |
| `I` | Executable predicate and preconditions. |
| `W` | Extension patch or fixture generator with SHA-256. |
| `ρ` | Primary reader and independent replayer. |
| `β` | CPU, memory, wall-time, output, process, and fixture bounds. |
| `C` | Exact build, run, replay, and receipt commands. |

An eligible invariant has executable form

\[
\forall x\in D,\;P(x)\Rightarrow I(x).
\]

Prose with no executable predicate remains `OPEN`.

## Admission

Every case carries:

```text
Eval-ID
Target commit and source hashes
Claim strength: exact | construction | open
Named invariant and declared scope
Domain and generator seed
Extension or fixture hash
Reader set and resolution
Resource bounds
Build, run, replay, and receipt commands
```

The preflight reader returns `REJECT` when a carrier is absent, the base is
unpinned, the domain is unbounded, the target has no executable predicate, or
the requested capability exceeds the worker contract.

## Worker boundary

Each admitted case receives a fresh checkout of `B`, a writable output
directory, and no credential, network, repository-write, or external-service
capability. It has fixed CPU, memory, wall-time, process, fixture-byte, and
output-byte bounds. The worker emits only its receipt bundle.

`HALT` ends one evaluation case and freezes its target for adjudication. It
carries no operation on the repository, host, accounts, or external services.

## Verdicts

| Verdict | Meaning | Required receipt |
| --- | --- | --- |
| `PASS` | Predicate holds over the declared domain and readers. | Base, commands, outputs, hashes. |
| `OPEN` | A reproducible difference has an unresolved predicate, scope, reader rule, or determinism condition. | Minimal fixture and named residual. |
| `HALT` | A reproducible counterexample violates a named invariant at its declared resolution. | Full flag bundle and independent replay. |
| `REJECT` | The proposed case lacks a complete admitted carrier. | Preflight report. |

`HALT(E,x)` is admitted only when `x ∈ D`, the base and extension are pinned,
two fresh primary replays agree, and either the declared predicate evaluates
false with a certificate or declared-aligned readers conflict against the same
predicate.

## Flag bundle

```text
flags/F-<eval-id>/
  FLAG.md
  base.lock
  witness/
  commands.txt
  run-primary-1.txt
  run-primary-2.txt
  run-independent.txt
  certificate/
  reduce.log
  MANIFEST.sha256
```

The flag is the witness. The score measures receipt completeness.

## Shared channels

| Channel | Carrier | Function |
| --- | --- | --- |
| `briefs/` | Bounded question and invariant | Admits one challenge surface. |
| `cases/` | Fixture or extension | Carries an adversarial construction. |
| `receipts/` | Replay outputs and hashes | Preserves observed behavior. |
| `reductions/` | Minimized witness and trace | Isolates the least carrier. |
| `flags/` | Adjudicated flag bundle | Holds verified `HALT` evidence. |
| `open/` | Typed residual | Preserves ambiguity without strength inflation. |
| `scoreboard/` | Derived readout | Counts adjudicated receipts only. |

Improvisation belongs in `briefs/` and `cases/`. A record advances only when
it carries `Source · Reader · Claim · Check · Receipt · Delta · Open`.

## Score

| Result | Points | Requirement |
| --- | ---: | --- |
| Bounded `PASS` coverage | 1 | Replayable coverage receipt. |
| `OPEN-SEAM` | 10 | Minimal reproducible ambiguity. |
| `DIFFERENTIAL` | 30 | Aligned readers diverge on one admitted fixture. |
| `CONSTRUCTION` | 60 | Frozen construction receipt fails on a replayable witness. |
| `EXACT` / `HALT` | 100 | Independent minimized breach of an `exact` invariant. |
| `REJECT` or duplicate | 0 | No new admitted evidence. |

Scores release after two fresh reproductions and independent adjudication. A
clean run appends coverage at its tested resolution and preserves the target
claim's established strength.
