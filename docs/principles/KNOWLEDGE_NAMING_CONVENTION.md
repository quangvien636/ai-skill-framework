# Knowledge Naming Convention

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define deterministic names and identifiers for Knowledge Base artifacts. The
taxonomy and its meanings are defined by `knowledge/KNOWLEDGE_CATEGORIES.md`;
this document defines syntax only.

## General Rules

- Use English names for repository paths, identifiers, and metadata values.
- Use lowercase ASCII `kebab-case`.
- Use nouns or noun phrases that describe the knowledge subject.
- Use singular names unless the subject is conventionally plural.
- Avoid spaces, underscores, dates, version numbers, model names, and redundant
  words such as `knowledge`, `document`, `notes`, or `misc`.
- Keep names stable. A title change does not require an ID or path change unless
  the subject itself changes.

Valid: `software-engineering`, `postgresql`, `query-optimization`
Invalid: `Software Engineering`, `postgres_notes`, `misc-v2`, `gpt-guidance`

## Directory Names

Category, domain, and topic directories use:

```text
<category>/<domain>/<topic>/
```

Each segment must match:

```regex
^[a-z0-9]+(?:-[a-z0-9]+)*$
```

Names should be concise but unambiguous within their parent. Do not repeat the
parent name:

```text
technical/software-engineering/testing/
```

not:

```text
technical/technical-software-engineering/software-engineering-testing/
```

## Knowledge Document Filenames

Knowledge documents use:

```text
<subject>.md
```

The subject is lowercase `kebab-case` and describes one primary knowledge unit.
Do not include the category, domain, topic, lifecycle state, or version in the
filename.

Example:

```text
knowledge/technical/databases/query-optimization/index-selection.md
```

Reserved uppercase filenames are limited to repository navigation and governance
artifacts such as `README.md`, `KNOWLEDGE_INDEX.md`, and
`KNOWLEDGE_CATEGORIES.md`.

## Knowledge IDs

Every knowledge document has a globally unique, immutable ID:

```text
kb:<category>:<domain>:<topic>:<subject>
```

Each segment follows the same lowercase `kebab-case` rule. For example:

```text
kb:technical:databases:query-optimization:index-selection
```

The ID mirrors the canonical path at creation time. Moving or renaming a document
does not silently change an existing ID. If the knowledge subject changes enough
to require a new identity, create a new document and deprecate the old one.

## Titles

Document titles use human-readable title case and do not include the knowledge ID:

```markdown
# Index Selection
```

Prefer a precise subject title over a generic activity such as "Best Practices"
or "Guidelines".

## Collision and Rename Rules

- Search the Knowledge Index before assigning a name or ID.
- No two documents may share a knowledge ID.
- No two active documents may own the same primary concept.
- A path rename must update the Knowledge Index and all repository references in
  the same change.
- A taxonomy move must preserve the existing ID and record the move in revision
  history.
- A replacement document receives a new ID; the deprecated document links to it.

## Examples

| Element | Valid example |
| --- | --- |
| Category | `technical` |
| Domain | `databases` |
| Topic | `query-optimization` |
| Filename | `index-selection.md` |
| Knowledge ID | `kb:technical:databases:query-optimization:index-selection` |
| Title | `Index Selection` |

## Review Checklist

- Do all path segments and ID segments use lowercase `kebab-case`?
- Does the filename describe exactly one primary subject?
- Is the ID unique in `KNOWLEDGE_INDEX.md`?
- Does the path avoid redundant parent names?
- Are names free of implementation-, model-, and version-specific details?
- Were all references updated for a rename or move?

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established Knowledge Base naming rules |
