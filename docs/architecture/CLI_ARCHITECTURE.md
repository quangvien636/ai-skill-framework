# CLI Architecture

Version: 0.7
Status: Draft

Last updated: 2026-07-05

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

### Command Registry

The Command Registry is the concrete object command discovery populates: a
lookup from `(group, command)` to that command's declaration (arguments,
options, help text, exit-code contract) and its handler. It is built once
per invocation, after Plugin Discovery and before argument parsing, so:

- `--help` and any future machine-readable command manifest read the
  Registry, never a live handler;
- argument/option parsing for one command cannot see another command's
  declarations, preventing accidental cross-command flag leakage;
- a duplicate `(group, command)` key is the startup error Command Discovery
  already requires, detected at Registry construction, not at dispatch time.

The Registry is immutable for the remainder of the invocation once built;
a command handler cannot register additional commands at run time.

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

### Plugin Discovery

A plugin is declared in configuration the same way a Skill/Workflow
dependency is declared: `(id, version range)`. Discovery:

1. reads the declared plugin list from the resolved Configuration System
   (see below), in declaration order;
2. resolves each declared version range against installed plugin versions
   using the Version Specification's existing range rules — no separate
   plugin-version syntax;
3. loads plugins strictly in declaration order, so two plugins that both
   implement the same extension point have a deterministic, visible
   precedence instead of an unspecified one;
4. fails startup if a declared plugin cannot be resolved, naming the
   plugin ID and the range that failed to resolve.

There is no directory-scanning fallback: an installed-but-undeclared plugin
is inert. This keeps "what does this CLI invocation do" fully answerable
from configuration alone, matching the Plugin Model's reproducibility rule
above.

### Extension Model

Extension points are the stable seams plugins implement against:

| Extension point | Purpose | Related architecture |
| --- | --- | --- |
| IR adapter | Parse and normalize one artifact source format into IR, shared by `validate`, `generate`, and Runtime commands | [IR Architecture](IR_ARCHITECTURE.md), [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md) |
| Generator template source | Supply templates for one artifact kind | [Template Engine Architecture](TEMPLATE_ENGINE_ARCHITECTURE.md), [Generator Architecture](GENERATOR_ARCHITECTURE.md) |
| Renderer | Serialize one artifact kind's target IR back to its authoring format | [Generator Architecture](GENERATOR_ARCHITECTURE.md) |
| Command group | Register a namespaced set of commands | This document |
| Reporter | Render diagnostics or results in one output format | [Validation Guide](../guides/VALIDATION_GUIDE.md) |

An IR adapter's structural validation step still runs the schema in
`schemas/` for its artifact type; this table names the adapter once so
`validate` and `generate` commands both wrap it instead of each owning a
separate parser (see ADR-0005).

Each extension point is a narrow interface (inputs, outputs, and failure
contract) versioned independently of `AISkill.CLI` core, so core releases do
not force every extension to change in lockstep.

### Dependency Injection Strategy and Service Container

Commands and extension-point implementations declare the services they need
(configuration, logger, workspace root, Command Registry, IR adapter,
Generator, Reporter) rather than constructing them. The **Service
Container** is the concrete component that resolves and holds these
services for one invocation: it is built once, after Configuration Loading
and Plugin Discovery and Command Registry construction, and composes the
per-invocation `Context` commands receive. There is no ambient global
service locator — a command or extension-point implementation cannot reach
a service the Service Container did not explicitly hand it. This keeps
commands independently testable by substituting the `Context`/Service
Container with fakes, and keeps the dependency graph declared rather than
discovered at run time.

The Service Container's build order is fixed and matters: Configuration
Loading -> Workspace Discovery -> Plugin Discovery -> Command Registry ->
IR adapter / Generator / Reporter instantiation from active extension
points. Each stage may only depend on stages before it.

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

### Workspace Discovery

Most commands need to know the repository root before they can resolve a
relative artifact path or load repository configuration. Workspace
Discovery walks parent directories from the current working directory,
upward, for the nearest directory containing **both** `PROJECT_CONTEXT.md`
and `PROJECT_TRACKER.md`. Requiring both files (not just one, and not
`.git`) avoids a false match on an unrelated directory that happens to have
one similarly-named file, while not depending on a VCS marker a non-Git
checkout or a nested working copy might lack. See ADR-0007 for the
alternatives considered.

Discovery runs once, immediately after Configuration Loading and before
Plugin Discovery (plugin declarations may live in repository configuration,
which requires knowing the workspace root to locate). Failure to find a
marker within a bounded number of parent directories is a startup error
naming the directory where the search began; the CLI does not silently fall
back to the current directory as a pseudo-root.

### Project Discovery

Once the workspace root is known, Project Discovery enumerates existing
artifacts on demand: `skills/*/skill.yaml`, `workflows/*/workflow.yaml`, and
`knowledge/**/*.md` (excluding `_templates/`). Discovery is lazy and
per-command — a command declares which artifact kinds it needs (for
example, `validate` needs all three; `skill new` needs none) — rather than
eagerly walking and parsing the entire repository on every invocation.
Enumerated paths are handed to the relevant IR adapter; Project Discovery
itself does not parse or normalize anything.

The implemented discovery index also exposes embedded `evaluation` and
`reflection` locations by pointing to their owning `skill.yaml` plus the
embedded section name; these remain embedded contracts, not standalone files
or graph nodes. Example discovery enumerates non-README YAML, JSON, and Markdown
files below Skill and Workflow `examples/` directories. The immutable index is
sorted deterministically and can be reused by validation and the future Runtime
instead of rescanning the workspace.

### Template Discovery

`generate` commands resolve templates by reading the
[Template Registry](../../templates/README.md) plus any active "Generator
template source" plugin extension points, in that order. This is the same
registry the Template Engine Architecture defines — Template Discovery is
a lookup against it, not a second, competing index.

### Logging

Logging is structured (leveled, with a stable field set) and separated from
command output written to stdout. Diagnostics reuse the same `code`,
`severity`, `artifact`, `location`, `message` shape defined by the Contract
Validation Architecture rather than inventing a second diagnostic format.
Verbosity is controlled by configuration/flags, never by editing source.

### Validator Integration

`validate` commands wrap one or more IR adapters plus the
[Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md)'s
structural, semantic, and repository layers behind the Command Registry's
declared arguments. The command adds argument parsing, Project Discovery
(which artifacts to check), and Reporter output; it adds no validation
rule of its own. Sprint 8's `scripts/validate_contracts.py` is this
integration's prototype: a future `validate` command generalizes it from a
fixed fixture list to Project-Discovery-driven repository scanning without
changing what a diagnostic means.

### Generator Integration

`generate` commands wrap the [Generator Architecture](GENERATOR_ARCHITECTURE.md)'s
pipeline (resolve template -> resolve producer values -> build target IR ->
validate -> render -> plan -> apply) behind the Command Registry's declared
arguments. The command adds argument parsing (mapping CLI flags to producer
values), Template Discovery, and Reporter output for the generation plan and
result; it adds no generation, template-resolution, or overwrite-policy
logic of its own — all of that is owned by the Generator Architecture.

### Error Handling

Every command has a declared exit-code contract and emits diagnostics in one
shared shape; see Exit Codes and Diagnostics below. A command catches only
errors it can meaningfully translate into a diagnostic; unexpected
exceptions propagate with a non-zero exit and a redacted message, never a
partial silent success. Commands never leave the working directory partially
mutated on failure; multi-step commands checkpoint or operate on a staged
copy, consistent with the Generator's own plan-then-apply staging.

### Exit Codes

| Range | Meaning | Example |
| --- | --- | --- |
| `0` | Success | Command completed with no errors |
| `1` | Expected failure: validation error | Contract Validation Architecture reported one or more errors |
| `2` | Expected failure: usage or configuration error | Unknown flag, unresolved required configuration key |
| `3` | Expected failure: conflict | Generator Overwrite Policy or identity-conflict detected (Generator Architecture) |
| `4` | Expected failure: not found | Referenced artifact ID, template, or plugin does not resolve |
| `64-79` | Reserved: internal/unexpected error | Uncaught exception, adapter defect |

Exit codes `0-4` are part of this architecture's stable contract; a command
or plugin MUST NOT repurpose them for a different meaning. New expected
failure categories get the next unused code below `64` and a revision to
this table, not a reuse of an existing one.

### Diagnostics

Every diagnostic a command emits — whether from an IR adapter, the
Contract Validation Architecture's layers, or the Generator — uses the one
shape already defined by the Contract Validation Architecture: `code`,
`severity`, `artifact`, `location`, `message`, `rule_reference`, optional
`suggestion`. Code prefixes are allocated per owning layer so a Reporter can
group or filter without guessing intent:

| Prefix | Owner |
| --- | --- |
| `ASF-PARSE-*` | IR adapter parse/normalization failures (before or during IR construction), IR Architecture (ADR-0009) |
| `ASF-GRAPH-*` | Dependency Graph / Version Graph failures (cross-artifact, after IR construction succeeds), IR Specification (ADR-0010) |
| `ASF-SCHEMA-*` | Structural (JSON Schema) validation, Contract Validation Architecture |
| `ASF-SEMANTIC-*` | Semantic validation, Contract Validation Architecture |
| `ASF-REPO-*` | Repository-integrity validation, Contract Validation Architecture |
| `ASF-GEN-*` | Generator Architecture |
| `ASF-CLI-*` | CLI-layer errors (usage, configuration, plugin resolution) not owned by another layer |

This table only allocates prefixes; it does not assign individual numbers,
which remain owned by each prefix's source document.

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
- [IR Architecture](IR_ARCHITECTURE.md)
- [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md)
- [Template Engine Architecture](TEMPLATE_ENGINE_ARCHITECTURE.md)
- [Generator Architecture](GENERATOR_ARCHITECTURE.md)
- [Validation Guide](../guides/VALIDATION_GUIDE.md)
- [Validator Roadmap](../roadmaps/VALIDATOR_ROADMAP.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)
- [Specification Registry](../specifications/README.md)
- [Template Registry](../../templates/README.md)
- ADR-0007
- ADR-0009
- ADR-0010

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established CLI architecture: commands, plugins, extension points, DI, configuration, logging, error handling |
| 0.2 | 2026-07-04 | Broadened the Validator adapter extension point to the shared IR adapter (ADR-0005) |
| 0.3 | 2026-07-04 | Added the Renderer extension point for the Generator Architecture |
| 0.4 | 2026-07-04 | Added Command Registry, Plugin Discovery, Service Container, Workspace/Project/Template Discovery, Generator/Validator Integration, Exit Codes, and Diagnostics (ADR-0007) |
| 0.5 | 2026-07-04 | Added the ASF-PARSE-* diagnostic prefix for IR adapters (ADR-0009) |
| 0.6 | 2026-07-04 | Added the ASF-GRAPH-* diagnostic prefix for the Dependency/Version Graph (ADR-0010) |
| 0.7 | 2026-07-05 | Documented the implemented Project Index, embedded quality locations, and example discovery |
