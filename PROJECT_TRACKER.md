# AI Skill Framework - Project Tracker

Version: 0.27
Status: Active
Last updated: 2026-07-05

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 27 - Adapter Layer Build-Out (Priorities 1-4)**

Goal: implement the compile-only half of every adapter seam
`EXECUTION_ADAPTER_ARCHITECTURE.md` specified but had not yet built, per the
Build vs Reuse strategy's four stated priorities.

Status: **Completed**

### Sprint 27 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Priority 1: `PlanCompiler` — ExecutionPlan -> LangGraph `StateGraph` | Done | `adapters/langgraph_runtime/` (7 tests); `PlanStep.timeout_seconds` added; `PlanCompiler` Protocol added to `asf_runtime.interfaces` |
| Priority 2: `RetrievalConfigCompiler` — Knowledge IR -> LlamaIndex config | Done | `adapters/llamaindex_retrieval/` (5 tests, `llama-index-core` only) |
| Priority 3: `ModelDescriptorCompiler` — declarative provider descriptors | Done | `adapters/model_invokers/` (9 tests, zero SDK dependency) |
| Priority 4: `ExportDescriptorCompiler` — declarative cross-platform export | Done | `adapters/publisher_adapters/` (10 tests, zero SDK dependency); added as a fifth Protocol seam for "Export planning" |

### Sprint 27 Exit Criteria

- `python scripts/validate_contracts.py`, `build_ir.py`, `build_graph.py`,
  `build_semantics.py`, `validate_repository.py` all pass with zero
  regressions after every milestone commit.
- `python -m unittest discover -s tests/unit` passes all 106 core tests
  (unchanged — no adapter imports leak into core).
- Every adapter package's own test suite passes against its real dependency
  (no mocking): `langgraph_runtime` 7/7, `mcp_tools` 3/3,
  `llamaindex_retrieval` 5/5, `model_invokers` 9/9, `publisher_adapters`
  10/10 — 34 adapter tests total.
- `model_invokers` and `publisher_adapters` ship with zero external
  dependencies and actively reject credential-shaped parameter/metadata
  keys, enforcing "no API keys"/"no authentication" rather than only
  documenting it.

### Sprint 27 Deferred / Documented Gaps

- Only the *compile* half of `KnowledgeRetriever`, `ModelInvoker`, and
  `PublisherAdapter` exists. Their *execute* halves (`query`, `invoke`,
  `publish`) are unimplemented by design — Priorities 2-4 explicitly scoped
  this sprint to configuration/description only.
- No Runtime contract schema exists to resolve a Skill's
  `dependencies.runtime` reference to a specific `ModelDescriptor` (ADR-0011
  defers Runtime artifact schemas); `model_invokers` documents this gap
  rather than inventing a resolution mechanism.
- No adapter is wired into a live process end-to-end (a running MCP server,
  an invoked LangGraph run, an actual LlamaIndex query engine, a real model
  or publish call). All five adapter packages are exercised only via direct
  unit tests against their real dependency's data/config types.
- The `mcp_tools` adapter remains pinned to MCP SDK v1; v2 (stable
  2026-07-27) migration is still untracked work.

## Previous Sprint

**Sprint 26 - Build vs Reuse Execution Strategy**

Goal: stop building execution-layer subsystems the framework does not
differentiate on, and adopt mature OSS behind an explicit adapter layer,
per the "do not reinvent solved problems" strategy change.

Status: **Completed**

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Record the Build vs Reuse policy and per-subsystem decisions | Done | `docs/adr/ADR-0013-build-vs-reuse-execution-strategy.md` |
| Define adapter Protocol seams and package boundary | Done | `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md` |
| Prove the pattern with one real adapter | Done | `adapters/mcp_tools/` (ToolBinding seam, MCP Python SDK, 3 passing tests) |
| Point Runtime Architecture's next-steps at adapters instead of an implied native executor | Done | `RUNTIME_ARCHITECTURE.md` v0.2 |

**Sprint 25 - Tool and Connector Contracts**

Goal: extend declarative contracts, IR, and the dependency graph to cover
Tool and Connector artifacts, per ADR-0012.

Status: **Completed**

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Tool/Connector schemas and lifecycle | Done | `schemas/tool.schema.json`, `schemas/connector.schema.json`, `docs/architecture/TOOL_CONNECTOR_ARCHITECTURE.md`, ADR-0012 |
| Tool/Connector IR adapters | Done | `scripts/asf_validator/tool_ir.py`, `connector_ir.py` |
| Repository discovery includes Tool/Connector artifacts | Done | commit `92f9dad` |
| Dependency graph Tool/Connector nodes and edges (`skill-tool`, `tool-connector`) | Done | `dependency_graph.py`, `valid-tool-connector` fixture, commit `55bca39` |

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

1. Design and implement a Runtime contract schema (new artifact kind, IR
   adapter, discovery, and dependency-graph node) so a Skill's
   `dependencies.runtime` reference can resolve to a specific
   `ModelDescriptor` — `model_invokers` currently has no way to make that
   selection, per Sprint 27's documented gap.
2. Implement the execute halves the compile-only adapters deliberately
   deferred: `KnowledgeRetriever.query` (build an actual LlamaIndex index/
   query engine from a `RetrievalConfig`), `ModelInvoker.invoke` (call a
   real provider SDK or Ollama from a `ModelDescriptor`), and
   `PublisherAdapter.publish` (call a real platform API from an
   `ExportDescriptor`). Each needs its own explicit Build vs Reuse note for
   the chosen SDK before implementation, per the engineering rules.
3. Wire `adapters/langgraph_runtime/compile_plan()` into a live, invoked run
   with a real `step_executor` bound to an actual Skill-invocation path —
   current tests only prove compilation and a stub executor contract.
4. Track the MCP Python SDK v2 release (stable target 2026-07-27): re-check
   `adapters/mcp_tools/` against the new `MCPServer` naming and API once it
   ships, and update the `mcp>=1.27,<2` pin deliberately rather than
   incidentally.
5. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`,
   and wire `scripts/build_ir.py`/`scripts/build_graph.py`'s pipelines
   behind the `validate`/`generate` commands per `CLI_ARCHITECTURE.md`'s
   Validator/Generator Integration.
6. Consider whether `.ai/governance/DECISION_RIGHTS.md`'s ADR-acceptance
   convention needs a lighter-weight mechanical check (e.g., an ADR
   "Status" field the validator confirms is one of the allowed values).
7. Add precise line/column source-position tracking to IR adapter
   diagnostics (currently field/section names only) — Sprint 16's
   Deferred / Documented Gap, still open.
8. If pre-release versions are ever adopted, implement full SemVer
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
