# AI Skill Framework

## Vision

Build reusable AI Skills instead of one giant prompt.

---

## Goals

- Modular
- Reusable
- Maintainable
- Testable
- Versioned

---

## Current Version

v0.1

---

## Status

Under Development

## Documentation

### Foundation

- [Project Context](PROJECT_CONTEXT.md)
- [Project Tracker](PROJECT_TRACKER.md)
- [Design Principles](docs/principles/DESIGN_PRINCIPLES.md)
- [Naming Convention](docs/principles/NAMING_CONVENTION.md)
- [Architecture Decision Records](docs/adr/) (start at `ADR-0001-repository-is-the-source-of-truth.md`)
- [AI Team](.ai/README.md) (roles, playbooks, standards, governance)

### Architecture

- [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md)
- [Knowledge Architecture](docs/architecture/KNOWLEDGE_ARCHITECTURE.md)
- [Skill Architecture](docs/architecture/SKILL_ARCHITECTURE.md)
- [Workflow Architecture](docs/architecture/WORKFLOW_ARCHITECTURE.md)
- [Evaluation Architecture](docs/architecture/EVALUATION_ARCHITECTURE.md)
- [Reflection Architecture](docs/architecture/REFLECTION_ARCHITECTURE.md)
- [Contract Validation Architecture](docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [IR Architecture](docs/architecture/IR_ARCHITECTURE.md)
- [Template Engine Architecture](docs/architecture/TEMPLATE_ENGINE_ARCHITECTURE.md)
- [Generator Architecture](docs/architecture/GENERATOR_ARCHITECTURE.md)
- [Runtime Architecture](docs/architecture/RUNTIME_ARCHITECTURE.md)
- [Tool and Connector Architecture](docs/architecture/TOOL_CONNECTOR_ARCHITECTURE.md)
- [Runtime Contract Architecture](docs/architecture/RUNTIME_CONTRACT_ARCHITECTURE.md)
- [Execution Adapter Architecture](docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md)
- [CLI Architecture](docs/architecture/CLI_ARCHITECTURE.md)

### Specifications, Schemas, and Registries

- [AI Skill Framework Specifications](docs/specifications/README.md)
- [IR Specification](docs/specifications/IR_SPECIFICATION.md)
- [Machine-Readable Schemas](schemas/README.md)
- [Template Registry](templates/README.md)

### Validation

- [Validation Guide](docs/guides/VALIDATION_GUIDE.md)
- [Compiler Lifecycle](docs/guides/COMPILER_LIFECYCLE.md)
- [Validator Roadmap](docs/roadmaps/VALIDATOR_ROADMAP.md)

### Operations

- [Monthly Operator Plan](docs/guides/MONTHLY_OPERATOR_PLAN.md) — the
  month-scoped content-skill readiness roadmap
- [Weekly Operator Plan](docs/guides/WEEKLY_OPERATOR_PLAN.md) — the
  two-week infrastructure trigger runbook (MCP SDK v2, SemVer pre-release)

## Production Skills

The first production-quality framework package,
[`skill:content-creation`](skills/content-creation/README.md). It creates short
video scripts, social posts, long-form article outlines, caption and hashtag
sets, and title and thumbnail ideas. Five canonical
[Knowledge documents](knowledge/KNOWLEDGE_INDEX.md) supply format, tone,
platform, hook, and call-to-action guidance.

Use the
[`content-brief-to-package`](workflows/content-brief-to-package/README.md)
Workflow for the end-to-end path. Its production artifacts are registered
directly in contract, IR, and graph fixture manifests.

The canonical compiler reference is the composite
[`research-content-review`](workflows/research-content-review/README.md)
Workflow. It connects Research -> Content Creation -> Review Quality through
explicit artifact mappings and stops at a Reviewed Content Package.

The second package, [`skill:research`](skills/research/README.md), turns a topic
and caller-supplied evidence into research questions, source requirements,
reliability assessments, claim-evidence mappings, calibrated findings, gaps,
citations, and a structured brief. Its
[`research-topic-to-brief`](workflows/research-topic-to-brief/README.md)
Workflow and six methodology Knowledge documents are likewise validated from
their canonical production paths. Research v1 defines artifact and reasoning
structure only; it does not browse or fetch external sources.

The third package,
[`skill:review-quality`](skills/review-quality/README.md), reviews supplied
content packages, research briefs, and generic drafts for editorial quality,
evidence alignment, tone, platform fit, CTA, pacing, and safety. It produces
traceable revisions and an `approve`, `revise`, or `reject` recommendation.
Seven foundational quality documents and the
[`draft-to-reviewed-package`](workflows/draft-to-reviewed-package/README.md)
Workflow are validated from canonical production paths. Review v1 defines the
review contract only; it does not execute an LLM or external fact-check.

## Validator Prototype

A minimal, offline conformance check for the schemas in `schemas/`:

```bash
pip install -r requirements-validator.txt
python scripts/validate_contracts.py
```

See the [Validation Guide](docs/guides/VALIDATION_GUIDE.md) and
`docs/adr/ADR-0002-prototype-contract-validator.md` for scope and rationale.

## IR Adapters and Dependency/Version Graph

`scripts/asf_validator/` turns a schema-validated Skill/Workflow/Knowledge/
Evaluation/Reflection document into the typed IR object
`docs/specifications/IR_SPECIFICATION.md` defines, and builds the
Dependency Graph / Version Graph across multiple loaded artifacts:

```bash
python scripts/build_ir.py                 # 46 IR fixture cases
python scripts/build_graph.py              # 13 multi-artifact graph scenarios
python scripts/build_semantics.py          # 4 semantic conformance scenarios
python scripts/validate_repository.py       # discover and validate canonical artifacts
python -m unittest discover -s tests/unit  # core unit tests
```

Each `adapters/<name>/` package has its own isolated test suite (own
`_bootstrap.py`, own dependency), run independently so core validator tests
never require an execution-backend dependency:

```bash
cd adapters/langgraph_runtime/tests && python -m pytest
cd adapters/mcp_tools/tests && python -m pytest
cd adapters/llamaindex_retrieval/tests && python -m pytest
cd adapters/model_invokers/tests && python -m pytest
cd adapters/publisher_adapters/tests && python -m pytest
cd adapters/ollama_execution/tests && python -m pytest
```

The semantic layer checks evaluation metric uniqueness and weight totals,
Evaluation/Reflection routing, Workflow mapping availability and types, retry
routing, unreachable steps, and Runtime Contract policy consistency. It emits
structured `ASF-SEMANTIC-*` diagnostics over typed IR and performs no
discovery or execution.

`validate_repository.py` finds the workspace using the two ADR-0007 markers,
builds a deterministic internal index, loads all canonical artifacts, and runs
every implemented validation layer. The current repository index contains 48
locations, including embedded Evaluation/Reflection locations and executable
examples, and loads 30 Skill/Workflow/Knowledge/Tool/Runtime artifacts.

Repository validation also checks local Markdown targets and section anchors,
duplicate anchors, ADR references, explicit stale canonical identities,
production placeholders, narrow obvious-secret signatures, and active
Skill/Knowledge/Runtime Contract orphan policy. Drafts and templates retain
their documented placeholder allowance.

## Runtime Preparation

`scripts/asf_runtime/` turns validated production IR into an immutable execution
context, exact dependency resolutions, and a deterministic Workflow plan. It
does not execute Skills or invoke models, tools, connectors, browsers, MCP, or
external systems. See the [Runtime Architecture](docs/architecture/RUNTIME_ARCHITECTURE.md)
and ADR-0011.

See `docs/roadmaps/VALIDATOR_ROADMAP.md` (Phases 2-3),
`docs/adr/ADR-0009-ir-adapter-package-and-scope.md`, and
`docs/adr/ADR-0010-dependency-and-version-graph-scope.md` for scope,
assumptions, and deferred work.

## Runtime Contracts

`runtime:<name>` artifacts (`runtime/<name>/runtime.yaml` or
`contracts/runtime/<name>/runtime.yaml`) bind a Skill to a model, retriever,
tools, and publisher plus timeout/retry/safety/audit/concurrency/fallback
policy — the missing link between a Skill and the adapter layer below. Five
canonical contracts ship in `runtime/`: `simple`, `content`, `research`,
`offline`, and `hybrid`. `runtime:offline` is the active, loopback-Ollama
contract consumed by `skill:content-creation`; `runtime:content` is now a draft
example. Other production Skills continue to consume their active contracts.
`asf_runtime.planner` resolves a Skill's `dependencies.runtime` reference and
that Runtime Contract's own Knowledge/Tool/fallback references, entirely at
planning time — no model, tool, retriever, or publisher is ever invoked. See
[Runtime Contract Architecture](docs/architecture/RUNTIME_CONTRACT_ARCHITECTURE.md)
and ADR-0014.

## Build vs Reuse Strategy

ASF builds contracts, shared IR, semantic validation, repository discovery,
runtime planning, evaluation, reflection, review, export planning, and the
adapter layer. It does not rebuild a graph execution engine, scheduler,
retry engine, state manager, streaming layer, tool runtime, MCP runtime,
RAG engine, vector database, publishing/auth flows, or LLM SDK — mature
open-source projects already solve those. The one bounded execution path is
local Ollama text generation for the canonical composite workflow. See
[ADR-0013](docs/adr/ADR-0013-build-vs-reuse-execution-strategy.md) for the
per-subsystem decisions and
[Execution Adapter Architecture](docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md)
for the five Protocol seams and package boundary.

`adapters/` (see [adapters/README.md](adapters/README.md)) contains the five
compile/binding packages plus the isolated local Ollama execution adapter.
Each compile package also has a Runtime Contract binding function
(ADR-0014, Phase 6) that takes an already-resolved `RuntimeIR` and produces
that adapter's descriptor/registration — no new dependency, no invocation:

| Package | Seam | Reuse target | Scope | Runtime Contract binding |
| --- | --- | --- | --- | --- |
| [`langgraph_runtime/`](adapters/langgraph_runtime/) | `PlanCompiler` | LangGraph | Compiles an `ExecutionPlan` into a `StateGraph`; never invokes it | `compile_plan(..., runtime_bindings=...)` prefers the contract's retry/timeout policy |
| [`mcp_tools/`](adapters/mcp_tools/) | `ToolBinding` | MCP Python SDK | Binds `ToolIR`/`ConnectorIR` to MCP wire types and a caller-supplied handler | `bind_runtime_tools(...)` |
| [`llamaindex_retrieval/`](adapters/llamaindex_retrieval/) | `RetrievalConfigCompiler` / `KnowledgeRetriever` | LlamaIndex + scikit-learn | Compiles config, then builds and queries a real local in-memory index with deterministic lexical hashing embeddings | `retrieval_config_from_runtime(...)` |
| [`model_invokers/`](adapters/model_invokers/) | `ModelDescriptorCompiler` / `ModelInvoker` | official Ollama SDK | Describes all supported providers; invokes loopback Ollama only and rejects cloud descriptors | `model_descriptor_from_runtime(...)` |
| [`publisher_adapters/`](adapters/publisher_adapters/) | `ExportDescriptorCompiler` / `PublisherAdapter` | local filesystem + PyYAML | Describes all targets; publishes safe local Markdown only and rejects external platforms | `export_descriptor_from_runtime(...)` |
| [`ollama_execution/`](adapters/ollama_execution/) | canonical `StepExecutor` | local Ollama | Runs only Research -> Content -> Review with explicit opt-in; no cloud, rendering, or publishing | consumes resolved `RuntimeBinding`; `--model` overrides non-Ollama production bindings locally |

Every package ships its own `requirements-<name>.txt`, isolated from
`requirements-validator.txt` and from every other adapter package (adapters
never import each other).

## ASF CLI

The offline CLI composes the same Validator, IR, graph, Runtime Binding,
Planner, and LangGraph adapter APIs used by the test suites:

```bash
python scripts/asf.py validate
python scripts/asf.py build-ir
python scripts/asf.py graph
python scripts/asf.py doctor
python scripts/asf.py bindings --workflow workflow:research-topic-to-brief --inputs "{\"topic\":\"Determinism\",\"objective\":\"Prepare a brief.\"}"
python scripts/asf.py plan --workflow workflow:research-topic-to-brief --inputs "{\"topic\":\"Determinism\",\"objective\":\"Prepare a brief.\"}"
python scripts/asf.py compile --workflow workflow:research-topic-to-brief --inputs "{\"topic\":\"Determinism\",\"objective\":\"Prepare a brief.\"}"
python scripts/asf.py compile content-workflow
python scripts/asf.py snapshot
python scripts/asf.py inspect
python scripts/asf.py explain
python scripts/asf.py run content-workflow --topic "Local AI" --mode dry-run
python scripts/asf.py run content-workflow --topic "Local AI" --mode live-local --model llama3
```

Use `--format json` before the command for a versioned structured report.
`compile` returns a compiled `StateGraph` description only. `run` defaults to
dry-run and calls no model. `live-local` is the only execution mode and accepts
only a loopback Ollama endpoint. No command renders or publishes.
