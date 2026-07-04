# Machine-Readable Schemas

The canonical JSON Schema Draft 2020-12 contracts for framework artifacts:

| Schema | Validates |
| --- | --- |
| `metadata.schema.json` | Shared artifact metadata definitions |
| `version.schema.json` | Semantic versions and dependency ranges |
| `evaluation.schema.json` | Evaluation declarations |
| `reflection.schema.json` | Reflection declarations |
| `skill.schema.json` | Parsed `skill.yaml` manifests |
| `workflow.schema.json` | Parsed `workflow.yaml` manifests |
| `knowledge.schema.json` | Normalized model extracted from Knowledge Markdown |

Schemas are model-neutral and tool-neutral. Relative `$ref` values assume all
schema files remain together. JSON Schema handles structural validation; semantic
and repository-integrity rules are defined by the
[Contract Validation Architecture](../docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md).
