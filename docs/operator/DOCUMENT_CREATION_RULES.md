# Future Document Creation Rules

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define what a session must determine before creating any new document, to
prevent uncontrolled one-off Markdown file creation.

## Scope

Applies whenever a session considers creating a new file anywhere under
`docs/`, `.ai/`, `knowledge/`, or the repository root. Does not apply to
non-documentation artifacts (Skills, Workflows, schemas), which already
have their own creation rules in their owning specifications.

## Design

### Pre-creation checklist

Before creating a new document, determine, in order:

1. **Does this content already belong in an existing document?**
   Check [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)'s
   placement decision procedure first. Most content belongs somewhere that
   already exists.
2. **Should an existing document be extended instead?**
   If a document's Scope already covers this concern, extend it rather than
   fragmenting the concern across two files (see
   [Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md)'s
   merge threshold).
3. **What document class is this?**
   Per [Required Sections by Document Type](REQUIRED_SECTIONS_BY_DOCUMENT_TYPE.md).
4. **What is its authoritative status?**
   Normative, descriptive/synthesis, or a proposal — stated in the
   document's own opening per
   [Documentation & Writing Standards](DOCUMENTATION_AND_WRITING_STANDARDS.md).
5. **Who owns it?**
   Which role's Decision Right covers this document's content, per
   [Governance Model](GOVERNANCE_MODEL.md).
6. **What is its lifecycle?**
   Per the Document Status Model in
   [Markdown, Cross-Link & Status Standards](MARKDOWN_CROSSLINK_AND_STATUS_STANDARDS.md).
7. **Where is it indexed?**
   Every new document must be discoverable from exactly one index (its
   category's README, or `MASTER_OPERATOR.md`'s Table of Contents for
   `docs/operator/` specifically) — never left orphaned.
8. **What links back to it?**
   At minimum, its category's index; ideally the specific document(s) that
   motivated its creation.
9. **What validates it?**
   At minimum, `python scripts/validate_repository.py`'s link/anchor
   checks; a normative document additionally needs the review per
   [Documentation Review Workflow & Quality Gates](DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md).

### Specific rule for `docs/operator/*.md`

A new `docs/operator/*.md` chapter file MUST already appear as a row in
`MASTER_OPERATOR.md`'s Table of Contents (added in the same commit if not
already present from a prior Batch's planning) before or at the moment it
is created — no orphan chapters, per
[Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md).

### Specific rule for a new top-level documentation category

Creating a new peer of `docs/operator/` (a new top-level documentation
directory) is itself a structural documentation decision requiring the same
governance weight as any other — a Documentation Engineer call, and if it
introduces a new cross-cutting rule (not just a new location), an ADR,
matching the precedent ADR-0020 set for `docs/operator/` itself.

### When NOT to create a new document

- The content is a one-off, non-reusable detail with no promotion-threshold
  justification (see
  [Knowledge Classification, Lifecycle & Capture](KNOWLEDGE_CLASSIFICATION_AND_LIFECYCLE.md)) —
  a commit message or code comment is sufficient.
- The content genuinely fits an existing document's Scope, even if that
  document would grow somewhat longer as a result.
- The content is speculative ("we might need this later") with no current
  task motivating it — per Design Principle 2's "does not mean producing
  speculative documentation for work that has not been selected."

## Examples

This Batch itself illustrates the rule: every one of its ~30
`docs/operator/*.md` chapters already had a named target path in
`MASTER_OPERATOR.md`'s planned Table of Contents (from this Batch's own
planning, done before any chapter file was written) or is added to it in
the same consolidation pass that creates the file — no chapter exists
without a corresponding, discoverable Table of Contents row.

## References

- [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)
- [Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md)
- [Governance Model](GOVERNANCE_MODEL.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 4) |
