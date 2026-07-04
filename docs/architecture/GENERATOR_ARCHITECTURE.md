# Generator Engine Architecture

Version: 0.1
Status: Draft

Last updated: 2026-07-04

## Purpose

Define the pipeline, template resolution, dependency resolution, overwrite
and conflict policy, extension model, validation, and diagnostics for a
future Generator Engine that emits filled artifacts from
[templates](TEMPLATE_ENGINE_ARCHITECTURE.md) and producer-supplied values,
without implementing it.

## Scope

This architecture defines what a Generator does and the safety rules it
must follow. It does not implement a Generator, does not add a CLI
`generate` command (that belongs to the [CLI Architecture](CLI_ARCHITECTURE.md)
wiring this pipeline behind a command), and does not change what "valid"
means (owned by the [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md)).
The Generator consumes [IR](IR_ARCHITECTURE.md); it MUST NOT parse Markdown
or YAML directly, per ADR-0005.

## Definitions

- **Generation request:** an artifact kind, a template, and a set of
  producer-supplied placeholder values.
- **Generation plan:** the set of file writes a request would perform,
  computed before anything is written.
- **Target IR:** the IR object the Generator builds by filling a template
  with producer values, before it is rendered to source text.
- **Rendered output:** the target-format text (YAML or Markdown) produced
  from a target IR.
- **Safe overwrite:** replacing an existing file only when its current
  content is byte-identical to what the same template and inputs would
  already produce.
- **Conflict:** a generation request whose target ID or path collides with
  a different existing artifact.

## Design

### Generation Pipeline

```text
Generation request
  -> Resolve template               (Template Resolver)
  -> Resolve producer values         (fill declared placeholders only)
  -> Build target IR                 (template shape + values)
  -> Validate target IR               (Contract Validation Architecture, all layers)
  -> Render to target format          (Renderer extension point)
  -> Compute generation plan          (file paths, create/overwrite/skip)
  -> Apply plan under Overwrite Policy
  -> Emit Generator diagnostics/report
```

Validation happens on the target IR **before** rendering and writing, so an
invalid request never touches the working tree. This mirrors the Contract
Validation Architecture's pipeline instead of inventing a second one.

### Generation Stages

| Stage | Responsibility | Failure behavior |
| --- | --- | --- |
| Resolve template | Locate the template by kind + name via the Template Registry | Unknown kind/name is a request error, not a fallback guess |
| Resolve producer values | Fill only placeholders the template declares | An unfilled required placeholder or an undeclared extra value is a request error |
| Build target IR | Merge template shape with resolved values | Structural mismatch (wrong type for a field) is a request error |
| Validate target IR | Run structural, semantic, and repository validation | Any error blocks rendering; warnings are surfaced but do not block |
| Render | Serialize target IR to YAML or Markdown via a Renderer | A renderer that cannot round-trip its own output deterministically is a Renderer defect, not a request error |
| Plan | Compute create/overwrite/skip per target file against Overwrite Policy | A detected conflict halts the plan for that file only |
| Apply | Write planned files | A write failure leaves prior successful writes in place; it does not roll back siblings, since each generated file is independently valid |

### Template Resolver

The Template Resolver looks up a template by `(kind, name)` against
`templates/README.md`'s registry (or, for governance templates, their
colocated path) — the same registry the Template Engine Architecture
defines. It does not invent a new lookup mechanism; adding a template kind
to the registry makes it resolvable without Generator changes.

### Dependency Resolution

When a generation request declares references (a Skill's `dependencies`, a
Workflow step's `skill`), the Generator MUST resolve them against the
[Dependency Graph](../specifications/IR_SPECIFICATION.md#dependency-graph) before finalizing
the plan: a required reference to a nonexistent or archived ID is a request
error, not a warning. The Generator does not implement its own reference
resolution — it queries the same Dependency Graph the Validator and future
Runtime use, per ADR-0005's "one IR, many consumers" rule.

### Incremental Generation

Regenerating an artifact that already exists is a distinct, cautious case:

- The Generator MAY be asked to regenerate an existing `draft` artifact; it
  treats this as a normal generation request subject to the Overwrite
  Policy below.
- The Generator MUST NOT regenerate an `active`, `deprecated`, or
  `archived` artifact automatically. Modifying a promoted artifact is a
  human/reviewed edit, not a generation request.
- The Generator has no concept of "generator-owned regions" inside a file
  (partial-file merge). It only ever proposes whole-file content; splitting
  human edits from generated content is explicitly out of scope to avoid
  the complexity and silent-corruption risk of a merge strategy.

### Overwrite Policy

Default behavior, in order:

1. If the target path does not exist: write it.
2. If the target path exists and its content is byte-identical to what this
   request would render (a **safe overwrite**): write is a no-op; report
   "already up to date."
3. If the target path exists and differs: refuse, and report the request as
   a conflict requiring an explicit, separate confirmation step. The
   Generator never silently discards a difference it cannot prove is
   generator-produced.

There is no forced-overwrite mode that skips step 3's content check; see
ADR-0006.

### Conflict Resolution

A conflict is either an overwrite conflict (above) or an identity conflict:
the requested ID or canonical path already belongs to a different existing
artifact (per the Naming Convention's collision rules). The Generator MUST
stop and report the exact colliding ID/path; it MUST NOT auto-rename,
auto-suffix, or otherwise invent a new name to route around a collision.
Renaming is a human decision per the Naming Convention's rename rules.

### Generator Extension Model

Two extension points, both registered the same way as other CLI extension
points (see [CLI Architecture](CLI_ARCHITECTURE.md#extension-model)):

| Extension point | Purpose |
| --- | --- |
| Generator template source | Supply templates for one artifact kind (already named in the CLI Architecture; the Generator is its primary consumer) |
| Renderer | Serialize one artifact kind's target IR to its authoring format (YAML or Markdown) |

A Renderer is the inverse of an IR adapter's normalizer: normalizer maps
source -> IR, Renderer maps IR -> source. Keeping them as separate,
independently testable extension points (rather than one bidirectional
adapter) lets a future read-only tool depend on just the normalizer.

### Generator Validation

A generated artifact is validated by the same layers and rules as an
authored one — the Generator does not get a relaxed or separate validation
path. A Generator MUST leave every artifact it writes in `draft` status;
it MUST NOT promote an artifact's lifecycle state.

### Generator Diagnostics

Generator diagnostics reuse the Contract Validation Architecture's shape
(`code`, `severity`, `artifact`, `location`, `message`, `rule_reference`,
optional `suggestion`) with the `ASF-GEN-<NUMBER>` code prefix, so a
Reporter extension point (CLI Architecture) can render Validator and
Generator diagnostics identically.

## Examples

Generating `skills/summarize-document/` from `templates/skill/` with a
producer value set fills `skill.yaml`'s placeholders into a target IR,
validates it against `schemas/skill.schema.json` and the Skill Architecture's
semantic rules, and only then renders and plans the five package files. If
`skills/summarize-document/skill.yaml` already exists with hand-edited
`procedure` steps, the Overwrite Policy detects the difference and reports a
conflict instead of overwriting it.

## References

- [Template Engine Architecture](TEMPLATE_ENGINE_ARCHITECTURE.md)
- [IR Architecture](IR_ARCHITECTURE.md)
- [IR Specification](../specifications/IR_SPECIFICATION.md)
- [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md)
- [CLI Architecture](CLI_ARCHITECTURE.md)
- [Naming Convention](../principles/NAMING_CONVENTION.md)
- ADR-0005
- ADR-0006

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established Generator Engine pipeline, resolution, and overwrite safety |
