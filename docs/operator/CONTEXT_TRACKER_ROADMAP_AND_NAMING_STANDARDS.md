# Context, Tracker, Roadmap Responsibilities and Naming Standards

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Give an operator-facing, unambiguous split of responsibility between
`PROJECT_CONTEXT.md`, `PROJECT_TRACKER.md`, and the roadmap documents, plus
the metadata and naming standards a session applies when creating or
updating any of them (or any other repository document).

## Scope

Extends `PROJECT_CONTEXT.md`'s and `PROJECT_TRACKER.md`'s own Purpose
sections with concrete update triggers and anti-duplication rules; extends
`docs/principles/NAMING_CONVENTION.md` with metadata conventions this Batch
introduces for `docs/operator/*.md` chapters specifically.

## Design

### Project Context

Should contain: durable current-project understanding (Vision, Architecture
summary, Working Principles, Documentation-First Workflow), the Current
Focus narrative (one paragraph per completed sprint, append-only), and a
Revision History table.

Should not contain: per-item actionable task status (belongs in the
tracker), architectural rationale for a specific decision (belongs in an
ADR), or step-by-step procedure (belongs in a guide or operator chapter).

Update trigger: once per completed sprint, always in the same commit as the
sprint's other deliverables — never as a separate later commit.

### Project Tracker

Should contain: Current Sprint (goal, backlog table, exit criteria),
Previous/Earlier Sprint sections, Sprint History (one row per sprint, terse),
Risks and Guardrails, Next Actions.

Should not contain: long-form architecture narrative (belongs in
`PROJECT_CONTEXT.md` or `docs/architecture/`), permanent policy (belongs in
a principle or ADR).

Update trigger: whenever a Current Sprint opens, closes, or its backlog
changes; whenever a Next Action is added, resolved, or reprioritized.

Anti-duplication rule: a completed sprint's detail lives in exactly one
place — its own (now Previous/Earlier) section until the next restructuring
threshold (see
[Deprecation, Archival & Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md)),
then only in the Sprint History summary row. Do not keep both a full
section and a summary row live simultaneously beyond the sprint immediately
after closure — this repository's own convention already does this
correctly (compare how Sprint 41-43 each retain full detail while older
sprints exist only as Sprint History rows).

### Roadmap Documents

Should contain: ordered strategic development intent, milestone
dependencies, a terse "Completed / Next / Later" structure.

Should not contain: per-sprint backlog detail (belongs in the tracker),
narrative decision rationale (belongs in an ADR).

Update trigger: when a milestone completes (append one Notes-section
bullet) or when strategic sequencing changes.

### Responsibility summary table

| Question a reader might ask | Authoritative document |
| --- | --- |
| "What is this project, architecturally, right now?" | `PROJECT_CONTEXT.md` |
| "What is being worked on this sprint?" | `PROJECT_TRACKER.md` Current Sprint |
| "What's blocked, and on what?" | `PROJECT_TRACKER.md` Next Actions |
| "What was delivered in Sprint N?" | `PROJECT_TRACKER.md` Sprint History (terse) or that sprint's own section if still recent |
| "What's the long-term plan?" | `docs/roadmaps/ROADMAP.md` / `VALIDATOR_ROADMAP.md` |
| "Why was X decided this way?" | The relevant ADR |
| "How do I do task Y?" | The relevant `docs/guides/*.md` or `docs/operator/*.md` chapter |

### Metadata and naming standards

Every repository document (existing convention, per
`docs/_templates/DOCUMENTATION_TEMPLATE.md`) already carries: Title,
Version, Status, Last updated. This Batch adds no new required metadata
field — deliberately, per this chapter's own "do not introduce excessive
metadata" constraint — but makes the existing fields' meaning precise for
`docs/operator/*.md` chapters specifically:

| Field | Meaning for a `docs/operator/*.md` chapter |
| --- | --- |
| Title | Matches its Table of Contents row in `MASTER_OPERATOR.md` exactly |
| Version | Starts at `0.1`; increments on any content change; independent of `MASTER_OPERATOR.md`'s own version |
| Status | `Active` once written and validated; a chapter is never committed as `Draft` — if it is not ready, it stays `Planned` in the Table of Contents and unwritten |
| Last updated | The date of the chapter's most recent substantive revision |

Filenames follow the existing `docs/architecture/*.md`-style convention:
`UPPER_SNAKE_CASE.md`, no numeric prefix (ordering is conveyed by
`MASTER_OPERATOR.md`'s Table of Contents, matching how `docs/architecture/`'s
ordering is conveyed by `README.md`, not by filename). Names should be
precise noun phrases describing the chapter's scope, matching
`docs/principles/NAMING_CONVENTION.md`'s general rule against vague or
generic suffixes.

Do not add: an "owner" field beyond what the Decision Rights model already
assigns by role (adding a per-document named owner would create a second,
competing authority record); a "related tests" field for documentation-only
chapters (not applicable); a "superseded documents" field beyond what the
References section already links to Marking excessive metadata a
requirement here would itself violate this chapter's own scope constraint.

## Examples

A session completes this Batch's Phase 2 and needs to decide where "Sprint
44 also wrote `docs/operator/REPOSITORY_ARCHITECTURE_MAP.md`" belongs.
Per the Responsibility summary table: this is per-sprint backlog detail ->
`PROJECT_TRACKER.md`'s Current Sprint backlog table, not
`PROJECT_CONTEXT.md`'s narrative (which gets only the one-paragraph summary
once the sprint closes) and not the roadmap (too fine-grained for strategic
intent).

## References

- `PROJECT_CONTEXT.md`
- `PROJECT_TRACKER.md`
- `docs/roadmaps/ROADMAP.md`
- `docs/principles/NAMING_CONVENTION.md`
- `docs/_templates/DOCUMENTATION_TEMPLATE.md`

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 2) |
