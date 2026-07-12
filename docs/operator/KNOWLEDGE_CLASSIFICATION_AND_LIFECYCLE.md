# Knowledge Classification and Lifecycle

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define a taxonomy of knowledge classes this repository produces, where each
class's authoritative storage location is, and the lifecycle a piece of
knowledge moves through from discovery to archival — so a session can
correctly classify what it just learned instead of either over-documenting
trivia or losing something genuinely reusable.

## Scope

Applies to knowledge *about the repository and its operation* (this is
distinct from `knowledge/`, which is domain content Skills consume — see
the Knowledge Base Management chapter, planned, for that separate concern).

## Design

### Knowledge classes

| Class | Definition | Authoritative storage | Required metadata | Update owner | Obsolescence rule |
| --- | --- | --- | --- | --- | --- |
| Normative rule | A MUST/MUST NOT constraint on future work | Principles, specifications, or an ADR's Decision/Enforcement | Version, Status | Chief Architect (ADR) / Documentation Engineer (principle) | Superseded by a new ADR/principle revision, never silently edited |
| Accepted decision | A resolved architectural choice with rationale | ADR (`Status: Accepted`) | Status, Date, Decision owners | Chief Architect | Superseded by a new ADR |
| Implementation fact | How a specific piece of code currently behaves | The code itself, plus the owning architecture document | N/A (code is ground truth) | Framework Engineer | Obsolete the moment the code changes; the doc must be updated in the same change |
| Current state | What is true about the repository right now (versions, active bindings, etc.) | `PROJECT_CONTEXT.md` Current Focus, verified artifacts | Date | Principal Engineer | Obsolete on the next sprint; expected to lag briefly, a defect only if stale beyond one sprint |
| Roadmap intent | What is planned, in what order | `docs/roadmaps/*.md` | Version, Status | Principal Engineer | Revised when priorities change; old intent is historical, not deleted |
| Hypothesis | An untested idea or design option | Session working notes; promoted to a design document only if pursued | N/A while a hypothesis | Whoever proposes it | Discarded freely if not pursued; no permanent record required |
| Experiment result | Evidence from a bounded, deliberate test | An Investigation Report (see [Template Framework](TEMPLATE_FRAMEWORK.md), planned) or, if it changes a decision, an ADR | Date, method, evidence | Whoever ran it | Retained as historical evidence even if the conclusion is later revised |
| Historical evidence | A record of what happened and why, at the time | Git history; ADR Alternatives Considered; `PROJECT_TRACKER.md` Sprint History | Date | N/A — read-only once written | Never deleted; a correction is a new entry |
| Operational procedure | A repeatable how-to for a recurring task | `docs/guides/*.md` or `docs/operator/*.md` | Version, Status, Last updated | Automation Engineer / Documentation Engineer | Revised when the procedure's actual mechanics change |
| Reusable lesson | A generalizable finding from a specific incident (root cause, edge case, failed approach) | The relevant architecture/guide document, or a new regression test | N/A | Framework Engineer / Test Engineer | Retained as long as the risk it guards against remains possible |
| Temporary investigation | Exploration that has not yet produced a durable conclusion | Session working notes only | N/A | N/A | Discarded at session end unless promoted |
| External dependency | A fact about something outside the repository's control (a library version, an upstream release date) | The ADR or architecture doc that depends on it, with the fact dated | Date checked | Whoever checked it | Re-verified, not assumed, each time it becomes relevant again (see `WEEKLY_OPERATOR_PLAN.md`'s trigger-check pattern) |
| Unresolved question | Something genuinely unknown that blocks a decision | `PROJECT_TRACKER.md` Next Actions, or a Proposed ADR's Context section naming the open question | N/A | Whoever raised it | Resolved when answered; the resolution is then reclassified into one of the classes above |

### Lifecycle

```text
Discovery
  -> evidence collection      (what specifically was observed, and how)
  -> classification            (which class above)
  -> validation                 (is the evidence actually sufficient?)
  -> temporary recording        (session working notes if not yet promoted)
  -> review                     (does it survive a second look / a validator run?)
  -> promotion                  (see threshold below)
  -> authoritative placement    (per the class's storage location)
  -> cross-linking               (linked from the chapter/document that would lead a reader to it)
  -> maintenance                 (kept current as the thing it describes changes)
  -> deprecation                 (marked, not deleted, when superseded)
  -> archival                    (moved out of normal navigation, never destroyed)
```

### Worked lifecycle transitions

- **A bug lesson becomes a regression test and documentation rule:**
  discovery (a defect is found) -> evidence (the failing input/output) ->
  classification (Reusable lesson) -> a `tests/unit/` case is added
  (authoritative placement as code) -> if the lesson also implies a rule
  future code must follow, the owning architecture document gains one
  sentence citing the invariant, not a retelling of the incident.
- **An experiment becomes accepted knowledge or rejected evidence:** a
  session tries an approach in a scratch context -> evidence collection (did
  it work, under what conditions) -> if it changes a decision, promoted to
  an ADR (`Status: Proposed`, pending human acceptance); if it does not
  change a decision but is worth remembering, promoted to a documented
  Alternatives Considered-style note in the relevant document; if it simply
  failed and teaches nothing generalizable, it is not promoted at all.
- **An implementation detail becomes an architecture decision when
  appropriate:** most implementation details stay Implementation Fact
  (code + architecture doc). One is promoted to an ADR only when it meets
  the "mandatory ADR" bar in
  [ADR Governance & Decision Rules](ADR_GOVERNANCE.md) — e.g., it commits
  the framework to a cross-cutting boundary future code must respect, not
  merely "this is how it happens to work today."
- **A temporary report becomes historical evidence:** an Investigation or
  Validation Report (see [Template Framework](TEMPLATE_FRAMEWORK.md),
  planned) is committed once, is never edited to "fix" its conclusion after
  the fact, and remains as the record of what was known and decided at that
  time — a later, better understanding is a *new* report, cross-linked to
  the old one, not a rewrite of it.
- **Stale guidance is corrected without erasing history:** see
  [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md).
  The correction is a new revision-history row in the corrected document,
  not a silent edit with no trace that it once said something else.

### Promotion threshold

Promote from "temporary recording" to "authoritative placement" only when
the finding scores positively on enough of the following to justify the
maintenance cost of a permanent record:

- **Recurrence risk** — could the same mistake or question happen again?
- **Impact** — how costly would rediscovery or repetition be?
- **Generality** — does it apply beyond the one place it was found?
- **Cost of rediscovery** — how hard was it to find the first time?
- **Architectural significance** — does it constrain future design?
- **Operator relevance** — would a future session's boot sequence benefit
  from knowing this?

A trivial, one-off detail with no reuse value (e.g., "this specific typo
existed in one file") does not need permanent documentation beyond the
commit that fixed it — Git history is sufficient memory for it.

## Examples

A session fixes a bug where a Runtime Contract's fallback chain resolution
silently picked the wrong candidate when two contracts had the same
priority. This scores high on recurrence risk, impact, and architectural
significance -> promoted: a regression test in `tests/unit/test_dependency_resolver.py`
(Reusable lesson, authoritative as code) plus one sentence in
`docs/architecture/RUNTIME_CONTRACT_ARCHITECTURE.md` naming the tie-breaking
rule explicitly (Implementation fact, authoritative as an architecture
statement). No new `docs/operator/*.md` chapter and no ADR were warranted —
the existing architecture already had a home for this fact; it was simply
missing.

## References

- [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)
- [Repository Architecture Map](REPOSITORY_ARCHITECTURE_MAP.md)
- ADR-0001

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 2) |
