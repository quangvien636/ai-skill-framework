# ADR-0016: CLI Implementation Language and Phased Adoption

- **Status:** Accepted
- **Date:** 2026-07-12
- **Decision owners:** Project maintainers

## Context

`docs/architecture/CLI_ARCHITECTURE.md` defines `AISkill.CLI`'s full shape
(Command Registry, Plugin Model and Discovery, Extension Model, a
Dependency Injection Service Container, a five-level Configuration
System, Workspace/Project/Template Discovery, Validator/Generator
Integration, Exit Codes, Diagnostics) but deliberately "does not select an
implementation language or runtime... the concrete language/runtime is an
open decision left to the Sprint that first implements it, recorded in an
ADR at that time." `PROJECT_TRACKER.md`'s Next Actions names exactly that
open item, plus a concrete first slice: "wire `scripts/build_ir.py`/
`scripts/build_graph.py`'s pipelines behind the `validate`/`generate`
commands per `CLI_ARCHITECTURE.md`'s Validator/Generator Integration."

`scripts/asf_cli.py` already exists and already implements ten commands
(`validate`, `build-ir`, `graph`, `plan`, `bindings`, `compile`, `run`,
`doctor`, `snapshot`, `inspect`, `explain`) as a single Python module using
`argparse` directly — built incrementally across Sprints 28-33 without a
dedicated ADR recording *why* Python, or what its relationship to the full
`CLI_ARCHITECTURE.md` contract is. This ADR closes that gap rather than
starting a parallel, from-scratch `AISkill.CLI` implementation.

## Decision

### 1. Language: Python

Python, not a new choice: `scripts/asf_validator/`, `scripts/asf_runtime/`,
every adapter package, and `scripts/asf_cli.py` itself are already Python.
Introducing a second implementation language for the CLI specifically
would mean either reimplementing the entire validator/runtime/adapter
stack a second time behind a language boundary, or the CLI shelling out to
Python subprocesses for every real operation — both contradict "reuse
existing components before creating new ones" (Working Principle 7) for
no capability gain. No other language was seriously evaluated for this
reason: there is no requirement in `CLI_ARCHITECTURE.md` or elsewhere that
motivates paying that cost.

### 2. `scripts/asf_cli.py` already satisfies the Validator Integration
   contract for `validate` — confirmed, not re-implemented

`CLI_ARCHITECTURE.md`'s Validator Integration section: "`validate`
commands wrap one or more IR adapters plus the Contract Validation
Architecture's structural, semantic, and repository layers... The command
adds argument parsing, Project Discovery..., and Reporter output; it adds
no validation rule of its own... a future `validate` command generalizes
[Sprint 8's fixed-fixture-list prototype] to Project-Discovery-driven
repository scanning without changing what a diagnostic means."

`scripts/asf_cli.py`'s `load_workspace()` already calls `discover_project()`
(Project Discovery) then `build_ir()` for every discovered artifact — the
exact function `scripts/build_ir.py` calls — and `validate_workspace()`
already calls `build_dependency_graph()`/`build_version_graph()` (the exact
functions `scripts/build_graph.py` calls), `validate_semantics()`, and
`validate_repository()`, emitting the shared `Diagnostic` shape through
`diagnostic_dict()`. This already *is* Project-Discovery-driven repository
scanning behind a `validate` command producing the same diagnostic
meaning `build_ir.py`/`build_graph.py` produce standalone — the Next
Action's literal ask (wire those two scripts' pipelines behind `validate`)
was satisfied incrementally across Sprints 28-33 without ever being
recorded as such. This ADR records that fact rather than re-wiring
something already wired.

### 3. `generate` is explicitly out of scope today — no Generator execution
   reference exists yet

`CLI_ARCHITECTURE.md`'s Generator Integration section describes wrapping
"the Generator Architecture's pipeline (resolve template -> resolve
producer values -> build target IR -> validate -> render -> plan ->
apply)." No `scripts/generate*.py` or equivalent reference implementation
of that pipeline exists anywhere in this repository today — Generator
Architecture is a design document (`docs/architecture/
GENERATOR_ARCHITECTURE.md`), not yet a working module the CLI could wrap.
Adding a `generate` command that does not actually generate anything would
be exactly the "partial silent success" `CLI_ARCHITECTURE.md`'s own Error
Handling section forbids. This is a separate, larger prior gap (there is
no tracked Sprint that built a Generator reference implementation), not
something this ADR can respons­ibly close as a side effect of a CLI
language decision. Recorded as its own Next Action.

### 4. Package layout: stay a single module until Phase 2 needs otherwise

`scripts/asf_cli.py` stays one file for now. It does not yet need a Command
Registry, Plugin Model, Plugin Discovery, or a Dependency Injection Service
Container — it has ten commands, all core (no plugin has ever been
proposed), and `main()`'s existing `argparse` dispatch plus the shared
`_run_command()`/`diagnostic_dict()`/`_render()` functions already give it
a single, consistent diagnostic shape and exit-code contract without that
machinery. Splitting into a package now would be a purely organizational
change to a working, tested module for no immediate capability gain —
exactly the premature-abstraction Working Principle "reuse existing
components... one skill = one responsibility" warns against when there is
no second consumer yet.

**Phased adoption, recorded now so the next contributor does not have to
re-derive it:**

- **Phase 1 (this ADR, done):** confirm Python, confirm `validate`
  already satisfies Validator Integration, record `generate`'s blocker.
- **Phase 2 (future, triggered by an actual second command-group need —
  e.g. a Skill/Workflow `new`/scaffold command, or the first real plugin
  proposal):** split into a package, `scripts/asf_cli/`, with at minimum
  `__init__.py` (the `main()` entry point), `commands/` (one module per
  command group), `registry.py` (Command Registry), and `render.py`
  (Reporter). Do not build the Plugin Model, Plugin Discovery, Service
  Container, or five-level Configuration System speculatively before a
  real second plugin or a real multi-source configuration need exists —
  each is real, non-trivial scope `CLI_ARCHITECTURE.md` describes in
  detail, and building any of them against zero real consumers would be
  exactly the kind of speculative infrastructure this repository's own
  engineering rules discourage.
- **Phase 3 (future, triggered by a real Generator Architecture reference
  implementation existing):** add a `generate` command wrapping it, per
  the Generator Integration section already specified.

## Consequences

### Positive

- No new implementation language, dependency, or execution model
  introduced — this ADR is almost entirely a *confirmation* of already-
  working, already-tested code, closing a documentation gap rather than
  opening new implementation risk.
- The phased plan gives Phase 2/3 a concrete trigger condition instead of
  an open-ended "eventually build the full architecture," consistent with
  how ADR-0014/0015 both phased their own large scopes.

### Costs and Tradeoffs

- `scripts/asf_cli.py` remaining a single ~640-line module means it will
  need the Phase 2 split before it can safely support a second, real
  plugin author — deferred, not eliminated, cost.
- `generate` remains unavailable through the CLI until a Generator
  reference implementation exists; anyone wanting to scaffold a new
  Skill/Workflow/Knowledge document today must still do so by hand or
  from `templates/`, unchanged from before this ADR.

## Enforcement

- Any new CLI command group must be added to `scripts/asf_cli.py`'s
  existing `_run_command()`/`_parser()` structure (or, once Phase 2
  triggers, the new package) — not a second, parallel CLI entry point.
- A `generate` command may only be added once a real Generator Architecture
  pipeline reference implementation exists to wrap; the command must not
  be added first with a stub pipeline behind it.
- `tests/unit/test_cli.py` remains the conformance suite for `scripts/
  asf_cli.py`'s existing commands' diagnostic shape and exit codes.

## Alternatives Considered

### Start a from-scratch `AISkill.CLI` package today, separate from `scripts/asf_cli.py`

Rejected. `scripts/asf_cli.py` already correctly wraps the shared
validator/runtime/adapter functions with the right diagnostic shape and
exit-code contract (`tests/unit/test_cli.py`, 15 passing tests as of
Sprint 33). Starting over would discard working, tested integration code
to satisfy a naming preference, not a real capability gap.

### Build the full Command Registry/Plugin Model/Service Container now

Rejected for today. Zero real plugins or command groups currently need
it; building it against no real consumer is speculative infrastructure,
not a proportionate response to a documented need — see Working Principle
7 ("reuse existing components before creating new ones") and this
repository's broader preference for the smallest architecture-aligned
change.

### Choose a non-Python language for a future, separate production CLI

Rejected for now, not permanently. `CLI_ARCHITECTURE.md` itself leaves
this open for "the Sprint that first implements it" — this ADR is that
Sprint, and nothing in the current requirements motivates a second
language. Revisiting this would need its own ADR citing a concrete
capability gap Python cannot fill, per ADR-0013's same Build vs Reuse
discipline.

## Related Documents

- `docs/architecture/CLI_ARCHITECTURE.md`
- `docs/architecture/GENERATOR_ARCHITECTURE.md`
- ADR-0007 (Workspace Discovery precedent this ADR's Phase 1 confirms
  `scripts/asf_cli.py` already implements via `discover_workspace_root()`)
- ADR-0009 (IR adapter package and scope — `build_ir()` is the function
  both `scripts/build_ir.py` and `scripts/asf_cli.py` already share)
- ADR-0013 (Build vs Reuse — the same engineering discipline this ADR's
  Alternatives Considered applies to the CLI's own scope)
