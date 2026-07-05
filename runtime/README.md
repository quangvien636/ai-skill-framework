# Runtime

Runtime implementation is currently limited to non-executing preparation:

- immutable execution context and plan models;
- an artifact catalog built from shared IR;
- exact Workflow, Skill, and Knowledge dependency resolution;
- deterministic topological planning and parallel-ready batches;
- tool-neutral loader, catalog, planner, and plan-store interfaces.

The implementation lives in `scripts/asf_runtime/` while the framework remains
a Python validation/reference prototype. It consumes the shared IR and Project
Index and does not parse artifacts independently.

There is no Skill executor, LLM invocation, tool call, connector, retry loop,
state persistence implementation, or external side effect.
