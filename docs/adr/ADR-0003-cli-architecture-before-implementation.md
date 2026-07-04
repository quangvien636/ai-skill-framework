# ADR-0003: CLI Gets an Architecture Before Any Implementation Language Is Chosen

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

Sprint 8 shipped a minimal Python fixture-conformance script
(`scripts/validate_contracts.py`, ADR-0002) as Validator Roadmap Phase 1. The
Validator Roadmap's Phase 5 ("Thin Interfaces") and the framework's own
Documentation-First principle both call for a CLI shape to exist before a CLI
is built, so that the fixture script, and future generator/template tooling,
have one stable command, plugin, and configuration contract to grow into
instead of each tool inventing its own.

There is pressure to jump straight to a concrete CLI implementation (a
specific language, framework, and package layout) because the validator
prototype and future generator work both want a real entrypoint. Doing that
now would fix a language and dependency footprint before the Template Engine
(Milestone 10) and Generator Engine (Milestone 11) architectures exist, and
before more than one real command (`validate`) has a use case to design
against.

## Decision

Sprint 9 defines `docs/architecture/CLI_ARCHITECTURE.md`: the command system,
plugin model, extension points, dependency-injection strategy, configuration
precedence, logging shape, and error/exit-code contract for `AISkill.CLI`.
`AISkill.CLI` is treated as a logical component name in this document, not a
committed namespace or language.

No CLI code, package manifest, or dependency is added in this sprint. The
concrete implementation language and package structure are deferred to the
sprint that first implements a real command (expected to be the `validate`
command wrapping the Sprint 8 script), and that sprint must record its
language/runtime choice in its own ADR rather than silently assuming this
one.

## Consequences

### Positive

- Future commands (`validate`, and later `skill new`, `workflow inspect`,
  generator commands) share one documented contract for arguments, exit
  codes, configuration precedence, and diagnostics shape instead of each
  wrapper improvising its own.
- The plugin/extension-point split lets the Template Engine and Generator
  Engine (Milestones 10-11) register as CLI extensions later without a CLI
  core rewrite.
- Deferring the language choice avoids constraining Milestones 10-11 to
  whatever runtime the CLI happens to pick first.

### Costs and Tradeoffs

- Contributors cannot run `AISkill.CLI` yet; the Sprint 8 script remains the
  only executable validation entrypoint until a real CLI implementation
  sprint follows this architecture.
- The architecture's extension-point table names Milestones 10-11 concepts
  that do not exist yet; those references must be kept in sync once those
  architectures land.

## Enforcement

Any future CLI implementation must conform to
`docs/architecture/CLI_ARCHITECTURE.md`'s command, plugin, configuration,
logging, and error-handling contracts, or must supersede this ADR with a new
one explaining the deviation.

## Alternatives Considered

### Implement a concrete CLI now in a chosen language

Rejected because only one real command (`validate`) currently exists as a
candidate, which is too small a sample to validate a plugin/extension design
against, and because it would force a language decision ahead of the
Template/Generator Engine architectures that the CLI is meant to host.

### Skip a CLI architecture and let each tool (validator, generator) define its own entrypoint

Rejected because it repeats the "one giant prompt" failure mode this
framework rejects for Skills: it would produce several inconsistent ad hoc
entrypoints instead of one composable command surface, and would make plugin
reuse across tools impossible without a rewrite.

## Related Documents

- `docs/architecture/CLI_ARCHITECTURE.md`
- `docs/roadmaps/VALIDATOR_ROADMAP.md`
- ADR-0002
- `docs/principles/DESIGN_PRINCIPLES.md`
