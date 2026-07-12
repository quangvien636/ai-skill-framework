# Work Decomposition, Dependency, and Impact Analysis

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define how to split a large task into safe, coherent units; how to
identify what a task depends on; and what minimum impact analysis a change
requires before implementation, scaled to the task's Change Classification.

## Scope

Supports the `planning` state of
[Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md) and
feeds [Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md)'s
decomposition step.

## Design

### Work decomposition

A unit of decomposed work must be:

- **Independently understandable** — readable and reviewable without
  needing the other units open at the same time.
- **Testable** — has its own validation that can confirm it, specifically.
- **Reversible** — a single `git revert` undoes exactly that unit, not a
  tangle of others.
- **Committable** — forms one coherent commit (or a small, clearly ordered
  sequence).
- **Documented** — its own Definition-of-Done documentation travels with
  it, not deferred to "later."
- **Valuable on its own** — even if no further unit is ever done, this one
  left the repository better than before it.
- **Ordered by dependency** — a unit that another depends on is sequenced
  first.

### When to decompose vs. keep atomic

| Signal | Response |
| --- | --- |
| The task touches files with no shared concern (e.g., one chapter's content plus an unrelated bug fix) | Decompose — these are two units, two commits |
| The task is one coherent concern spread across several files that only make sense together (e.g., a schema change plus its fixtures plus its documentation) | Keep atomic — splitting would leave an intermediate commit in a broken or half-documented state |
| The task is large but strictly ordered (e.g., this Batch's four phases) | Decompose along the natural phase/chapter boundaries, since each phase is independently valuable and reviewable, per this Batch's own instruction to prefer one commit per phase |
| Decomposing would leave documentation and validation incoherent (e.g., splitting one ADR's Decision from its Consequences into separate commits) | Keep atomic |

### Dependency analysis

| Dependency type | Example | Handling |
| --- | --- | --- |
| Hard dependency | A chapter that structurally requires another chapter to exist first (rare in this Batch, since chapters are designed to be independently readable) | Sequence strictly; do not start the dependent unit's implementation before the dependency is at least drafted |
| Soft dependency | A chapter that reads better after another but is still correct alone | Prefer the natural order but do not block on it |
| Optional enhancement | A cross-link that would help but whose absence does not make either document wrong | Add when convenient; never let it block completion |
| Unavailable external dependency | A future MCP SDK v2 release | Treat per [External dependency wait](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md#stop-condition-taxonomy); do not simulate or assume its behavior |
| Speculative future dependency | "We might need X later" | Do not build for it now — matches Design Principle 8's "does not mean producing speculative documentation for work that has not been selected" |

### Impact analysis

Before a consequential change, assess, scaled by Change Classification (see
[Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)):

| Change class | Minimum impact analysis required |
| --- | --- |
| Documentation-only | Which other documents link to or reference the changed one (grep for the filename) |
| Test-only | Which other tests exercise the same code path |
| Internal non-breaking implementation | Affected modules; whether any test asserts the specific internal detail being changed |
| Public contract change | Affected modules, public interfaces, contracts, tests, documentation, workflows, examples, compatibility, migration needs, rollback — the full list, because this class is exactly where an incomplete impact analysis causes the most damage |
| Architecture change | Every document the Repository Architecture Map lists as depending on that architectural area |
| Security change | Every consumer of the affected boundary, plus a threat-model note |

## Examples

This Batch's own Phase 1 files (7 chapters) were decomposed along
chapter boundaries — each independently understandable, testable via
`validate_repository.py`, reversible via `git revert` of its own commit,
and each individually valuable (a session reading only
[Recovery Procedures](RECOVERY_PROCEDURES.md) gains something even without
having read the other six). They were kept in one commit as a phase-level
unit per this Batch's own "prefer one commit per phase when changes are
logically separable" instruction, since splitting into seven commits would
not have added reviewability given they were authored together as one
coherent deliverable.

## References

- [Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md)
- [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)
- [Rollback Planning & Risk Register](ROLLBACK_PLANNING_AND_RISK_REGISTER.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
