# ADR-0010: Dependency/Version Graph Scope — Node Kinds, Excluded Edges, ASF-GRAPH-*, SemVer Precedence

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

Sprint 17 implements Validator Roadmap Phase 3's Dependency Graph and
Version Graph on top of Sprint 16's IR adapters. `docs/specifications/IR_SPECIFICATION.md`
already defines both graphs' node/edge shape, but the Sprint 17 brief asks
for graph support that goes beyond what the specification states, and for
version-satisfaction logic Sprint 16 explicitly deferred. Four decisions
need to be made explicit before writing code, per this sprint's own
instruction to "document the gap instead of inventing behavior":

1. **Node kinds.** The IR Specification's Dependency Graph section defines
   nodes as `skill:*`, `workflow:*`, `kb:*` only. The Sprint 17 brief asks
   for Evaluation and Reflection graph nodes and edges (`skill -> evaluation`,
   `reflection -> skill/workflow/evaluation`, etc.). But Evaluation and
   Reflection have no `id` field, no `schema_version`, and are validated as
   *embedded* objects inside a Skill manifest (`evaluation.schema.json`/
   `reflection.schema.json` have no `commonArtifact` fields) — there is
   nothing to make a node out of.
2. **Which reference kinds become edges.** A Skill's `dependencies.runtime`
   and `dependencies.tools` are `versionedReference`s (Metadata Specification),
   but no IR adapter exists for a `runtime:*` or any `tool:*` artifact kind
   (the `runtime/` directory is an empty placeholder; `NAMING_CONVENTION.md`
   does not define a `tool` artifact kind at all).
3. **Diagnostic prefix.** Graph-stage failures (missing dependency, cycle,
   duplicate ID, unsatisfiable version range) happen after IR construction
   succeeds, across multiple artifacts — not during one artifact's parse,
   so reusing `ASF-PARSE-*` would conflate two different pipeline stages.
4. **Version-satisfaction semantics.** Full SemVer 2.0.0 precedence orders
   pre-release identifiers by a specific comparison algorithm. Implementing
   that fully is a nontrivial undertaking on its own.

## Decision

1. **Node kinds stay exactly as specified:** `skill:*`, `workflow:*`,
   `kb:*`. Evaluation and Reflection are **not** Dependency/Version Graph
   nodes and have no graph edges. They remain fields of a Skill's IR
   (`SkillIR.evaluation`, `SkillIR.reflection`), reachable by looking at the
   owning Skill, not by graph traversal. This does not implement the
   Evaluation/Reflection graph edges the Sprint 17 brief listed as
   "if specified" — they are not specified, so they are not built.
2. **Edges built in this sprint:** Skill -> Knowledge
   (`SkillIR.dependencies.knowledge`), Workflow step -> Skill
   (`WorkflowStepIR.skill`), and Knowledge -> Knowledge
   (`KnowledgeIR.related_knowledge`). Skill -> Runtime/Tool references are
   read from the IR (they still exist on `SkillDependenciesIR.runtime`/
   `.tools`) but are **not** added as Dependency Graph edges, since there is
   no Runtime/Tool node kind to connect them to; extending the graph to
   those kinds is deferred until a Runtime/Tool IR adapter exists.
3. **New `ASF-GRAPH-*` prefix** (`CLI_ARCHITECTURE.md`'s Diagnostics table)
   for graph-stage diagnostics: `ASF-GRAPH-001` unresolved/missing required
   reference, `ASF-GRAPH-002` reference cycle, `ASF-GRAPH-003` duplicate
   artifact ID, `ASF-GRAPH-004` a version range with zero satisfying known
   versions, `ASF-GRAPH-005` a dependency resolving to a `deprecated` or
   `archived` version, `ASF-GRAPH-006` an ambiguous version reference (the
   same dependent declares two different constraints for the same target
   ID), `ASF-GRAPH-007` a self-contradictory version range (for example
   `>=2.0.0 <1.0.0`, valid syntax, no version can ever satisfy it).

   `ASF-GRAPH-005`'s severity is not uniform: a `deprecated` dependency is
   always a **warning** (Version Specification: "Normal consumers SHOULD
   warn on deprecated artifacts"), but an `archived` dependency that is
   still `required: true` is an **error** — matching the worked example
   already in `IR_SPECIFICATION.md` ("If `kb:...` is archived while that
   edge is still `required: true`... it is an error, not a warning"). An
   optional dependency on an archived artifact remains a warning.
4. **SemVer precedence simplification:** version comparison and
   satisfaction (`version_satisfies_range` in `scripts/asf_validator/version_ir.py`)
   compares `(major, minor, patch)` tuples only. Pre-release precedence
   (SemVer 2.0.0 §11's identifier-by-identifier comparison) is **not**
   implemented; a pre-release version is compared using only its numeric
   core. This is a documented simplification, not a silent gap: it is
   sufficient for every fixture and every current repository artifact
   (none uses a pre-release version), and revisiting it is deferred rather
   than invented now.

## Consequences

### Positive

- The graph implementation matches what `IR_SPECIFICATION.md` already
  committed to, rather than silently expanding it to match a request that
  contradicts it.
- `ASF-GRAPH-*` gives a Reporter a clean way to distinguish "this artifact's
  own document is malformed" (`ASF-PARSE-*`) from "this artifact is fine on
  its own, but the repository around it is inconsistent" (`ASF-GRAPH-*`).
- Deferring Runtime/Tool edges avoids inventing a fake artifact kind just to
  complete a graph edge.

### Costs and Tradeoffs

- The Sprint 17 brief's Evaluation/Reflection graph requirement is not
  fulfilled; if a future need for it emerges (for example, cross-Skill
  evaluation-metric reuse), it requires a new ADR and likely a schema change
  to give Evaluation/Reflection their own identity — not a quiet graph
  addition.
- Pre-release version precedence is wrong if a repository ever adopts
  pre-release versions before this is revisited; today's repository has
  none, so the risk is latent, not active.

## Enforcement

Any future work adding Evaluation/Reflection nodes, Runtime/Tool nodes, or
full SemVer pre-release precedence must supersede or extend this ADR rather
than silently changing `dependency_graph.py`/`version_graph.py`'s node
kinds.

## Alternatives Considered

### Add synthetic IDs for Evaluation/Reflection so they can be graph nodes

Rejected because it would require inventing an identity scheme
`IR_SPECIFICATION.md` does not define, and because Evaluation/Reflection
are validated as embedded objects specifically so they never need
independent identity (Sprint 6's design).

### Reuse ASF-PARSE-* for graph-stage diagnostics

Rejected per this sprint's explicit instruction and because it would make
`ASF-PARSE-*` mean two different things depending on when it fires.

### Implement full SemVer pre-release precedence now

Rejected as disproportionate scope for a sprint focused on graph
construction; no current fixture or repository artifact needs it.

## Related Documents

- `docs/specifications/IR_SPECIFICATION.md`
- `docs/architecture/CLI_ARCHITECTURE.md`
- ADR-0009
