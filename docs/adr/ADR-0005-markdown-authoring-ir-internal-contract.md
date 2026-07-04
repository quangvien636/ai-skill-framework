# ADR-0005: Markdown/YAML Is the Authoring Format; IR Is the Internal Contract

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

The Contract Validation Architecture (Sprint 7) already defined a
"normalized model": a tool-neutral object produced from YAML or Markdown
and checked against `schemas/*.schema.json`. It was scoped only to
validation. Sprint 9's CLI Architecture and Sprint 10's Template Engine
Architecture both anticipate a Generator and a Runtime that will need the
same kind of object — a Generator must decide what to emit without
re-parsing Markdown, and a future Runtime must execute a Skill/Workflow
without re-parsing YAML on every step.

Without a named, cross-cutting concept, each of Validator, Generator, CLI,
and Runtime would either duplicate parsing logic or invent slightly
different in-memory shapes for "a parsed Skill," risking the exact drift
this framework's Documentation-First and reuse principles exist to prevent.
There is also a risk of accidentally treating the parsed object as a second
source of truth (for example, caching it to disk and letting it drift from
the Markdown/YAML it was derived from), which would contradict ADR-0001.

## Decision

Sprint 11 promotes the existing "normalized model" concept to a named,
first-class **Intermediate Representation (IR)**, documented in
`docs/architecture/IR_ARCHITECTURE.md` and
`docs/specifications/IR_SPECIFICATION.md`:

- Markdown (Knowledge) and YAML (Skill, Workflow) remain the durable,
  Git-tracked, human-authored **source**. This does not change ADR-0001.
- The IR is the **internal contract**: the only shape the Validator,
  Generator, CLI, and future Runtime are allowed to consume. None of them
  parses source directly; all of them consume the output of one shared IR
  adapter (parser + normalizer) per source format.
- IR is transient. It is rebuilt from source per invocation, MAY be
  serialized to JSON for one build/process handoff, and MUST NOT be
  committed or treated as authoritative.
- Two new Graph IR constructs — the Dependency Graph and Version Graph —
  are introduced as derived, read-only views built from multiple artifacts'
  IR, to support cross-artifact checks (orphans, cycles, impact analysis)
  that no single artifact's IR can answer alone.

`docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md`,
`docs/architecture/CLI_ARCHITECTURE.md`, and `schemas/README.md` are updated
in the same change to use "IR" as the primary term, with "normalized model"
kept as a recognized synonym where it already appeared, so existing
cross-references are not broken.

No parser, normalizer, Generator, or Runtime is implemented in this sprint.

## Consequences

### Positive

- Generator (Milestone 12) and a future Runtime can be specified against
  the same IR the Validator already exercises via the Sprint 8 prototype,
  instead of each defining its own parsed-object shape.
- The Dependency Graph and Version Graph give the Quality Platform
  (Milestone 14 in the prior instruction set) and future breaking-change
  tooling one shared structure instead of ad hoc reference-walking code
  per tool.
- Naming the concept once prevents the "several inconsistent ad hoc
  entrypoints" failure mode already rejected for the CLI in ADR-0003, now
  extended to parsing.

### Costs and Tradeoffs

- Introduces one more named concept (IR) contributors must learn, on top of
  "manifest," "normalized model," and "artifact" already in use; this ADR
  and the updated documents treat "normalized model" as a synonym rather
  than deleting the term, to limit churn.
- The Workflow IR's "built step graph" is now specified as part of the IR
  rather than something each consumer recomputes; any future change to
  graph-building logic (Workflow Architecture's Execution Model) must keep
  the IR Specification's description in sync.

## Enforcement

Any future parser, Generator, CLI command, or Runtime component MUST consume
IR, not source, for framework-specific decisions. A new artifact type MUST
add one IR adapter and one schema (per the IR Architecture's Extension
Points section), not one adapter per consumer. Reviews must check that
`CONTRACT_VALIDATION_ARCHITECTURE.md`, `CLI_ARCHITECTURE.md`, and
`schemas/README.md` stay consistent with the IR Specification's vocabulary.

## Alternatives Considered

### Let each consumer (Validator, Generator, CLI, Runtime) parse source independently

Rejected because it repeats the "one giant prompt" / duplicated-logic
failure mode this framework already rejects for Skills (Design Principle 5)
and for the CLI (ADR-0003), and because it risks the four consumers
silently disagreeing about what a Skill or Workflow means.

### Treat the IR as a new stored artifact with its own version

Rejected because it would create a second source of truth alongside
Markdown/YAML, directly contradicting ADR-0001. The IR is deliberately
transient and rebuilt from source.

### Defer naming the IR until the Generator Engine architecture needs it

Rejected because the CLI Architecture and Template Engine Architecture
already assume a shared parsed-object concept exists; naming it now, before
Generator design, lets Milestone 12 specify against a stable contract
instead of retrofitting one.

## Related Documents

- `docs/architecture/IR_ARCHITECTURE.md`
- `docs/specifications/IR_SPECIFICATION.md`
- `docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md`
- `docs/architecture/CLI_ARCHITECTURE.md`
- ADR-0001
- ADR-0003
