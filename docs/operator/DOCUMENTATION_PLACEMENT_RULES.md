# Documentation Placement Rules

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Give the concrete, checkable version of `MASTER_OPERATOR.md`'s
Documentation Architecture: exactly which document category a given piece
of content belongs in, and when content should be embedded, summarized,
referenced, extracted, merged, deprecated, or archived.

## Scope

Applies to every documentation decision a session makes, including its own
future edits to `docs/operator/*.md`. Does not restate
`MASTER_OPERATOR.md`'s Documentation Architecture section — extends it with
a decision procedure and placement table.

## Design

### Placement decision procedure

For any new piece of content, in order:

1. **Does it record a decision with lasting architectural consequence?**
   Yes -> an ADR (`docs/adr/`), per
   [ADR Governance & Decision Rules](ADR_GOVERNANCE.md).
2. **Does it describe how an existing component works?**
   Yes -> the relevant `docs/architecture/*.md` file. Create a new one only
   if no existing file's scope covers it.
3. **Does it define a contract a producer/consumer must follow?**
   Yes -> `docs/specifications/` plus, if machine-checkable, `schemas/`.
4. **Does it define a cross-cutting design/naming rule?**
   Yes -> `docs/principles/`.
5. **Is it actionable current status (done/in-progress/blocked)?**
   Yes -> `PROJECT_TRACKER.md`. Never duplicate this into a narrative
   document.
6. **Is it durable narrative context (why the project is where it is)?**
   Yes -> `PROJECT_CONTEXT.md`, in its Current Focus / Revision History.
7. **Is it a step-by-step procedure for one recurring operational task?**
   Yes -> `docs/guides/` (task-specific) or a `docs/operator/*.md` chapter
   (cross-cutting session process). Use the guide if the task is narrow and
   domain-specific (e.g., running the validator); use an operator chapter if
   the task is about how *any* session operates (e.g., how to recover from
   an interrupted rebase).
8. **Is it reusable domain knowledge a Skill consumes?**
   Yes -> `knowledge/`, per `docs/architecture/KNOWLEDGE_ARCHITECTURE.md`.
9. **Is it a synthesis across several of the above, aimed at helping a
   session use them together?**
   Yes -> a `docs/operator/*.md` chapter, referencing (never duplicating)
   the sources it synthesizes.
10. **None of the above fits.**
    This is itself a signal the content may not need to exist yet — see
    [Future Document Creation Rules](DOCUMENT_CREATION_RULES.md) (planned)
    before creating a new document class.

### Embed / summarize / reference / extract / merge / deprecate / archive

| Action | When to use it | Example in this repository |
| --- | --- | --- |
| **Embed** | The content is short, stable, and has no other legitimate home (e.g., this manual's own Vision/Mission) | `MASTER_OPERATOR.md`'s spine sections |
| **Summarize** | A longer authoritative procedure exists elsewhere and a shorter derived version helps a specific reader, provided the summary links back and never contradicts the source | A `docs/operator/*.md` chapter's one-paragraph restatement of an ADR's Decision, always followed by a link to the ADR itself |
| **Reference** | The content already has a complete, correct home; no restatement is needed | `MASTER_OPERATOR.md`'s Table of Contents linking to chapters instead of inlining them |
| **Extract** | Content has outgrown the document it lives in and deserves its own file | If `PROJECT_TRACKER.md`'s per-sprint sections ever grow unmanageable, extracting older sprints to a dedicated archive file (not yet needed at 44 sprints; see [Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md) for the threshold) |
| **Merge** | Two documents cover the same concern with no meaningful distinction | Not currently needed anywhere in this repository — the existing document set was found well-factored during the Prompt 01 audit; if a future addition creates real overlap, merge then |
| **Deprecate** | A document's guidance is superseded but the document itself, or its history, still has value (e.g., as evidence of a prior approach) | Mark `Status: Deprecated` in the document's own header, add a note pointing to its replacement; do not delete |
| **Archive** | A deprecated document no longer needs to be discoverable in normal navigation but must not be destroyed | Move to an archive location (not yet created — see [Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md)) with inbound links updated to point at the archive note, not left dangling |

### The "never link to an unwritten chapter" rule, generalized

Any cross-reference (Markdown link syntax) from one document to another
MUST target a file that exists at commit time. A reference to planned-but-
unwritten content MUST be plain text naming the target path, not a link —
this is mechanically enforced by `python scripts/validate_repository.py`
(`ASF-REPOSITORY-006`) for every Markdown file in the repository, not just
`docs/operator/`.

## Examples

A session discovers a genuinely new, reusable fact about how the semantic
validator resolves Runtime Contract fallback chains, learned while fixing a
bug. Applying the decision procedure: it is not a new architectural
decision (step 1, no); it describes how an existing component
(`asf_runtime.dependency_resolver`) works (step 2, yes) -> it belongs in
`docs/architecture/RUNTIME_CONTRACT_ARCHITECTURE.md` or
`docs/adr/ADR-0015-...md`'s own scope, not in a new `docs/operator/*.md`
chapter and not left undocumented in a commit message alone.

## References

- [MASTER_OPERATOR.md](../../MASTER_OPERATOR.md) — Documentation Strategy
  and Documentation Architecture
- [Repository Architecture Map](REPOSITORY_ARCHITECTURE_MAP.md)
- [Knowledge Classification, Lifecycle & Capture](KNOWLEDGE_CLASSIFICATION_AND_LIFECYCLE.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 2) |
