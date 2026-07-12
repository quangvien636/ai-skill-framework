# Contract Validation Guide

Version: 0.8
Status: Active
Last updated: 2026-07-12

## Purpose

Explain how contributors and tools apply schemas, interpret contract
validation, and consume diagnostics through the offline ASF CLI.

## Scope

This guide covers current schema review, the fixture-conformance prototype,
the integrated repository validator, and the compile-only CLI.

## Integrated CLI

`python scripts/asf.py validate` runs structural loading, dependency/version
graph validation, semantic validation, and repository integrity checks through
the existing reusable services. `--format json` emits a `report_version: "1.0"`
report with the shared diagnostic fields: code, severity, artifact, location,
message, rule reference, and suggestion.

Exit codes follow the CLI architecture: `0` success, `1` validation failure,
`2` invalid command input, and `4` unresolved artifacts. The CLI never executes
a graph or contacts an external service.

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
fixtures it is told about. It does not walk `skills/` or `workflows/`. See
ADR-0002 for the scope and rationale of this increment.

### IR, Graph, and Semantic Checks

The current validation core adds three offline layers:

```text
python scripts/build_ir.py
python scripts/build_graph.py
python scripts/build_semantics.py
python scripts/validate_repository.py
python -m unittest discover
```

`build_semantics.py` loads the explicit cases in
`tests/fixtures/semantic/cases.json`, builds typed IR, and checks stable
`ASF-SEMANTIC-*` diagnostics. Current rules cover Evaluation metric-name
uniqueness and weight totals; Evaluation/Reflection routing and hard gates;
Workflow mapping targets, sources, and declared type compatibility; retry
routing; and step reachability from the entrypoint.

The semantic validator does not discover repository artifacts, execute Skills,
or infer missing types. The separate repository layer supplies canonical
filesystem context.

`validate_repository.py` is the first integrated offline repository check. It
discovers the workspace and project index, builds IR for every canonical Skill,
Workflow, and Knowledge artifact, then runs graph, version, semantic, canonical
path, package-file, Knowledge Index, and case-collision validation. It exits
nonzero when any error is present and never rewrites source.

Repository content checks use `ASF-REPOSITORY-006` through
`ASF-REPOSITORY-013`. They validate local Markdown files and anchors, duplicate
anchors, ADR numbers, explicitly retired canonical identities, active-package
TODO/FIXME/TBD and angle-token placeholders, obvious credential signatures,
and active Skill/Knowledge consumers. Secret checks deliberately recognize
only high-confidence formats; they are not an entropy scanner.

### Current Manual Checks

Contributors must still:

1. compare schema fields with the owning Markdown specification and template;
2. review semantic rules not yet encoded in the current semantic core;
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
error identifies an instance path, exact source line/column, and schema rule.
YAML/JSON IR-adapter and semantic diagnostics likewise retain their field path
and append the closest exact source mark; a missing field points to its
containing mapping because the absent key has no mark. Markdown Knowledge
diagnostics use their heading path. A repository error cites both the
referencing and target artifact where applicable.

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
| 0.4 | 2026-07-05 | Added IR, graph, and semantic validation commands and current rule coverage |
| 0.5 | 2026-07-05 | Added integrated Project Discovery and repository validation usage |
| 0.6 | 2026-07-05 | Documented automated content-integrity and lifecycle policies |
| 0.8 | 2026-07-12 | Documented position-preserving YAML/JSON schema, IR-adapter, and semantic diagnostics |
