# Framework Naming Convention

Version: 1.0
Status: Active
Last updated: 2026-07-04

## Purpose

Define canonical names, IDs, paths, and filenames across the AI Skill Framework
while delegating Knowledge-specific syntax to its existing naming authority.

## Scope

This convention covers Skills, Workflows, Templates, Runtime components,
documentation, and ADRs. Knowledge category, domain, topic, document, and ID
syntax remains governed by the Knowledge Naming Convention.

## Definitions

- **Canonical name:** stable lowercase `kebab-case` token used in paths and IDs.
- **Artifact ID:** globally unique identity with a type prefix.
- **Display name:** human-readable title derived from or associated with a
  canonical name.
- **Reserved filename:** uppercase repository filename with framework meaning.

## Design

### General Rules

- Use English ASCII for canonical names, IDs, paths, and schema fields.
- Use lowercase `kebab-case` for artifact names and directory segments.
- Use `snake_case` for YAML field names.
- Use `PascalCase` only for future source-code types where the language expects it.
- Prefer precise nouns or verb-object phrases.
- Do not include vendor/model names, dates, versions, statuses, or generic suffixes
  such as `new`, `final`, `misc`, or `v2`.
- Keep IDs stable across path and display-name changes.

Canonical names MUST match:

```regex
^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$
```

### Artifact Rules

| Artifact | Name style | ID form | Canonical path |
| --- | --- | --- | --- |
| Skill | Verb-object describing one responsibility | `skill:<name>` | `skills/<name>/` |
| Workflow | Outcome or business-process phrase | `workflow:<name>` | `workflows/<name>/` |
| Template | Artifact or use-case noun phrase | `template:<name>` | `templates/<name>/` |
| Runtime component | Capability noun phrase | `runtime:<name>` | `runtime/<name>/` |
| Knowledge | Knowledge Naming Convention | `kb:<category>:<domain>:<topic>:<subject>` | `knowledge/<category>/<domain>/<topic>/` |
| ADR | Four-digit sequence plus descriptive slug | `adr:<number>` | `docs/adr/ADR-<number>-<slug>.md` |

Skill names SHOULD start with a verb: `summarize-document`, `review-code`. Workflow
names describe the composed outcome: `research-and-publish`, `review-pull-request`.
Do not append `-skill` or `-workflow`; the path and ID already provide type.

### Manifest and Package Filenames

- Skill manifest: `skill.yaml`
- Workflow manifest: `workflow.yaml`
- Human package guide: `README.md`
- Skill instructions: `instructions.md`

Examples and tests live in lowercase plural directories: `examples/`, `tests/`.
Machine-readable fixtures use lowercase `kebab-case` plus the appropriate
extension.

### Template Naming

Reusable executable templates live under `templates/<name>/` and use
`template:<name>`. Governance templates colocated with a subsystem may use the
existing reserved uppercase pattern, such as
`knowledge/_templates/KNOWLEDGE_TEMPLATE.md`.

Template names describe what they produce, not the tool that generates them.

### Knowledge Naming

Do not restate Knowledge syntax here. Category/domain/topic paths, document
filenames, immutable Knowledge IDs, and rename behavior are defined by
`docs/principles/KNOWLEDGE_NAMING_CONVENTION.md`.

### Runtime Naming

Runtime component names describe infrastructure capability rather than domain
work: `artifact-validator`, `dependency-resolver`, `workflow-executor`. Names that
perform domain work belong to Skills, not Runtime.

### Documentation Naming

- Repository governance and specification documents use uppercase
  `SCREAMING_SNAKE_CASE.md`.
- ADRs use `ADR-NNNN-lowercase-kebab-case.md`.
- Package-local human guides use `README.md`.
- Knowledge content documents follow the Knowledge Naming Convention.

Documentation titles use human-readable title case and do not need to mirror
filename capitalization.

### Rename and Collision Rules

- Search artifact IDs and canonical paths before naming.
- Two artifacts MUST NOT share an ID.
- A rename updates the canonical path and every repository reference in one
  coherent change.
- A rename preserves ID when responsibility and meaning remain the same.
- A materially new responsibility or meaning requires a new artifact and ID.
- Case-only names are collisions on all supported platforms.

## Examples

| Intent | Valid | Invalid |
| --- | --- | --- |
| Skill that checks facts | `skill:check-facts` | `skill:fact-check-skill-v2` |
| Workflow for research and writing | `workflow:research-and-write` | `workflow:Research_Write` |
| Runtime schema validation | `runtime:artifact-validator` | `runtime:writing-engine` |
| Specification document | `AI_SKILL_SPECIFICATION.md` | `ai-skill-spec-final.md` |
| ADR file | `ADR-0002-artifact-manifest-format.md` | `adr2_manifest.md` |

## Validation

Validators MUST check regex conformance, type prefixes, canonical path agreement,
reserved filenames, case-insensitive collisions, and immutable IDs. Validation
errors identify the invalid value and expected form.

## References

- [Metadata Specification](../specifications/METADATA_SPECIFICATION.md)
- [AI Skill Specification](../specifications/AI_SKILL_SPECIFICATION.md)
- [Workflow Specification](../specifications/WORKFLOW_SPECIFICATION.md)
- [Knowledge Naming Convention](KNOWLEDGE_NAMING_CONVENTION.md)
- [Version Specification](../specifications/VERSION_SPECIFICATION.md)
- [Design Principles](DESIGN_PRINCIPLES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Initial placeholder |
| 1.0 | 2026-07-04 | Established framework-wide naming contract |
