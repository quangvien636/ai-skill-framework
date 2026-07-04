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

- [Project Context](PROJECT_CONTEXT.md)
- [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md)
- [Design Principles](docs/principles/DESIGN_PRINCIPLES.md)
- [Knowledge Architecture](docs/architecture/KNOWLEDGE_ARCHITECTURE.md)
- [AI Skill Framework Specifications](docs/specifications/README.md)
- [Machine-Readable Schemas](schemas/README.md)
- [Contract Validation Architecture](docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [Validation Guide](docs/guides/VALIDATION_GUIDE.md)
- [Validator Roadmap](docs/roadmaps/VALIDATOR_ROADMAP.md)
- [CLI Architecture](docs/architecture/CLI_ARCHITECTURE.md)

## Validator Prototype

A minimal, offline conformance check for the schemas in `schemas/`:

```bash
pip install -r requirements-validator.txt
python scripts/validate_contracts.py
```

See the [Validation Guide](docs/guides/VALIDATION_GUIDE.md) and
`docs/adr/ADR-0002-prototype-contract-validator.md` for scope and rationale.
