# Skill Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define the lifecycle, repository structure, authoring flow, validation, testing,
and example standards for compliant Skills.

## Scope

This architecture operationalizes the AI Skill Specification. It defines no
production Skill and does not change the responsibilities of the Master Skill,
Workflow Engine, Knowledge Base, Evaluation Engine, or Reflection Engine.

## Definitions

- **Skill package:** self-contained repository directory for one responsibility.
- **Template:** neutral package skeleton used by a future generator.
- **Promotion:** reviewed lifecycle transition to `active`.
- **Contract fixture:** deterministic input and expected observable behavior.

## Design

### Lifecycle

```text
Proposed -> Draft -> Validated -> Active -> Deprecated -> Archived
```

- Proposed: responsibility and reuse need are reviewed before files are created.
- Draft: package is authored from the canonical template.
- Validated: structure, contract, examples, tests, and dependencies pass review.
- Active: eligible for Workflow resolution.
- Deprecated: compatibility only, with replacement and migration guidance.
- Archived: retained for history and excluded from resolution.

Only maintainers promote a Skill. A rejected proposal creates no package. A
responsibility change creates a new Skill instead of stretching an existing one.

### Folder Standard

```text
skills/<skill-name>/
  skill.yaml
  instructions.md
  README.md
  examples/
    README.md
    <case-name>.yaml
  tests/
    README.md
    <case-name>.yaml
```

No Knowledge content, nested Skill, Workflow, credential, generated output, or
runtime cache belongs in a Skill package. Empty required directories contain a
`README.md` until fixtures are added.

### Template Structure

`templates/skill/` is the canonical authoring skeleton. A generator copies the
structure, replaces every `<placeholder>`, validates names and references, and
leaves status as `draft`. The template is guidance, not an active Skill and is
never registered in the Skill Library.

### Input and Output Contract

`skill.yaml` is authoritative. Inputs and outputs are named, typed, described,
and explicitly required or optional. Defaults are deterministic. Unknown inputs
and outputs fail unless explicitly allowed. Sensitive values are marked and
redacted. Success output, structured errors, evaluation reports, and reflection
records remain separate envelopes.

Instructions may explain how to satisfy the contract but cannot add hidden
inputs, outputs, side effects, or Knowledge.

### Validation Rules

Validation runs in order:

1. Package paths and required files.
2. YAML syntax and supported `schema_version`.
3. Metadata, naming, ID/path agreement, and lifecycle.
4. One-responsibility review.
5. Input/output schema and constraint checks.
6. Runtime, tool, and Knowledge dependency resolution.
7. Evaluation and optional reflection configuration.
8. Example and test coverage.
9. Link, secret, duplication, and prohibited-content review.

Failures identify a file, field, and governing rule. Validators never silently
repair a package or promote lifecycle status.

### Testing Rules

Active Skills require deterministic contract fixtures for minimal valid,
representative, boundary, invalid, dependency-failure, constraint, evaluation,
and reflection paths as applicable. Fixtures declare the Skill version and exact
resolved dependency versions. Tests assert observable contracts rather than model
wording. Nondeterministic behavior uses controlled fixtures and invariant checks.

Breaking releases retain compatibility fixtures for the supported prior major
version during the deprecation window.

### Example Standard

Examples teach intended use and are not tests. Each YAML example contains:

- `name` and `description`;
- `skill` ID and exact version;
- `inputs`;
- `expected` output properties and evaluation decision;
- exact dependency resolutions;
- notes explaining the boundary demonstrated.

Examples contain no secrets, machine-local paths, or claims that are absent from
their fixtures.

### Authoring and Review Flow

1. Search for an existing Skill with the same responsibility.
2. Review and approve the proposed single responsibility.
3. Generate a draft from `templates/skill/`.
4. Complete manifest, instructions, guide, examples, and tests.
5. Run validation and contract tests.
6. Review Knowledge reuse, security, and architecture boundaries.
7. Promote to `active`, commit, and register when a registry exists.

## Examples

`templates/skill/` demonstrates the compliant package layout without creating a
production Skill. `<skill-name>` becomes `summarize-document`; the resulting
identity is `skill:summarize-document`, while its instructions still perform only
summarization and never invoke a review Skill.

## References

- [AI Skill Specification](../specifications/AI_SKILL_SPECIFICATION.md)
- [Metadata Specification](../specifications/METADATA_SPECIFICATION.md)
- [Knowledge Dependency Specification](../specifications/KNOWLEDGE_DEPENDENCY_SPECIFICATION.md)
- [Naming Convention](../principles/NAMING_CONVENTION.md)
- [Version Specification](../specifications/VERSION_SPECIFICATION.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)
- [Skill Template](../../templates/skill/README.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established Skill lifecycle and package architecture |
