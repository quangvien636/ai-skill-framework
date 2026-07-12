# Session Bootstrap Protocol

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the exact, ordered sequence a session (human or AI) runs before making
any change in this repository, and the minimum state that must be known
before implementation starts. This replaces ad hoc "read some files and
guess" onboarding with a deterministic procedure, per
[MASTER_OPERATOR.md](../../MASTER_OPERATOR.md)'s Mission.

## Scope

Covers the Repository Boot Sequence (18 ordered steps) and the Session
Initialization Contract (the minimum state a session must hold before it is
safe to implement). It does not cover what to do *after* boot — see
[Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md) for
the state machine boot feeds into, and
[Context Restoration](CONTEXT_RESTORATION.md) for how disagreements between
sources encountered during boot are resolved.

## Definitions

- **Boot sequence:** the fixed 18-step procedure below, run once per session
  before the first repository-modifying action.
- **Marker files:** `PROJECT_CONTEXT.md` and `PROJECT_TRACKER.md`, the two
  files ADR-0007 requires together to identify the repository root.
- **Concurrent-work risk:** evidence that another session, human or AI, may
  be mid-change in this working tree or on the remote branch right now.

## Design

### The Repository Boot Sequence

Run in order. Do not skip a step because an earlier one "looked fine" — each
step's output is an input to a later one. Commands are the verified,
currently-working commands for this repository (Python 3.14, Git, no other
toolchain required); if a future environment lacks one, the "Failure
condition" column tells you what to do instead of guessing.

| # | Step | Purpose | Method | Expected output | Failure condition | Recovery / escalation |
| - | --- | --- | --- | --- | --- | --- |
| 1 | Confirm repository identity | Avoid operating on the wrong checkout | Walk upward from the working directory for the nearest ancestor containing **both** `PROJECT_CONTEXT.md` and `PROJECT_TRACKER.md` (ADR-0007's Workspace Discovery rule — not `.git`) | A directory containing both marker files | Neither file found within a bounded number of parent directories | Hard stop: report the search start directory; do not fall back to the current directory as a pseudo-root (ADR-0007) |
| 2 | Confirm branch | Know what you are about to change | `git branch --show-current` | A branch name (this repository's convention so far: `main`) | Detached HEAD (empty output) | See the "Detached HEAD" row of [Recovery Procedures](RECOVERY_PROCEDURES.md) |
| 3 | Fetch remote state | Learn what the remote has that local doesn't, without merging it | `git fetch origin` | Exit 0; updated remote-tracking refs | Network unavailable, no `origin` configured | Continue in offline mode; record "remote state unknown" in the session's initialization record; do not treat this as a hard stop unless the task requires pushing |
| 4 | Inspect working tree | Detect uncommitted changes before touching anything | `git status --porcelain` | Empty (clean) or a list of paths | Non-empty output | See step 5 |
| 5 | Inspect uncommitted changes | Distinguish your own prior in-progress work from another party's | `git diff HEAD --stat` and read the changed paths | A stat summary you can attribute to a known task, or nothing | Changes you cannot attribute to any known task or session | Do not overwrite or discard them. Treat as possible concurrent work — see the "Worktree containing unrelated changes" row of [Recovery Procedures](RECOVERY_PROCEDURES.md) |
| 6 | Inspect latest commits | Learn what the last session actually did (not what it claimed) | `git log -5 --oneline` | Commit subjects matching `PROJECT_TRACKER.md`'s Sprint History | A commit with no matching tracker entry | Treat `PROJECT_TRACKER.md` as stale; update it as part of this session's work per [Context, Tracker, Roadmap & Naming Standards](CONTEXT_TRACKER_ROADMAP_AND_NAMING_STANDARDS.md) |
| 7 | Determine remote divergence | Know whether local and remote have diverged | `git rev-list --left-right --count origin/<branch>...HEAD` | `<n_behind>\t<n_ahead>` | Both counts nonzero (true divergence, not just unpushed local commits) | Escalate before pushing — see the "Remote branch movement" row of [Recovery Procedures](RECOVERY_PROCEDURES.md) |
| 8 | Identify concurrent-work risk | Avoid colliding with another live session | Cross-reference steps 4-7: uncommitted changes you did not make, or remote commits not reflected in `PROJECT_TRACKER.md` | No unexplained signal | Any unexplained signal | Do not proceed with writes; isolate your own work (a new branch or a clearly-scoped subset) until the ambiguity is resolved or explicitly accepted as out of scope |
| 9 | Load authoritative documentation | Orient before acting | Read `MASTER_OPERATOR.md` in full | You can state the Repository Truth Hierarchy and current Autonomous Development Rules from memory | Document missing or unreadable | Hard stop — this file is the entry point; its absence means the repository is in an unexpected state |
| 10 | Load project context | Learn current architecture and focus | Read `PROJECT_CONTEXT.md`, especially Current Focus | Current Focus names a specific, recent sprint | Current Focus references something that no longer matches `git log` | Treat as stale documentation — see [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md) |
| 11 | Load tracker and roadmap | Learn current actionable state | Read `PROJECT_TRACKER.md`'s Current Sprint and Next Actions, `docs/roadmaps/ROADMAP.md`, and `docs/roadmaps/VALIDATOR_ROADMAP.md` | A Current Sprint with a Status and, if `Completed`, a set of Next Actions | Current Sprint has no Status, or Next Actions is empty with open roadmap work remaining | Note the gap; do not invent a Current Sprint without following `.ai/playbooks/SPRINT_WORKFLOW.md`'s ownership rule |
| 12 | Inspect current blockers | Avoid repeating blocked work | Read `PROJECT_TRACKER.md`'s Next Actions and Risks and Guardrails sections for trigger-gated items | A clear list of what is gated and on what trigger | A trigger's fire condition is undocumented | Treat the item as blocked pending clarification, not as cleared |
| 13 | Inspect recent validation state | Know whether the repository was green when the last session ended | Run `python scripts/validate_repository.py` | `0 errors, 0 warnings` (or a known, already-documented exception) | Nonzero errors | Do not attribute pre-existing errors to your own upcoming change; record them before touching anything — see [Validation & Repair Loop](VALIDATION_AND_REPAIR_LOOP.md) |
| 14 | Inspect relevant ADRs | Avoid contradicting an accepted decision | Skim `docs/adr/` filenames for topics your task touches; read any whose title matches | You can name which ADRs constrain your task, if any | An ADR appears relevant but its Status is `Proposed` | A Proposed ADR describes an *intended* decision, not yet binding — see [ADR Governance & Decision Rules](ADR_GOVERNANCE.md) |
| 15 | Identify the latest completed milestone | Anchor "what's done" | `PROJECT_TRACKER.md`'s Sprint History, most recent row | A sprint number and one-line output | None (empty tracker) | Escalate: a repository this mature should not have an empty tracker; treat as a data-integrity concern |
| 16 | Determine the next eligible task | Know what to work on if none was assigned | Apply the [Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md) to `PROJECT_TRACKER.md`'s Next Actions and the roadmap | One selected task with a stated reason | No eligible task (everything blocked or out of scope) | This is a legitimate Clean Stop — see [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md) |
| 17 | Classify task authority and risk | Know what you may decide alone | Apply [Authority Levels](AUTHORITY_LEVELS.md) and [Change & Risk Classification](RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md) | A Level (0-5) and a risk tier | Ambiguous classification | Treat as the higher (more restrictive) of the plausible classifications |
| 18 | Begin work or stop with an evidence-based blocker report | Convert boot into action | Enter [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md) at `planning`, or produce a blocker report per [Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md) | Either a plan or a report — never silence | N/A | N/A |

### Session Initialization Contract

A session is not safe to start implementing until it can state all of the
following, gathered during the boot sequence above:

| Field | Source (boot step) | Required before implementation? |
| --- | --- | --- |
| Repository identity (absolute path) | Step 1 | Yes |
| Branch | Step 2 | Yes |
| HEAD commit | Step 6 | Yes |
| Remote relationship (ahead/behind/diverged/unknown) | Steps 3, 7 | Yes |
| Worktree state (clean / attributable changes / unexplained changes) | Steps 4, 5, 8 | Yes |
| Current project phase (from `PROJECT_CONTEXT.md` Current Focus) | Step 10 | Yes |
| Current milestone (latest completed sprint) | Step 15 | Yes |
| Active task (assigned, or selected via step 16) | Step 16 | Yes |
| Task source (explicit instruction, Next Action, roadmap item, defect) | Step 16 | Yes |
| Authority classification (Level 0-5) | Step 17 | Yes |
| Risk classification | Step 17 | Yes |
| Expected deliverables | Derived from task | Yes, before the first write |
| Required validation | Derived from task's Change Classification | Yes, before the first write |
| Files likely to change | Derived from task | Should be stated; may be refined during planning |
| Explicit out-of-scope areas | Derived from task and step 5/8 findings | Yes if step 5 or 8 found anything unexplained |
| Known blockers | Step 12 | Yes |

#### Initialization states

- **Complete:** every "Yes" field above is known and consistent. Proceed to
  planning.
- **Incomplete but recoverable:** a "Yes" field is missing only because a
  tool was unavailable (e.g., no network for step 3). Record the gap
  explicitly in the session's working notes and proceed if the missing field
  does not block the specific task (e.g., a documentation-only task does not
  need remote divergence resolved before drafting begins, but does need it
  resolved before push).
- **Unsafe to continue:** step 8 found unexplained concurrent-work risk, step
  1 could not identify the repository, or a "Yes" field is missing for a
  reason that is itself unexplained. Stop; produce a blocker report per
  [Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md) instead
  of guessing.

## Examples

**Complete initialization:** `git status --porcelain` is empty, `git log -1`
matches the latest `PROJECT_TRACKER.md` Sprint History row,
`origin/main...HEAD` shows the local branch ahead by a small number of
unpushed commits from the immediately preceding session, and
`validate_repository.py` reports 0/0. The session proceeds directly to
planning.

**Unsafe to continue, correctly stopped:** `git status --porcelain` lists a
modified file in `skills/content-creation/` that matches no open task in
`PROJECT_TRACKER.md`'s Next Actions and no recent commit. The session does
not touch that file, does not run a workflow that would write output near
it, and reports the finding instead of guessing whether it is abandoned work
or another session's in-progress change.

## References

- [MASTER_OPERATOR.md](../../MASTER_OPERATOR.md) — Repository Truth
  Hierarchy, Operating Principles
- ADR-0007 — Workspace Discovery marker-file rule
- `.ai/playbooks/SPRINT_WORKFLOW.md` — the Understand step this protocol
  makes precise
- `.ai/playbooks/HANDOVER.md` — what the *previous* session should have left
  for this boot sequence to find
- [Context Restoration](CONTEXT_RESTORATION.md)
- [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 1) |
