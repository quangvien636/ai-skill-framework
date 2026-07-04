# AI Skill Framework

## Vision

Build reusable AI Skills instead of one giant prompt.

---

## Goals

- Modular
- Reusable
- Maintainable
- Testable
- Versioned

---

## Current Version

v0.1

---

## Status

Under Development

## Documentation

### Foundation

- [Project Context](PROJECT_CONTEXT.md)
- [Project Tracker](PROJECT_TRACKER.md)
- [Design Principles](docs/principles/DESIGN_PRINCIPLES.md)
- [Naming Convention](docs/principles/NAMING_CONVENTION.md)
- [Architecture Decision Records](docs/adr/) (start at `ADR-0001-repository-is-the-source-of-truth.md`)
- [AI Team](.ai/README.md) (roles, playbooks, standards, governance)

### Architecture

- [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md)
- [Knowledge Architecture](docs/architecture/KNOWLEDGE_ARCHITECTURE.md)
- [Skill Architecture](docs/architecture/SKILL_ARCHITECTURE.md)
- [Workflow Architecture](docs/architecture/WORKFLOW_ARCHITECTURE.md)
- [Evaluation Architecture](docs/architecture/EVALUATION_ARCHITECTURE.md)
- [Reflection Architecture](docs/architecture/REFLECTION_ARCHITECTURE.md)
- [Contract Validation Architecture](docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [IR Architecture](docs/architecture/IR_ARCHITECTURE.md)
- [Template Engine Architecture](docs/architecture/TEMPLATE_ENGINE_ARCHITECTURE.md)
- [Generator Architecture](docs/architecture/GENERATOR_ARCHITECTURE.md)
- [CLI Architecture](docs/architecture/CLI_ARCHITECTURE.md)

### Specifications, Schemas, and Registries

- [AI Skill Framework Specifications](docs/specifications/README.md)
- [IR Specification](docs/specifications/IR_SPECIFICATION.md)
- [Machine-Readable Schemas](schemas/README.md)
- [Template Registry](templates/README.md)

### Validation

- [Validation Guide](docs/guides/VALIDATION_GUIDE.md)
- [Validator Roadmap](docs/roadmaps/VALIDATOR_ROADMAP.md)

## Validator Prototype

A minimal, offline conformance check for the schemas in `schemas/`:

```bash
pip install -r requirements-validator.txt
python scripts/validate_contracts.py
```

See the [Validation Guide](docs/guides/VALIDATION_GUIDE.md) and
`docs/adr/ADR-0002-prototype-contract-validator.md` for scope and rationale.

## IR Adapters and Dependency/Version Graph

`scripts/asf_validator/` turns a schema-validated Skill/Workflow/Knowledge/
Evaluation/Reflection document into the typed IR object
`docs/specifications/IR_SPECIFICATION.md` defines, and builds the
Dependency Graph / Version Graph across multiple loaded artifacts:

```bash
python scripts/build_ir.py                 # 16 IR fixture cases
python scripts/build_graph.py              # 10 multi-artifact graph scenarios
python -m unittest discover -s tests/unit  # 53 unit tests
```

See `docs/roadmaps/VALIDATOR_ROADMAP.md` (Phases 2-3),
`docs/adr/ADR-0009-ir-adapter-package-and-scope.md`, and
`docs/adr/ADR-0010-dependency-and-version-graph-scope.md` for scope,
assumptions, and deferred work.
