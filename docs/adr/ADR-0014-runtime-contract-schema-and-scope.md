# ADR-0014: Runtime Contract Schema, Discovery, and Graph Scope

- **Status:** Accepted
- **Date:** 2026-07-05
- **Decision owners:** Project maintainers

## Context

`Skill.dependencies.runtime` has existed as a versioned reference field since
the Skill schema was written, but nothing defines what it points at.
ADR-0011 explicitly deferred this: "Runtime and Tool dependency declarations
do not become graph nodes until schemas and IR adapters define those
artifact kinds." Tool and Connector closed that gap for
`dependencies.tools` (ADR-0012); this ADR closes it for
`dependencies.runtime`.

Separately, Sprint 27 built five adapter packages
(`langgraph_runtime`, `mcp_tools`, `llamaindex_retrieval`, `model_invokers`,
`publisher_adapters`) that each compile one kind of descriptor
(`ExecutionPlan`, `ToolIR`/`ConnectorIR` binding, `RetrievalConfig`,
`ModelDescriptor`, `ExportDescriptor`) but had no way to say, for one Skill,
*which* model, retriever, tools, and publisher apply together as one
resource profile. The Runtime Contract is that missing link: a declarative
artifact a Skill can depend on, that names a model/retriever/tools/publisher
combination plus operational policy (timeout, retry, safety, audit,
concurrency, fallback), for adapters to bind against.

Several design questions have no existing answer and must be resolved before
implementation rather than guessed:

1. **Where do Runtime Contract files live?** The top-level `runtime/`
   directory already exists but is reserved by ADR-0009 for "a future
   CLI/Runtime implementation," not contract data — and the actual Runtime
   reference implementation lives in `scripts/asf_runtime/`, not there.
2. **Do `model`/`retriever`/`tools`/`publisher` reference other artifact
   kinds, or embed declarative descriptors inline?** No `model:`, `retriever:`,
   or `publisher:` artifact kind exists, and creating three more full
   contract schemas is out of this milestone's scope.
3. **What does "missing model" / "missing retriever" / "missing tool" mean**
   as a *semantic* validation rule, given the Dependency Graph already has a
   generic "missing dependency" mechanism for any edge?
4. **Does the Runtime Contract layer duplicate execution?** It must not —
   Engineering Rules for this milestone are explicit: no `execute()`, no API
   keys, no network, no SDK calls, no provider-specific logic.

## Decision

### 1. Canonical identity and file locations

- Canonical identity: `runtime:<name>`, pattern
  `^runtime:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`, matching Tool/Connector.
- Canonical path: `runtime/<name>/runtime.yaml`. This reclaims the
  already-reserved, currently-empty top-level `runtime/` directory for
  declarative Runtime Contract data, not code — ADR-0013 already decided ASF
  will not build a native execution runtime, so ADR-0009's "future
  CLI/Runtime implementation" reservation for that directory no longer
  applies; nothing else claims it.
- Also discovered: `contracts/runtime/<name>/runtime.yaml`, an alternate
  location for repositories that group all contracts under `contracts/<kind>/`.
  Both locations produce full `runtime` kind IR artifacts.
- `examples/runtime/*.yaml` (flat files, no per-example subdirectory) are
  discovered as `example` kind, not `runtime` kind — identical to how
  `skills/*/examples/**` fixtures are `example` kind, never re-validated as
  full Skill IR. This is the first real use of the previously-empty
  top-level `examples/` directory; it does not collide with the existing
  package-relative `*/examples/**` convention because it is a distinct,
  additional glob, not a replacement.

### 2. Schema shape (`schemas/runtime.schema.json`)

All of the following are **required top-level keys** (a Runtime Contract
must take an explicit position on every profile), but four of them
(`model`, `retriever`, `tools`, `publisher`) carry their own `enabled: bool`
so a contract can decline a capability without omitting the section ASF
needs to validate:

| Field | Shape | Notes |
| --- | --- | --- |
| `responsibility` | string | Single observable responsibility, matching Skill/Tool/Connector. |
| `execution_profile` | enum `sync\|async\|streaming\|batch` | Declarative label only; no scheduler behavior. |
| `model` | `{enabled, provider?, model?, parameters?, endpoint?}` | `provider` enum matches `model_invokers.SUPPORTED_PROVIDERS`. Inline descriptor, not a reference — no `model:` artifact kind exists. |
| `retriever` | `{enabled, knowledge: [KnowledgeReferenceIR-shaped], similarity_top_k?}` | `knowledge` reuses the exact reference shape `skill.schema.json#/properties/dependencies/properties/knowledge` already uses (`kb:` id, version range, required, purpose) — a real, resolvable Dependency Graph reference. |
| `tools` | `{enabled, refs: [versionedReference]}` | `refs` reuses `metadata.schema.json#/$defs/versionedReference`, the same shape `Skill.dependencies.tools` and `Tool.dependencies.connectors` already use — real, resolvable references to `tool:` artifacts. |
| `publisher` | `{enabled, target?, metadata?}` | `target` enum matches `publisher_adapters.SUPPORTED_TARGETS`. Inline descriptor, not a reference. |
| `timeout_policy` | `{timeout_seconds, on_timeout: fail\|retry\|fallback}` | |
| `retry_policy` | `{max_attempts (1-5), backoff: none\|fixed\|exponential}` | |
| `safety_profile` | `{content_filter: none\|standard\|strict, blocked_terms?}` | |
| `audit_profile` | `{log_level: none\|basic\|detailed, redact_fields?}` | |
| `concurrency_profile` | `{max_parallel_steps, max_parallel_tool_calls}` | |
| `fallback_profile` | `{enabled, fallback_runtime?: versionedReference, max_fallback_depth (1-5)}` | `fallback_runtime` is a real, resolvable reference to another `runtime:` artifact. |

`model` and `publisher` stay inline descriptors — not references — because
no OSS-backed "Model" or "Publisher" artifact kind exists to reference, and
inventing one now would be new contract surface with no consumer beyond
this ADR, contradicting "only build what provides unique value." `retriever`
and `tools` reuse *existing* reference shapes because Knowledge and Tool are
already real, resolvable artifact kinds.

### 3. Validation split (why "enabled" earns its keep)

- **Structural** (`ASF-SCHEMA-*`): the shape above.
- **Dependency Graph** (`ASF-GRAPH-*`, entirely reused mechanisms, no new
  code beyond registering new node/edge kinds): `skill-runtime` (from
  `Skill.dependencies.runtime`, finally activating the edge ADR-0010/0011
  deferred), `runtime-knowledge` (from `retriever.knowledge`),
  `runtime-tool` (from `tools.refs`), `runtime-runtime` (from
  `fallback_profile.fallback_runtime`). The existing generic missing-dependency
  check, duplicate-id check, and `detect_cycle` call cover "invalid runtime
  reference," "missing tool," "missing retriever" (unresolvable
  `kb:`/`tool:`/`runtime:` id), "duplicate runtime ids," and multi-hop
  "invalid fallback chain" for free.
- **Semantic** (`ASF-SEMANTIC-*`, new rules in this milestone): single-artifact
  internal consistency schema cannot express as cleanly as a business rule,
  matching this codebase's existing precedent (e.g.
  `SEMANTIC_REFLECTION_ROUTING_INCONSISTENT` for two fields that must agree).
  Concretely: `model.enabled` true with an empty `model.model` ("missing
  model"); `retriever.enabled` true with an empty `retriever.knowledge`
  ("missing retriever"); `tools.enabled` true with empty `tools.refs`
  ("missing tool," the single-artifact half); `publisher.enabled` true with
  no `publisher.target` ("invalid publisher"); `retry_policy.backoff ==
  "exponential"` with `max_attempts < 2` ("incompatible retry policy");
  `timeout_policy.on_timeout` referencing a policy that contradicts
  `retry_policy`/`fallback_profile` ("invalid timeout profile");
  `fallback_profile.enabled` disagreeing with `fallback_runtime` presence,
  or a self-referential `fallback_runtime` ("invalid fallback chain," the
  single-artifact half).
- **Repository** (`ASF-REPOSITORY-012`, reused): an active Runtime Contract
  with no Skill consumer and no other active Runtime's fallback reference is
  an orphan, extending the existing lifecycle-orphan rule.

### 4. Planning, not execution

`scripts/asf_runtime/catalog.py`'s `_catalog_artifact` gains Tool, Connector,
and Runtime entries (Tool/Connector were a latent gap — the Dependency Graph
already knew about them, but the planning catalog did not). The planner
resolves `Skill -> Runtime Contract -> (Knowledge via retriever, Tool via
tools.refs, fallback Runtime)` into `ExecutionPlan.resolutions`, and each
`PlanStep` gains a `runtime: tuple[DependencyResolution, ...]` field
mirroring the existing `knowledge` field. `model`/`publisher` are not
further resolved — they are terminal inline descriptors already fully
contained in the Runtime Contract's own IR. No plan step gains new
executable behavior; this is index-and-resolve work identical in kind to
existing Skill/Knowledge resolution.

### 5. Adapter integration is binding only

Phase 6 adds one small binding function per adapter package that converts a
resolved `RuntimeIR` (plus its resolved Tool/Knowledge artifacts) into that
adapter's existing descriptor type — `RuntimeIR.model` ->
`model_invokers.ModelDescriptor`, `RuntimeIR.retriever` + resolved Knowledge
-> `llamaindex_retrieval.RetrievalConfig`, `RuntimeIR.tools` + resolved Tool
IR -> `mcp_tools` bindings, `RuntimeIR.publisher` ->
`publisher_adapters.ExportDescriptor`. No adapter gains a new external
dependency, and no binding function calls `.invoke()`/`.query()`/`.publish()`/
a network/API — they only translate already-validated declarative data into
an existing descriptor shape, same pattern as every prior adapter milestone.

## Consequences

### Positive

- Closes a three-ADR-old gap (`Skill.dependencies.runtime` has been
  IR-representable but graph-invisible since before Tool/Connector existed).
- Every "missing X" example in the milestone brief gets a real, traceable
  home (Graph vs. Semantic vs. Repository) instead of one undifferentiated
  validator.
- `model`/`publisher` staying inline avoids inventing two speculative
  artifact kinds with no second consumer.

### Costs and Tradeoffs

- The `enabled` flag on four sections means schema validity alone does not
  guarantee a usable Runtime Contract; semantic validation must run too.
- Reclaiming top-level `runtime/` for contracts means a future reader must
  consult this ADR (not ADR-0009 alone) to know what belongs there.
- `contracts/runtime/` and `runtime/` both being canonical, discoverable
  locations means two authoring conventions exist simultaneously; this ADR
  does not pick one as preferred, only both as valid.

## Enforcement

No adapter package may import another adapter package to perform Runtime
Contract binding (the existing isolation rule applies unchanged). No new
code under `scripts/asf_validator/` or `scripts/asf_runtime/` may call a
network, import a provider/platform SDK, or read an API key — Runtime
Contracts are structurally incapable of triggering execution, matching
`TOOL_CONNECTOR_ARCHITECTURE.md`'s existing "no placeholder runtime
implementations" rule extended to this artifact kind.

## Alternatives Considered

### Give Model, Retriever, and Publisher their own artifact kinds and schemas

Rejected for this milestone. Each would need its own lifecycle, discovery
path, and lone consumer (the Runtime Contract) with no other repository
artifact referencing them — three new contract kinds for one relationship
each. Revisit only if a second, independent consumer emerges.

### Make `model`/`retriever`/`tools`/`publisher` fully optional keys instead of always-required-with-`enabled`

Rejected because it removes semantic validation's reason to exist for
"missing model/retriever/tool/publisher": an absent optional key is simply
valid, not a flagged inconsistency. Requiring the section but allowing
`enabled: false` keeps the "declared a stance for every profile" property
the milestone brief implies with "the contract must remain declarative"
plus giving each of the five Phase 7 example flavors a real reason to differ.

### Discover only `runtime/`, not also `contracts/runtime/`

Rejected because the milestone brief explicitly names both as automatic
discovery targets; this ADR records the reasoning rather than silently
picking one.

## Related Documents

- `docs/architecture/RUNTIME_ARCHITECTURE.md`
- `docs/architecture/TOOL_CONNECTOR_ARCHITECTURE.md`
- `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`
- `docs/adr/ADR-0009-ir-adapter-package-and-scope.md`
- ADR-0010
- ADR-0011
- ADR-0012
- ADR-0013
