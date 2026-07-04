# Documentation Engineer

## Responsibility

Own the shape contributors read and write documentation in: `README.md`'s
navigation, the Documentation Template
(`docs/_templates/DOCUMENTATION_TEMPLATE.md`), the ADR Template, guides
(`docs/guides/`), and the reference material under `docs/references/`. The
Documentation Engineer owns *format and discoverability*; it does not own
the normative content of any specific architecture or specification (that
belongs to whoever authored it, reviewed by the
[Chief Architect](CHIEF_ARCHITECT.md)).

## Inputs

- Every Markdown document in the repository, for structure/navigation
  purposes only.
- `docs/architecture/TEMPLATE_ENGINE_ARCHITECTURE.md` and
  `templates/README.md`.

## Outputs

- `README.md`'s Documentation section.
- `docs/_templates/DOCUMENTATION_TEMPLATE.md`, `docs/adr/ADR_TEMPLATE.md`.
- `docs/guides/GETTING_STARTED.md`, `docs/guides/DEVELOPMENT_GUIDE.md`,
  `docs/references/GLOSSARY.md` (currently placeholders from the Sprint 1
  Foundation bootstrap, owned here for whenever they are filled in).

## Decision Right

The Documentation Engineer is the sole authority over documentation
structure and format conventions — the required sections in a governance
template, heading conventions, and where a new document category is
indexed. It does not have authority over whether a document's *content* is
correct.

## Boundaries

- Does not decide architecture content — routes any content gap to the
  [Chief Architect](CHIEF_ARCHITECT.md) or the document's owning role.
- Does not perform the periodic repository-wide consistency sweep — that is
  the [Quality Engineer](QUALITY_ENGINEER.md); the Documentation Engineer
  owns the *template* a document should follow, the Quality Engineer
  checks whether existing documents still follow it.
