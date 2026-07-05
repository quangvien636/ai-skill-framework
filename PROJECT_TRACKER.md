# AI Skill Framework - Project Tracker

Version: 0.26
Status: Active
Last updated: 2026-07-05

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 26 - Build vs Reuse Execution Strategy**

Goal: stop building execution-layer subsystems the framework does not
differentiate on, and adopt mature OSS behind an explicit adapter layer,
per the "do not reinvent solved problems" strategy change.

Status: **Completed (first adapter proven); roadmap continues into Sprint 27**

### Sprint 26 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Record the Build vs Reuse policy and per-subsystem decisions | Done | `docs/adr/ADR-0013-build-vs-reuse-execution-strategy.md` |
| Define adapter Protocol seams and package boundary | Done | `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md` |
| Prove the pattern with one real adapter | Done | `adapters/mcp_tools/` (ToolBinding seam, MCP Python SDK, 3 passing tests) |
| Point Runtime Architecture's next-steps at adapters instead of an implied native executor | Done | `RUNTIME_ARCHITECTURE.md` v0.2 |

### Sprint 26 Exit Criteria

- `python scripts/validate_contracts.py` passes 20/20.
- `python scripts/validate_repository.py` reports zero errors and warnings.
- `python -m unittest discover -s tests/unit` passes all 106 tests.
- `adapters/mcp_tools/tests/test_binding.py` passes 3/3 against the real
  `mcp` package (no mocking of the reuse target).
- No execution-backend dependency (`mcp`, or any future `langgraph`/
  `llama-index`) appears in `requirements-validator.txt` or is imported by
  `scripts/asf_validator/` or `scripts/asf_runtime/`.

### Sprint 26 Deferred / Documented Gaps

- Only the `ToolBinding` seam has a concrete adapter. `PlanCompiler`
  (LangGraph), `KnowledgeRetriever` (LlamaIndex), and `ModelInvoker`
  (provider SDKs / Ollama) are specified in
  `EXECUTION_ADAPTER_ARCHITECTURE.md` but not yet implemented.
- The `mcp_tools` adapter is pinned to MCP SDK v1 (`mcp>=1.27,<2`). v2 lands
  2026-07-27 and renames `FastMCP` to `MCPServer`; migrating is untracked
  work until that release is stable.
- No adapter is wired into a live server/graph process; `MCPToolRegistry`
  is exercised only via direct unit tests, not an end-to-end MCP session.

## Previous Sprint

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

1. Implement the `PlanCompiler` adapter (`adapters/langgraph_runtime/`):
   compile an `ExecutionPlan` into a LangGraph `StateGraph` (steps -> nodes,
   `depends_on` -> edges, `on_error`/`max_attempts` -> `RetryPolicy`), per
   `EXECUTION_ADAPTER_ARCHITECTURE.md`. This is the highest-value next
   adapter: it is the seam every Workflow execution eventually needs.
2. Implement the `KnowledgeRetriever` adapter (`adapters/llamaindex_retrieval/`)
   over resolved Knowledge documents.
3. Implement `ModelInvoker` adapter(s) (`adapters/model_invokers/`) for at
   least one provider SDK plus Ollama, selected by a Skill's
   `dependencies.runtime` reference.
4. Track the MCP Python SDK v2 release (stable target 2026-07-27): re-check
   `adapters/mcp_tools/` against the new `MCPServer` naming and API once it
   ships, and update the `mcp>=1.27,<2` pin deliberately rather than
   incidentally.
5. Wire at least one adapter into a live end-to-end example (a real MCP
   server process, or a compiled-and-invoked LangGraph run) — current
   adapter tests exercise the translation logic only, not a live session.
6. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`,
   and wire `scripts/build_ir.py`/`scripts/build_graph.py`'s pipelines
   behind the `validate`/`generate` commands per `CLI_ARCHITECTURE.md`'s
   Validator/Generator Integration.
7. Consider whether `.ai/governance/DECISION_RIGHTS.md`'s ADR-acceptance
   convention needs a lighter-weight mechanical check (e.g., an ADR
   "Status" field the validator confirms is one of the allowed values).
8. Add precise line/column source-position tracking to IR adapter
   diagnostics (currently field/section names only) — Sprint 16's
   Deferred / Documented Gap, still open.
9. If pre-release versions are ever adopted, implement full SemVer
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
