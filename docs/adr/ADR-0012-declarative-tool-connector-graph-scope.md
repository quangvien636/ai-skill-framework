# ADR-0012: Tool and Connector Contracts Are Declarative Graph Resources

- **Status:** Accepted
- **Date:** 2026-07-05
- **Decision owners:** Project maintainers

## Context

Skills already declare `dependencies.tools` as versioned references, but the
framework has no Tool contract or graph node to resolve them against. Connector
definitions are also needed before Runtime can safely integrate providers such
as LLMs, browsers, search, filesystems, MCP servers, or business systems.
Adding execution while identities, safety, authentication, audit, and lifecycle
contracts are undefined would make provider behavior implicit and unreviewable.

ADR-0010 deliberately excluded Tool and Runtime graph nodes until real schemas
and IR adapters existed. This milestone introduces Tool and Connector contracts,
so their graph scope must now be explicit.

## Decision

1. Tool and Connector manifests are declarative, versioned repository artifacts.
   They describe capabilities and boundaries but contain no credentials,
   executable code, provider clients, runtime state, or invocation behavior.
2. Canonical identities and paths are:
   - `tool:<name>` at `tools/<name>/tool.yaml`;
   - `connector:<name>` at `connectors/<name>/connector.yaml`.
3. Tool and Connector artifacts become Dependency/Version Graph nodes once
   their IR adapters successfully build them.
4. Existing `Skill.dependencies.tools` references create `skill-tool` edges.
   These edges mean “requires this declared capability,” not “invoke now.”
5. No Connector edges are created in this milestone. Existing Skill and
   Workflow schemas have no Connector reference field, and inventing one merely
   to populate the graph would violate the artifact boundary. Workflows consume
   Tools indirectly through referenced Skills.
6. Tool/Connector lifecycle uses the common `draft`, `active`, `deprecated`,
   and `archived` states. Normal dependency version and lifecycle diagnostics
   apply to Tool nodes.
7. Structural validation owns contract fields; IR adapters own normalization;
   Project Discovery owns enumeration; repository validation owns canonical
   paths/packages; graph validation owns reference existence and version
   compatibility.

## Explicitly Deferred

- Tool, Connector, LLM, browser, search, filesystem, or MCP execution.
- Credentials, secret values, token acquisition, and auth refresh.
- Network access, queues, workers, rate-limit enforcement, retries, and timeout
  enforcement.
- Connector references or edges until an owning artifact schema declares them.
- Runtime/Tool invocation edges and execution-state graph nodes.
- Vendor-specific implementations or fake production Tools/Connectors.

## Consequences

### Positive

- Existing Skill Tool dependencies become resolvable without implying execution.
- Safety, side effects, network needs, authentication shape, errors, and audit
  expectations are reviewable before provider code exists.
- Connector resources can be discovered and validated without synthetic edges.

### Costs and Tradeoffs

- Connector nodes may have no graph edges until a future contract owns a
  Connector reference.
- A valid Tool contract proves declarative conformance, not availability or safe
  execution.
- Adding Connector references later requires a compatible schema and graph
  extension.

## Enforcement

Schemas and IR must contain declarations only. Graph construction must create
only edges backed by source artifact references. Tests must prove that no
execution, credentials, network calls, or placeholder graph nodes are added.

## Related Documents

- `docs/architecture/TOOL_CONNECTOR_ARCHITECTURE.md`
- `docs/specifications/IR_SPECIFICATION.md`
- `docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md`
- ADR-0005
- ADR-0010
- ADR-0011
