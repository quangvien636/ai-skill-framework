# Contract Validation Guide

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Explain how contributors and future tools apply schemas and interpret contract
validation without implying that a full validator already exists.

## Scope

This guide covers current schema review and the future validation flow. It does
not provide a production command or CLI.

## Definitions

- **Schema check:** validation of a normalized object against Draft 2020-12.
- **Conformance check:** schema, semantic, repository, and package validation.
- **Error:** issue that blocks activation.
- **Warning:** reviewable risk that does not automatically block validation.

## Design

### Current Sprint 7 Checks

Contributors must:

1. validate every `schemas/*.json` file as JSON;
2. verify local `$ref` targets and fragments;
3. compare schema fields with the owning Markdown specification and template;
4. validate schema examples against their schema when tooling is available;
5. review semantic rules not encoded in JSON Schema;
6. check links, paths, duplicate IDs, secrets, and Git diff.

PowerShell `ConvertFrom-Json` proves JSON syntax only; it is not a JSON Schema
validator. Until the validator is implemented, activation requires documented
manual semantic and repository review.

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
- [Schema Registry](../../schemas/README.md)
- [Validator Roadmap](../roadmaps/VALIDATOR_ROADMAP.md)
- [Version Specification](../specifications/VERSION_SPECIFICATION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established validation usage and review guidance |
