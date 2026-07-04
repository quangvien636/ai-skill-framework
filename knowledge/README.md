# Knowledge Base

The Knowledge Base contains reusable, repository-managed knowledge consumed by
Skills and quality components. It is separate from prompts, Skill logic, and
workflow orchestration.

## Start Here

1. Read the
   [Knowledge Architecture](../docs/architecture/KNOWLEDGE_ARCHITECTURE.md).
2. Select a registered category from
   [Knowledge Categories](KNOWLEDGE_CATEGORIES.md).
3. Follow the
   [Knowledge Naming Convention](../docs/principles/KNOWLEDGE_NAMING_CONVENTION.md).
4. Search the [Knowledge Index](KNOWLEDGE_INDEX.md) for existing coverage.
5. Create new content from the
   [Knowledge Template](_templates/KNOWLEDGE_TEMPLATE.md).

## Structure

```text
knowledge/
  README.md
  KNOWLEDGE_CATEGORIES.md
  KNOWLEDGE_INDEX.md
  _templates/
    KNOWLEDGE_TEMPLATE.md
  <category>/<domain>/<topic>/<knowledge-document>.md
```

Governance files explain or index the Knowledge Base; they are not knowledge
documents and are not registered as knowledge entries.

## Contribution Rule

Search before creating. Extend the canonical document when the concept already
exists. Create a new document only for a distinct reusable subject, and add it to
the Knowledge Index in the same change.
