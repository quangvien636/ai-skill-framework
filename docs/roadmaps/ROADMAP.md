# Roadmap

Version: 0.10
Status: Active

## Purpose

Summarize delivered framework capabilities and the next bounded development
directions. Detailed validator work remains in `VALIDATOR_ROADMAP.md`.

## Scope

- Foundation architecture, specifications, schemas, templates, and governance.
- Production Skill and Knowledge packages.
- Validator, IR, dependency graph, and version graph evolution.
- Future execution, discovery, and interface layers.

## Notes

- Completed: framework foundation and schema contracts (Sprints 1-15).
- Completed: IR adapters and dependency/version graphs (Sprints 16-17).
- Completed: Content Creation v1 production package (Sprint 18).
- Completed: Research v1 production package (Sprint 19).
- Completed: Review Quality v1 production package (Sprint 20).
- Completed: IR-level semantic validation for metrics, routing, mappings,
  types, and Workflow topology (Sprint 21).
- Completed: deterministic workspace/project discovery plus canonical
  path/package/Knowledge Index integrity (Sprint 22).
- Completed: immutable Runtime catalog, execution context, dependency
  resolution, and Workflow planning (Sprint 23).
- Completed: bounded Repository Integrity content, secret, stale-reference, and
  lifecycle rules (Sprint 24).
- Completed: Tool and Connector contracts, IR, discovery, and dependency graph
  nodes/edges (Sprint 25, ADR-0012).
- Completed: adopted a Build vs Reuse execution strategy -- ASF no longer
  builds execution-layer subsystems (graph engine, scheduler, retries, tool/
  MCP runtime, RAG engine, LLM SDKs); adapters bind ASF's validated IR/plans
  to external frameworks instead (Sprint 26, ADR-0013).
- Completed: implemented the compile/describe half of all five adapter
  Protocol seams -- `langgraph_runtime` (`PlanCompiler`), `mcp_tools`
  (`ToolBinding`), `llamaindex_retrieval` (`RetrievalConfigCompiler`),
  `model_invokers` (`ModelDescriptorCompiler`), `publisher_adapters`
  (`ExportDescriptorCompiler`) (Sprint 27).
- Completed: Runtime Contract -- the declarative artifact binding a Skill to
  a model/retriever/tools/publisher plus timeout/retry/safety/audit/
  concurrency/fallback policy. Schema, IR, discovery, dependency graph edges,
  semantic validation, lifecycle orphan policy, Runtime Planning resolution,
  adapter binding functions for all five adapters, and five canonical
  examples (Sprint 28, ADR-0014).
- Next: design a Runtime contract schema extension (or a small resolution
  convention) so a Skill's `dependencies.runtime` can be wired to a real,
  active Runtime Contract in production -- the five Sprint 28 examples are
  intentionally `draft` and not yet consumed by any Skill.
- Later: implement the execute halves every compile-only adapter deferred
  (`KnowledgeRetriever.query`, `ModelInvoker.invoke`,
  `PublisherAdapter.publish`, an actually-invoked `PlanCompiler` graph),
  each behind its own Build vs Reuse note, plus a thin CLI interface.
  Production Skills and Runtime Contracts intentionally define artifact,
  reasoning, and binding contracts without live execution or retrieval.

## Revision History

| Version | Date | Description |
|---------|------|-------------|
| 0.1 | 2026-07-04 | Initial draft |
| 0.2 | 2026-07-05 | Recorded production Skill milestones and next framework phases. |
| 0.3 | 2026-07-05 | Recorded Review Quality v1 as the third production Skill package. |
| 0.4 | 2026-07-05 | Recorded the Sprint 21 IR-level Semantic Validator milestone. |
| 0.5 | 2026-07-05 | Recorded the Sprint 22 Repository Discovery and integrity milestone. |
| 0.6 | 2026-07-05 | Recorded the Sprint 23 non-executing Runtime planning milestone. |
| 0.7 | 2026-07-05 | Recorded Sprint 24 completion of Repository Integrity Phase 4. |
| 0.8 | 2026-07-05 | Recorded Sprint 25 Tool/Connector contracts and Sprint 26 Build vs Reuse execution strategy. |
| 0.9 | 2026-07-05 | Recorded Sprint 27 adapter layer build-out (all five Protocol seams, compile/describe half). |
| 0.10 | 2026-07-05 | Recorded Sprint 28 Runtime Contract milestone (schema, IR, discovery, graph, semantic, planning, adapter binding, five canonical examples). |
