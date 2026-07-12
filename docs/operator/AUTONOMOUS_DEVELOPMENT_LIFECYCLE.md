# Autonomous Development Lifecycle

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the full lifecycle a session runs after
[Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md) completes, as a
deterministic state machine, plus the Planning Contract and Implementation
Rules that govern the `planning` and `implementation` states specifically.

## Scope

Covers session-level execution flow from task selection through the next
task. It does not cover task *selection* itself (see
[Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md)) or
validation mechanics (see
[Validation & Repair Loop](VALIDATION_AND_REPAIR_LOOP.md)) in detail — both
are referenced at the states that use them.

## Design

### The lifecycle

```text
Open repository
  -> Verify repository            (Session Bootstrap Protocol steps 1-8)
  -> Restore context               (Context Restoration)
  -> Inspect state                 (Session Bootstrap Protocol steps 9-15)
  -> Select eligible task          (Priority & Autonomous Planning Engine)
  -> Classify authority and risk   (Authority Levels; Risk Classification)
  -> Plan                          (this document: Planning Contract)
  -> Implement                     (this document: Implementation Rules)
  -> Validate                      (Validation & Repair Loop)
  -> Diagnose failures             (Validation & Repair Loop)
  -> Repair                        (Validation & Repair Loop)
  -> Revalidate                    (Validation & Repair Loop)
  -> Update documentation          (Documentation Placement Rules)
  -> Update tracker/context        (Context, Tracker, Roadmap & Naming Standards)
  -> Commit                        (this document: Commit state)
  -> Push when permitted           (this document: Push state)
  -> Select next task              (loop to "Select eligible task")
  -> Repeat
```

### State machine

| State | Purpose | Required inputs | Allowed actions | Prohibited actions | Required outputs | Completion criteria | Failure transition | Recovery transition | Escalation condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ready` | Session has booted and restored context | Session Initialization Contract fully populated (or "incomplete but recoverable") | Select a task | Any repository write | An entry state, no output yet | Task selected | N/A | N/A | Initialization state is "unsafe to continue" -> go to `blocked` |
| `planning` | Produce a Planning Contract for the selected task | Selected task, its Authority Level and Risk tier | Read repository files; draft a plan; draft an ADR candidate if required | Any repository write outside session working notes | A completed Planning Contract (below) | Plan covers every required field for the task's Change Classification | Plan reveals the task needs a governance decision the session cannot make -> `waiting for human` | Plan reveals missing information recoverable by more reading -> stay in `planning` | Plan reveals the task exceeds the session's Authority Level -> `waiting for human` or `blocked` (governance stop) |
| `implementation` | Produce the durable artifact(s) the plan describes | Approved-by-self Planning Contract (Level 0-2 tasks) or human-approved plan (Level 3+) | Edit/create files within the plan's stated scope | Expand scope beyond the plan without re-planning; weaken validation to pass; hide errors | Modified/created files matching the plan | All planned changes made; no unrelated files touched | Implementation reveals the plan was wrong in a way that changes scope -> back to `planning` | Implementation blocked by a missing dependency -> `waiting for external dependency` | Implementation would require a prohibited action (Section 2.7 class) -> `blocked` (hard stop) |
| `validation` | Run applicable checks | Completed implementation | Run validators/tests named in the plan; run broader regression validation before commit | Skip validation to save time; mark validation "passed" without running it | A Validation Report (see [Documentation & Writing Standards](DOCUMENTATION_AND_WRITING_STANDARDS.md) report conventions) | All applicable validation run and recorded | Any failure -> `repair` | N/A | A failure class requires human judgment (e.g., ambiguous pre-existing failure) -> `waiting for human` |
| `repair` | Fix defects found in `validation` | Validation Report with at least one failure | Fix failures caused by the current change immediately; investigate (but do not silently fix) pre-existing failures | Modify scope unrelated to the failure; disable the failing check | A diagnosis per failure, plus a fix for in-scope failures | Every current-change-caused failure fixed | Fix itself fails -> stay in `repair`, escalate after repeated failure (see [Validation & Repair Loop](VALIDATION_AND_REPAIR_LOOP.md) for the repeat threshold) | N/A | A pre-existing failure is out of the current task's scope -> record it as a Next Action, return to `validation` to confirm no new failures, do not silently leave it undocumented |
| `documentation` | Update all documentation the change requires | Passing validation | Update affected `docs/`, `docs/operator/`, or other reference documents in the same change | Leave a stale claim in place; document a feature that does not yet exist as if it does | Updated documentation matching actual repository state | Every document the [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md) require for this change class is current | N/A | N/A | The change's documentation implications are themselves architecturally significant -> may require an ADR; escalate to `planning` |
| `commit-ready` | Update tracker/context and stage the change | Current documentation | Update `PROJECT_TRACKER.md`/`PROJECT_CONTEXT.md` per [Context, Tracker, Roadmap & Naming Standards](CONTEXT_TRACKER_ROADMAP_AND_NAMING_STANDARDS.md); review the staged diff | Stage unrelated files; use `git add -A` blindly | A reviewed `git diff --stat` matching the plan's stated file list | Staged diff contains exactly the planned files, nothing more, nothing less | Unexpected files appear staged -> unstage and investigate, stay in `commit-ready` | N/A | Staged diff reveals a file the session does not recognize touching -> `blocked`, investigate before proceeding |
| `completed` | One task's lifecycle is finished | A commit (and push, if permitted) | Select the next task (loop to `ready`) | N/A | A commit hash; updated tracker | Commit exists; working tree clean | N/A | N/A | N/A |
| `blocked` | The session cannot proceed on the current task | A specific, named blocking condition | Document the blocker (see [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md)); select a different eligible task if one exists and is unaffected | Force progress on the blocked task; silently drop it | A Blocker record | Blocker recorded in `PROJECT_TRACKER.md` Next Actions or session report | N/A | Blocker resolves (e.g., trigger fires, human responds) -> `ready` | Blocker is a hard-stop class (Section 15.1) -> also produce the hard-stop report defined in [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md) |
| `waiting for human` | A governance-level decision is required | A specific decision named (ADR acceptance, lifecycle promotion, destructive Git op, scope expansion) | Draft the proposal/candidate for the human to review; continue other unrelated eligible work | Make the decision itself | A clearly labeled proposal (e.g., a `Status: Proposed` ADR) | Proposal exists and is discoverable from `PROJECT_TRACKER.md` Next Actions | N/A | Human responds -> `ready` with the decision now resolved | N/A (this state is itself the correct response to a governance escalation) |
| `waiting for external dependency` | A prerequisite outside the session's control is missing | A specific named dependency (e.g., an upstream release, an unavailable service) | Continue other unrelated eligible work; monitor the dependency per any existing plan (e.g., `WEEKLY_OPERATOR_PLAN.md`'s trigger checks) | Force the dependency by working around its absence in an unsafe way | A recorded trigger condition and re-check cadence | Dependency becomes available -> `ready` | N/A | The dependency has no known availability date and blocks milestone-critical work -> escalate to a human for a scope decision |
| `interrupted` | The session ended before reaching `completed` (quota, crash, closed terminal) | N/A — this is detected by the *next* session, not declared by the interrupted one | N/A (this state describes what the next session finds) | N/A | N/A | N/A | N/A | Next session runs [Recovery Procedures](RECOVERY_PROCEDURES.md) -> `ready` | Recovery finds data loss risk -> hard stop |
| `recovery` | A prior interruption or failure is being resolved | Findings from [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md) steps 4-8 | Follow the specific procedure in [Recovery Procedures](RECOVERY_PROCEDURES.md) matching the detected condition | Any destructive cleanup before preservation and ownership determination | A restored, understood, and either recovered or explicitly-preserved-and-escalated state | Working tree is in a known, explainable state | Recovery procedure itself fails or is unsafe -> hard stop | Recovery succeeds -> `ready` | Recovery would require overwriting unexplained changes -> hard stop, preserve evidence |
| `abandoned because obsolete` | A previously-selected task is no longer valid (superseded, already done, roadmap changed) | Evidence the task's premise no longer holds | Record why; remove or update the corresponding `PROJECT_TRACKER.md` entry | Silently delete the historical record of why it was abandoned | An updated tracker entry with the reason | Tracker reflects reality | N/A | N/A | N/A |

### Planning Contract

Required before `implementation` for any task above the lightweight
threshold (see below). A plan is a working note, not necessarily a
committed file — it becomes a committed artifact only when the task's
Change Classification requires a design document or ADR (see
[Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md) and
[ADR Governance & Decision Rules](ADR_GOVERNANCE.md)).

| Field | Content |
| --- | --- |
| Problem statement | One or two sentences: what is wrong or missing, for whom |
| Evidence | The command output, file, or ADR that establishes the problem is real (not assumed) |
| Scope | Exactly what will change |
| Non-goals | What will explicitly not change, even if related |
| Affected contracts | Any schema, specification, or ADR the change touches |
| Affected files | Best-known list; refined as planning proceeds |
| Dependencies | What must exist or be true first (see [Work Decomposition, Dependency & Impact Analysis](WORK_DECOMPOSITION_AND_IMPACT_ANALYSIS.md)) |
| Risks | What could go wrong, and how likely/severe (see [Risk Classification & Governance Scenarios](RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md)) |
| Validation strategy | Which validators/tests will confirm correctness |
| Rollback strategy | How to undo this if it turns out wrong (see [Rollback Planning & Risk Register](ROLLBACK_PLANNING_AND_RISK_REGISTER.md)) |
| Documentation changes | Which documents this change updates |
| Commit boundary | What forms one coherent commit versus multiple |

#### When a lightweight plan is sufficient

A one-paragraph mental plan (problem, scope, validation strategy) is
sufficient, and a written Planning Contract is not required, when **all**
of the following hold: the change is Authority Level 0-1 (see
[Authority Levels](AUTHORITY_LEVELS.md)), it is reversible by a simple
`git revert`, it touches no public contract (schema, specification, ADR),
and existing validation already covers the area. Examples: fixing a broken
relative link, correcting a typo, adding a missing tracker row for
already-completed work, adding a regression test for an already-understood
defect.

#### When a design document or ADR is required

A full written Planning Contract *and* a design document is required when
the change is Authority Level 3+ (architecture change requiring human
review) per [Authority Levels](AUTHORITY_LEVELS.md). An ADR specifically is
required per [ADR Governance & Decision Rules](ADR_GOVERNANCE.md)'s
mandatory-ADR list. Do not add ceremony beyond what the task's actual
Authority Level and Change Classification require — see
[Implementation Rules](#implementation-rules) below on avoiding speculative
process.

### Implementation Rules

1. **Make the smallest sufficient safe change.** Do not restructure code or
   documentation the task did not ask you to touch.
2. **Preserve backward compatibility** unless an approved breaking change
   (an Accepted ADR authorizing it) exists.
3. **Avoid unrelated refactoring** in the same change as a functional fix or
   addition — split them into separate commits if both are genuinely needed.
4. **Avoid speculative abstractions.** Per Design Principle 8 and this
   repository's own working style, prefer duplication over a premature
   shared abstraction until a third real use case appears.
5. **Inspect neighboring behavior before editing** — read the file(s)
   around the change, not just the lines being changed, so the change fits
   existing conventions. A future planned Coding Standards chapter (Part
   VII of this manual's Table of Contents; not yet written) will formalize
   language-level conventions; until then, match the file's own existing
   style.
6. **Add regression coverage for real defects.** A bug fix without a test
   that would have caught it is incomplete, per this repository's Test
   Engineer Decision Right (`.ai/roles/TEST_ENGINEER.md`).
7. **Do not weaken validation to make tests pass.** A failing check names a
   real problem; fix the problem, not the check, unless the check itself is
   demonstrably wrong (which is itself a change requiring its own
   justification and, if it changes a rule's meaning, review).
8. **Do not hide errors.** Do not catch and silently discard an exception,
   suppress a diagnostic, or reduce a validator's severity to make output
   look clean.
9. **Do not silently change contracts.** A schema, specification, or ADR
   change is never a side effect of an unrelated task; it is its own
   planned, classified change.
10. **Preserve user changes.** Never discard uncommitted work found during
    boot without first determining its ownership (see
    [Recovery Procedures](RECOVERY_PROCEDURES.md)).
11. **Keep generated and hand-maintained files distinct.** Do not
    hand-edit a file a script generates (none currently exist in this
    repository, but the rule applies pre-emptively to `runs/` output and any
    future generator output).
12. **Document non-obvious behavior** at the point of the code or decision,
    not only in a separate narrative document.

#### Handling a newly discovered issue outside current scope

| Situation | Response |
| --- | --- |
| The issue blocks the current task from being correct | Fix it now, as part of the current change; it is in scope by necessity |
| The issue is real, unrelated, and low-risk | Record it as a new `PROJECT_TRACKER.md` Next Action; do not fix it in this commit |
| The issue is real, unrelated, and high-risk or security-relevant | Escalate immediately per [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md); do not wait for the current task to finish |
| The issue is a pre-existing validation failure unrelated to the current change | Document it in the Validation Report; add a Next Action; continue — do not let a pre-existing, unrelated failure block otherwise-safe work (but never claim the repository is fully green when it is not) |
| The issue is trivial and outside any reasonable reuse value | Note it in passing (commit message or session notes) and otherwise ignore; do not create tracker noise for it |

## Examples

**Fast path (Level 0-1, lightweight plan):** A relative link in a guide
points to a renamed file. Mental plan: fix the path, run
`validate_repository.py`, commit. No written Planning Contract, no ADR.

**Full path (Level 3, full plan + ADR):** A task requires changing how
Runtime Contracts resolve fallback chains. This touches an accepted ADR's
subject matter (ADR-0015), so it requires a written Planning Contract, a
Planning Contract sign-off against [Authority Levels](AUTHORITY_LEVELS.md),
and — because it changes an accepted architectural decision — a new ADR
proposing the change, left `Proposed` for human review rather than
implemented unilaterally.

## References

- [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md)
- [Validation & Repair Loop](VALIDATION_AND_REPAIR_LOOP.md)
- [Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md)
- [Authority Levels](AUTHORITY_LEVELS.md)
- `.ai/playbooks/SPRINT_WORKFLOW.md`
- Design Principles 2, 8, 9, 10 (`docs/principles/DESIGN_PRINCIPLES.md`)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 1) |
