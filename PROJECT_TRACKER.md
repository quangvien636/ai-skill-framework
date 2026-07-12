# AI Skill Framework - Project Tracker

Version: 0.33
Status: Active
Last updated: 2026-07-12

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 33 - `bindings` CLI command reports diagnostics instead of crashing**

Goal: Next Actions item ("fix `scripts/asf_cli.py`'s `bindings` command so
`_bindings()` collects `ASF-BINDING-001` into the report's `diagnostics`
array instead of raising a bare `RuntimeError`").

Status: **Completed**

### Sprint 33 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| `_bindings()` no longer raises on a missing binding | Done | `scripts/asf_cli.py`: `_bindings()` now returns `(bindings, diagnostics)`, collecting every step's diagnostics (including `ASF-BINDING-001`) instead of raising and abandoning the remaining steps; the `bindings` command's report now has `status: "error"` + a populated `diagnostics` array when any step's binding fails, matching `validate`/`graph`'s existing shape (`_render()`'s generic top-of-report diagnostic printing picks this up for free — no text-format rendering change needed) |
| Test | Done | `tests/unit/test_cli.py::test_bindings_reports_missing_binding_as_a_diagnostic_not_a_crash` — a step with a non-required, unresolvable runtime reference now produces `{"ASF-BINDING-001"}` in `diagnostics` and `bindings == []`, not an exception |

### Sprint 33 Exit Criteria

- `python scripts/validate_contracts.py` (23/23), `build_ir.py` (47/47),
  `build_graph.py` (14/14), `build_semantics.py` (4/4),
  `validate_repository.py` (0 errors/warnings),
  `python -m unittest discover -s tests/unit` (155/155, up from 154) all
  pass.
- `tests/unit/test_cli.py`'s full 15-test suite passes, including the
  pre-existing `test_plan_and_bindings_reuse_runtime_pipeline` (a
  successfully-resolving binding is completely unaffected by this change).
- No change to any other CLI command's behavior, exit code, or report
  shape.

## Previous Sprint

**Sprint 32 - First real invoked run through a compiled RuntimeBinding graph**

Status: **Completed**

Proved `compile_plan_from_binding` + `model_descriptor_from_binding`
compose into a real, invoked LangGraph run backed by a real local Ollama
call (`adapters/langgraph_runtime/tests/test_live_ollama_invocation.py`,
opt-in `ASF_TEST_OLLAMA=1`, verified passing for real against an installed
local Ollama server, 36.95s) — Next Actions items 1 and 5. Also found and
corrected a stale Next Action: `runtime:content` has been `status: active`
and wired into `skill:content-creation` since a pre-Sprint-31 commit
(`37556ae`) — item 3 was already done. Wiring an Ollama-backed Runtime
Contract into a production Skill and promoting its status remains a
human/reviewed decision per `.ai/governance/DECISION_RIGHTS.md`.

## Earlier Sprint (Sprint 31)

**Sprint 31 - Dependency Resolution and Runtime Binding (ADR-0015)**

Status: **Completed**

Caught the tracker up to Sprints 29-30's real work (composite compiler
proof, local Ollama execution adapter) and adopted ADR-0015: a Dependency
Resolver (`scripts/asf_runtime/dependency_resolver.py`), the
`RuntimeBinding`/`BindingIR` engine (`scripts/asf_runtime/binding.py`),
seven `ASF-BINDING-001..007` diagnostics (all seven now with explicit test
coverage — 003 was a real gap, closed that sprint), and — closing ADR-0015
Section 5 — one additive `*_from_binding` function per adapter
(`model_descriptor_from_binding`, `retrieval_config_from_binding`,
`export_descriptor_from_binding`, `bind_binding_tools`,
`compile_plan_from_binding`), every existing `*_from_runtime` function left
untouched. 66 adapter tests total (up from 44). Sprint 30 (Local Ollama
Execution Adapter) is summarized in Sprint History below.

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
| 32 | First real invoked run through a compiled RuntimeBinding graph | Real `.ainvoke()` through `compile_plan_from_binding` + `model_descriptor_from_binding`, backed by a real local Ollama call; confirmed Runtime Contract -> production Skill wiring was already done pre-Sprint-31 |
| 33 | `bindings` CLI command reports diagnostics instead of crashing | `scripts/asf_cli.py`'s `_bindings()` collects `ASF-BINDING-001` per step instead of raising; new `test_cli.py` coverage |

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

1. **Human/reviewed decision needed** (per `.ai/governance/DECISION_RIGHTS.md`
   — lifecycle promotion past `draft` is not an AI Decision Right, no
   session-delegation carve-out): wire `runtime:offline` (or another
   Ollama-backed canonical Runtime Contract) into a production Skill's
   `dependencies.runtime` and flip its `status` to `active`. Sprint 32
   proved the technical wiring works (a real invoked LangGraph run through
   a local-Ollama `RuntimeBinding`) without touching any lifecycle status;
   this item is the human sign-off to make it a real, discoverable
   production binding rather than a test-only proof.
2. Implement the execute halves the compile-only adapters deliberately
   deferred: `KnowledgeRetriever.query` (build an actual LlamaIndex index/
   query engine from a `RetrievalConfig`), `ModelInvoker.invoke` (call a
   real provider SDK from a `ModelDescriptor` — Sprint 32 already proved
   `model_descriptor_from_binding` -> a real local Ollama call composes
   correctly in a test; this item is making that a reusable adapter
   capability, not just a proof), and `PublisherAdapter.publish` (call a
   real target from an `ExportDescriptor`). Each needs its own explicit
   Build vs Reuse note for the chosen SDK before implementation, per the
   engineering rules.
3. Track the MCP Python SDK v2 release (stable target 2026-07-27): re-check
   `adapters/mcp_tools/` against the new `MCPServer` naming and API once it
   ships, and update the `mcp>=1.27,<2` pin deliberately rather than
   incidentally.
4. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`,
   and wire `scripts/build_ir.py`/`scripts/build_graph.py`'s pipelines
   behind the `validate`/`generate` commands per `CLI_ARCHITECTURE.md`'s
   Validator/Generator Integration.
5. Consider whether `.ai/governance/DECISION_RIGHTS.md`'s ADR-acceptance
   convention needs a lighter-weight mechanical check (e.g., an ADR
   "Status" field the validator confirms is one of the allowed values).
6. Add precise line/column source-position tracking to IR adapter
   diagnostics (currently field/section names only) — Sprint 16's
   Deferred / Documented Gap, still open.
7. If pre-release versions are ever adopted, implement full SemVer
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
| 0.32 | 2026-07-12 | Completed Sprint 32: real invoked LangGraph run via `compile_plan_from_binding` + `model_descriptor_from_binding` + local Ollama; corrected a stale Next Action (Runtime Contract -> production Skill wiring was already done pre-Sprint-31) |
| 0.33 | 2026-07-12 | Completed Sprint 33: `bindings` CLI command now reports `ASF-BINDING-001` as a diagnostic instead of crashing |
