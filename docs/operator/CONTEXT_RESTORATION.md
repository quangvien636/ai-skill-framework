# Context Restoration

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define a deterministic procedure for reconstructing project context from
repository state rather than from chat history, per ADR-0001's "conversation
history is not authoritative" rule. This is what a session does *during*
[Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md) steps 9-16, made
precise enough to run identically whether the session is the tenth in a row
or the first after a long gap.

## Scope

Covers what to reconstruct, where each piece comes from, and how to resolve
disagreement between sources encountered while reconstructing it. It does
not cover the general Repository Truth Hierarchy (see
[Truth Hierarchy & Conflict Resolution](TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md)
for the full, example-driven version) — this document applies that hierarchy
specifically to the act of restoring session context.

## Design

### What must be reconstructed, and from where

| Element | Authoritative source | Fallback if source is stale/missing |
| --- | --- | --- |
| Project mission | `PROJECT_CONTEXT.md` Vision; `MASTER_OPERATOR.md` Vision/Mission | None — hard stop if both missing |
| Architectural state | `docs/architecture/SYSTEM_ARCHITECTURE.md` plus `PROJECT_CONTEXT.md` Architecture section | `git log` for recent architecture-doc commits |
| Roadmap position | `docs/roadmaps/ROADMAP.md`, `docs/roadmaps/VALIDATOR_ROADMAP.md` | `PROJECT_TRACKER.md` Sprint History (more current, less strategic) |
| Completed tasks | `PROJECT_TRACKER.md` Sprint History table | `git log --oneline` cross-referenced against Sprint History for gaps |
| Active work | `PROJECT_TRACKER.md` Current Sprint | `git status`/`git diff HEAD` for uncommitted evidence of work in progress |
| Deferred work | `PROJECT_TRACKER.md` Next Actions | ADRs' "Alternatives Considered" and architecture docs' documented gaps |
| Blocked work | `PROJECT_TRACKER.md` Next Actions trigger conditions | `docs/guides/WEEKLY_OPERATOR_PLAN.md` / `MONTHLY_OPERATOR_PLAN.md` trigger definitions |
| Human decisions | Accepted ADRs (`Status: Accepted`); `.ai/governance/DECISION_RIGHTS.md` | `PROJECT_CONTEXT.md` Sprint narrative mentioning "human maintainer reviewed/accepted" |
| Unresolved ADRs | ADRs with `Status: Proposed` | None — a Proposed ADR is unresolved by definition until a human changes its Status |
| Recent regressions | Latest `python scripts/validate_repository.py` / test suite run, this session | `PROJECT_TRACKER.md` Sprint exit criteria for the most recent sprint |
| Known out-of-scope modifications | `git status --porcelain` findings not attributable to any tracked task | N/A — if unknown, treat per [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md)'s concurrent-work-risk step |
| Next recommended task | `PROJECT_TRACKER.md` Next Actions, filtered through [Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md) | If Next Actions is empty, the roadmap's "Next"/"Later" notes |

### Role and authority of each source during restoration

Per the Repository Truth Hierarchy, during context restoration specifically:

1. **`MASTER_OPERATOR.md`** — authoritative for *how to restore context at
   all* (this document is one of its chapters) and for cross-cutting
   operating rules. Not authoritative for what the current sprint is.
2. **`PROJECT_CONTEXT.md`** — authoritative for the current narrative
   understanding of architecture and focus, updated once per sprint.
3. **`PROJECT_TRACKER.md`** — authoritative for actionable status: what is
   done, in progress, blocked, or next. This is the single most
   frequently-consulted source during restoration.
4. **Roadmap documents** — authoritative for strategic sequencing and
   longer-horizon intent; less current than the tracker on a session-to-
   session basis.
5. **ADRs** — authoritative for any decision they cover, regardless of how
   old; an ADR is never superseded by a newer narrative document, only by
   another ADR.
6. **Git history** — authoritative for what actually happened, as opposed to
   what a document claims happened. When a tracker entry says "Done" and
   `git log` shows no corresponding commit, Git wins per the Truth
   Hierarchy's "repository as it currently validates" rule.
7. **Validation artifacts** (this session's own `validate_repository.py` /
   test run) — authoritative for current correctness; supersedes any
   document's claim that "all tests pass" as of an earlier session.
8. **Issue or backlog documents** — this repository currently has none
   beyond `PROJECT_TRACKER.md`'s Next Actions; if one is introduced later,
   it ranks alongside the tracker.

### Disagreement handling

| Disagreement | Resolution |
| --- | --- |
| `PROJECT_CONTEXT.md` Current Focus names a sprint not in `PROJECT_TRACKER.md` Sprint History | Tracker wins (more specific, more frequently updated); flag `PROJECT_CONTEXT.md` as stale and correct it as part of the current session's documentation update |
| `PROJECT_TRACKER.md` marks an item "Done" but `git log` shows no matching commit | Git wins; treat the item as not actually done, investigate before trusting any other "Done" claim from the same tracker revision |
| Roadmap says a capability is "Next" but an ADR already implemented it | ADR + Git history win; the roadmap is stale and should be updated in the same change that discovers this |
| Two ADRs appear to conflict | The later-dated `Accepted` ADR wins if one explicitly supersedes the other; if neither supersession is recorded, this is a governance defect — record it and escalate per [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md), do not silently pick one |
| A `docs/operator/*.md` chapter states something a more specific architecture document contradicts | The architecture document wins, per the Repository Truth Hierarchy; the chapter is corrected in the same session that finds the conflict, per [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md) |

## Examples

A session restoring context finds `PROJECT_CONTEXT.md`'s Current Focus
describing Sprint 43 as in progress, but `PROJECT_TRACKER.md`'s Current
Sprint section shows Sprint 44 completed and `git log -1` matches Sprint
44's commit. Resolution: trust the tracker and Git; treat
`PROJECT_CONTEXT.md` as one sprint stale (a normal, expected lag — see
[Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)
for when staleness is expected versus a defect), and update it if the
current task touches it, or note the lag if not.

## References

- ADR-0001 — repository is the source of truth
- [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md)
- [Truth Hierarchy & Conflict Resolution](TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md)
- [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 1) |
