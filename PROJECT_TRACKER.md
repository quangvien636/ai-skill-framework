# AI Skill Framework - Project Tracker

Version: 0.31
Status: Active
Last updated: 2026-07-12

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 31 - Dependency Resolution and Runtime Binding (ADR-0015)**

Goal: catch this tracker up to real work already merged through `ecf78aa`
(ADR-0015 adoption, the Dependency Resolver, the RuntimeBinding/BindingIR
engine, the compile-only `asf` CLI, compiled vertical slices, the canonical
composite workflow, the local Ollama execution adapter, and its
topic-relevance gate — none of it previously recorded as a sprint), then
close ADR-0015's own explicitly deferred piece: Section 5, additive
`*_from_binding` functions on all five adapters.

Status: **Completed**

### Sprint 31 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| ADR-0015 adoption | Done | `docs/adr/ADR-0015-dependency-resolution-and-runtime-binding.md` — Dependency Resolver, `RuntimeBinding`/`BindingIR` split, `ASF-BINDING-*` prefix, Phase 4 adapter contract |
| Dependency Resolver | Done | `scripts/asf_runtime/dependency_resolver.py` — fallback-chain walk with inheritance/override (`resolve_fallback_chain`, `inherit_model`/`inherit_retriever`/`inherit_tools`/`inherit_publisher`, `resolve_retriever_knowledge`, `resolve_tools`); `tests/unit/test_dependency_resolver.py` |
| RuntimeBinding + BindingIR | Done | `scripts/asf_runtime/binding.py` — `build_runtime_binding`, `resolve_skill_runtime_binding`, `to_binding_ir`, `validate_binding_batch`; `tests/unit/test_binding.py` |
| `ASF-BINDING-001..007` diagnostics | Done | Allocated in `scripts/asf_validator/diagnostics.py`; all seven now have explicit test coverage (001/004/005/006/007 in `test_binding.py`; 002/003 in `test_dependency_resolver.py` — 003 was a real gap, closed this sprint) |
| Compile-only `asf` CLI | Done (pre-sprint) | `scripts/asf.py`, `scripts/asf_cli.py` (`validate`/`build-ir`/`graph`/`plan`/`bindings`/`compile`/`run`/`doctor`/`snapshot`/`inspect`/`explain` commands) |
| Compiled vertical slices | Done (pre-sprint) | `adapters/langgraph_runtime/vertical_slice.py` + golden snapshots `adapters/langgraph_runtime/tests/snapshots/{content-creation,research,review-quality}.json` |
| Canonical composite workflow | Done (pre-sprint) | `workflows/research-content-review/` (workflow, execution-plan, and binding golden snapshots), `tests/unit/test_composite_workflow.py`, `adapters/langgraph_runtime/tests/test_composite_snapshots.py`, `test_cli_compile.py` |
| Local Ollama execution adapter | Done (pre-sprint) | `adapters/ollama_execution/` — `OllamaStepExecutor` (loopback-only, dry-run default), composite runner, artifact-boundary checks; already consumes a resolved `RuntimeBinding` directly (`executor.py`'s `execute(..., binding: RuntimeBinding, ...)`) for a real local model call — the one adapter that goes past "compile/describe only" today, and only for loopback Ollama |
| Topic-relevance semantic gate | Done (pre-sprint) | `adapters/ollama_execution/topic_relevance.py` + `topic_relevance_config.py`, word-boundary domain matching, `detected_domains` diagnostic, integration tests |
| **ADR-0015 Phase 4: `*_from_binding` adapters** | Done (this sprint) | `model_descriptor_from_binding` (`adapters/model_invokers/descriptors.py`), `retrieval_config_from_binding` (`adapters/llamaindex_retrieval/retrieval_config.py`), `export_descriptor_from_binding` (`adapters/publisher_adapters/descriptors.py`), `bind_binding_tools` (`adapters/mcp_tools/binding.py`), `compile_plan_from_binding` (`adapters/langgraph_runtime/compiler.py`) — see ADR-0015 Section 5 |

### Sprint 31 Exit Criteria

- Purely additive: every existing `*_from_runtime` function's signature and
  behavior is unchanged; no `schemas/runtime.schema.json`,
  `scripts/asf_validator/runtime_ir.py`, or Dependency Graph edge-kind change.
- No adapter gained an execution-backend dependency from this work; every new
  function still only compiles/describes/binds — never `execute()`/
  `invoke()`/`query()`/`publish()`.
- Every new function has unit tests exercising its real dependency (real
  `RuntimeBinding` built from `tests/fixtures/graph/valid-runtime/` via
  `asf_runtime.binding.build_runtime_binding`, real LangGraph/LlamaIndex/MCP
  types) — no mocking.
- `python scripts/validate_contracts.py` (23/23), `build_ir.py` (47/47),
  `build_graph.py` (14/14), `build_semantics.py` (4/4),
  `validate_repository.py` (50 locations, 31/31 loaded, 0 errors/warnings),
  `python -m unittest discover -s tests/unit` (154/154) all pass.
- All five adapters' own test suites pass against their real dependency:
  `model_invokers` 13/13, `llamaindex_retrieval` 9/9, `publisher_adapters`
  14/14, `mcp_tools` 7/7, `langgraph_runtime` 13/13 (unittest) + 10/10
  (pytest: vertical slice, composite snapshots, CLI compile) — 66 adapter
  tests total, up from 44 at Sprint 28.

### Sprint 31 Deferred / Documented Gaps

- None of the five new `*_from_binding` functions are yet called from a live
  invoked path — they are the same "compile/describe/bind only" boundary as
  their `*_from_runtime` siblings. Wiring one into an actual run (e.g.
  `compile_plan_from_binding` behind a real `step_executor`, or
  `model_descriptor_from_binding` behind a real call) is future work — see
  Next Actions.
- `langgraph_runtime` has no single-object `*_from_runtime` function to
  mirror one-for-one (its existing binding surface is the
  `runtime_bindings` parameter on `compile_plan` itself, since a compiled
  graph spans many steps). `compile_plan_from_binding(plan, step_executor,
  runtime_bindings: Mapping[str, RuntimeBinding])` is that shape's additive
  sibling — documented in the function's own docstring so the naming
  deviation from the other four adapters is not mistaken for an oversight.
- `RuntimeBinding` (Phase 2, unchanged by this sprint) does not carry
  `execution_profile` or `concurrency_profile`, so
  `compile_plan_from_binding`'s node metadata omits the two keys the
  `*_from_runtime` path adds from a raw `RuntimeIR`. Not a regression —
  those two fields were never part of Phase 2's `RuntimeBinding` dataclass.
- `scripts/asf_cli.py`'s `bindings` command (`_bindings()`) already serves as
  the repository-level entry point that surfaces `ASF-BINDING-*`
  diagnostics end-to-end for a real workflow plan, the same role
  `validate_repository.py` plays for `ASF-SEMANTIC-*`/`ASF-REPOSITORY-*` —
  no new `scripts/build_bindings.py` was added, since inventing a second
  entry point for the same seven codes would duplicate working
  infrastructure ADR-0015 did not ask for. Real, documented gap found while
  confirming this: `_bindings()` raises a bare `RuntimeError` when a step's
  Skill has no resolvable binding at all (`ASF-BINDING-001`) instead of
  collecting it into the report's diagnostics the way `validate`/`graph`
  do — inconsistent error handling, not a missing feature. Left unfixed
  this sprint (out of ADR-0015 Phase 4's scope); tracked as a Next Action.

## Previous Sprint

**Sprint 30 - Local Ollama Execution Adapter**

Status: **Completed**

Loopback-only `OllamaStepExecutor` (no API key, no cloud path), a sequential
canonical Research -> Content Creation -> Review runner, artifact-boundary
checks, dry-run-default/live-local modes, `asf run content-workflow`, and
JSON/human-readable/per-step reports under `runs/`. Compiler v1 contracts,
IR, binding, planner, and interfaces were left unchanged.

## Earlier Sprint

**Sprint 28 - Runtime Contract (Phases 1-7)**

Status: **Completed**

### Sprint 28 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Phase 1+2: schema + IR | Done | `schemas/runtime.schema.json`, `scripts/asf_validator/runtime_ir.py`, ADR-0014 |
| Phase 3: repository discovery | Done | `runtime/`, `contracts/runtime/` canonical; `examples/runtime/` folded into `example` kind |
| Phase 4: dependency graph + semantic validation | Done | `skill-runtime`/`runtime-knowledge`/`runtime-tool`/`runtime-runtime` edges (generic missing-dep/duplicate-id/cycle reused); `ASF-SEMANTIC-010..016` |
| Lifecycle orphan policy | Done | `ASF-REPOSITORY-012` extended to active Runtime Contracts |
| Phase 5: Runtime Planning resolution | Done | Catalog now indexes Tool/Connector/Runtime; planner resolves Skill -> Runtime -> Knowledge/Tool/fallback; `PlanStep.runtime`; `ASF-RUNTIME-PLAN-006..009` |
| Phase 6: adapter binding (no invocation) | Done | One binding function per adapter: `model_descriptor_from_runtime`, `retrieval_config_from_runtime`, `bind_runtime_tools`, `export_descriptor_from_runtime`, `compile_plan(..., runtime_bindings=...)` |
| Phase 7: canonical examples | Done | `runtime/{simple,content,research,offline,hybrid}/runtime.yaml` (draft) + `tools/read-file/tool.yaml` (first real production Tool) |

### Sprint 28 Exit Criteria

- `python scripts/validate_contracts.py` (22/22), `build_ir.py` (46/46),
  `build_graph.py` (13/13), `build_semantics.py` (4/4),
  `validate_repository.py` (48 locations, 30/30 loaded, 0 errors/warnings)
  all pass after every milestone commit.
- `python -m unittest discover -s tests/unit` passes all 116 core tests.
- All five adapter test suites pass against their real dependency:
  `langgraph_runtime` 9/9, `mcp_tools` 5/5, `llamaindex_retrieval` 7/7,
  `model_invokers` 11/11, `publisher_adapters` 12/12 — 44 adapter tests total.
- No `execute()`/`invoke()`/`publish()`/`query()` implementation, no API
  keys, no network call, no provider-specific SDK call anywhere in the
  Runtime Contract layer or its adapter bindings.

### Sprint 28 Deferred / Documented Gaps

- The five canonical Runtime Contracts are `status: draft` and not yet
  referenced by any Skill's `dependencies.runtime` — wiring one into a real
  production Skill is future work.
- No Runtime contract resolution mechanism exists yet for `model_invokers`
  beyond what Phase 5's planner resolves structurally; a Skill still cannot
  *automatically* select a `ModelDescriptor` without a caller supplying the
  resolved `RuntimeIR`.
- The execute halves every compile-only adapter deferred in Sprint 27
  (`KnowledgeRetriever.query`, `ModelInvoker.invoke`,
  `PublisherAdapter.publish`, an actually-invoked `PlanCompiler` graph)
  remain unimplemented — Runtime Contract binding (Phase 6) only extends
  the same "compile/describe, never execute" boundary.
- The `mcp_tools` adapter remains pinned to MCP SDK v1; v2 (stable
  2026-07-27) migration is still untracked work.

## Earlier Adapter Sprint

**Sprint 27 - Adapter Layer Build-Out (Priorities 1-4)**

Goal: implement the compile-only half of every adapter seam
`EXECUTION_ADAPTER_ARCHITECTURE.md` specified but had not yet built, per the
Build vs Reuse strategy's four stated priorities.

Status: **Completed**

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Priority 1: `PlanCompiler` — ExecutionPlan -> LangGraph `StateGraph` | Done | `adapters/langgraph_runtime/`; `PlanStep.timeout_seconds` added; `PlanCompiler` Protocol added to `asf_runtime.interfaces` |
| Priority 2: `RetrievalConfigCompiler` — Knowledge IR -> LlamaIndex config | Done | `adapters/llamaindex_retrieval/` (`llama-index-core` only) |
| Priority 3: `ModelDescriptorCompiler` — declarative provider descriptors | Done | `adapters/model_invokers/` (zero SDK dependency) |
| Priority 4: `ExportDescriptorCompiler` — declarative cross-platform export | Done | `adapters/publisher_adapters/` (zero SDK dependency); added as a fifth Protocol seam for "Export planning" |

## Sprint History

Full per-sprint backlogs and exit criteria for completed sprints live in Git
history and the ADRs/architecture documents each sprint produced; this table
is the durable summary so this tracker does not grow one repeated section per
sprint indefinitely.

| Sprint | Title | Key Output |
| --- | --- | --- |
| 1 | Foundation | Repository governance, System Architecture, Design Principles, ADR-0001 |
| 2 | Knowledge Architecture | Knowledge hierarchy, taxonomy, template, discovery index, naming rules |
| 3 | AI Skill Specification | Normative artifact contracts, specification registry |
| 4 | Skill Architecture | Skill lifecycle, package architecture, `templates/skill/` |
| 5 | Workflow Architecture | Workflow lifecycle, package, execution, mapping design, `templates/workflow/` |
| 6 | Evaluation and Reflection Architecture | Quality evaluation and bounded reflection contracts |
| 7 | Machine-Readable Schemas | Draft 2020-12 schemas, Contract Validation Architecture, Validator Roadmap |
| 8 | Validator Prototype | `scripts/validate_contracts.py`, 10 fixture cases, ADR-0002 |
| 9 | CLI Architecture | `docs/architecture/CLI_ARCHITECTURE.md`, ADR-0003 |
| 10 | Template Engine | `docs/architecture/TEMPLATE_ENGINE_ARCHITECTURE.md`, `templates/README.md`, ADR-0004 |
| 11 | Intermediate Representation (IR) | `docs/architecture/IR_ARCHITECTURE.md`, `docs/specifications/IR_SPECIFICATION.md`, ADR-0005 |
| 12 | Generator Engine Architecture | `docs/architecture/GENERATOR_ARCHITECTURE.md`, ADR-0006 |
| 13 | CLI Design Expansion | `docs/architecture/CLI_ARCHITECTURE.md` v0.4, ADR-0007 |
| 14 | Repository Engineering Review | README navigation rework, broken-link fix, IR terminology alignment |
| 15 | AI Team Architecture | `.ai/roles/`, `.ai/playbooks/`, `.ai/standards/`, `.ai/governance/`, ADR-0008 |
| 16 | Validator Roadmap Phase 2 (IR Adapters) | `scripts/asf_validator/`, `scripts/build_ir.py` (16/16), 30 unit tests, ADR-0009 |
| 17 | Validator Roadmap Phase 3 (Dependency/Version Graph) | `dependency_graph.py`, `version_graph.py`, `scripts/build_graph.py` (10/10), 53 unit tests, ADR-0010 |
| 18 | Content Creation Skill v1 | Active Skill, five Knowledge documents, end-to-end Workflow, production graph scenario |
| 19 | Research Skill v1 | Active Skill, six methodology documents, topic-to-brief Workflow, production graph scenario |
| 20 | Review Quality Skill v1 | Active Skill, seven quality documents, draft-to-reviewed-package Workflow, production graph scenario |
| 21 | Semantic Validator Core | Nine IR-level semantic rules, conformance runner, structured diagnostics |
| 22 | Repository Discovery and Integrity | Workspace/Project index, five repository rules, integrated validation command |
| 23 | Runtime Planning Foundation | Immutable context/catalog/plan, exact resolutions, deterministic batches, ADR-0011 |
| 24 | Repository Integrity Completion | Links, anchors, ADRs, secrets, stale identities, placeholders, lifecycle policy |
| 25 | Tool and Connector Contracts | `tool.schema.json`, `connector.schema.json`, IR adapters, dependency graph nodes/edges, ADR-0012 |
| 26 | Build vs Reuse Execution Strategy | ADR-0013, `EXECUTION_ADAPTER_ARCHITECTURE.md`, `adapters/mcp_tools/` (ToolBinding proof of concept) |
| 27 | Adapter Layer Build-Out (Priorities 1-4) | `adapters/langgraph_runtime/`, `llamaindex_retrieval/`, `model_invokers/`, `publisher_adapters/` (34 tests total) |
| 28 | Runtime Contract (Phases 1-7) | `runtime.schema.json`, `runtime_ir.py`, graph/semantic/planning/orphan extensions, 5 adapter bindings, 5 canonical examples, ADR-0014 |
| 29 | Canonical Composite Compiler Proof | Three-Skill workflow, artifact flow, Reviewed Content Package, golden snapshots, composite CLI |
| 30 | Local Ollama Execution Adapter | Loopback StepExecutor, canonical runner, artifact checks, reports, dry/live CLI |
| 31 | Dependency Resolution and Runtime Binding (ADR-0015) | Dependency Resolver, `RuntimeBinding`/`BindingIR`, `ASF-BINDING-001..007`, 5 adapter `*_from_binding` functions (Phase 4), tracker caught up to Sprints 29-30 |

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |
| Governance documents (this tracker) grow unbounded | Summarize completed sprints in Sprint History instead of repeating sections |

## Next Actions

1. Wire at least one of the five new `*_from_binding` functions (ADR-0015
   Section 5, Sprint 31) into an actual invoked/compiled path — e.g.
   `compile_plan_from_binding` behind a real `step_executor`, or
   `model_descriptor_from_binding` behind a real call. Phase 4 shipped the
   binding functions themselves; nothing yet consumes a `RuntimeBinding`
   end-to-end through them the way `adapters/ollama_execution` already
   does through its own bespoke path (see Sprint 31's Deferred/Documented
   Gaps).
2. Fix `scripts/asf_cli.py`'s `bindings` command (`_bindings()`) to collect
   `ASF-BINDING-001` (a step's Skill has no resolvable binding at all) into
   the report's `diagnostics` array instead of raising a bare
   `RuntimeError` — bring it in line with how `validate`/`graph` already
   handle errors gracefully. Documented gap found while confirming Sprint
   31's Step 3 (a repository-level `ASF-BINDING-*` entry point already
   exists via this command; its error handling just does not match the
   rest of the CLI yet).
3. Wire one of the five canonical Runtime Contracts into a real production
   Skill's `dependencies.runtime` (e.g. `runtime:content` into
   `skill:content-creation`) and flip that Runtime Contract to `status:
   active` — this is the first end-to-end production use of the chain
   Sprint 28 built, and will need the lifecycle orphan policy re-verified
   against a real active/consumer pair.
4. Implement the execute halves the compile-only adapters deliberately
   deferred: `KnowledgeRetriever.query` (build an actual LlamaIndex index/
   query engine from a `RetrievalConfig`), `ModelInvoker.invoke` (call a
   real provider SDK from a `ModelDescriptor` — note `adapters/
   ollama_execution` already calls real local Ollama, but via its own
   `RuntimeBinding`-consuming executor, not via `model_invokers`'
   `ModelDescriptor`/`model_descriptor_from_binding`), and
   `PublisherAdapter.publish` (call a real platform API from an
   `ExportDescriptor`). Each needs its own explicit Build vs Reuse note for
   the chosen SDK before implementation, per the engineering rules.
5. Wire `adapters/langgraph_runtime/compile_plan()`/`compile_plan_from_binding()`
   into a live, invoked run with a real `step_executor` bound to an actual
   Skill-invocation path — current tests only prove compilation and a stub
   executor contract. `adapters/ollama_execution`'s composite runner is a
   separate, bespoke sequential executor that does not go through either
   compiled-graph function today.
6. Track the MCP Python SDK v2 release (stable target 2026-07-27): re-check
   `adapters/mcp_tools/` against the new `MCPServer` naming and API once it
   ships, and update the `mcp>=1.27,<2` pin deliberately rather than
   incidentally.
7. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`,
   and wire `scripts/build_ir.py`/`scripts/build_graph.py`'s pipelines
   behind the `validate`/`generate` commands per `CLI_ARCHITECTURE.md`'s
   Validator/Generator Integration.
8. Consider whether `.ai/governance/DECISION_RIGHTS.md`'s ADR-acceptance
   convention needs a lighter-weight mechanical check (e.g., an ADR
   "Status" field the validator confirms is one of the allowed values).
9. Add precise line/column source-position tracking to IR adapter
   diagnostics (currently field/section names only) — Sprint 16's
   Deferred / Documented Gap, still open.
10. If pre-release versions are ever adopted, implement full SemVer
    pre-release precedence in `version_ir.py` (Sprint 17's documented
    simplification).

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Sprint 1 Foundation tracker |
| 0.2 | 2026-07-04 | Added Sprint 2 Knowledge Architecture progress |
| 0.3 | 2026-07-04 | Completed Sprint 3 AI Skill Specification |
| 0.4 | 2026-07-04 | Completed Sprint 4 Skill Architecture |
| 0.5 | 2026-07-04 | Completed Sprint 5 Workflow Architecture |
| 0.6 | 2026-07-04 | Completed Sprint 6 quality architecture |
| 0.7 | 2026-07-04 | Completed Sprint 7 schemas and validation foundation |
| 0.8 | 2026-07-04 | Completed Sprint 8 validator prototype |
| 0.9 | 2026-07-04 | Completed Sprint 9 CLI architecture |
| 0.10 | 2026-07-04 | Completed Sprint 10 Template Engine |
| 0.11 | 2026-07-04 | Completed Sprint 11 IR; consolidated sprint history table |
| 0.12 | 2026-07-04 | Completed Sprint 12 Generator Engine architecture |
| 0.13 | 2026-07-04 | Completed Sprint 13 CLI Design Expansion |
| 0.14 | 2026-07-04 | Completed Sprint 14 Repository Engineering Review |
| 0.15 | 2026-07-04 | Completed Sprint 15 AI Team Architecture |
| 0.16 | 2026-07-04 | Completed Sprint 16 Validator Roadmap Phase 2 (IR adapters); removed a stray duplicated "Previous Sprint" section left over from an earlier edit |
| 0.17 | 2026-07-04 | Completed Sprint 17 Validator Roadmap Phase 3 (Dependency/Version Graph) |
| 0.18 | 2026-07-05 | Completed Sprint 18 Content Creation Skill v1 |
| 0.19 | 2026-07-05 | Completed Sprint 19 Research Skill v1 |
| 0.20 | 2026-07-05 | Completed Sprint 20 Review Quality Skill v1 |
| 0.21 | 2026-07-05 | Completed Sprint 21 Semantic Validator core |
| 0.22 | 2026-07-05 | Completed Sprint 22 Repository Discovery and initial integrity validation |
| 0.23 | 2026-07-05 | Completed Sprint 23 Runtime planning foundation |
| 0.24 | 2026-07-05 | Completed Sprint 24 Repository Integrity Phase 4 |
| 0.25 | 2026-07-05 | Completed Sprint 25 Tool and Connector Contracts (schemas, IR, discovery, dependency graph) |
| 0.26 | 2026-07-05 | Completed Sprint 26 Build vs Reuse Execution Strategy (ADR-0013, adapter architecture, mcp_tools proof of concept) |
| 0.27 | 2026-07-05 | Completed Sprint 27 Adapter Layer Build-Out: langgraph_runtime, llamaindex_retrieval, model_invokers, publisher_adapters (34 adapter tests) |
| 0.28 | 2026-07-05 | Completed Sprint 28 Runtime Contract: schema, IR, discovery, graph, semantic, planning, adapter binding, 5 canonical examples, ADR-0014 |
| 0.29 | 2026-07-05 | Completed Sprint 29 composite compiler proof, snapshots, CLI, and Reviewed Content Package boundary |
| 0.30 | 2026-07-05 | Completed Sprint 30 local Ollama execution adapter and canonical workflow runner |
| 0.31 | 2026-07-12 | Completed Sprint 31: caught tracker up to Sprints 29-30's real work, adopted ADR-0015, closed its Phase 4 (5 adapter `*_from_binding` functions), added missing `ASF-BINDING-003` test coverage |
