# Truth Hierarchy and Conflict Resolution (Detailed)

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Give the fully worked-out version of `MASTER_OPERATOR.md`'s Repository
Truth Hierarchy: category-based conflict resolution rules and concrete
examples, precise enough that a session never has to improvise when two
documents disagree. The compact ordered list in `MASTER_OPERATOR.md` is the
canonical summary; this chapter is its expansion, not a competing version —
if the two ever appear to differ, `MASTER_OPERATOR.md`'s own list wins,
since it is higher in the hierarchy it itself defines (spine over chapter).

## Scope

Covers conflict resolution *by category* (authority, architecture, current
state, implementation behavior, historical evidence, planning intent,
operational procedure) rather than a single flat document ranking, because a
flat ranking alone produces wrong answers in real cases — for example, it
must not let this general handbook override a specific accepted
architecture decision.

## Design

### Why category-based, not purely document-based

A purely positional hierarchy ("ADRs beat architecture docs beat this
manual") is necessary but not sufficient. The right resolution also depends
on *what kind of claim* is in conflict. A `docs/operator/*.md` chapter
about session process does not compete with `docs/architecture/*.md` about
system design — they answer different questions and should rarely conflict
at all; when a document strays outside its category (e.g., a guide making
an architectural claim), the category test below applies before the
positional one.

### Conflict categories

| Category | What it governs | Highest authority for this category | Notes |
| --- | --- | --- | --- |
| Authority (who may decide) | Which role/human may make a given decision | `.ai/governance/DECISION_RIGHTS.md`, expanded by [Authority Levels](AUTHORITY_LEVELS.md) | `MASTER_OPERATOR.md`'s Decision Hierarchy is a summary of this, never a competing source |
| Architecture (how a component works) | Structural design of a named component | The specific `docs/architecture/<COMPONENT>.md` file | An ADR that changes it supersedes the architecture doc until the doc itself is updated to match — treat the ADR as correct and the doc as due for a sync |
| Current state (what exists right now) | What is implemented, passing, or true today | The repository's actual code/schema/tests, verified by running them | No document, however authoritative in general, outranks a direct verification |
| Implementation behavior (what a specific function/validator actually does) | Precise mechanics | The source file itself (e.g., `scripts/asf_validator/content_integrity.py`) | `docs/guides/VALIDATION_GUIDE.md` describes it; if they diverge, the guide is stale, not the code |
| Historical evidence (what happened and why) | Past decisions, past incidents, past sprint outputs | Git history and the ADR/tracker entries from that time | Never rewritten to "fix" the historical record — a correction is a *new* entry, not an edit to an old one |
| Planning intent (what should happen next) | Strategic sequencing | `docs/roadmaps/ROADMAP.md` / `VALIDATOR_ROADMAP.md`, refined by `PROJECT_TRACKER.md` Next Actions | The tracker is more current but narrower; the roadmap is more strategic but slower to update — prefer the tracker for "is this next," the roadmap for "does this fit the plan" |
| Operational procedure (how to do a routine task) | Step-by-step mechanics of a recurring activity | The specific runbook/guide/chapter naming that procedure | If two procedures for the same task exist, this is itself a defect — resolve per [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md), do not silently pick one |

### The positional hierarchy (restated with category cross-reference)

This restates `MASTER_OPERATOR.md`'s ordered list, annotated with which
category each rank is *for*:

1. Accepted ADRs — Authority + Architecture (for the specific decision)
2. Repository as it currently validates/tests — Current state
3. `PROJECT_CONTEXT.md` / `PROJECT_TRACKER.md` — Planning intent (near-term) + historical evidence (recent)
4. Architecture documents — Architecture
5. Specifications and schemas — Architecture (contract-level)
6. Principles — Authority (cross-cutting) + Architecture (naming/design)
7. Guides and runbooks — Operational procedure
8. This manual and its chapters — Operational procedure (process/navigation only)
9. Knowledge Base — none of the above; scoped to Skill domain content only
10. Everything else (conversation, memory, routing files) — none; never authoritative

### Worked conflict-resolution examples

| Conflict | Category | Resolution |
| --- | --- | --- |
| `docs/architecture/RUNTIME_ARCHITECTURE.md` says Runtime Contracts are not yet wired into any production Skill; `PROJECT_CONTEXT.md` Sprint 38 says `runtime:offline` is now active for `skill:content-creation` | Current state | `PROJECT_CONTEXT.md` + verified `runtime/offline/runtime.yaml` win — the architecture doc is stale on this specific point and should be corrected on next touch, not treated as still true |
| A `docs/operator/*.md` chapter describes a "Coding Standards" rule that contradicts an actual pattern used throughout `scripts/asf_validator/` | Implementation behavior vs. operational procedure | The existing code pattern wins for "what is current style"; the chapter is wrong and must be corrected — a chapter never gets to define a new standard by assertion, only by documenting or, if genuinely proposing a new one, routing through [ADR Governance & Decision Rules](ADR_GOVERNANCE.md) if the change is significant |
| Two ADRs' Alternatives Considered sections describe different reasons for rejecting the same alternative | Historical evidence | Both are valid historical records of *that decision's own* reasoning; they do not need to agree with each other, since each is scoped to its own decision's context — do not "fix" one to match the other |
| `docs/roadmaps/ROADMAP.md` lists a capability as "Later"; a Next Action in `PROJECT_TRACKER.md` is actively pursuing it now | Planning intent | The tracker wins for "is this happening now" (it is more current and more specific); update the roadmap in the same change if the reprioritization is intentional, per [Context, Tracker, Roadmap & Naming Standards](CONTEXT_TRACKER_ROADMAP_AND_NAMING_STANDARDS.md) |
| This manual's Autonomous Development Rules say "MUST NOT promote past draft"; a specific task's instructions ask for a promotion | Authority | The rule wins unless the human operating the session has explicitly delegated that authority for this session (matching `.ai/governance/DECISION_RIGHTS.md`'s own escape clause) — the delegation itself must be explicit and session-scoped, not inferred |
| A `docs/guides/*.md` runbook and a `docs/operator/*.md` chapter both describe how to do the same recurring task, with slightly different steps | Operational procedure, duplication | This is a defect, not a hierarchy question — see [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md); the fix is to designate one as authoritative and make the other a summary linking to it, not to pick a winner and ignore the loser's existence |

### When no category fits

If a conflict does not clearly fit any category above, treat it as a
governance gap: record it (a `PROJECT_TRACKER.md` Next Action or, if
significant enough, a proposed ADR), resolve it conservatively (favor the
more specific, more recently verified source), and do not let the ambiguity
block unrelated work.

## Examples

See the worked table above — each row is itself a complete example with
its own resolution and reasoning, per this Batch's preference for concrete
decision tables over abstract prose.

## References

- [MASTER_OPERATOR.md](../../MASTER_OPERATOR.md) — Repository Truth
  Hierarchy (canonical summary)
- ADR-0001
- [Context Restoration](CONTEXT_RESTORATION.md)
- [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 2) |
