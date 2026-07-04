# Knowledge Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define how reusable knowledge is organized, governed, discovered, and consumed by
the AI Skill Framework without embedding that knowledge in prompts or Skills.

## Scope

This architecture covers durable, reusable knowledge stored under `knowledge/`.
It does not define Skill behavior, workflow order, runtime retrieval
implementation, or transient task context.

## Architectural Role

The Knowledge Base is a repository-managed content layer:

```text
Repository source of truth
  -> Knowledge Index
  -> Category
  -> Domain
  -> Topic
  -> Knowledge document
  -> Skill or evaluator consumes selected knowledge
```

The Master Skill may coordinate knowledge selection through a workflow or future
retrieval component, but it does not contain or interpret domain knowledge.
Skills consume only the knowledge relevant to their single responsibility.

## Scalable Hierarchy

```text
knowledge/
  README.md
  KNOWLEDGE_CATEGORIES.md
  KNOWLEDGE_INDEX.md
  _templates/
    KNOWLEDGE_TEMPLATE.md
  <category>/
    <domain>/
      <topic>/
        <knowledge-document>.md
```

The hierarchy has four semantic levels:

1. **Category** — a stable top-level family of knowledge.
2. **Domain** — a coherent discipline or subject area inside a category.
3. **Topic** — a focused body of related knowledge inside a domain.
4. **Knowledge document** — one reusable knowledge unit with one primary subject.

Categories are deliberately broad and stable. Domains and topics provide growth
without creating an unbounded flat directory. Knowledge documents are the units
that contributors review, version, index, and consumers retrieve.

## Component Responsibilities

| Artifact | Responsibility | Authoritative for |
| --- | --- | --- |
| `KNOWLEDGE_CATEGORIES.md` | Defines and governs taxonomy | Category identifiers and boundaries |
| `KNOWLEDGE_INDEX.md` | Registers discoverable knowledge documents | Document ID-to-path mapping and status |
| `KNOWLEDGE_TEMPLATE.md` | Defines required document fields | Knowledge document schema |
| `KNOWLEDGE_NAMING_CONVENTION.md` | Defines names and identifiers | Path, filename, and ID syntax |
| Individual knowledge documents | Hold reusable subject matter | Content for one primary subject |

These responsibilities must not be duplicated. For example, the index references
a category but does not redefine its boundary.

## Category Standard

A category is permitted only when it:

- represents a broad knowledge family reusable across multiple Skills or
  workflows;
- has a unique lowercase `kebab-case` identifier;
- has a clear inclusion boundary and exclusion guidance;
- does not overlap an existing category;
- is registered in `knowledge/KNOWLEDGE_CATEGORIES.md` before use.

Category changes require architecture review because they affect repository
navigation and long-term discoverability.

## Domain Standard

A domain groups related topics within exactly one category. It must be cohesive,
use lowercase `kebab-case`, and remain understandable without relying on a
specific Skill or workflow name.

If a domain appears relevant to multiple categories, place it under the category
that owns its primary subject and use index metadata to make consumers
discoverable. Do not duplicate its documents.

## Topic Standard

A topic narrows one domain into a retrieval-friendly subject area. A topic must:

- have one clear subject and a short `kebab-case` name;
- belong to exactly one domain;
- contain related documents rather than act as a miscellaneous bucket;
- be split when its documents no longer share a coherent subject.

Topic directories are created when the first approved knowledge document for
that topic is added.

## Knowledge Document Standard

Each document:

- addresses one primary reusable subject;
- is created from the canonical Knowledge Template;
- declares a globally unique knowledge ID and its taxonomy;
- separates normative guidance from examples and references;
- cites sources or records provenance when claims depend on external material;
- has an explicit lifecycle status;
- appears exactly once in the Knowledge Index.

Knowledge documents must not contain workflow orchestration or Skill-specific
execution logic. A Skill may reference knowledge; it must not own a second copy.

## Metadata Contract

Every knowledge document uses the following fields:

| Field | Required | Purpose |
| --- | --- | --- |
| Knowledge ID | Yes | Stable repository-wide identity |
| Title | Yes | Human-readable subject |
| Status | Yes | Lifecycle state |
| Category | Yes | Registered category ID |
| Domain | Yes | Parent domain ID |
| Topic | Yes | Parent topic ID |
| Version | Yes | Content version |
| Last updated | Yes | Maintenance date |
| Summary | Yes | Retrieval-oriented description |
| Applies to | Yes | Intended consumers or use cases |
| Sources | When applicable | Provenance and verification |

The template is the canonical definition of field placement and document
sections. The naming convention is canonical for field syntax.

## Lifecycle

Knowledge moves through these states:

```text
Draft -> Active -> Deprecated -> Archived
```

- **Draft:** incomplete or awaiting review; consumers must not treat it as
  authoritative.
- **Active:** reviewed and available for use.
- **Deprecated:** still discoverable but replaced or scheduled for removal; it
  must identify its replacement when one exists.
- **Archived:** retained for history and excluded from normal consumption.

Promotion to Active requires taxonomy validation, template compliance, source
review when applicable, index registration, and duplicate-content review.

## Discovery and Consumption

`knowledge/KNOWLEDGE_INDEX.md` is the human- and machine-readable discovery
entrypoint. Consumers resolve an ID to one canonical path, inspect its status and
summary, then load the document only when relevant.

The index stores metadata, not document content. Runtime retrieval, ranking,
caching, and context-window strategies are future implementation concerns and
must preserve this repository model.

## Change Workflow

1. Search the Knowledge Index and repository for existing coverage.
2. Choose an existing category, domain, and topic.
3. Propose a category change only if existing boundaries cannot represent the
   subject.
4. Create the document from the Knowledge Template.
5. Review scope, sources, naming, and duplication.
6. Register or update the document in the Knowledge Index.
7. Update affected documentation in the same commit.

## Quality and Validation Rules

A knowledge change is acceptable when:

- its taxonomy and names comply with the documented standards;
- one canonical document owns each concept;
- links and index paths resolve;
- facts are distinguishable from recommendations and examples;
- external claims have adequate provenance;
- stale or conflicting guidance is removed or explicitly deprecated;
- no prompt or Skill duplicates the new reusable content.

## Related Documents

- `docs/architecture/SYSTEM_ARCHITECTURE.md`
- `docs/principles/DESIGN_PRINCIPLES.md`
- `docs/principles/KNOWLEDGE_NAMING_CONVENTION.md`
- `knowledge/README.md`
- `knowledge/KNOWLEDGE_CATEGORIES.md`
- `knowledge/KNOWLEDGE_INDEX.md`
- `knowledge/_templates/KNOWLEDGE_TEMPLATE.md`

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Knowledge Base architecture |
