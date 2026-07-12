# Multi-Session Continuity and Handover

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define how work survives across sessions and across different agent tools
(Claude Code, Codex, Gemini, or any future engineering agent), and the
mandatory checklist a session runs before ending. This expands
`.ai/playbooks/HANDOVER.md` into a full protocol and closes the "how does
the *next* agent, possibly a different product, pick this up" gap that a
single-tool assumption would leave.

## Scope

Covers the minimum handoff record, what must persist in the repository
(never in a conversation transcript), and the Session Completion Checklist.
Does not cover recovery mechanics for an interrupted session — see
[Recovery Procedures](RECOVERY_PROCEDURES.md).

## Design

### What must persist, and where

Per ADR-0001, nothing about session continuity may depend on a conversation
transcript. Everything below must exist in the repository itself:

| Element | Location | Format |
| --- | --- | --- |
| Last completed task | `PROJECT_TRACKER.md` Sprint History (most recent row) | One-line title + key output |
| Active task (if any left incomplete) | `PROJECT_TRACKER.md` Current Sprint, Status not `Completed` | Backlog table with per-item Status |
| Current milestone | `PROJECT_TRACKER.md` Current Sprint header | Sprint number + title |
| Validation state | `PROJECT_TRACKER.md` Sprint exit criteria / this session's own report | Command + result, not a bare claim |
| Blockers | `PROJECT_TRACKER.md` Next Actions, each with its trigger | Numbered list |
| Decisions | ADRs (`Status: Accepted` or `Proposed`) | One file per decision |
| Known risks | `PROJECT_TRACKER.md` Risks and Guardrails, or a chapter's own risk register (see [Rollback Planning & Risk Register](ROLLBACK_PLANNING_AND_RISK_REGISTER.md)) | Table |
| Next eligible task | `PROJECT_TRACKER.md` Next Actions, ranked | Numbered list, most eligible first |
| Files intentionally left changed | `git status` should be clean at handoff; if not, the reason must be in session notes committed to the tracker, not left implicit | Prose note in Current Sprint |
| External conditions required to resume | Trigger definitions (e.g., `WEEKLY_OPERATOR_PLAN.md`'s trigger pattern) | Named trigger + check command/method |

### Tool-agnostic resumption guarantee

A different agent tool resuming this repository must be able to reach a
correct `ready` state using only: `CLAUDE.md` or `AGENTS.md` (whichever its
own convention loads) -> `MASTER_OPERATOR.md` ->
[Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md) ->
[Context Restoration](CONTEXT_RESTORATION.md). None of these name a
specific tool or assume a specific chat product's memory. If a future
chapter or template ever assumes a specific tool's behavior, that is a
defect against this guarantee and must be corrected on discovery (see
[Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)).

### Session Completion Checklist

Run before ending any session that made repository changes — whether
ending because the work is done, quota is low, or a stop condition was hit:

1. Requested scope is completed, or correctly and explicitly blocked (per
   [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md)).
2. `git status --porcelain` shows no unexpected file changes — everything
   present is either committed or a deliberately-flagged in-progress state
   recorded in the tracker.
3. Relevant tests passed (the subset the Change Classification requires —
   see [Change & Risk Classification](RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md)).
4. Broader regression validation passed when the change's Risk
   Classification required it.
5. Documentation updated for every affected document (see
   [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)).
6. `PROJECT_TRACKER.md` updated: Current Sprint status accurate, Sprint
   History row added if a sprint closed, Next Actions current.
7. `PROJECT_CONTEXT.md` updated: Current Focus accurate, revision history
   row added if the version changed.
8. ADR status accurate — no ADR left implicitly accepted/rejected without
   its `Status:` field reflecting that explicitly.
9. Known limitations recorded (in the tracker or the relevant chapter),
   not only mentioned in the session's own final message.
10. One or more logical commits created, each covering one coherent
    concern (see [ADR Governance & Decision Rules](ADR_GOVERNANCE.md) and
    the general commit discipline in
    [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)).
11. Commit messages accurately describe what changed and why, including
    validation evidence.
12. Push completed if permitted (see
    [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)
    for push authorization rules) and confirmed against the remote.
13. Remote state verified after push (`git log origin/<branch> -1` matches
    local `HEAD`), or, if push was not permitted/possible, that fact is
    explicit in the final report.
14. Next task recorded in `PROJECT_TRACKER.md` Next Actions, ranked per
    [Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md).
15. Stop reason classified per
    [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md).
16. Final report grounded in actual command output, not summarized from
    memory — every claim traceable to a command this session actually ran.

### Handover Report shape

Mirrors `.ai/playbooks/HANDOVER.md`'s existing structure, made concrete:

- Completed sprints/milestones this session, with commit hashes.
- Files created and modified, one line each stating its role.
- New ADRs, and what each decided (or proposed).
- Remaining backlog and technical debt, each classified per
  [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md).
- Any hard-stop or governance-stop condition hit, and why.
- A recommended next task or sprint, with its Authority Level pre-classified
  if determinable.

## Examples

A session completes three chapters of documentation, runs
`validate_repository.py` (0 errors/0 warnings), commits with an accurate
message, but cannot push because the environment has no network access.
The Session Completion Checklist item 12 is marked not-applicable-this-
session with the reason stated; item 13 is explicitly "not verified, no
push attempted"; the final report states the exact HEAD commit hash so the
next session (or a human) can push it once connectivity is available,
rather than silently claiming the work reached the remote.

## References

- ADR-0001
- `.ai/playbooks/HANDOVER.md`
- [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md)
- [Recovery Procedures](RECOVERY_PROCEDURES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 1) |
