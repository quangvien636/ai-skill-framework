# Runtime Contract Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-05

## Purpose

Define the Runtime Contract: the declarative artifact that binds a Skill to
the model, retriever, tools, and publisher it needs, plus the operational
policy (timeout, retry, safety, audit, concurrency, fallback) governing that
binding. See ADR-0014 for the schema, discovery, and validation-split
decisions this document summarizes.

## Scope

Runtime Contracts declare *what resources a Skill needs and under what
policy*, not how those resources execute. They contain no credentials,
executable code, provider clients, or invocation behavior — identical in
spirit to Tool and Connector contracts (`TOOL_CONNECTOR_ARCHITECTURE.md`).

## Position in the Chain

```text
Skill
  -> (Skill.dependencies.runtime) Runtime Contract
       -> model            (inline ModelDescriptor-shaped data)
       -> retriever         (Knowledge references -> RetrievalConfig-shaped data)
       -> tools              (Tool references)
       -> publisher           (inline ExportDescriptor-shaped data)
       -> timeout/retry/safety/audit/concurrency/fallback profiles
  -> ExecutionPlan (asf_runtime.planner resolves all of the above)
  -> Adapter binding (Phase 6: langgraph_runtime, mcp_tools, llamaindex_retrieval,
                       model_invokers, publisher_adapters -- binding only)
  -> Future Executor (out of scope; ADR-0013)
```

## Design

### Canonical Identity and Locations

- `runtime:<name>` at `runtime/<name>/runtime.yaml` or
  `contracts/runtime/<name>/runtime.yaml` (both canonical and discoverable).
- `examples/runtime/*.yaml` are `example` kind fixtures, not validated as
  full Runtime IR, matching the existing `*/examples/**` convention.

### The `enabled` Pattern

`model`, `retriever`, `tools`, and `publisher` are always-required schema
sections, each carrying its own `enabled: bool`. A Runtime Contract must
take an explicit position on every capability; declining one still requires
naming that decision rather than omitting the section. This is what gives
semantic validation ("missing model," "missing retriever," "missing tool,"
"invalid publisher") real content: enabled-but-unconfigured is the
inconsistency being flagged, not mere absence.

### Reference vs. Inline Descriptor

| Field | Kind | Why |
| --- | --- | --- |
| `retriever.knowledge` | Real reference (`kb:` id + version range) | Knowledge is an existing, resolvable artifact kind. |
| `tools.refs` | Real reference (`tool:` id + version range) | Tool is an existing, resolvable artifact kind. |
| `fallback_profile.fallback_runtime` | Real reference (`runtime:` id + version range) | Runtime Contracts can reference each other. |
| `model` | Inline descriptor | No `model:` artifact kind exists; would be new contract surface with one consumer. |
| `publisher` | Inline descriptor | No `publisher:` artifact kind exists; same reasoning. |

### Validation Ownership

| Layer | Owns |
| --- | --- |
| Structural (`ASF-SCHEMA-*`) | Field shapes, enums, required keys. |
| Dependency Graph (`ASF-GRAPH-*`) | `skill-runtime`, `runtime-knowledge`, `runtime-tool`, `runtime-runtime` edges: missing-reference, duplicate-id, and cycle detection — all reused, generic mechanisms. |
| Semantic (`ASF-SEMANTIC-*`) | Single-artifact internal consistency: `enabled` vs. configured content, retry/timeout/fallback policy agreement. |
| Repository (`ASF-REPOSITORY-012`) | Lifecycle orphan policy: an active Runtime Contract with no Skill consumer and no fallback reference from another active Runtime. |

### Planning

`asf_runtime.planner.plan_workflow` resolves each step's Skill's
`dependencies.runtime` references against the catalog (now including
Tool/Connector/Runtime artifacts, closing a latent catalog gap), then
resolves that Runtime Contract's `retriever.knowledge`, `tools.refs`, and
`fallback_profile.fallback_runtime` the same way. Every resolution is
recorded in `ExecutionPlan.resolutions`; `PlanStep.runtime` carries the
step's own resolutions, mirroring the existing `PlanStep.knowledge` field.
`model` and `publisher` need no further resolution — they are terminal
inline descriptors.

### Adapter Binding

Binding functions (one per adapter package, Phase 6) convert a resolved
Runtime Contract into that adapter's existing descriptor type. They call no
network, import no provider SDK, and invoke nothing — translation only,
identical in kind to every prior adapter milestone (ADR-0013).

## Non-Goals

- No `execute()`/`invoke()`/`publish()`/`query()` implementation.
- No API keys, network access, or SDK calls anywhere in this layer.
- No new Model, Retriever, or Publisher artifact kind.
- No production deployment platform or hosting model decision.

## References

- `docs/adr/ADR-0014-runtime-contract-schema-and-scope.md`
- `docs/architecture/RUNTIME_ARCHITECTURE.md`
- `docs/architecture/TOOL_CONNECTOR_ARCHITECTURE.md`
- `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`
- ADR-0010, ADR-0011, ADR-0012, ADR-0013

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-05 | Initial Runtime Contract architecture |
