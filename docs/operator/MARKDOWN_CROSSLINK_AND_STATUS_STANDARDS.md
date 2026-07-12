# Markdown, Cross-Link, and Status Standards

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define Markdown formatting conventions, cross-link rules, and the document
status model, following this repository's existing tooling rather than
inventing incompatible requirements.

## Scope

Applies to every Markdown file. Grounded in what
`scripts/asf_validator/content_integrity.py` actually checks (verified this
session), not invented conventions.

## Design

### Markdown standards (as this repository's tooling actually enforces or expects)

| Element | Convention | Why |
| --- | --- | --- |
| Heading hierarchy | `#` for title, `##` for top-level sections, `###` for subsections; never skip a level | Matches every existing document in `docs/` |
| Headings must be unique within a file | No two headings (at any level) produce the same GitHub-style slug | `ASF-REPOSITORY-*` duplicate-anchor check fails otherwise (verified: `_anchors()` in `content_integrity.py` flags any repeated slug) |
| Lists | `-` for unordered, `1.` for ordered; consistent within one list | Readability |
| Tables | Preferred over long prose lists for enumerable, multi-attribute content | This Batch's own consistent choice, matching the "no shallow documentation... prefer decision tables" instruction |
| Code fences | Triple backtick with a language hint (` ```text `, ` ```bash `, ` ```python `) for anything meant to be copy-pasted or read as literal syntax | Distinguishes literal commands from prose |
| Command blocks | The exact runnable command, no shell prompt prefix (`$`) unless showing expected output alongside it | Matches `README.md`'s existing style |
| Diagrams | Plain `text` fenced ASCII diagrams (arrows, boxes) as already used throughout `PROJECT_CONTEXT.md`, `docs/architecture/`, and this Batch's own lifecycle diagrams — not Mermaid, since no renderer/tooling in this repository currently processes Mermaid | Consistency with verified existing practice; see [Diagram Standards](#diagram-standards-summary) below |
| Anchors | Rely on GitHub-style auto-slugging from headings; explicit `<a name="...">` anchors only when a heading's auto-slug is insufficient (rare; none used in this Batch) | Matches `content_integrity.py`'s `_anchors()` behavior exactly |
| Relative links | Markdown link syntax with a relative path and optional `#anchor` fragment, resolved from the linking file's own directory | Matches `_validate_links()`'s exact resolution behavior (`source.parent / path_text`) |
| Line length | No hard limit enforced by tooling; prefer natural paragraph wrapping over forced line breaks | No validator checks this; do not invent a constraint tooling does not enforce |
| Status banners | The existing `Version: / Status: / Last updated:` header block, not a separate banner element | Matches `docs/_templates/DOCUMENTATION_TEMPLATE.md` |
| Blockquotes | Not currently used anywhere in this repository's documentation; avoid introducing them without a specific reason, to keep formatting consistent | Verified absence in existing docs |
| Checklists | `- [ ]` / `- [x]` GitHub task-list syntax, used for genuinely sequential completion tracking (e.g., a Session Completion Checklist), not for arbitrary bullet lists | Matches the semantic meaning of a checklist |

### Cross-link standards

1. **Always relative**, never absolute filesystem paths or `https://github.com/...` URLs for in-repository content.
2. **A link's target MUST exist at commit time.** A reference to planned
   content is plain text, never a Markdown link — see
   [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)'s
   generalized rule.
3. **Authoritative backlinks:** a summary document links to its source; the
   source does not need to link back to every summary that cites it (that
   would create unbounded backlink maintenance) — but a source *should*
   link forward to `MASTER_OPERATOR.md` or the relevant `docs/operator/`
   chapter when doing so meaningfully helps navigation (as this Batch did
   for `README.md`, `PROJECT_CONTEXT.md`, `.ai/README.md` in Prompt 01).
4. **Avoid circular navigation without hierarchy:** two chapters may link
   to each other only when they are genuinely peers on the same question
   (e.g., [Governance Model](GOVERNANCE_MODEL.md) and
   [Authority Levels](AUTHORITY_LEVELS.md) reference each other because
   each is incomplete without the other) — a chapter should not link back
   to `MASTER_OPERATOR.md`'s Table of Contents merely for navigation padding.
5. **Links from summaries to source documents:** every synthesis chapter's
   References section links every document it summarizes.
6. **Links from ADRs to implementation and validation:** an ADR's Related
   Documents section links forward once implementation exists; it is not
   retroactively required to update every past ADR, only good practice
   going forward.
7. **Links from tracker items to evidence:** `PROJECT_TRACKER.md`'s
   existing "Evidence / Output" column convention already does this; no new
   rule needed.
8. **Handling moved or deprecated documents:** update every inbound link in
   the same change that moves or deprecates a file (see
   [Deprecation, Archival & Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md)).
9. **Link validation:** `python scripts/validate_repository.py` checks
   every relative link and anchor in every `*.md` file in the repository
   (excluding `.git`, `.agents`, `.codex`) — run it before every commit
   touching Markdown.

### Document status model

| Status | Meaning | Authority | Valid transitions |
| --- | --- | --- | --- |
| Draft | Being written; not yet reviewed or relied upon | None yet | -> Active, or discarded |
| Proposed | Complete and committed, awaiting acceptance (ADRs specifically) | Drafting role | -> Accepted, or revised and re-proposed |
| Active | Current, authoritative, in force | Its owning role | -> Deprecated, or (ADRs) -> Superseded |
| Accepted | An ADR's binding status | Human maintainer | -> Superseded by ADR-<NNNN> |
| Superseded | An ADR replaced by a newer one | N/A (historical) | Terminal |
| Deprecated | Guidance replaced but document retained for reference | Its owning role | -> Archived |
| Archived | Removed from normal navigation, retained for history | Its owning role | Terminal |
| Historical | A report/record of a past event, never meant to change | N/A | Terminal |
| Rejected | A proposal (e.g., an ADR candidate) considered and declined | Human maintainer | Terminal, or superseded by a differently-framed new proposal |

Not every document type uses every status — an ADR uses
Proposed/Accepted/Superseded (per `ADR_TEMPLATE.md`'s own allowed values,
mechanically checked by `ASF-REPOSITORY-014`); a `docs/operator/*.md`
chapter uses Draft/Active/Deprecated/Archived; a report uses Historical
from the moment it is committed. Do not force a status from one type's set
onto a document of another type.

### Diagram Standards (summary)

Diagrams add value only when they represent a genuine flow, hierarchy, or
state machine more clearly than a table would — this Batch's lifecycle
state machine ([Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md))
is the clearest example: sequence and looping are easier to read as a
`text`-fenced diagram than as a table. A diagram MUST match the written
rules exactly (no transition in the diagram that the accompanying table
does not also define), MUST label every transition, and MUST be updated in
the same change as any behavior change it depicts. Prefer the plain-text
arrow-diagram style already used throughout this repository over
introducing a new diagramming syntax with no existing renderer.

## Examples

This document's own Markdown standards table is itself an example of
preferring a table to enumerable prose, per the standards it defines.

## References

- `scripts/asf_validator/content_integrity.py` (verified source of the
  mechanical link/anchor/ADR-status rules cited above)
- [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)
- `docs/_templates/DOCUMENTATION_TEMPLATE.md`

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 4) |
