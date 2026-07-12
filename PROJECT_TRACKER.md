# AI Skill Framework - Project Tracker

Version: 0.37
Status: Active
Last updated: 2026-07-12

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 37 - Ollama Runtime promotion approval and readiness**

Goal: durably record the human-approved promotion scope and define mechanical
readiness gates before wiring or lifecycle mutation.

Status: **Completed**

### Sprint 37 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Record human approval | Done | `docs/guides/RUNTIME_PROMOTION_READINESS.md` scopes approval to `runtime:offline@1.0.0` and `skill:content-creation@1.0.0` only |
| Define readiness and rollback gates | Done | Checklist requires binding resolution, loopback-only execution, structured failures, real installed-model/live evidence, full validation, and a bounded rollback |
| Preserve lifecycle | Done | No artifact status or Skill dependency changes in this sprint |

### Sprint 37 Exit Criteria

- Full offline repository validation and unit tests pass.
- No live Ollama or external API call is made in this documentation/readiness
  sprint.

## Previous Sprint

**Sprint 36 - CLI implementation language and phased adoption decision**

Goal: close the CLI language/package-layout Next Action without creating a
parallel CLI or a stub Generator pipeline.

Status: **Completed as a proposal pending human ADR acceptance**

### Sprint 36 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Record implementation language and package layout | Done | Proposed `docs/adr/ADR-0016-cli-implementation-language-and-phased-adoption.md`: Python; retain `scripts/asf_cli.py` until a real second command-group need triggers a package split |
| Verify Validator Integration | Done | `scripts/asf_cli.py::load_workspace()` already reuses `build_ir()` and `validate_workspace()` reuses dependency/version graph, semantic, and repository validation over Project Discovery |
| Assess Generator Integration | Deferred with prerequisite | No executable Generator pipeline exists to wrap; adding `generate` first would be a stub and violate the CLI error-handling contract. A real Generator reference implementation is now the explicit prerequisite. |

### Sprint 36 Exit Criteria

- ADR-0016 remains `Proposed`: `.ai/governance/DECISION_RIGHTS.md` reserves
  ADR acceptance for a human maintainer, and this session has no acceptance
  delegation.
- Full repository validation and unit tests pass.

## Earlier Sprint

**Sprint 35 - Real line/column tracking for parse-error diagnostics**

Goal: Next Actions item ("add precise line/column source-position
tracking to IR adapter diagnostics (currently field/section names
only)") — Sprint 16's Deferred/Documented Gap.

Status: **Completed, narrowed scope** (see Design Notes — this closes the
parse-error layer only, not every IR adapter diagnostic; the item stays
open in Next Actions for the remainder)

### Sprint 35 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| YAML parse errors report real line/column | Done | `scripts/asf_validator/loader.py::load_yaml()` now reads `yaml.YAMLError.problem_mark` (PyYAML already computes this on every syntax error) and reports `"line {N}, column {N}"` instead of the placeholder `"<yaml>"` |
| JSON parse errors report real line **and** column | Done | `load_json()` already reported `exc.lineno`; now also includes `exc.colno` (both already computed by `json.JSONDecodeError`, only `lineno` was being used) |
| Tests | Done | New `tests/unit/test_loader.py` (3 tests): malformed YAML and malformed JSON both report a `"line N, column N"` location; valid input is unaffected |

### Sprint 35 Design Notes

- **Why this is a narrowed, not full, close of the Next Action**: the item
  as written covers "IR adapter diagnostics" broadly — that includes every
  `ASF-SCHEMA-*` (jsonschema structural validation) and IR-adapter-level
  (`ASF-PARSE-*` beyond the top-level malformed-source case) diagnostic
  across `skill_ir.py`/`workflow_ir.py`/`runtime_ir.py`/`knowledge_ir.py`/
  `tool_ir.py`/`connector_ir.py`/`evaluation_ir.py`/`reflection_ir.py` and
  the shared jsonschema validator, none of which carry a source line/column
  today (they report a field/section path, e.g. `metadata.id`). Adding
  that requires a position-preserving YAML loader (PyYAML's `safe_load`
  discards line/column once parsing succeeds — only a parse *error* still
  carries a mark) and mapping each jsonschema error's JSON-pointer path
  back to a line/column via the re-parsed-with-positions document — a
  materially larger, cross-cutting change than today's proportionate scope
  allowed. What *is* done here is real and immediately useful: the one
  place a source position was already fully computed and just not
  surfaced (parse errors) now surfaces it.
- This item stays in Next Actions, re-scoped to name exactly what remains.

### Sprint 35 Exit Criteria

- `python scripts/validate_contracts.py` (23/23 — malformed-syntax fixture
  cases still correctly resolve to `invalid`, only the diagnostic's
  location text changed), `build_ir.py` (47/47), `build_graph.py` (14/14),
  `build_semantics.py` (4/4), `validate_repository.py` (0 errors/warnings),
  `python -m unittest discover -s tests/unit` (163/163, up from 160) all
  pass.
- No existing test asserted the old placeholder location strings (`"<yaml>"`,
  bare `"line N"` without column) — confirmed by grep before changing them.

## Earlier Diagnostics Sprint

**Sprint 34 - ADR Status field mechanical check**

Status: **Completed**

New `ASF-REPOSITORY-014`: every `docs/adr/ADR-<NNNN>-*.md`'s own
`- **Status:**` field must be exactly `Proposed`, `Accepted`, or
`Superseded by ADR-<NNNN>` naming a real ADR, matching `ADR_TEMPLATE.md`'s
documented allowed values — a mechanical field-shape check only, per
`.ai/governance/DECISION_RIGHTS.md`'s existing rule that ADR acceptance
itself is a human decision. All 15 real ADRs already pass clean; 5 new
tests in `test_content_integrity.py`.

## Earlier Runtime Contract Sprint

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
| 34 | ADR Status field mechanical check | `ASF-REPOSITORY-014`, `content_integrity._validate_adr_status()`; 5 new tests; all 15 real ADRs already pass |
| 35 | Real line/column tracking for parse-error diagnostics | `loader.py`'s YAML/JSON parse errors now report a real `line N, column N`; narrowed scope (schema/semantic diagnostics still report a field path, not a line — remains open) |
| 36 | CLI implementation language and phased adoption decision | Proposed ADR-0016 selects Python, retains the existing single-module CLI until a real split trigger, confirms `validate` already wraps the shared IR/graph pipeline, and records the missing Generator implementation prerequisite |
| 37 | Ollama Runtime promotion approval and readiness | Durable human-approval scope and readiness/rollback gates for `runtime:offline@1.0.0` -> `skill:content-creation@1.0.0`; no lifecycle mutation |

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

1. Wire the approved `runtime:offline@1.0.0` into
   `skill:content-creation@1.0.0` using the existing RuntimeBinding and
   loopback-only Ollama adapter. Satisfy
   `docs/guides/RUNTIME_PROMOTION_READINESS.md`; lifecycle promotion remains
   a separate following sprint and requires truthful live Ollama evidence.
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
4. Review and accept or revise proposed ADR-0016. Python and the current
   `scripts/asf_cli.py` layout are proposed; `validate` already wraps the
   shared IR/graph pipelines. Before a real `generate` command can be added,
   implement the Generator Architecture's reference pipeline so the CLI has
   a real operation to wrap rather than a partial-success stub.
5. Extend line/column source-position tracking beyond the parse-error
   layer Sprint 35 closed. Needs: (a) a position-preserving YAML loader
   (PyYAML's `safe_load` discards line/column once parsing succeeds —
   `scripts/asf_validator/loader.py` would need a custom `Loader` that
   attaches a mark to every node, or a switch to `ruamel.yaml`), and
   (b) mapping each `ASF-SCHEMA-*`/IR-adapter-level diagnostic's field
   path back to a line/column via that position-preserving document.
   Sprint 16's original Deferred/Documented Gap, still open.
6. If pre-release versions are ever adopted, implement full SemVer
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
| 0.34 | 2026-07-12 | Completed Sprint 34: new `ASF-REPOSITORY-014` mechanical check for each ADR's Status field |
| 0.35 | 2026-07-12 | Completed Sprint 35: real line/column tracking for YAML/JSON parse-error diagnostics (narrowed scope; schema/semantic diagnostics remain open in Next Actions) |
| 0.36 | 2026-07-12 | Completed Sprint 36 as a proposal: ADR-0016 selects Python/current CLI layout, confirms existing Validator Integration, and records the missing Generator reference implementation prerequisite |
| 0.37 | 2026-07-12 | Completed Sprint 37: recorded bounded human approval and readiness/rollback gates for the local Ollama Runtime promotion; no lifecycle mutation |
