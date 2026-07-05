# ADR-0011: Runtime Planning Precedes Execution

- **Status:** Accepted
- **Date:** 2026-07-05
- **Decision owners:** Project maintainers

## Context

After Semantic Validation and Repository Discovery, the framework can load and
validate production artifacts but has no Runtime. Building an LLM or tool
executor now would combine dependency resolution, graph planning, state,
external effects, and provider contracts in one unsafe increment. The existing
Workflow Architecture already requires exact version resolution, frozen input
context, and deterministic graph construction before invocation.

## Decision

Runtime begins with a non-executing preparation layer:

1. consume the shared IR and Project Index rather than parse sources;
2. build an artifact catalog keyed by identity and version;
3. freeze one execution context;
4. resolve exact active Workflow, Skill, and Knowledge versions;
5. produce an immutable execution plan and deterministic ready-step batches;
6. define narrow pipeline Protocol interfaces without concrete executors.

The reference implementation lives in `scripts/asf_runtime/` alongside the
existing Python validation reference core. This does not create an
`AISkill.CLI` implementation or select a production deployment platform.

No Skill, LLM, tool, connector, browser, MCP server, filesystem mutation, or
external API may be invoked by this planning layer. Runtime and Tool dependency
declarations do not become graph nodes until schemas and IR adapters define
those artifact kinds.

## Consequences

### Positive

- Dependency and ordering failures are found before any side effect.
- Plans are inspectable, deterministic, testable, and suitable for later state
  persistence.
- Exact dependency versions are retained for reproducibility.
- Executor and provider contracts can evolve behind explicit interfaces.

### Costs and Tradeoffs

- A valid plan still cannot produce an output.
- Top-level input type checks do not yet enforce every field constraint.
- Optional steps, retries, reflection, and manual review are recorded but not
  executed.
- A later production Runtime may use another implementation language, but must
  preserve these model and planning contracts or supersede this ADR.

## Enforcement

Runtime code must not invoke artifact behavior during catalog construction or
planning. Tests must prove plan determinism, immutable context, exact dependency
resolution, structured planning failures, and absence of executor side effects.

## Alternatives Considered

### Implement an LLM executor first

Rejected because execution would precede deterministic resolution, planning,
state, and provider boundaries.

### Let every executor build its own graph

Rejected because it would duplicate Workflow IR interpretation and violate
ADR-0005's one-IR-many-consumers decision.

### Add placeholder Runtime/Tool graph nodes

Rejected because ADR-0010 explicitly defers those node kinds until real schemas
and IR adapters exist.

## Related Documents

- `docs/architecture/RUNTIME_ARCHITECTURE.md`
- `docs/architecture/WORKFLOW_ARCHITECTURE.md`
- `docs/architecture/IR_ARCHITECTURE.md`
- ADR-0005
- ADR-0010
