# Template Registry

Canonical index of every framework template, its location, and what it
produces. See the [Template Engine Architecture](../docs/architecture/TEMPLATE_ENGINE_ARCHITECTURE.md)
for the shared conventions every template follows.

| Kind | Location | Category | Produces |
| --- | --- | --- | --- |
| Skill | [`skill/`](skill/README.md) | Reusable executable | `skills/<name>/` |
| Workflow | [`workflow/`](workflow/README.md) | Reusable executable | `workflows/<name>/` |
| Knowledge | [`../knowledge/_templates/KNOWLEDGE_TEMPLATE.md`](../knowledge/_templates/KNOWLEDGE_TEMPLATE.md) | Governance | `knowledge/<category>/<domain>/<topic>/<doc>.md` |
| ADR | [`../docs/adr/ADR_TEMPLATE.md`](../docs/adr/ADR_TEMPLATE.md) | Governance | `docs/adr/ADR-<NNNN>-<slug>.md` |
| Documentation | [`../docs/_templates/DOCUMENTATION_TEMPLATE.md`](../docs/_templates/DOCUMENTATION_TEMPLATE.md) | Governance | Architecture, guide, roadmap, or specification documents under `docs/` |

Reusable executable templates (Skill, Workflow) live under `templates/<name>/`
and include `examples/README.md` and `tests/README.md` stubs; Examples and
Tests are not registered as a separate template kind because they only have
meaning attached to one Skill or Workflow template.

Governance templates (Knowledge, ADR, Documentation) stay colocated with the
subsystem they belong to instead of moving here, per the Naming Convention's
existing exception for `knowledge/_templates/`.

Every template is neutral and non-executable: replace every angle-bracket
placeholder, keep the lowest lifecycle state until reviewed, and follow the
linked architecture or specification for the target artifact's validation
rules.
