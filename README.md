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

## Production Skills

The first production-quality framework package,
[`skill:content-creation`](skills/content-creation/README.md). It creates short
video scripts, social posts, long-form article outlines, caption and hashtag
sets, and title and thumbnail ideas. Five canonical
[Knowledge documents](knowledge/KNOWLEDGE_INDEX.md) supply format, tone,
platform, hook, and call-to-action guidance.

Use the
[`content-brief-to-package`](workflows/content-brief-to-package/README.md)
Workflow for the end-to-end path. Its production artifacts are registered
directly in contract, IR, and graph fixture manifests.

The second package, [`skill:research`](skills/research/README.md), turns a topic
and caller-supplied evidence into research questions, source requirements,
reliability assessments, claim-evidence mappings, calibrated findings, gaps,
citations, and a structured brief. Its
[`research-topic-to-brief`](workflows/research-topic-to-brief/README.md)
Workflow and six methodology Knowledge documents are likewise validated from
their canonical production paths. Research v1 defines artifact and reasoning
structure only; it does not browse or fetch external sources.

The third package,
[`skill:review-quality`](skills/review-quality/README.md), reviews supplied
content packages, research briefs, and generic drafts for editorial quality,
evidence alignment, tone, platform fit, CTA, pacing, and safety. It produces
traceable revisions and an `approve`, `revise`, or `reject` recommendation.
Seven foundational quality documents and the
[`draft-to-reviewed-package`](workflows/draft-to-reviewed-package/README.md)
Workflow are validated from canonical production paths. Review v1 defines the
review contract only; it does not execute an LLM or external fact-check.

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
python scripts/build_ir.py                 # 40 IR fixture cases
python scripts/build_graph.py              # 13 multi-artifact graph scenarios
python scripts/build_semantics.py          # 3 semantic conformance scenarios
python scripts/validate_repository.py       # discover and validate canonical artifacts
python -m unittest discover -s tests/unit  # 84 unit tests
```

The semantic layer checks evaluation metric uniqueness and weight totals,
Evaluation/Reflection routing, Workflow mapping availability and types, retry
routing, and unreachable steps. It emits structured `ASF-SEMANTIC-*`
diagnostics over typed IR and performs no discovery or execution.

`validate_repository.py` finds the workspace using the two ADR-0007 markers,
builds a deterministic internal index, loads all canonical artifacts, and runs
every implemented validation layer. The current repository index contains 42
locations, including embedded Evaluation/Reflection locations and executable
examples, and loads 24 Skill/Workflow/Knowledge artifacts.

See `docs/roadmaps/VALIDATOR_ROADMAP.md` (Phases 2-3),
`docs/adr/ADR-0009-ir-adapter-package-and-scope.md`, and
`docs/adr/ADR-0010-dependency-and-version-graph-scope.md` for scope,
assumptions, and deferred work.
