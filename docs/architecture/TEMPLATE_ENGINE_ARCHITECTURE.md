# Template Engine Architecture

Version: 0.1
Status: Active

Last updated: 2026-07-04

## Purpose

Define one reusable template model shared by Skill, Workflow, Knowledge, ADR,
Documentation, Examples, and Tests templates, so every generator or
contributor fills placeholders the same way instead of each template kind
inventing its own convention.

## Scope

This architecture formalizes conventions the Skill, Workflow, and Knowledge
templates already follow (Sprints 2, 4, and 5) and extends them to ADR and
generic Documentation templates. It does not implement a Generator (see
Milestone 11's Generator Engine architecture) and does not add a `template`
CLI command; it defines the contract a future generator or contributor fills.

## Definitions

- **Template:** a neutral, non-executable skeleton for one artifact kind,
  with every variable part marked by a placeholder.
- **Placeholder:** an angle-bracket token (`<skill-name>`, `<owner>`) marking
  a value a producer must supply; a template MUST NOT contain resolved,
  invented example content in place of a placeholder.
- **Reusable executable template:** a template for an artifact that is
  itself validated and activated (Skill, Workflow) — lives under
  `templates/<name>/` per the Naming Convention.
- **Governance template:** a template for a document artifact that is
  reviewed by convention rather than schema-validated (Knowledge, ADR,
  Documentation) — colocated with the subsystem it belongs to, using the
  reserved uppercase filename pattern.
- **Producer:** a contributor or future generator that instantiates a
  template into a real artifact.

## Design

### Template Registry

`templates/README.md` is the canonical index of every template kind, its
location, and what it produces:

| Kind | Location | Category | Produces |
| --- | --- | --- | --- |
| Skill | `templates/skill/` | Reusable executable | `skills/<name>/` |
| Workflow | `templates/workflow/` | Reusable executable | `workflows/<name>/` |
| Knowledge | `knowledge/_templates/KNOWLEDGE_TEMPLATE.md` | Governance | `knowledge/<category>/<domain>/<topic>/<doc>.md` |
| ADR | `docs/adr/ADR_TEMPLATE.md` | Governance | `docs/adr/ADR-<NNNN>-<slug>.md` |
| Documentation | `docs/_templates/DOCUMENTATION_TEMPLATE.md` | Governance | Architecture, guide, roadmap, or specification documents under `docs/` |

Governance templates stay colocated with their subsystem rather than moving
under `templates/<name>/`, matching the exception the Naming Convention
already grants Knowledge templates. Examples and Tests are not a fifth
template location; they are a required sub-skeleton inside each reusable
executable template (see below), because an Example or Test only has meaning
attached to one Skill or Workflow template.

### Shared Conventions

Every template, regardless of category, follows the same rules:

1. **Placeholder marking.** Every variable value uses an angle-bracket
   placeholder (`<skill-name>`, `[Knowledge Title]`, `<owner>`). A producer
   replaces every placeholder; none may remain in an activated artifact.
2. **Neutral status.** A template's own manifest or frontmatter (where one
   exists) declares the lowest lifecycle state (`draft`) so an unedited copy
   can never pass activation validation by accident.
3. **Non-executable.** A template is never itself a Skill, Workflow, Runtime
   component, or CLI plugin. It contains no logic to run, only structure to
   copy.
4. **Architecture-traceable.** Each template's own README (or the template
   file itself) links to the architecture and specification that define its
   target artifact's validation rules, so a producer edits against the
   current contract, not a frozen copy of it.
5. **Sub-skeletons for Examples and Tests.** A reusable executable template
   includes `examples/README.md` and `tests/README.md` stubs describing what
   representative examples and contract tests that artifact kind requires,
   per its owning architecture (see `templates/skill/` and
   `templates/workflow/`).

### Relationship to the Generator Engine and CLI

A template is input, not a tool. The Generator Engine (Milestone 11)
consumes templates and producer-supplied values to emit a filled artifact;
this architecture does not define that pipeline. The CLI Architecture's
"Generator template source" extension point (see
[CLI Architecture](CLI_ARCHITECTURE.md)) is the future seam through which a
generator command discovers templates from this registry — this document
does not implement that command.

### Adding a New Template Kind

1. Confirm the artifact kind has an owning architecture/specification.
2. Decide reusable-executable vs. governance using the categories above.
3. Add the template under `templates/<name>/` (executable) or colocated with
   its subsystem using a reserved uppercase filename (governance).
4. Register it in `templates/README.md`.
5. Link the owning architecture from the template, and the template from the
   owning architecture, so the two do not drift apart.

## Examples

The Skill template (`templates/skill/`) is a reusable executable template:
its `skill.yaml` placeholders are the same fields `schemas/skill.schema.json`
validates, and it ships `examples/README.md` and `tests/README.md` stubs.

The Knowledge template (`knowledge/_templates/KNOWLEDGE_TEMPLATE.md`) is a
governance template: contributors fill it by convention and review, and its
normalized model — not the template file — is what `schemas/knowledge.schema.json`
validates.

## References

- [Skill Architecture](SKILL_ARCHITECTURE.md)
- [Workflow Architecture](WORKFLOW_ARCHITECTURE.md)
- [Knowledge Architecture](KNOWLEDGE_ARCHITECTURE.md)
- [CLI Architecture](CLI_ARCHITECTURE.md)
- [Naming Convention](../principles/NAMING_CONVENTION.md)
- `templates/README.md`
- ADR-0004

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established shared Template Engine conventions and registry |
