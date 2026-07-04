# ADR-0004: Template Engine Uses One Registry With Two Template Categories

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

Sprints 2, 4, and 5 already produced three template-like artifacts through
three different processes: `knowledge/_templates/KNOWLEDGE_TEMPLATE.md`
(colocated governance file), and `templates/skill/` /
`templates/workflow/` (reusable executable skeletons registered in the
Naming Convention). Milestone 10 asks for templates covering Skill,
Workflow, Knowledge, ADR, Documentation, Examples, and Tests. Without a
formal Template Engine architecture, each new template kind would repeat the
same "where does this live and what convention does it follow" decision
independently, and ADR/Documentation templates in particular have no
existing home.

The Naming Convention already grants Knowledge templates a colocated,
reserved-uppercase-filename exception instead of forcing them under
`templates/<name>/`. The question this ADR resolves is whether ADR and
Documentation templates should follow that same exception, or be forced into
`templates/adr/` and `templates/documentation/` for superficial uniformity
with Skill and Workflow.

## Decision

`docs/architecture/TEMPLATE_ENGINE_ARCHITECTURE.md` formalizes two template
categories:

- **Reusable executable templates** (Skill, Workflow) stay under
  `templates/<name>/`, each with an `examples/README.md` and
  `tests/README.md` sub-skeleton, because their target artifacts are
  themselves schema-validated and activated.
- **Governance templates** (Knowledge, ADR, Documentation) stay colocated
  with the subsystem they belong to, using a reserved uppercase filename:
  `knowledge/_templates/KNOWLEDGE_TEMPLATE.md` (unchanged),
  `docs/adr/ADR_TEMPLATE.md` (new), and
  `docs/_templates/DOCUMENTATION_TEMPLATE.md` (new).

`templates/README.md` becomes the single registry listing every template
kind, its location, category, and target, regardless of which category it
falls into. Examples and Tests are not registered as a fifth template kind;
they are a required part of each reusable executable template because they
have no meaning independent of the Skill or Workflow they belong to.

No generator, CLI command, or template-discovery code is added in this
sprint; this ADR only fixes where templates live and how they are indexed.

## Consequences

### Positive

- ADR and Documentation authors now have a starting skeleton, closing a real
  gap (previously every ADR was written by copying a prior ADR's structure
  by eye).
- The two-category split avoids forcing governance documents into an
  executable-artifact directory shape that implies schema validation they do
  not have.
- One registry (`templates/README.md`) gives contributors and a future
  generator a single lookup regardless of category, without moving any
  existing file and risking broken references (Knowledge templates are
  referenced from `knowledge/README.md`, `knowledge/KNOWLEDGE_INDEX.md`,
  `docs/architecture/KNOWLEDGE_ARCHITECTURE.md`, and
  `docs/principles/NAMING_CONVENTION.md`).

### Costs and Tradeoffs

- Two categories with different locations is a small extra rule contributors
  must learn versus one uniform `templates/<name>/` location for everything.
- The registry must be kept in sync by hand whenever a template is added or
  moved; nothing yet enforces that mechanically.

## Enforcement

Adding a new template kind must: name its category (executable vs.
governance), place it accordingly, and add a row to `templates/README.md` in
the same change, per the Template Engine Architecture's "Adding a New
Template Kind" procedure.

## Alternatives Considered

### Move the Knowledge template under `templates/knowledge/` for uniformity

Rejected because it would require updating four existing documents'
references for a cosmetic consistency gain with no functional benefit, and
because Knowledge documents are not schema-validated as a whole artifact the
way Skills and Workflows are — the existing colocated exception already fits
its nature.

### Put ADR and Documentation templates under `templates/adr/` and `templates/documentation/`

Rejected for the same reason: these are governance documents reviewed by
convention, not executable artifacts a generator instantiates and a
validator activates, so colocating them with `docs/adr/` and `docs/` (via
`docs/_templates/`) keeps them next to the documents they template.

## Related Documents

- `docs/architecture/TEMPLATE_ENGINE_ARCHITECTURE.md`
- `templates/README.md`
- `docs/principles/NAMING_CONVENTION.md`
- ADR-0003
