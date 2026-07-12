# Autonomous Continuation Rules and Stop Conditions

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define exactly when a session must keep working automatically, when it must
stop, and the five stop-condition classes, so a session never has to ask
"should I continue?" — the answer is always derivable from this document
plus current repository state, per
[MASTER_OPERATOR.md](../../MASTER_OPERATOR.md)'s Autonomous Development
Rules.

## Scope

Covers continuation rules and the taxonomy of stop conditions with, for
each, required evidence, repository state before stopping, required
documentation, final report contents, and resume instructions. It does not
cover *how* to recover from a stop — see
[Recovery Procedures](RECOVERY_PROCEDURES.md) for that.

## Design

### Continuation rules

A session **must continue** (select and begin the next eligible unit of
work without asking) when any of the following hold:

1. The current task is incomplete but safe and within the session's
   Authority Level.
2. Validation revealed a defect caused by the session's own current change
   (repair it; this is not new scope, it is finishing the current one).
3. A completed change's own required documentation is not yet updated
   (finish it; per the Autonomous Development Lifecycle, `documentation` is
   part of the same unit of work as `implementation`).
4. `PROJECT_TRACKER.md` or `PROJECT_CONTEXT.md` is stale relative to what
   the session just did (update it; this is Definition-of-Done, not
   optional follow-up).
5. Another eligible task exists within the currently approved scope (the
   task the operator assigned, or — for an explicitly multi-phase mandate
   like this one — the next phase/chapter named in that mandate).
6. A task can be safely decomposed to route around a non-critical blocked
   subtask (see [Work Decomposition, Dependency & Impact Analysis](WORK_DECOMPOSITION_AND_IMPACT_ANALYSIS.md)).
7. Evidence — not assumption — supports the next step (a passing validator,
   a matching tracker entry, a resolved dependency).

A session **must not** manufacture work to appear active: it must not
implement a speculative feature, expand scope beyond what was authorized,
or invent a task with no basis in the roadmap, tracker, an explicit
instruction, or a defect actually found during this session.

### Stop condition taxonomy

#### 15.1 Hard stop

Repository or safety risk. Examples: risk of data loss; repository
corruption; a security incident (e.g., a credential found committed);
an unexpected destructive Git operation about to occur; an unresolved
conflict with changes the session cannot attribute to a known task; a
legal/licensing concern (e.g., a dependency with an incompatible license);
a required human-only decision (ADR acceptance, lifecycle promotion);
missing credentials that must not be created by the session; a
production-impacting action requested without prior approval.

- **Required evidence:** the exact command/output/file that revealed the
  risk.
- **Repository state before stopping:** no further writes; if mid-change,
  leave the working tree exactly as found (do not attempt a "helpful"
  partial commit of a hard-stop-triggering change).
- **Required documentation:** a blocker entry in session notes; if the
  session has commit authority for unrelated safe work, that work may
  still be committed separately, never combined with the hard-stop finding.
- **Final report contents:** what was found, why it is a hard stop (which
  Section 2.7/15.1 category), exact reproduction evidence, and what a human
  needs to decide.
- **Resume instructions:** only after a human has reviewed and explicitly
  authorized a path forward.

#### 15.2 Governance stop

A decision exists that only a human, or a specific role acting with
delegated human authority, may make. Examples: ADR acceptance; architecture
authority exceeded (Level 3+ per [Authority Levels](AUTHORITY_LEVELS.md));
repository scope expansion beyond what was authorized; public release
authorization; dependency licensing approval; breaking-change approval.

- **Required evidence:** the specific decision named, and why it exceeds
  the session's Authority Level.
- **Repository state before stopping:** any proposal (e.g., a `Status:
  Proposed` ADR) may be committed; the decision itself is never marked
  accepted/final by the session.
- **Required documentation:** the proposal itself, plus a
  `PROJECT_TRACKER.md` Next Action naming exactly what a human needs to
  review.
- **Final report contents:** the proposal's location, its consequences, and
  the specific approval being requested.
- **Resume instructions:** the next session (same or different) reads the
  tracker's Next Action, checks whether the human decision has been
  recorded (e.g., ADR Status changed to `Accepted`), and proceeds only if
  so.

#### 15.3 External dependency wait

Examples: a required stable upstream release is not yet available (e.g.,
this repository's own tracked MCP Python SDK v2 wait); an external service
is unavailable; a pending third-party decision; an unavailable test
environment.

- **Required evidence:** the specific dependency and its current state
  (e.g., "MCP SDK latest is 1.28.1, target is 2.x stable").
- **Repository state before stopping:** clean; any other eligible unrelated
  work should have already been done before declaring this stop, since a
  dependency wait blocks only the specific task, not the session.
- **Required documentation:** the trigger condition and re-check cadence,
  matching the existing `WEEKLY_OPERATOR_PLAN.md` pattern.
- **Final report contents:** what is being waited on and when it will next
  be checked.
- **Resume instructions:** re-check the trigger; if fired, re-enter
  `planning` for the previously blocked task.

#### 15.4 Temporary recoverable stop

Examples: quota exhaustion; process interruption; machine restart; a local
tool failure; a merge conflict that can be safely resumed later.

- **Required evidence:** none required at stop time (this class is often
  involuntary — the *next* session supplies the evidence during recovery).
- **Repository state before stopping:** whatever it happens to be; this is
  why [Recovery Procedures](RECOVERY_PROCEDURES.md) exists — the next
  session must not assume a clean handoff.
- **Required documentation:** if the session has any warning (e.g.,
  approaching quota), it should commit whatever is safely committable and
  update `PROJECT_TRACKER.md` before the interruption; if no warning, none
  is possible.
- **Final report contents:** produced by the *next* session's recovery
  procedure, not the interrupted one.
- **Resume instructions:** [Recovery Procedures](RECOVERY_PROCEDURES.md).

#### 15.5 Clean completion stop

All actionable work in the current authorized scope is complete, validation
is green, documentation is current, and remaining tasks are explicitly
blocked, deferred, or outside current scope.

- **Required evidence:** a passing `validate_repository.py` run (and the
  relevant test suites for the scope touched), a `PROJECT_TRACKER.md` with
  no remaining eligible (unblocked, in-scope) Next Action.
- **Repository state before stopping:** clean; all commits made; pushed if
  permitted.
- **Required documentation:** `PROJECT_TRACKER.md` Next Actions lists
  exactly what remains and why each remaining item is blocked/deferred/out
  of scope.
- **Final report contents:** the full session report per
  [Multi-Session Continuity, Handover & Completion Checklist](MULTI_SESSION_CONTINUITY_AND_HANDOVER.md).
- **Resume instructions:** the next session's boot sequence will find a
  clean, fully-documented state and select from the recorded Next Actions.

### Stop-condition decision table

| Situation | Class | Continue this session? |
| --- | --- | --- |
| Current task done, another eligible task exists | Continuation rule 5 | Yes |
| Validation fails due to current change | Continuation rule 2 | Yes (repair first) |
| Validation fails, pre-existing, unrelated, low severity | Repair loop "pre-existing" path | Yes (record, continue) |
| Uncommitted changes found that match no known task | Hard stop 15.1 | No |
| A task requires promoting an artifact past `draft` | Governance stop 15.2 | No (draft the request, stop on the promotion itself) |
| A dependency this task needs (e.g., MCP v2) has not shipped | External wait 15.3 | Yes for other work; no for this specific task |
| Editor/agent process about to exceed its context/quota | Temporary stop 15.4 | Commit what's safe, then stop |
| Every Next Action is blocked/deferred, all validation green | Clean completion 15.5 | No — this is success, not failure |

## Examples

A session working through this Batch's Phase 3 (Governance & Planning)
finds that implementing "Priority Engine" would benefit from an ADR
formalizing authority levels as binding (not just descriptive). Because
accepting a new binding governance rule is a human decision
(`.ai/governance/DECISION_RIGHTS.md`), the session documents the Authority
Levels model as a *synthesis* of existing rules (no new ADR needed, since
no new rule is created — see [Authority Levels](AUTHORITY_LEVELS.md)'s own
scope note) and continues rather than triggering an unnecessary governance
stop.

## References

- `.ai/governance/DECISION_RIGHTS.md`
- [MASTER_OPERATOR.md](../../MASTER_OPERATOR.md) — Autonomous Development
  Rules
- [Recovery Procedures](RECOVERY_PROCEDURES.md)
- [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 1) |
