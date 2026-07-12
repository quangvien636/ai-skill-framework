# Duplication, Staleness, and Conflict Detection

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define repeatable audit procedures for three related defect classes —
duplicated guidance, stale documentation, and unresolved conflicts — so a
session can run a bounded, deterministic check instead of an open-ended
"does anything look wrong" review.

## Scope

Covers detection procedures, acceptable-vs-unacceptable duplication, stale-
document indicators, and conflict resolution recording. Applies to every
Markdown document in the repository, including this Batch's own new
`docs/operator/*.md` chapters.

## Design

### Duplication audit procedure

1. Identify repeated terminology: grep for a term across `docs/`, `.ai/`,
   root files; a term defined in more than one place is a candidate.
2. Locate multiple definitions of the same rule: for each candidate,
   compare the surrounding rule text.
3. Identify contradictory variants: do the multiple definitions actually
   agree, or only use the same word for different things?
4. Choose the correct authoritative home per
   [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md).
5. Replace duplicates with summaries or links, keeping exactly one
   authoritative statement of the rule.
6. Preserve historical context where required (a past ADR's own restatement
   of a rule, as it understood it at the time, is historical evidence, not
   a duplicate to be pruned).
7. Validate all references — after consolidating, run
   `python scripts/validate_repository.py` to confirm no link/anchor broke.

### Acceptable vs. unacceptable duplication

| Pattern | Acceptable? | Why |
| --- | --- | --- |
| A short checklist in a guide that restates the steps of a longer authoritative procedure, linking back to it | Yes | It adds convenience without creating a second, divergent authority — the guide does not redefine the procedure, it repeats already-authoritative steps and cites the source |
| Two documents both stating "the repository is the source of truth" in their own words | Yes, in moderation | ADR-0001's principle is foundational enough that brief restatement in multiple entry points (README, this manual, PROJECT_CONTEXT) aids onboarding, provided none of them adds a conflicting nuance |
| Two documents each defining, differently, when an ADR is mandatory | No | This is the exact failure mode this Batch's [ADR Governance & Decision Rules](ADR_GOVERNANCE.md) chapter exists to prevent — there must be exactly one authoritative answer |
| A `docs/operator/*.md` chapter restating an ADR's full Decision text instead of summarizing and linking | No | Violates "reference, don't duplicate" (`MASTER_OPERATOR.md` Philosophy); the ADR can be superseded later and the chapter's copy would silently go stale |

### Stale-document indicators

| Indicator | How to check |
| --- | --- |
| References to removed files | `python scripts/validate_repository.py` (`ASF-REPOSITORY-006`/`007`) catches this mechanically for Markdown links; grep for a filename elsewhere (prose mentions, not just links) as a manual supplement |
| Status inconsistent with code or tests | Compare a document's claim (e.g., "not yet implemented") against the actual code/test presence |
| Completed roadmap items still marked pending | Cross-reference `docs/roadmaps/ROADMAP.md` against `PROJECT_TRACKER.md` Sprint History |
| Old branch or commit assumptions | A document naming a specific commit hash or branch state that `git log` no longer supports |
| Deprecated dependency behavior | A document describing a library API that the pinned version (per `requirements-*.txt`) no longer exposes |
| Obsolete commands | A documented command that fails when actually run |
| Duplicate "source of truth" claims | Two documents both claiming final authority over the same specific fact (not the general ADR-0001 principle, which is fine per the table above) |
| Current-state claims without dates or evidence | A sentence asserting "X is true" with no way to tell when that was last verified |
| References to superseded ADRs as if still controlling | `ASF-REPOSITORY-014` catches malformed Status fields; a manual check is needed for prose that cites an ADR number without checking whether it was later superseded |

### Deterministic review procedure

1. Run `python scripts/validate_repository.py` — catches broken links,
   duplicate anchors, invalid ADR references, invalid ADR status,
   placeholder violations, secret patterns, and lifecycle orphans
   mechanically, today.
2. For claims validation does not check (prose staleness, terminology
   duplication, obsolete commands): run the specific greps/comparisons in
   the tables above, scoped to the documents the current task touched plus
   any document that references them (search for the changed document's own
   filename elsewhere in the repository).
3. Record findings; fix what is in scope; add a Next Action for what is
   not, per [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)'s
   "newly discovered issue outside current scope" table.

### When automated validation should be added instead of relying on manual review

Add a new mechanical check (an `ASF-REPOSITORY-*` rule, following the
pattern in `scripts/asf_validator/content_integrity.py`) when a staleness or
duplication class has occurred more than once, or when its detection
requires no judgment (e.g., "does this filename still exist," which is
exactly how the existing link/anchor/ADR-reference/ADR-status checks were
each justified in their own sprints). Keep relying on manual review when
detection genuinely requires judgment (e.g., "do these two prose
descriptions actually contradict, or just phrase the same rule
differently") — automating a judgment call risks false positives that erode
trust in the validator, which is itself a Quality Engineer / Automation
Engineer Decision Right tradeoff, not a default answer.

### Conflict detection and resolution recording

| Conflict type | Detection | Resolution record |
| --- | --- | --- |
| Governance conflict (two documents disagree on who decides) | Manual review triggered by any Authority Level classification uncertainty | A `PROJECT_TRACKER.md` Next Action naming both documents and the ambiguity, until a human or an ADR resolves it |
| Architectural conflict | An ADR and an architecture doc disagree | Treat the ADR as correct (per the Truth Hierarchy); file a Next Action to sync the architecture doc's text |
| Terminology conflict | The same term used with two different meanings | Fix in the more general document (principles/glossary once populated); the more specific document's usage is presumed correct for its own narrow context unless it is actually wrong |
| Status conflict | A document's own status field contradicts its observable state (e.g., `Status: Draft` on a document actively cited as authoritative elsewhere) | Correct the status field to match reality; do not silently start treating a Draft as Active without updating the field |
| Process conflict | Two procedures for the same recurring task | Resolve per the Duplication audit procedure above — designate one authoritative, the other becomes a link |
| Conflicting examples | Two documents' worked examples imply different correct answers for the same scenario | Re-derive the correct answer from the underlying rule (not either example), fix both examples to agree |
| Conflicting validation commands | Two documents give different commands for "the" validation step | `docs/guides/VALIDATION_GUIDE.md` is authoritative for command syntax; any other document citing a command must match it exactly or link to it instead of restating it |

Do not silently delete contradictory historical material when it is
relevant evidence — an ADR's Alternatives Considered section describing a
rejected approach stays even after the accepted approach is later revised
by a superseding ADR, because it explains what was actually weighed at
decision time.

## Examples

During this Batch's own writing, a session finds that
`docs/guides/GETTING_STARTED.md` is a stub (`TODO` placeholders only) while
`README.md`'s navigation lists it as a real onboarding document. This is a
Stale-document indicator ("current-state claim without evidence" — the
navigation implies content that does not exist). Resolution recorded per
Prompt 01's Gap Analysis and this Batch's own tracker update: the gap is
named explicitly rather than silently linked to as if it were complete.

## References

- `python scripts/validate_repository.py` / `docs/guides/VALIDATION_GUIDE.md`
- [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)
- [Truth Hierarchy & Conflict Resolution](TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 2) |
