# Knowledge Index

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Provide the canonical discovery registry for Knowledge Base documents. Each
knowledge ID maps to exactly one repository path.

## How to Use This Index

- Search by ID, title, category, domain, topic, status, or summary.
- Load only documents relevant to the current Skill responsibility.
- Treat only `Active` entries as approved for normal consumption.
- Follow a deprecated entry's replacement instead of selecting it for new work.

## Registry

No knowledge documents are registered yet. Governance files and templates are
not knowledge entries.

| Knowledge ID | Title | Category | Domain | Topic | Status | Path | Summary |
| --- | --- | --- | --- | --- | --- | --- | --- |

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
