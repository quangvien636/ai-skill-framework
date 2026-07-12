# Documentation and Writing Standards

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the qualities every repository document must have, differentiated by
document type, and the writing-level standards (voice, tense, normative
terms, formatting of examples/warnings/limitations) that make a document
actionable by a cold-start session.

## Scope

Applies to every Markdown document this repository produces going forward,
including this Batch's own `docs/operator/*.md` chapters. Extends
`docs/_templates/DOCUMENTATION_TEMPLATE.md` rather than replacing it.

## Design

### Required qualities (every document)

- **Accurate** — matches verified repository state, not aspiration.
- **Actionable** — a reader can do something differently after reading it.
- **Scoped** — states what it does not cover, naming the document that
  does.
- **Current** — Last-updated date reflects the most recent substantive
  change.
- **Linked** — cross-references real files with real anchors.
- **Testable where possible** — a claim about behavior is checkable by
  running something.
- **Explicit about authority** — states plainly whether it is normative,
  descriptive, or a proposal.
- **Explicit about current vs. planned** — never lets a reader infer
  something exists when it does not (see
  [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)).
- **Free of unnecessary duplication** — references instead of restates.
- **Understandable without chat context** — per ADR-0001, assume the reader
  has no memory of any conversation.

### Standards by document type

| Type | Distinguishing standard |
| --- | --- |
| Normative document (ADR, specification, principle) | Every rule uses MUST/MUST NOT/SHOULD/MAY precisely; ambiguity is a defect |
| Guide / runbook | Every step is executable as written; commands are copy-pasteable |
| Specification | States current behavior and, if relevant, proposed/future behavior, clearly separated |
| ADR | Follows `docs/adr/ADR_TEMPLATE.md` exactly; Status field is mechanically validated |
| Tracker (`PROJECT_TRACKER.md`) | Every "Done" cites its evidence (command + result), per this repository's own 44-sprint convention |
| Report (validation, incident, investigation — see [Template Framework](TEMPLATE_FRAMEWORK.md)) | States exactly what was run/observed, never a summary presented as if it were the raw evidence |
| Historical evidence | Never edited after the fact to "fix" its conclusion; a correction is a new entry |

### Writing standards

- **Audience:** a cold-start AI or human session with no prior context, per
  ADR-0001.
- **Terminology:** use this repository's already-established terms
  (Skill, Workflow, Knowledge, Runtime Contract, IR, Diagnostic) exactly as
  `docs/specifications/` and `docs/architecture/` define them; do not
  introduce a synonym for an existing concept.
- **Voice:** direct, second/third person as natural; avoid first-person
  narration of the writing process itself ("I think," "we decided") except
  inside an ADR's own Context/Decision framing, where the deciding party is
  the subject.
- **Tense:** present tense for current state and rules; past tense only for
  historical narrative (Sprint History, ADR Context).
- **Normative terms:** MUST / MUST NOT for hard requirements; SHOULD /
  SHOULD NOT for strong defaults with a legitimate exception path; MAY for
  genuine optionality. Do not use "should" casually where a rule is
  actually a MUST.
- **Avoid vague pronouns:** "this" or "it" must have an unambiguous
  antecedent within the same sentence or the immediately preceding one.
- **Command formatting:** fenced code blocks with the exact, runnable
  command; never a paraphrase of a command.
- **Examples:** at least one concrete worked example per normative
  document; prefer a table of examples over a single one when the rule has
  several distinct branches (this Batch's own chapters follow this
  throughout).
- **Warnings:** stated as their own sentence or table row, not buried
  inside a longer paragraph — e.g., "Never force-push" stands alone.
- **Assumptions:** stated explicitly when a rule depends on one (e.g., "this
  repository currently has no production environment" is stated wherever a
  rule would otherwise be misread as covering one).
- **Limitations:** a document's own Scope section states what it does not
  cover; do not let a limitation surface only as an implicit gap a reader
  discovers by absence.
- **Dated status statements:** any claim about current repository state
  should be traceable to a Last-updated date, so a later reader can judge
  whether to re-verify it.

### Project-specific terminology requiring definition

Every document introducing a term not already defined in
`docs/specifications/METADATA_SPECIFICATION.md`, the relevant architecture
document, or a prior `docs/operator/*.md` chapter must define it in its own
Definitions section, per `docs/_templates/DOCUMENTATION_TEMPLATE.md`'s
existing convention. This Batch defines: Authority Level, Change
Classification, Risk Classification, Planning Contract, Decision Engine
disposition, Blocker class, Knowledge class — each defined once, in its
owning chapter, and referenced (not redefined) elsewhere.

### Avoiding excessive verbosity

A rule stated once, precisely, with one worked example, is better than the
same rule restated three ways "for clarity." Prefer a table over three
paragraphs when the content is enumerable — this Batch's own chapters use
tables as the default structure for exactly this reason.

## Examples

This document itself follows its own standard: MUST/SHOULD/MAY are used
deliberately in the tables above (implicitly, through "must," "should" —
note for future revision: a stricter pass could bold every normative term;
see [Documentation Review Workflow & Quality Gates](DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md)
for the review level that would catch this kind of refinement).

## References

- `docs/_templates/DOCUMENTATION_TEMPLATE.md`
- `docs/adr/ADR_TEMPLATE.md`
- [Required Sections by Document Type](REQUIRED_SECTIONS_BY_DOCUMENT_TYPE.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 4) |
