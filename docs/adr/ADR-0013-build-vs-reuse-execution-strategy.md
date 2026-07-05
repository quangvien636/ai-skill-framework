# ADR-0013: Build vs Reuse Strategy for Execution-Layer Subsystems

- **Status:** Accepted
- **Date:** 2026-07-05
- **Decision owners:** Project maintainers

## Context

Through ADR-0011 and `RUNTIME_ARCHITECTURE.md`, the framework already stops
deliberately at a non-executing planning layer: an `ExecutionPlan` of
resolved, ordered `PlanStep`s is produced, but "No LLM, Skill, tool, browser,
MCP, connector, or filesystem executor" exists, and
`TOOL_CONNECTOR_ARCHITECTURE.md` explicitly defers "resolving Tool/Connector
references dynamically, managing auth/connection pooling, executing
operations, sandboxing" to "a future Runtime layer (currently out of
scope)."

The project's strategy now makes that boundary permanent by policy rather
than temporary by sequencing: ASF will not build a graph execution engine,
scheduler, retry engine, state manager, streaming layer, tool runtime, MCP
runtime, RAG/vector engine, or LLM SDK. These are solved problems with
mature, actively maintained open-source implementations. Building them would
duplicate work with a worse maintenance position than the incumbents, and
would dilute focus from ASF's actual differentiation: contracts, shared IR,
semantic validation, repository discovery, runtime *planning*, evaluation,
reflection, review, and the adapter layer that connects planned artifacts to
real execution backends.

This ADR is the first application of that policy. Research was performed
against current (2026-07-05) project state, not training-data assumptions,
because this space moves fast:

- **LangGraph** shipped 1.2 on 2026-05-11: durable graph execution,
  `RetryPolicy` at graph/node/task granularity, `MemorySaver` /
  `SqliteSaver` / `PostgresSaver` checkpointers for state persistence,
  content-block-aware streaming, Python 3.10-3.14 support. Its
  `StateGraph` (nodes, edges, compiled executable, `.invoke()`/`.stream()`)
  is structurally close to ASF's own `ExecutionPlan` (`steps`, `batches`,
  `depends_on`, `on_error`, `max_attempts`).
- **MCP Python SDK**: v1.x (`mcp>=1.27,<2`) is the current production
  recommendation; maintenance mode with security patches. v2 is in alpha
  (stable target 2026-07-27, spec release 2026-07-28) and renames
  `FastMCP` to `MCPServer` among other breaking changes. `@mcp.tool()` /
  `@mcp.resource()` decorators plus stdio/SSE/Streamable-HTTP transports
  already implement exactly the "tool runtime" and "MCP runtime" ASF is
  choosing not to rebuild.
- **Semantic Kernel** is no longer the right name for this space: Microsoft
  shipped **Agent Framework 1.0 GA** on 2026-04-03
  (`Microsoft.Agents.AI`), unifying Semantic Kernel and AutoGen into one
  SDK. It is a better-alternative candidate per this ADR's own decision
  rule, but is deferred (see Decision, Deferred section) because it does
  not add capability ASF needs beyond what LangGraph already covers for a
  Python-only reference Runtime.
- **LlamaIndex** remains the retrieval/ingestion-native choice; **Haystack**
  is the production-pipeline-native alternative. Current guidance treats
  them as complementary to, not competing with, LangGraph-style
  orchestration ("LlamaIndex for ingestion/indexing, LangGraph for
  orchestration and tool use" is a common paired pattern).
- **Ollama** provides a local model-serving backend; it is one interchangeable
  provider behind an LLM SDK boundary, not an orchestration engine.

## Decision

Adopt "do not reinvent solved problems" as an enforceable rule, not a
preference: any new subsystem proposal must record a Build vs Reuse decision
before implementation (see Enforcement). For the areas named in scope today:

| Excluded ASF responsibility | Reuse target | Status |
| --- | --- | --- |
| Runtime execution engine, workflow scheduler, retry engine, state management, streaming | **LangGraph** (`langgraph`, pinned to a 1.2.x-compatible range) | Selected |
| Tool runtime, MCP runtime | **MCP Python SDK** (`mcp>=1.27,<2`, v1 API surface) | Selected, v2 migration tracked |
| RAG engine, vector database, retrieval/ingestion | **LlamaIndex** (primary), Haystack noted as alternative for pipeline-heavy production RAG | Selected (primary), Haystack deferred |
| LLM SDKs | Official provider SDKs (Anthropic, OpenAI, etc.) plus **Ollama** for local/open-weight serving, behind one ASF `ModelInvoker` seam | Selected, no single library chosen by design |
| Enterprise .NET/cross-language agent runtime | Microsoft **Agent Framework** (successor to Semantic Kernel + AutoGen) | Deferred — re-evaluate only if a non-Python production Runtime is chartered |

In every selected case, ASF **designs an adapter, not a reimplementation**.
The adapter's job is to translate ASF's already-validated IR
(`ExecutionPlan`, `ToolIR`, `ConnectorIR`, Knowledge documents) into the
target framework's native constructs, and to translate that framework's
results back into ASF-shaped outputs. The target framework owns execution,
state, retries, transport, and side effects. ASF owns the contract, the
plan, and the validation that ran before either existed. The concrete
Protocol seams and package boundaries are specified in
`docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`.

Nothing in this ADR changes ADR-0011's planning-layer scope, ADR-0012's
Tool/Connector graph scope, or any existing validation gate. It only decides
what sits on the other side of the Protocol interfaces those ADRs already
defined without concrete implementations.

### Deferred, not rejected

Haystack and Microsoft Agent Framework are not ruled out permanently. They
are not selected now because LangGraph + LlamaIndex + MCP SDK already cover
every excluded responsibility in scope for a Python reference Runtime
without redundant coverage. Re-opening either requires a new ADR citing the
capability gap, per the same rule this ADR establishes.

## Consequences

### Positive

- ASF's own code surface for execution-adjacent concerns shrinks to
  translation logic instead of protocol/scheduler/state-machine
  implementations, each of which is a multi-year, security-sensitive
  engineering effort upstream projects already fund.
- Every reuse target chosen is independently swappable behind its Protocol
  seam; a future decision to replace LangGraph with something else touches
  one adapter package, not `scripts/asf_validator/` or `scripts/asf_runtime/`.
- The existing non-executing planning layer (ADR-0011) turns out to already
  be the correct shape for this strategy — `ExecutionPlan` is designed to be
  compiled into a backend graph, not run in-process, so no planning-layer
  rework is required.

### Costs and Tradeoffs

- ASF now depends on the release cadence and breaking-change policy of
  external projects it does not control (notably MCP SDK v2, landing
  2026-07-27, which renames `FastMCP` and restructures protocol types).
  The v1 pin contains this risk but creates a tracked migration item.
- Contributors must learn one more framework's execution model (LangGraph's
  `StateGraph`/checkpointer vocabulary) to work on the adapter layer, even
  though core validator/runtime-planning work never needs it.
- Any latent assumption in `RUNTIME_ARCHITECTURE.md` that a *future* ASF
  executor would be written from scratch is now explicitly false; that
  document's "Limitations and Next Steps" section needs a follow-up edit
  pointing at the adapter architecture instead of an eventual native
  executor.

## Enforcement

- No PR may add a hand-rolled scheduler, retry loop, state persistence
  layer, tool-calling transport, MCP-shaped protocol, vector index, or LLM
  HTTP client under `scripts/asf_validator/` or `scripts/asf_runtime/`.
  Such code belongs in an adapter package and must import the reuse target
  rather than reimplement its behavior.
- Any new subsystem proposal (any future ADR touching execution) must
  include a "Build vs Reuse" section with: (1) what mature OSS already
  solves this, (2) why an adapter is or is not practical, (3) if building
  anyway, the specific capability gap no reuse target fills.
- `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md` is the enforcement
  reference for where adapter code lives and which Protocol it implements.

## Alternatives Considered

### Build a native ASF executor

Rejected. `RUNTIME_ARCHITECTURE.md` already treats this as a large,
security-sensitive undertaking (state, retries, side effects, provider
contracts) explicitly deferred by ADR-0011; building it now would spend
effort re-deriving what LangGraph 1.2 already ships in production, with
none of ASF's differentiated value in that layer.

### Pick Microsoft Agent Framework as the primary orchestration reuse target

Rejected for now. It is a credible "better alternative" per this ADR's own
rule and is newer/more unified than legacy Semantic Kernel, but it targets
.NET-first, cross-language enterprise agent orchestration. ASF's reference
Runtime is Python and already shares a structural shape with LangGraph's
graph model; adopting a second, heavier orchestration framework alongside it
would violate the "only build/adopt what provides unique value" principle
this same strategy is meant to enforce.

### Pick Haystack over LlamaIndex as the primary RAG reuse target

Rejected as primary, kept as a documented alternative. Current guidance
treats Haystack as stronger for pipeline-heavy production RAG deployments,
while LlamaIndex is the more retrieval/ingestion-native fit for ASF's
contract-first Knowledge documents and pairs more commonly with
LangGraph-style orchestration. Either is an acceptable future substitution
behind the same `KnowledgeRetriever` seam.

### Wait for MCP SDK v2 before building any MCP adapter

Rejected. v1.x is the current production recommendation and is in
maintenance mode, not deprecated; v2 lands 2026-07-27. Building the adapter
against the documented v1 API now, with the migration tracked as a roadmap
item, delivers value sooner than blocking on a not-yet-stable release.

## Related Documents

- `docs/architecture/RUNTIME_ARCHITECTURE.md`
- `docs/architecture/TOOL_CONNECTOR_ARCHITECTURE.md`
- `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`
- ADR-0010
- ADR-0011
- ADR-0012
