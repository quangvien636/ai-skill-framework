# Version Specification

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define version syntax, compatibility, breaking-change handling, and deprecation
for executable or consumable framework artifacts.

## Scope

This contract applies to Skills, Workflows, Knowledge documents, Templates,
Runtime components, and their schema versions. Editorial versions printed on
governance documents use their existing document revision scheme. ADRs are
immutable decision records and are superseded by another ADR rather than versioned.

## Definitions

- **Semantic Version:** `MAJOR.MINOR.PATCH` as defined by Semantic Versioning 2.0.0.
- **Schema version:** contract version used to parse an artifact.
- **Artifact version:** version of one artifact's behavior or content.
- **Compatible change:** change existing consumers can accept without modification.
- **Breaking change:** change requiring a consumer, producer, or declared mapping
  to change.

## Design

### Semantic Versioning

Artifact and schema versions MUST use:

```text
MAJOR.MINOR.PATCH
```

- Increment `MAJOR` for breaking changes.
- Increment `MINOR` for backward-compatible capability or substantive knowledge.
- Increment `PATCH` for backward-compatible fixes or clarifications.

Versions below `1.0.0` may evolve rapidly, but every incompatible contract change
MUST still increment `MINOR`; compatible fixes increment `PATCH`.

### Compatibility Rules

| Change | Compatibility | Increment |
| --- | --- | --- |
| Correct prose without changing behavior | Compatible | Patch |
| Add an optional field with a defined default | Compatible | Minor |
| Add an output field consumers may ignore | Compatible | Minor |
| Add or materially update reusable knowledge | Compatible when meaning is preserved | Minor |
| Remove or rename an input/output/required field | Breaking | Major |
| Change a field type, meaning, or validation rule incompatibly | Breaking | Major |
| Change Skill responsibility or Workflow semantics | New identity or Major |
| Tighten acceptance so previously valid output fails | Breaking | Major |

Consumers MUST declare supported schema versions. Dependencies MUST use a
Semantic Version range; execution MUST resolve that range to one exact version and
record the resolution for reproducibility.

### Dependency Range Syntax

The contract uses comparator ranges:

```text
>=1.2.0 <2.0.0
```

Exact pins such as `1.4.2` are valid. Floating labels such as `latest`, branches,
commit aliases, and incomplete versions such as `1.2` MUST NOT appear in artifact
dependencies.

### Breaking Changes

A breaking change MUST:

1. document migration impact;
2. increment the required version component;
3. update examples, tests, mappings, and dependents in the same change when
   possible;
4. preserve the old version during its announced deprecation window when
   operationally feasible.

Changing an artifact into a different responsibility or primary meaning SHOULD
create a new artifact ID instead of hiding the change behind a major version.

### Deprecation Policy

Deprecation MUST identify:

- the deprecated artifact or field;
- the replacement, or an explicit statement that none exists;
- migration guidance;
- the earliest removal version or review date.

Normal consumers SHOULD warn on deprecated artifacts. New artifacts MUST NOT add
deprecated dependencies. Removal occurs only in a breaking release.

### Repository and Release Tags

Repository release tags use `vMAJOR.MINOR.PATCH`. Artifact versions are
independent and MUST NOT be inferred from repository tags or document revision
labels.

## Examples

Compatible dependency:

```yaml
skill:
  id: "skill:summarize-document"
  version: ">=1.2.0 <2.0.0"
```

Invalid dependency:

```yaml
skill:
  id: "skill:summarize-document"
  version: "latest"
```

## Validation

Validators MUST reject incomplete versions, invalid ranges, incompatible schema
major versions, and active dependencies on archived artifacts. They SHOULD
surface deprecation warnings with migration guidance.

## References

- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)
- [Metadata Specification](METADATA_SPECIFICATION.md)
- [AI Skill Specification](AI_SKILL_SPECIFICATION.md)
- [Workflow Specification](WORKFLOW_SPECIFICATION.md)
- [Knowledge Architecture](../architecture/KNOWLEDGE_ARCHITECTURE.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established artifact version and compatibility rules |
