# Blocker Classification and Escalation

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Classify blockers, define required evidence and handling per class, and
give deterministic rules for when a session must resolve something
independently versus when it must involve a human — preventing both
over-escalation (constant unnecessary interruption) and unauthorized
autonomy (proceeding on something that needed a human).

## Scope

Feeds the `blocked` and `waiting for human` states in
[Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md).

## Design

### Blocker classes

| Class | Definition | Required evidence | Workarounds allowed? | Parallel work allowed? | Documentation location | Resume trigger | Escalation path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | A code/tooling defect prevents progress | The exact failing command/output | Only if the workaround does not weaken validation or hide the defect | Yes | `PROJECT_TRACKER.md` Next Action | Defect fixed | Framework Engineer, then Chief Architect if architectural |
| Governance | A decision only a human/specific role may make | The specific decision and why it exceeds session authority | No | Yes | `PROJECT_TRACKER.md` Next Action, proposal committed | Human decision recorded (e.g., ADR Status change) | Human maintainer |
| External release | A needed upstream release has not shipped | Current version vs. target version, checked this session | No | Yes | Trigger + re-check cadence (matching `WEEKLY_OPERATOR_PLAN.md` pattern) | Release ships | N/A — periodic re-check only |
| Missing evidence | A claim cannot be verified (e.g., "is this test still flaky") | What was checked and what remains unknown | Only well-labeled provisional work | Yes | `PROJECT_TRACKER.md` Next Action | Evidence becomes available | Whoever can generate the missing evidence |
| Environment | A tool/service is unavailable in the current session's environment | The specific unavailable tool/service | Yes, for non-critical opt-in checks only | Yes | Session notes; not necessarily tracker-worthy unless recurring | Environment changes | N/A |
| Human decision | Distinct from Governance in that it may be a product/direction choice rather than a repository-authority one (e.g., "should the roadmap prioritize X over Y") | The specific choice and its tradeoffs, stated neutrally | No | Yes | `PROJECT_TRACKER.md` Next Action | Human responds | Human maintainer |
| Licensing | A dependency's license is unresolved/unacceptable | The specific license and the concern | No | Yes | Blocker record | Human/legal review resolves it | Human maintainer |
| Security | A vulnerability or unsafe pattern is found | The specific finding | No | Only on fully unrelated work | Blocker record, escalated immediately | Verified fixed | Human maintainer immediately |
| Production access | An action would affect a production system | N/A — this repository has none in scope | No | Yes | N/A until this class becomes real | N/A | Human maintainer |
| Repository conflict | Unattributed concurrent changes found | `git status`/`git diff` output | No | Only on clearly unrelated files | Blocker record per [Recovery Procedures](RECOVERY_PROCEDURES.md) | Attribution resolved | Human, if attribution cannot be determined |

### Resolving independently vs. escalating

A session **must resolve independently** (no human interruption) when the
situation is:

- Routine naming consistent with existing repository conventions.
- Adding missing tests for an already-understood defect.
- Correcting a broken link.
- Updating the tracker after completed work.
- Choosing the next task from an already-approved backlog
  ([Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md)).
- Repairing a defect its own current change caused.
- Adding documentation a completed change clearly requires.
- Splitting a task safely (per
  [Work Decomposition, Dependency & Impact Analysis](WORK_DECOMPOSITION_AND_IMPACT_ANALYSIS.md)).
- Selecting an existing, already-appropriate validator for a check.

A session **must escalate to a human** when the situation is:

- Any Governance, Licensing, Security, Production-access, or Human-decision
  blocker class above.
- Any Level 4-5 action per [Authority Levels](AUTHORITY_LEVELS.md).
- Any unattributed concurrent-work finding that cannot be resolved by
  investigation alone.
- Any conflict between two authoritative documents that
  [Truth Hierarchy & Conflict Resolution](TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md)'s
  category table does not clearly resolve.

This split is deliberately exhaustive enough to avoid the failure modes on
both ends: a session that escalates routine naming choices wastes the
human's time and defeats this manual's Mission; a session that resolves a
licensing question on its own risks exactly the kind of unauthorized
decision ADR-0001 exists to prevent.

### Escalation procedure

1. Classify the blocker (table above).
2. Gather the required evidence for that class.
3. Record it in `PROJECT_TRACKER.md` Next Actions (or, for a Security
   class, escalate immediately without waiting to finish the current
   task).
4. If a proposal can be drafted (e.g., an ADR candidate) without crossing
   into the human-reserved decision itself, draft it.
5. Continue other unrelated eligible work per
   [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md)'s
   continuation rules — a blocker on one task is not a reason to stop the
   whole session unless it is a Hard Stop class.
6. On resume, the next session's [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md)
   step 12 (inspect current blockers) finds this record and checks whether
   its resume trigger has fired.

## Examples

This Batch's own session finds, while writing
[Repository Architecture Map](REPOSITORY_ARCHITECTURE_MAP.md), that
`changelog/` is empty with no owning process yet defined. This is not a
blocker to *this* Batch's work (documenting the manual does not require
`changelog/` to be populated) — it is recorded as a gap for a future
Release Engineering chapter (Batch 2+), per the "must resolve
independently: adding documentation a completed change clearly requires"
vs. "propose, don't implement, out-of-scope work" distinction in
[Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)'s
"newly discovered issue outside current scope" table.

## References

- [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)
- [Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md)
- [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md)
- `.ai/governance/DECISION_RIGHTS.md`

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
