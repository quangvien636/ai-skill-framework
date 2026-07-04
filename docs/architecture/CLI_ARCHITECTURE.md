# CLI Architecture

Version: 0.1
Status: Draft

Last updated: 2026-07-04

## Purpose

Define the command system, plugin model, extension points, configuration,
dependency, logging, and error-handling architecture for the future AI Skill
Framework CLI (`AISkill.CLI`) without implementing it.

## Scope

This architecture defines the CLI's shape so future work has a stable contract
to implement against. It does not select an implementation language or
runtime, does not implement a command, plugin, generator, or validator, and
does not replace the Contract Validation Architecture, which owns validation
meaning. `AISkill.CLI` is the logical component name; the concrete
language/runtime is an open decision left to the Sprint that first implements
it, recorded in an ADR at that time.

## Definitions

- **Command:** a single named CLI operation with declared arguments, options,
  inputs, outputs, and exit-code contract.
- **Command group:** a namespace of related commands (for example `skill`,
  `workflow`, `validate`).
- **Plugin:** an independently versioned package that registers one or more
  commands or command groups without modifying `AISkill.CLI` core.
- **Extension point:** a stable interface the core exposes for plugins to
  implement (for example a validator adapter or a generator template source).
- **Context:** the resolved, immutable set of configuration, working
  directory, and services available to a command during one invocation.

## Design

### Command System

```text
AISkill.CLI
  <group> <command> [arguments] [--options]

Examples:
  AISkill.CLI validate contracts
  AISkill.CLI skill new <name>
  AISkill.CLI workflow inspect <name>
```

Commands are declarative: each command declares its name, group, arguments,
options, help text, and exit-code contract separately from its execution
logic, so help output and future machine-readable command manifests can be
generated without running the command. A command performs one operation and
delegates domain logic to the Validation, Generator, or Runtime cores it
wraps; it must not embed business logic that belongs to those layers (see
[Design Principle 4](../principles/DESIGN_PRINCIPLES.md#4-master-skill-only-orchestrates)
applied to the CLI as an orchestration boundary, not a Master Skill).

Command discovery walks registered command groups at startup, from the core
built-in groups first and then registered plugins in a deterministic,
declared order. Duplicate group or command names across plugins are a
startup error, not a silent override.

### Plugin Model

A plugin registers against one or more extension points and is identified,
versioned, and loaded the same way a Skill or Workflow is: explicit manifest,
resolvable version, and validation before activation. Plugins:

- MUST declare which extension point(s) they implement and their own version;
- MUST NOT reach into another plugin's internal state, only its declared
  extension-point contract;
- MUST NOT be required for `AISkill.CLI` core commands to function.

Plugin loading is explicit (declared in configuration), not automatic
filesystem scanning of arbitrary directories, so a CLI invocation's behavior
is reproducible from its configuration alone.

### Extension Model

Extension points are the stable seams plugins implement against:

| Extension point | Purpose | Related architecture |
| --- | --- | --- |
| Validator adapter | Parse/normalize/validate one artifact source format | [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md) |
| Generator template source | Supply templates for one artifact kind | Milestone 10/11 Template and Generator architecture |
| Command group | Register a namespaced set of commands | This document |
| Reporter | Render diagnostics or results in one output format | [Validation Guide](../guides/VALIDATION_GUIDE.md) |

Each extension point is a narrow interface (inputs, outputs, and failure
contract) versioned independently of `AISkill.CLI` core, so core releases do
not force every extension to change in lockstep.

### Dependency Injection Strategy

Commands and extension-point implementations declare the services they need
(configuration, logger, working-directory resolver, validator core, generator
core) rather than constructing them. The CLI composes a per-invocation
`Context` once at startup and passes it down explicitly; there is no ambient
global service locator. This keeps commands independently testable by
substituting the `Context` with fakes, and keeps the dependency graph
declared rather than discovered at run time.

### Configuration System

Configuration resolves in one deterministic precedence order, lowest to
highest:

```text
built-in defaults
  -> repository configuration file
  -> user configuration file
  -> environment variables
  -> command-line flags
```

Configuration is read once per invocation into the immutable `Context`; a
command must not re-read or mutate configuration mid-invocation. Unknown
configuration keys are a warning, not silently ignored, so typos are
discoverable. Secrets are never logged and never written back to a resolved
configuration file.

### Logging

Logging is structured (leveled, with a stable field set) and separated from
command output written to stdout. Diagnostics reuse the same `code`,
`severity`, `artifact`, `location`, `message` shape defined by the Contract
Validation Architecture rather than inventing a second diagnostic format.
Verbosity is controlled by configuration/flags, never by editing source.

### Error Handling

Every command has a declared exit-code contract: `0` for success, a
reserved-but-versioned range for expected failures (validation error, not
found, conflict), and a distinct range for unexpected/internal errors. A
command catches only errors it can meaningfully translate into a diagnostic;
unexpected exceptions propagate with a non-zero exit and a redacted message,
never a partial silent success. Commands never leave the working directory
partially mutated on failure; multi-step commands checkpoint or operate on a
staged copy.

## Examples

`AISkill.CLI validate contracts` would wrap the Sprint 8
`scripts/validate_contracts.py` prototype behind a stable command contract:
same diagnostics shape, same nonzero-on-failure behavior, no change to
validation meaning, and no coupling of validation logic into the CLI itself.

A future `report` plugin could register a `--format json` reporter extension
point implementation without changing `validate`'s core logic or exit-code
contract.

## References

- [System Architecture](SYSTEM_ARCHITECTURE.md)
- [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md)
- [Validation Guide](../guides/VALIDATION_GUIDE.md)
- [Validator Roadmap](../roadmaps/VALIDATOR_ROADMAP.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)
- [Specification Registry](../specifications/README.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established CLI architecture: commands, plugins, extension points, DI, configuration, logging, error handling |
