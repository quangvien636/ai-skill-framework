# AI Skill Framework - Project Context

Version: 0.34
Status: Active
Last updated: 2026-07-12

## Purpose

This document gives human and AI contributors the minimum shared context required
to work consistently on the AI Skill Framework.

## Vision

Build a modular, reusable, testable, and maintainable framework for AI-assisted
software development, writing, research, and workflow automation. The framework
is a long-lived system of skills and knowledge, not a collection of giant prompts.

## Source of Truth

This repository is the authoritative project record. Architecture, decisions,
requirements, skills, workflows, reusable knowledge, tests, and project status
must be represented here and versioned with Git.

Conversation history, model memory, local notes outside the repository, and
generated output are not authoritative. If they conflict with the repository,
contributors must follow the repository or propose a documented change.

## Contributor Model

AI models are contributors, not owners or sources of truth. An AI contributor
must read the relevant repository documentation before making a change, preserve
existing decisions, state assumptions, and record durable knowledge in the
appropriate repository artifact.

Human contributors remain responsible for project direction and approval.

## Architecture

The architecture separates orchestration, execution, knowledge, and quality:

```text
User
  -> Master Skill
  -> Workflow Engine
  -> Skill Library
  -> Knowledge Base
  -> Evaluation Engine
  -> Reflection Engine
  -> Final Output
```

- The **Master Skill** is a thin orchestrator. It detects intent, selects a
  workflow and skills, coordinates execution, and combines results. Specialized
  business logic does not belong in it.
- The **Workflow Engine** defines execution order without embedding deep domain
  knowledge.
- The **Skill Library** contains focused capabilities. One Skill has one
  responsibility.
- The **Knowledge Base** stores reusable domain knowledge separately from prompts
  and skills.
- The **Evaluation Engine** checks output quality.
- The **Reflection Engine** improves output before delivery.

See [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md) for the
component-level description.

## Working Principles

1. Repository is the source of truth.
2. Documentation comes before implementation.
3. AI models contribute through documented, reviewable changes.
4. Keep the Master Skill focused on orchestration.
5. One Skill = One Responsibility.
6. Keep reusable knowledge separate from prompts.
7. Reuse existing components before creating new ones.
8. Evaluate and reflect on outputs.
9. Record significant architectural decisions as ADRs.

## Documentation-First Workflow

1. Read `PROJECT_CONTEXT.md` and the relevant architecture, principles, and ADRs.
2. Confirm the requirement against the current project tracker.
3. Document new decisions or update affected documentation.
4. Implement the smallest architecture-aligned change.
5. Review and test the change.
6. Update the tracker and other affected repository documents.
7. Commit and push a coherent change set.

## Current Focus

The project's strategy changed: ASF builds only its differentiated
intellectual property (Skill/Knowledge/Workflow frameworks, contracts,
shared IR, semantic validation, repository discovery, runtime planning,
evaluation, reflection, review, and the adapter layer) and reuses mature
open-source projects for everything else — a graph execution engine,
scheduler, retry engine, state management, streaming, tool/MCP runtime,
RAG/vector engine, and LLM SDKs are no longer things ASF builds. See
`docs/adr/ADR-0013-build-vs-reuse-execution-strategy.md` and
`docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`.

The project completed **Sprint 25 - Tool and Connector Contracts**,
**Sprint 26 - Build vs Reuse Execution Strategy** (ADR-0013, the adapter
Protocol seams, and a first working adapter, `adapters/mcp_tools/`),
**Sprint 27 - Adapter Layer Build-Out** (the compile-only half of every
remaining seam across all five `adapters/` packages), and **Sprint 28 -
Runtime Contract** (ADR-0014): the declarative artifact binding a Skill to
a model, retriever, tools, and publisher plus timeout/retry/safety/audit/
concurrency/fallback policy — the missing link between a Skill and the
adapter descriptors Sprint 27 built. Runtime Contracts (`runtime:<name>` at
`runtime/<name>/runtime.yaml`) have a schema, IR, repository discovery
(`runtime/`, `contracts/runtime/`), Dependency Graph edges
(`skill-runtime`, `runtime-knowledge`, `runtime-tool`, `runtime-runtime`,
all resolved by the existing generic missing-dependency/duplicate-id/cycle
mechanisms), seven new semantic rules (`ASF-SEMANTIC-010..016`, mostly
"`enabled` disagrees with configured content"), lifecycle orphan coverage,
and Runtime Planning resolution (`asf_runtime.planner` now resolves Skill
-> Runtime Contract -> Knowledge/Tool/fallback-Runtime). All five adapters
gained a binding function that converts a resolved `RuntimeIR` into that
adapter's existing descriptor — `model_descriptor_from_runtime`,
`retrieval_config_from_runtime`, `bind_runtime_tools`,
`export_descriptor_from_runtime`, and `compile_plan(...,
runtime_bindings=...)` — still binding only, never invoking. Five canonical
examples ship in `runtime/` (`simple`, `content`, `research`, `offline`,
`hybrid`, all `status: draft`), plus the first real production Tool
artifact, `tools/read-file/tool.yaml`.

**Sprint 29** proved the canonical three-Skill composite (Research ->
Content Creation -> Review) compiles end-to-end without execution: explicit
artifact flow, a Reviewed Content Package boundary, golden snapshots, and a
composite CLI (`workflows/research-content-review/`). **Sprint 30** added
the framework's first adapter that actually executes something for real:
`adapters/ollama_execution`'s loopback-only `OllamaStepExecutor` runs the
canonical composite workflow through a local Ollama model (dry-run default;
live-local requires an explicit mode and model, no API key, no cloud path),
plus a deterministic topic-relevance semantic gate with word-boundary
domain matching for its content pipeline. **Sprint 31** adopted
**ADR-0015** (Dependency Resolution and Runtime Binding): a Dependency
Resolver (`scripts/asf_runtime/dependency_resolver.py`) that walks a
Runtime Contract's fallback chain and resolves inheritance/override per
capability, a `RuntimeBinding`/`BindingIR` engine
(`scripts/asf_runtime/binding.py`) that is the single resolved source of a
Skill's runtime dependencies, seven new `ASF-BINDING-001..007` diagnostics,
and -- closing ADR-0015 Section 5, the piece Sprint 28's Phase 6 explicitly
deferred -- an additive `*_from_binding` function on each of the five
adapters (`model_descriptor_from_binding`, `retrieval_config_from_binding`,
`bind_binding_tools`, `export_descriptor_from_binding`,
`compile_plan_from_binding`), every existing `*_from_runtime` function left
untouched. All prior validation and Runtime planning remain green, with 154
passing core unit tests plus 66 passing adapter tests across all five
compile-only packages, each exercised against its real dependency (no
mocking).

The framework still has no live executor process for the general case --
planning (ADR-0011) produces an `ExecutionPlan`, Runtime Contracts describe
a binding, and `langgraph_runtime`/`llamaindex_retrieval`/`model_invokers`/
`publisher_adapters`/`mcp_tools` compile/describe/bind, but none of them
yet invokes a compiled LangGraph graph, runs a live MCP server, queries a
real LlamaIndex index, calls a cloud model provider, or publishes to a
platform. That gap is intentional and permanent by policy for the
graph/tool/retrieval execution itself (closed by adapters calling into
external frameworks, never a native ASF executor); for model invocation and
publishing specifically, it is also incomplete by explicit scope -- Runtime
Contract binding (both the `*_from_runtime` and new `*_from_binding` forms)
extends the same "describe, never execute" boundary Priorities 3 and 4
established. The one exception is `adapters/ollama_execution` (Sprint 30):
it consumes a resolved `RuntimeBinding` directly and makes a real local
Ollama call, but through its own bespoke `StepExecutor`, not through
`langgraph_runtime`'s compiled graph or `model_invokers`' `ModelDescriptor`.

**Sprint 32** proved that second path works too, in a real, opt-in,
loopback-only test (`adapters/langgraph_runtime/tests/
test_live_ollama_invocation.py`, `ASF_TEST_OLLAMA=1`): a real
`RuntimeBinding` built from the canonical `runtime/offline/runtime.yaml`
example (`provider: ollama`), a `ModelDescriptor` obtained through
`model_invokers.model_descriptor_from_binding`, a graph compiled by
`langgraph_runtime.compile_plan_from_binding`, and a real
`await compiled.ainvoke({})` that made an actual local Ollama call and
returned real generated text through graph state -- run for real against
an installed local Ollama server, not just skip-verified. This sprint also
found that one of the framework's own Next Actions was stale: `runtime:
content` has been `status: active` and wired into `skill:content-creation`'s
`dependencies.runtime` since a pre-Sprint-31 commit (`37556ae`), not
still-pending as the tracker previously said. Wiring the Ollama-backed
example into an actual production Skill and promoting its status remains
open -- per `.ai/governance/DECISION_RIGHTS.md`, lifecycle promotion past
`draft` is a human/reviewed decision, not something this session performs
unilaterally. See `PROJECT_TRACKER.md`'s Next Actions for the remaining
work.

**Sprint 36** drafted ADR-0016 to record Python and the existing
`scripts/asf_cli.py` module as the CLI's current implementation choice. The
existing `validate` path already reuses Project Discovery, IR construction,
dependency/version graph construction, semantic validation, and repository
validation; no parallel CLI is needed. Generator Integration remains blocked
on a real Generator Architecture reference implementation, so no placeholder
`generate` command was added. ADR-0016 remains `Proposed` pending the human
acceptance required by `.ai/governance/DECISION_RIGHTS.md`.

## Definition of Done

A change is complete when:

- repository documentation and project status are current;
- the change follows the documented architecture and design principles;
- applicable review and tests have passed;
- significant decisions are captured in ADRs;
- the coherent change set is committed and pushed;
- the working tree is clean for the completed scope.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established shared context and contributor rules |
| 0.2 | 2026-07-04 | Set Sprint 2 Knowledge Architecture as current focus |
| 0.3 | 2026-07-04 | Set Sprint 3 AI Skill Specification as current focus |
| 0.4 | 2026-07-04 | Set Sprint 4 Skill Architecture as current focus |
| 0.5 | 2026-07-04 | Set Sprint 5 Workflow Architecture as current focus |
| 0.6 | 2026-07-04 | Set Sprint 6 quality architecture as current focus |
| 0.7 | 2026-07-04 | Set Sprint 7 schema and validation focus |
| 0.8 | 2026-07-04 | Set Sprint 8 validator prototype as current focus |
| 0.9 | 2026-07-04 | Set Sprint 9 CLI architecture as current focus |
| 0.10 | 2026-07-04 | Set Sprint 10 Template Engine as current focus |
| 0.11 | 2026-07-04 | Set Sprint 11 Intermediate Representation as current focus |
| 0.12 | 2026-07-04 | Set Sprint 12 Generator Engine architecture as current focus |
| 0.13 | 2026-07-04 | Set Sprint 13 CLI Design Expansion as current focus |
| 0.14 | 2026-07-04 | Completed Sprint 14 Repository Engineering Review |
| 0.15 | 2026-07-04 | Set Sprint 15 AI Team Architecture as current focus |
| 0.16 | 2026-07-04 | Completed Sprint 16 Validator Roadmap Phase 2 (IR adapters) |
| 0.17 | 2026-07-04 | Completed Sprint 17 Validator Roadmap Phase 3 (Dependency/Version Graph) |
| 0.18 | 2026-07-05 | Completed Sprint 18 Content Creation Skill v1 production package |
| 0.19 | 2026-07-05 | Completed Sprint 19 Research Skill v1 production package |
| 0.20 | 2026-07-05 | Completed Sprint 20 Review Quality Skill v1 production package |
| 0.21 | 2026-07-05 | Completed Sprint 21 IR-level Semantic Validator core |
| 0.22 | 2026-07-05 | Completed Sprint 22 Repository Discovery and initial integrity validation |
| 0.23 | 2026-07-05 | Completed Sprint 23 non-executing Runtime planning foundation |
| 0.24 | 2026-07-05 | Completed Sprint 24 bounded Repository Integrity rules |
| 0.25 | 2026-07-05 | Completed Sprint 25 Tool and Connector Contracts |
| 0.26 | 2026-07-05 | Adopted Build vs Reuse execution strategy (Sprint 26); framework no longer builds execution-layer subsystems |
| 0.27 | 2026-07-05 | Completed Sprint 27: implemented the compile/describe half of all five adapter Protocol seams |
| 0.28 | 2026-07-05 | Completed Sprint 28: Runtime Contract (schema, IR, discovery, graph, semantic, planning, adapter binding, 5 canonical examples), ADR-0014 |
| 0.29 | 2026-07-12 | Documented Sprints 29-31: composite compiler proof, local Ollama execution adapter, and ADR-0015 (Dependency Resolver, RuntimeBinding/BindingIR, 5 adapter `*_from_binding` functions) |
| 0.30 | 2026-07-12 | Completed Sprint 32: first real invoked LangGraph run via `compile_plan_from_binding`/`model_descriptor_from_binding`/local Ollama; corrected a stale claim about Runtime Contract -> production Skill wiring |
| 0.31 | 2026-07-12 | Completed Sprint 33: `scripts/asf_cli.py`'s `bindings` command reports `ASF-BINDING-001` as a diagnostic instead of raising |
| 0.32 | 2026-07-12 | Completed Sprint 34: new `ASF-REPOSITORY-014` mechanical check for each ADR's Status field |
| 0.33 | 2026-07-12 | Completed Sprint 35: real line/column tracking for YAML/JSON parse-error diagnostics (narrowed scope) |
| 0.34 | 2026-07-12 | Completed Sprint 36 as a proposal: recorded the Python/current-module CLI choice in proposed ADR-0016, confirmed existing Validator Integration, and documented the Generator implementation prerequisite |
