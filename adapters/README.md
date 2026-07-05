# Adapters

Each subdirectory here implements one Protocol seam from
[Execution Adapter Architecture](../docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md)
against exactly one external execution backend, per
[ADR-0013](../docs/adr/ADR-0013-build-vs-reuse-execution-strategy.md).

An adapter package:

- imports IR/model types from `scripts/asf_validator` and/or
  `scripts/asf_runtime`, plus exactly one external framework;
- never imports another adapter package;
- ships its own `requirements-<name>.txt` so core validator/runtime
  dependencies stay untouched by execution-backend churn;
- translates ASF's already-validated contracts into the backend's native
  constructs and back;
- owns only the bounded behavior declared by its seam. Compile-only adapters
  never execute; the Ollama adapter performs only explicit local text
  generation for the canonical composite workflow.

| Package | Seam | Reuse target |
| --- | --- | --- |
| [`mcp_tools/`](mcp_tools/) | `ToolBinding` | MCP Python SDK (`mcp`) |
| [`langgraph_runtime/`](langgraph_runtime/) | `PlanCompiler` | LangGraph (`langgraph`) |
| [`llamaindex_retrieval/`](llamaindex_retrieval/) | `RetrievalConfigCompiler` (config half of `KnowledgeRetriever`) | LlamaIndex (`llama-index-core`) |
| [`model_invokers/`](model_invokers/) | `ModelDescriptorCompiler` (descriptor half of `ModelInvoker`) | none yet — declarative only, no SDK dependency (Priority 3) |
| [`publisher_adapters/`](publisher_adapters/) | `ExportDescriptorCompiler` (descriptor half of `PublisherAdapter`) | none yet — declarative only, no SDK dependency (Priority 4) |
| [`ollama_execution/`](ollama_execution/) | Canonical composite `StepExecutor` | local Ollama HTTP API, loopback only |
