# Execution Adapter Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-05

## Purpose

Define where and how ASF connects its validated IR and immutable
`ExecutionPlan` (ADR-0011) to external execution backends, per the Build vs
Reuse strategy in ADR-0013. This document specifies the Protocol seams
adapters implement and the package boundary that keeps `scripts/asf_validator/`
and `scripts/asf_runtime/` free of any execution-backend dependency.

## Scope

In scope: the interface contracts between ASF-owned planning/IR and
externally-owned execution, and the package layout adapters live in. Out of
scope: the internal implementation of any reuse target (LangGraph, MCP SDK,
LlamaIndex, provider SDKs) — those are consumed as dependencies, never
vendored or reimplemented.

## Design

### Principle

ASF is the source of truth for artifacts, contracts, IR, validation, and
planning. External frameworks are execution backends only. An adapter
translates one direction (ASF IR/plan -> backend construct) and the other
(backend result -> ASF-shaped output). No adapter may weaken, bypass, or
duplicate a validation or planning guarantee already established upstream —
if a plan says a step is unreachable, no adapter may make it reachable.

### Package Boundary

```text
scripts/asf_validator/   # contracts, IR, semantic validation, dependency graph — no execution deps
scripts/asf_runtime/     # catalog, context, planning — no execution deps
adapters/                # NEW: one package per reuse target, each importing exactly one external framework
  langgraph_runtime/     # ExecutionPlan -> StateGraph compiler
  mcp_tools/             # ToolIR/ConnectorIR -> MCP server tool/resource bindings
  llamaindex_retrieval/  # Knowledge IR -> retrieval configuration (compile half only)
  model_invokers/        # declarative provider/model descriptors (compile half only)
  publisher_adapters/    # declarative cross-platform export descriptors (compile half only)
```

Each `adapters/<name>/` package:

- depends on `scripts/asf_validator` and/or `scripts/asf_runtime` for the IR
  types it translates, plus exactly one external framework;
- never imports another adapter package (adapters do not depend on each
  other; composition happens above them, in a future orchestration
  entrypoint that is not part of this decision);
- ships its own `requirements-<name>.txt` so the core validator/runtime
  dependency footprint (`requirements-validator.txt`, ADR-0002) stays
  untouched by execution-backend churn (e.g., the MCP v1 -> v2 migration).

### Protocol Seams

Five seams cover the excluded responsibilities from ADR-0013 plus the
"Export planning" area ASF owns. Each is a `Protocol` owned by ASF (defined
alongside the IR/models it takes as input), implemented by exactly one
adapter package today. Three of the five (`KnowledgeRetriever`,
`ModelInvoker`, `PublisherAdapter`) split into a compile half (implemented)
and an execute half (deliberately not — out of scope for the milestone that
introduced them).

#### `PlanCompiler`

```python
class PlanCompiler(Protocol):
    def compile(self, plan: ExecutionPlan, step_executor: Any | None = None) -> Any: ...
```

(`asf_runtime.interfaces.PlanCompiler`; the return type stays `Any` in the
core Protocol so `scripts/asf_runtime/` never imports an execution backend —
the adapter's own `compile_plan` function is fully typed.)

Takes the immutable `ExecutionPlan` (`scripts/asf_runtime/models.py`) and a
caller-supplied `step_executor` (the actual per-step behavior; Runtime
Planning never invokes a Skill, so compilation alone has nothing to run — a
missing executor compiles to a node that raises `NotImplementedError` if
ever invoked, never silently no-ops). `adapters/langgraph_runtime/compiler.py`
implements this by mapping each `PlanStep` to a `StateGraph` node: its
`depends_on` becomes edges, its `on_error == "retry"` becomes a `RetryPolicy`
sized from `max_attempts` (other `on_error` values are preserved as node
metadata, not translated into retry behavior), its `timeout_seconds` becomes
the node's async timeout, and `execution_id`/`workflow_id`/`skill_id`/
`batch_index`/knowledge resolutions are attached as node metadata for audit
traceability. State uses a shallow-merge reducer
(`Annotated[dict, merge_fn]`) rather than LangGraph's default last-value
channel, because two steps in the same ready batch (ADR-0011) write
concurrently and a last-value channel rejects more than one write per
superstep. `compile_plan()` only calls `.compile()` — it never calls
`.invoke()`/`.stream()`/`.ainvoke()` on the result; the caller of
`PlanCompiler.compile(...)` gets back a LangGraph-native object and drives
it with LangGraph's own execution methods.

#### `ToolBinding`

```python
class ToolBinding(Protocol):
    def bind(
        self,
        tool: ToolIR,
        handler: ToolHandler,
        connector: ConnectorIR | None = None,
    ) -> None: ...
```

Takes a validated `ToolIR`, a caller-supplied `handler` (the tool's actual
operation — ASF Tool contracts are declarative only and never contain one,
per `TOOL_CONNECTOR_ARCHITECTURE.md`), and its resolved `ConnectorIR` if the
tool declares one. The `mcp_tools` adapter implements this by translating
`ToolIR.inputs` / `ToolIR.outputs` into an MCP wire-level `types.Tool`
(name, description, `inputSchema`, `outputSchema`) and dispatching
`call_tool` requests to the bound handler. `ConnectorIR.authentication` /
`ConnectorIR.configuration` are carried alongside the binding for a deployer
to wire into MCP's own auth primitives (`TokenVerifier`,
`OAuthAuthorizationServerProvider`); establishing a live connection is a
deployment concern this adapter does not perform. The adapter never defines
a tool's operation itself — it binds shape to behavior, it does not invent
the behavior.

#### `KnowledgeRetriever` (split into compile and query halves)

Following the same "compile only" pattern as `PlanCompiler`, this seam is
implemented in two stages, only the first of which is built today:

```python
class RetrievalConfigCompiler(Protocol):
    def compile(
        self, knowledge_docs: Sequence[KnowledgeIR], similarity_top_k: int = 5
    ) -> RetrievalConfig: ...


class KnowledgeRetriever(Protocol):
    def query(self, config: RetrievalConfig, query: str) -> RetrievalResult: ...
```

`adapters/llamaindex_retrieval/retrieval_config.py` implements
`RetrievalConfigCompiler.compile` (as `compile_retrieval_config`): it
translates validated `KnowledgeIR` into `llama_index.core.schema.Document`
objects (plain data containers) and an ASF-owned `RetrievalConfig`
(documents, knowledge IDs, `similarity_top_k`). It performs **no indexing,
no embedding generation, and no vector database access** — those remain
LlamaIndex's responsibility once a deployer builds an actual index (e.g.
`VectorStoreIndex.from_documents(config.documents, ...)`) from this config
and chooses an embedding model and vector store. `KnowledgeRetriever.query`
itself — actually running a query engine — is unimplemented; it is next on
the roadmap once a `RetrievalConfig` needs to be executed rather than only
produced.

#### `ModelInvoker` (descriptor half implemented; invoke half is not)

```python
class ModelDescriptorCompiler(Protocol):
    def compile(
        self, provider: str, model: str, parameters: Mapping[str, Any] | None = None
    ) -> ModelDescriptor: ...


class ModelInvoker(Protocol):
    def invoke(self, descriptor: ModelDescriptor, prompt: PreparedPrompt) -> ModelResponse: ...
```

`adapters/model_invokers/descriptors.py` implements
`ModelDescriptorCompiler.compile` (as `compile_model_descriptor`, plus one
convenience wrapper per provider: `openai_descriptor`,
`anthropic_descriptor`, `google_descriptor`, `ollama_descriptor`). It builds
an immutable `ModelDescriptor` (provider, model, generation parameters,
optional endpoint) and makes **no network call and imports no provider
SDK** — Priority 3's scope. It actively rejects any parameter whose name
looks like a credential (`api_key`, `token`, `authorization`, ...), so "no
API keys" is an enforced guarantee, not only a convention. `model_invokers`
does not yet resolve a Skill's `dependencies.runtime` reference to a
specific descriptor: no Runtime contract schema exists yet to carry
provider/model information (ADR-0011 defers Runtime artifact schemas), so
this module documents that gap rather than inventing one (ADR-0009's
precedent). `ModelInvoker.invoke` — actually calling a provider — is
unimplemented; when built, each provider's official SDK (or Ollama's local
API) is the reuse target, never a hand-rolled HTTP client.

#### `PublisherAdapter` (descriptor half implemented; publish half is not)

A fifth seam, added for the "Export planning" area ASF owns
(ADR-0013/PROJECT_TRACKER). Same split as `KnowledgeRetriever` and
`ModelInvoker`:

```python
class ExportDescriptorCompiler(Protocol):
    def compile(
        self, target: str, title: str, body: str, metadata: Mapping[str, Any] | None = None
    ) -> ExportDescriptor: ...


class PublisherAdapter(Protocol):
    def publish(self, descriptor: ExportDescriptor) -> PublishResult: ...
```

`adapters/publisher_adapters/descriptors.py` implements
`ExportDescriptorCompiler.compile` (as `compile_export_descriptor`, plus one
convenience wrapper per target: `youtube_export`, `tiktok_export`,
`facebook_export`, `wordpress_export`, `markdown_export`). It builds an
immutable `ExportDescriptor` (target, title, body, platform-specific
declarative metadata) and makes **no network call, imports no platform SDK,
and performs no filesystem write** — even the `markdown` target only
produces a descriptor, not a written file. It rejects any metadata key
(recursively, including nested mappings like a Markdown target's
`front_matter`) that looks like a credential or session token, enforcing
"no authentication." There is no mature OSS project that declaratively
plans a cross-platform export without also performing it, so this is ASF's
own "Export planning" intellectual property, not a wrapped reuse target.
`PublisherAdapter.publish` — actually publishing — is unimplemented; when
built, each platform's official SDK/API (e.g. google-api-python-client for
YouTube) is the reuse target, never a hand-rolled HTTP client.

### What Stays Unchanged

- `ArtifactLoader`, `CatalogBuilder`, `WorkflowPlanner`, `PlanStore`
  (`scripts/asf_runtime/interfaces.py`) are unaffected — they produce the
  `ExecutionPlan` an adapter consumes. This document adds seams *after*
  planning, not inside it.
- No graph node kind, schema, or validation rule changes. Adapters consume
  already-successful IR; a `result.ok is False` artifact never reaches an
  adapter, exactly as `dependency_graph.py` already skips it.
- `ASF-RUNTIME-PLAN-*` failure codes are unaffected. Adapter-side failures
  (a backend rejecting a compiled graph, an MCP transport error) are
  execution-time concerns and get their own diagnostics prefix when the
  first adapter milestone that needs one is implemented.

## Non-Goals

- No adapter package implements retries, checkpointing, transport, chunking,
  embedding, or vector storage itself — those are the reuse target's job.
- No adapter package is a general-purpose SDK wrapper; each implements
  exactly the Protocol seam above, scoped to ASF's own IR shapes.
- This document does not select a production deployment platform, an
  `AISkill.CLI` implementation, or a hosting model for MCP servers — those
  remain open per ADR-0011's existing scope limits.

## References

- `docs/adr/ADR-0011-runtime-planning-precedes-execution.md`
- `docs/adr/ADR-0012-declarative-tool-connector-graph-scope.md`
- `docs/adr/ADR-0013-build-vs-reuse-execution-strategy.md`
- `docs/architecture/RUNTIME_ARCHITECTURE.md`
- `docs/architecture/TOOL_CONNECTOR_ARCHITECTURE.md`

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-05 | Initial adapter Protocol seams and package boundary for the Build vs Reuse strategy |
| 0.2 | 2026-07-05 | Implemented `PlanCompiler` (`adapters/langgraph_runtime/`); finalized its signature with a caller-supplied `step_executor` and documented the state-merge reducer needed for parallel batches |
| 0.3 | 2026-07-05 | Split `KnowledgeRetriever` into `RetrievalConfigCompiler` (implemented, `adapters/llamaindex_retrieval/`) and an unimplemented `query` half, per Priority 2's configuration-only scope |
| 0.4 | 2026-07-05 | Split `ModelInvoker` into `ModelDescriptorCompiler` (implemented, `adapters/model_invokers/`, zero SDK dependency) and an unimplemented `invoke` half, per Priority 3's declarative-only scope |
| 0.5 | 2026-07-05 | Added a fifth seam, `PublisherAdapter`, split into `ExportDescriptorCompiler` (implemented, `adapters/publisher_adapters/`, zero SDK dependency) and an unimplemented `publish` half, per Priority 4's declarative-only scope |
