# Knowledge Index

Version: 0.2
Status: Active
Last updated: 2026-07-05

## Purpose

Provide the canonical discovery registry for Knowledge Base documents. Each
knowledge ID maps to exactly one repository path.

## How to Use This Index

- Search by ID, title, category, domain, topic, status, or summary.
- Load only documents relevant to the current Skill responsibility.
- Treat only `Active` entries as approved for normal consumption.
- Follow a deprecated entry's replacement instead of selecting it for new work.

## Registry

| Knowledge ID | Title | Category | Domain | Topic | Status | Path | Summary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `kb:creative:content:conversion:call-to-action-patterns` | Call-to-Action Patterns | creative | content | conversion | Active | `knowledge/creative/content/conversion/call-to-action-patterns.md` | Proportional patterns for choosing one clear audience action. |
| `kb:creative:content:formats:content-structures` | Content Structures | creative | content | formats | Active | `knowledge/creative/content/formats/content-structures.md` | Required structure for every deliverable supported by Content Creation v1. |
| `kb:creative:content:hooks:hook-formulas` | Hook Formulas | creative | content | hooks | Active | `knowledge/creative/content/hooks/hook-formulas.md` | Honest opening patterns that establish relevance and a fulfilled promise. |
| `kb:creative:content:platforms:publishing-constraints` | Publishing Constraints | creative | content | platforms | Active | `knowledge/creative/content/platforms/publishing-constraints.md` | Stable packaging guidance for generic, Instagram, LinkedIn, TikTok, and YouTube content. |
| `kb:creative:content:style:tone-guidelines` | Tone Guidelines | creative | content | style | Active | `knowledge/creative/content/style/tone-guidelines.md` | Observable tone and style choices for audience-appropriate content. |

## Registration Rules

1. Create the document from `_templates/KNOWLEDGE_TEMPLATE.md`.
2. Validate taxonomy against `KNOWLEDGE_CATEGORIES.md`.
3. Validate names and ID against the Knowledge Naming Convention.
4. Add exactly one row, sorted lexicographically by Knowledge ID.
5. Use a repository-relative path beginning with `knowledge/`.
6. Keep the summary concise and useful for retrieval.
7. Update status, path, or summary when the canonical document changes.

The index must not contain aliases or duplicate rows. Cross-references belong in
knowledge documents; replacements are declared in the deprecated document.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the empty canonical registry |
| 0.2 | 2026-07-05 | Registered five Content Creation v1 Knowledge documents. |
