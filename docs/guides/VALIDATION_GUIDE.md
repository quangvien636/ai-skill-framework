# Contract Validation Guide

Version: 0.3
Status: Active
Last updated: 2026-07-04

## Purpose

Explain how contributors and tools apply schemas and interpret contract
validation, including the Sprint 8 fixture-conformance prototype, without
implying that a full validator, CLI, or Runtime already exists.

## Scope

This guide covers current schema review, the fixture-conformance prototype,
and the future validation flow. It does not provide a production CLI.

## Definitions

- **Schema check:** validation of a normalized object against Draft 2020-12.
- **Conformance check:** schema, semantic, repository, and package validation.
- **Error:** issue that blocks activation.
- **Warning:** reviewable risk that does not automatically block validation.

## Design

### Sprint 8 Fixture-Conformance Prototype

`scripts/validate_contracts.py` (invoked directly, or via
`scripts/validate-contracts.ps1` on Windows) checks that every schema in
`schemas/` is a valid Draft 2020-12 schema and that the fixtures declared in
`tests/fixtures/contracts/cases.json` validate as expected:

```text
pip install -r requirements-validator.txt
python scripts/validate_contracts.py
```

Each fixture case names a fixture file under `tests/fixtures/contracts/<type>/`,
the schema to check it against, and the expected outcome (`valid` or
`invalid`). The script resolves local `$ref` values through a schema
registry, reports the first diagnostic for each case, and exits nonzero if
any case does not match its expected outcome. It performs no network access
and never rewrites a fixture or schema.

This prototype only proves schema-level (structural) conformance for the
fixtures it is told about. It does not walk `skills/` or `workflows/`, and it
implements none of the semantic or repository-integrity rules in the
[Contract Validation Architecture](../architecture/CONTRACT_VALIDATION_ARCHITECTURE.md).
See ADR-0002 for the scope and rationale of this increment.

### Current Manual Checks

Contributors must still:

1. compare schema fields with the owning Markdown specification and template;
2. review semantic rules not yet encoded in JSON Schema or the prototype;
3. check links, paths, duplicate IDs, secrets, and Git diff;
4. run the fixture-conformance prototype above and add fixtures for new or
   changed schemas.

### Future Validator Flow

A future command may accept an artifact path, infer its type, parse and normalize
it, load only repository schemas, run all validation layers, and emit human or
JSON diagnostics. It must return nonzero for errors and never rewrite source.

### Schema Selection

| Artifact | Source | Schema |
| --- | --- | --- |
| Skill | `skills/<name>/skill.yaml` | `schemas/skill.schema.json` |
| Workflow | `workflows/<name>/workflow.yaml` | `schemas/workflow.schema.json` |
| Knowledge | canonical Markdown normalized in memory | `schemas/knowledge.schema.json` |
| Evaluation | embedded object | `schemas/evaluation.schema.json` |
| Reflection | embedded object | `schemas/reflection.schema.json` |

Metadata and Version schemas are shared `$defs`, not standalone repository
artifacts.

### Reading Diagnostics

Fix errors at their source; do not edit generated normalized models. A schema
error identifies an instance path and schema rule. A semantic error cites the
Markdown specification. A repository error cites both the referencing and target
artifact where applicable.

## Examples

`version: "1.0"` fails structural validation because artifact versions require
full SemVer. Evaluation weights `0.7` and `0.4` pass individual numeric bounds but
fail semantic validation because their sum is not `1.0`.

## References

- [Contract Validation Architecture](../architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [IR Architecture](../architecture/IR_ARCHITECTURE.md)
- [Schema Registry](../../schemas/README.md)
- [Validator Roadmap](../roadmaps/VALIDATOR_ROADMAP.md)
- [Version Specification](../specifications/VERSION_SPECIFICATION.md)
- ADR-0002: Prototype Contract Validator
- ADR-0005: Markdown Authoring Format, IR Internal Contract

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established validation usage and review guidance |
| 0.2 | 2026-07-04 | Documented the Sprint 8 fixture-conformance prototype |
| 0.3 | 2026-07-04 | Cross-linked the IR Architecture (normalized object = IR, per ADR-0005) |
