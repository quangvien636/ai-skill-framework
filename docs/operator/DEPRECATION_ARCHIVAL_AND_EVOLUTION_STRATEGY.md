# Deprecation, Archival, and Repository Evolution Strategy

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define when and how documentation is deprecated or archived, and how the
documentation architecture as a whole evolves without either uncontrolled
sprawl or premature over-consolidation.

## Scope

Covers deprecation/archival mechanics for any repository document, and
structural evolution thresholds for `docs/operator/` and
`PROJECT_TRACKER.md` specifically, since those two grow the fastest.

## Design

### Deprecation

A document becomes deprecated when its guidance is superseded but the
document itself (or its history) still has evidentiary or navigational
value.

| Step | Action |
| --- | --- |
| 1 | Change the document's `Status:` field to `Deprecated` |
| 2 | Add one sentence at the top of the Purpose section naming its replacement, with a link |
| 3 | Do not delete or blank out its content — a deprecated document remains readable |
| 4 | Update every inbound link to point at the replacement, not the deprecated document, unless the link is itself historical (e.g., an old ADR's own reference, which stays as written per [Truth Hierarchy & Conflict Resolution](TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md)'s historical-evidence rule) |
| 5 | Run `python scripts/validate_repository.py` to confirm no link broke |

An ADR is never "deprecated" in this sense — it is superseded by a new ADR
per the Version Specification's existing rule; the old ADR's `Status:`
field becomes `Superseded by ADR-<NNNN>`, which `ASF-REPOSITORY-014`
already validates.

### Archival

A deprecated document is archived when it no longer needs to appear in
normal navigation (README, `MASTER_OPERATOR.md` Table of Contents) but must
remain retrievable.

- **What must never be silently deleted:** any ADR (accepted or
  superseded); any document Git history shows was once authoritative; any
  document a currently-accepted ADR's Related Documents section cites.
- **How archival differs from deletion:** the file remains in the
  repository (or a clearly-named archive location once one is needed —
  none exists yet, since no document has reached this threshold); deletion
  removes it from the working tree entirely and relies on Git history
  alone, which is acceptable only for content that was never authoritative
  (e.g., a truly abandoned draft with no inbound references and no
  historical citation).
- **When files may be moved:** only when the move updates every inbound
  link in the same change (mechanically verified by
  `validate_repository.py`).
- **Validation requirement after deprecation/archival:** full
  `validate_repository.py` run, plus a manual check (per
  [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md))
  that no remaining document's prose (not just Markdown links) still
  presents the deprecated content as current.

### Repository evolution strategy

#### Threshold for splitting a large document

Split when a document's single-topic cohesion breaks down — concretely,
when a reader has to skip past unrelated sections to find the part they
need, or when two sections would each independently satisfy
[Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)'s
"synthesis across several sources" test on their own. This repository
already applies this instinctively (e.g., `docs/specifications/` is many
small files, not one); `docs/operator/` follows the same instinct by
design — one chapter per coherent concern from the start, per ADR-0020.

#### Threshold for merging fragmented documents

Merge only when two documents cover the same concern with no meaningful
distinction (see [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)'s
Duplication audit). Do not merge merely because two documents are short —
a short, focused document is not itself a defect.

#### Index maintenance

`MASTER_OPERATOR.md`'s Table of Contents is the one index for
`docs/operator/`; `docs/specifications/README.md`, `schemas/README.md`,
`templates/README.md`, and `.ai/README.md` remain the indexes for their own
categories. Do not create a second index for any of these — per
[Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)'s
"Reference" action, an index should be referenced, not duplicated.

`PROJECT_TRACKER.md`'s specific evolution threshold: when the Sprint History
table plus the two-to-three most recent full sprint sections exceed a
length that makes the Current Sprint hard to find quickly (a judgment call
for the Principal Engineer, not a fixed line count), extract older full
sprint sections (already summarized in Sprint History) into a dated archive
file, updating the "Full per-sprint backlogs... live in Git history" note
this tracker already carries to also name the archive file. Not yet needed
at the current size (44 sprints, most already summarized to one row).

#### Compatibility with multiple AI agents

Any evolution of the documentation structure must preserve the tool-
agnostic resumption guarantee in
[Multi-Session Continuity, Handover & Completion Checklist](MULTI_SESSION_CONTINUITY_AND_HANDOVER.md) —
`CLAUDE.md`/`AGENTS.md` -> `MASTER_OPERATOR.md` -> boot sequence must keep
working regardless of how deep the `docs/operator/` chapter set grows.

#### Review cadence

No fixed calendar cadence is imposed (this repository's rhythm is
sprint-driven, not date-driven, per `.ai/playbooks/SPRINT_WORKFLOW.md`).
Instead: every session's [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md)
step 10-11 (loading context/tracker) is itself an implicit staleness check;
a dedicated audit (this document's Duplication/Staleness procedures run
deliberately, not incidentally) should happen at least once per Batch of
this manual's build-out, matching this Batch's own Phase 4 consolidation
step.

#### Preventing uncontrolled documentation sprawl

- Every new `docs/operator/*.md` file must already appear as a row in
  `MASTER_OPERATOR.md`'s Table of Contents before or at the moment it is
  created — no orphan chapters (see
  [Future Document Creation Rules](DOCUMENT_CREATION_RULES.md), planned).
- A new top-level documentation directory (a peer of `docs/operator/`)
  requires the same governance weight as any other structural
  documentation decision — a Documentation Engineer call, backed by an ADR
  if it changes a cross-cutting rule (matching ADR-0020's own precedent).

## Examples

If, after several more Batches, `docs/operator/` grows to 60+ chapter
files and a reader reports difficulty navigating even with the Table of
Contents, the evolution response is *not* to merge chapters back together
(that would violate the one-concern-per-file principle this Batch
establishes) but to consider whether `MASTER_OPERATOR.md`'s Table of
Contents itself needs a per-Part sub-index page — a decision to make at
that time, based on real difficulty observed, not pre-emptively now.

## References

- [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)
- [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)
- ADR-0020
- Version Specification (`docs/specifications/VERSION_SPECIFICATION.md`)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 2) |
