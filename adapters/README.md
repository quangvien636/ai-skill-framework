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
  constructs and back — it never implements execution, retries, transport,
  or storage itself.

| Package | Seam | Reuse target |
| --- | --- | --- |
| [`mcp_tools/`](mcp_tools/) | `ToolBinding` | MCP Python SDK (`mcp`) |
| [`langgraph_runtime/`](langgraph_runtime/) | `PlanCompiler` | LangGraph (`langgraph`) |
| [`llamaindex_retrieval/`](llamaindex_retrieval/) | `RetrievalConfigCompiler` (config half of `KnowledgeRetriever`) | LlamaIndex (`llama-index-core`) |
