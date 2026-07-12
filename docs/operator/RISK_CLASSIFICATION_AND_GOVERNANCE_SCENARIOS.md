# Risk Classification and Governance Scenarios

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define a risk matrix for classifying a change's blast radius and required
controls, and provide worked governance scenario tables covering realistic
situations this repository's own work has already encountered or is likely
to encounter.

## Scope

Complements [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)'s
Change Classification (which asks "what kind of change is this") with Risk
Classification (which asks "how dangerous is it").

## Design

### Risk matrix

| Factor | Low | Medium | High |
| --- | --- | --- | --- |
| Blast radius | One file, no downstream consumer | Several related files, one Skill/Workflow | Cross-cutting: a shared schema, IR, or core validator |
| Reversibility | `git revert`, no side effects | `git revert` plus a manual step (e.g., re-running a generator) | Not cleanly revertible (e.g., a live external call already made, a promoted lifecycle) |
| Data loss potential | None | Regeneratable artifact only | Any hand-authored content |
| Security impact | None | Internal-only exposure | Credential, secret, or external-network surface |
| Compatibility impact | None | Internal detail only | Public contract (schema/specification) |
| Dependency uncertainty | Pinned, already-vetted | New pinned-range dependency | New major dependency or license |
| Operator impact | None | Requires updating a runbook | Requires updating the Autonomous Development Rules themselves |
| Production impact | N/A (no production environment in scope) | N/A | N/A (would always be High if one existed) |
| Validation coverage | Full existing coverage | Partial coverage, gap noted | No existing coverage |

### Risk levels and required controls

| Risk level | Definition (how many factors above land High) | Required controls |
| --- | --- | --- |
| Low | 0 High factors, mostly Low | Level 1-2 authority sufficient; standard validation; no design document required |
| Medium | 1-2 High factors, or several Medium | Level 2-3 authority; full applicable validation; a written Planning Contract required |
| High | 3+ High factors, or any single Security/Data-loss/Production High | Level 3-4 authority; ADR required; human approval required before implementation proceeds past the proposal stage |

### Decision engine reference

The full deterministic "should I proceed" flow that combines Change
Classification and Risk Classification lives in
[Decision Engine](DECISION_ENGINE.md); this document supplies the risk
input to that flow.

### Governance scenario table

| Scenario | Classification | Authority | Action | Validation | Documentation | Stop or continue? |
| --- | --- | --- | --- | --- | --- | --- |
| Failing unit test after a code change this session made | Repair-loop, current-change-caused | Level 1-2 | Fix immediately | Re-run the specific test, then the full suite | None beyond the fix itself | Continue |
| A pending ADR exists (`Status: Proposed`) relevant to the current task | Governance | N/A (informational) | Treat as non-binding; do not implement its substance as final; may draft groundwork explicitly labeled contingent on acceptance | N/A | Note the dependency in the Planning Contract | Continue on unrelated work; wait on the ADR-dependent part |
| A stable upstream release the task needs has not shipped | External dependency wait | N/A | Continue other eligible work; do not force a workaround | N/A | Record the trigger and re-check cadence | Continue (other work); wait (this task) |
| A proposed breaking schema change | Public contract change, High risk | Level 3 draft, Level 4 accept | Draft the ADR and migration plan; do not implement the break itself | Full schema/fixture suite once implemented (post-approval) | ADR, specification update | Stop before implementation; continue on the proposal |
| A broken documentation link found incidentally | Documentation-only, Low risk | Level 1 | Fix immediately, in scope regardless of the original task (see Autonomous Development Lifecycle's "issue blocks correctness" rule) | `validate_repository.py` | None beyond the fix | Continue |
| A desire to add a cloud API | Security/scope change, High risk, Section 2.7 prohibited class | Level 5 (prohibited without prior authorization) | Do not implement; report as a hard stop / governance stop candidate for human decision | N/A | A blocker record naming the specific request | Stop |
| A discovered security vulnerability (e.g., a secret pattern hit) | Security, High risk | Level 4-5 depending on severity | Do not silently fix and move on; escalate immediately, even mid-task | Confirm via `_validate_obvious_secrets` or manual inspection | A blocker record; do not commit the vulnerable content further | Stop, immediately, regardless of current task state |
| An unrelated uncommitted user file found at boot | Concurrent-work risk | N/A | Do not touch; preserve via stash if needed; investigate ownership | N/A | Recorded per [Recovery Procedures](RECOVERY_PROCEDURES.md) | Stop for that file; continue on attributable work |
| A dependency update with a license change | Licensing, High risk | Level 4 | Do not adopt; escalate | N/A | A blocker record naming the license delta | Stop |
| A new feature already approved in the roadmap | Roadmap-authorized implementation | Level 2 | Implement within accepted architecture | Full applicable suite | Tracker/context update | Continue |
| An improvement not present in the roadmap | Scope question | Level 2-3 depending on size | Small (Level 1-2): may proceed if clearly beneficial and safe, recorded as a Next Action origin note. Larger: propose as a Next Action, do not implement unprompted | N/A until approved | A `PROJECT_TRACKER.md` Next Action | Continue (if small) / Stop and propose (if large) |
| A production release request | Release, High risk, Section 2.7 prohibited class | Level 4-5 | Do not tag or publish; this repository has no production release process in scope today | N/A | A blocker record | Stop |

## Examples

See the Governance scenario table above — each row is itself a complete
worked example, matching this Batch's stated preference for concrete
decision tables.

## References

- [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)
- [Decision Engine](DECISION_ENGINE.md)
- [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md)
- [MASTER_OPERATOR.md](../../MASTER_OPERATOR.md) — Autonomous Development
  Rules

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
