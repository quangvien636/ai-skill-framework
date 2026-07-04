# Knowledge Dependency Specification

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define how Skills, Workflows, evaluators, and Runtime consumers declare, validate,
resolve, and reuse Knowledge Base dependencies.

## Scope

This specification governs references to existing knowledge. The Knowledge
Architecture remains authoritative for category boundaries, hierarchy, document
content, lifecycle, indexing, and Knowledge naming.

## Definitions

- **Knowledge dependency:** a declared requirement for one canonical Knowledge
  document.
- **Knowledge reference:** immutable Knowledge ID plus a compatible version range.
- **Resolved knowledge:** one exact active document version selected from a
  valid reference.
- **Required dependency:** execution cannot proceed correctly without it.
- **Optional dependency:** improves execution but has defined behavior when absent.

## Design

### Knowledge References

Each reference MUST contain:

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `id` | string | Yes | Canonical ID from the Knowledge Index |
| `version` | string | Yes | Exact Semantic Version or comparator range |
| `required` | boolean | Yes | Controls missing-dependency behavior |
| `purpose` | string | Yes | Why this consumer needs the knowledge |
| `sections` | string array | No | Named sections to retrieve; omission means whole document |

Category, domain, and topic MUST NOT be copied into a dependency declaration;
they are resolved through the Knowledge Index. This prevents taxonomy metadata
from drifting between consumers and the canonical document.

### Categories

References may target any category registered in
`knowledge/KNOWLEDGE_CATEGORIES.md`. Consumers select knowledge by documented
purpose and ID, not merely by category. A category is a discovery boundary, not
permission to load every document inside it.

### Resolution

Resolution MUST:

1. locate the ID in `knowledge/KNOWLEDGE_INDEX.md`;
2. reject missing, duplicate, or archived entries;
3. confirm the indexed path exists and document metadata matches the index;
4. select one version satisfying the declared range;
5. verify lifecycle and source-integrity requirements;
6. record the exact ID, version, and repository revision used.

A required dependency that cannot resolve is a validation error before execution.
An unresolved optional dependency produces a warning and uses explicitly defined
fallback behavior; it MUST NOT be silently ignored.

### Knowledge Version

Knowledge document versions follow the Version Specification. A content change
that alters meaning or guidance increments the appropriate artifact version.
Consumers declare compatible ranges, while execution records exact resolutions.

### Validation

Static validation checks syntax, index membership, lifecycle, version
compatibility, unique references, path integrity, and section existence. Runtime
validation confirms that the resolved content was loaded and made available only
to the consuming responsibility.

### Reuse Rules

- Reference one canonical document; do not copy knowledge into manifests,
  prompts, Skills, or Workflows.
- Reuse the same ID across consumers when they need the same concept.
- Load only the smallest relevant document or declared sections.
- Do not mutate canonical knowledge during execution.
- Put consumer-specific instructions in the consumer, not in Knowledge.
- Propose a new Knowledge document only when no existing document owns the
  concept.

## Examples

```yaml
dependencies:
  knowledge:
    - id: "kb:technical:databases:query-optimization:index-selection"
      version: ">=1.0.0 <2.0.0"
      required: true
      purpose: "Apply canonical index-selection guidance."
      sections:
        - "Guidance"
        - "Decision Rules"
```

An invalid declaration copies `category`, omits `purpose`, or uses `latest` as a
version. Those fields either duplicate canonical metadata or prevent reproducible
resolution.

## Failure Handling

Required resolution failure stops validation and identifies the consumer, ID,
range, and reason. Optional failure emits a structured warning and activates only
the documented fallback. Consumers MUST NOT substitute a similarly named
document without an explicit reference.

## References

- [Knowledge Architecture](../architecture/KNOWLEDGE_ARCHITECTURE.md)
- [Knowledge Categories](../../knowledge/KNOWLEDGE_CATEGORIES.md)
- [Knowledge Index](../../knowledge/KNOWLEDGE_INDEX.md)
- [Knowledge Naming Convention](../principles/KNOWLEDGE_NAMING_CONVENTION.md)
- [Version Specification](VERSION_SPECIFICATION.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established Knowledge dependency contracts |
