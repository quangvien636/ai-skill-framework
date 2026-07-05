# AI Skill Framework - Project Context

Version: 0.24
Status: Active
Last updated: 2026-07-05

## Purpose

This document gives human and AI contributors the minimum shared context required
to work consistently on the AI Skill Framework.

## Vision

Build a modular, reusable, testable, and maintainable framework for AI-assisted
software development, writing, research, and workflow automation. The framework
is a long-lived system of skills and knowledge, not a collection of giant prompts.

## Source of Truth

This repository is the authoritative project record. Architecture, decisions,
requirements, skills, workflows, reusable knowledge, tests, and project status
must be represented here and versioned with Git.

Conversation history, model memory, local notes outside the repository, and
generated output are not authoritative. If they conflict with the repository,
contributors must follow the repository or propose a documented change.

## Contributor Model

AI models are contributors, not owners or sources of truth. An AI contributor
must read the relevant repository documentation before making a change, preserve
existing decisions, state assumptions, and record durable knowledge in the
appropriate repository artifact.

Human contributors remain responsible for project direction and approval.

## Architecture

The architecture separates orchestration, execution, knowledge, and quality:

```text
User
  -> Master Skill
  -> Workflow Engine
  -> Skill Library
  -> Knowledge Base
  -> Evaluation Engine
  -> Reflection Engine
  -> Final Output
```

- The **Master Skill** is a thin orchestrator. It detects intent, selects a
  workflow and skills, coordinates execution, and combines results. Specialized
  business logic does not belong in it.
- The **Workflow Engine** defines execution order without embedding deep domain
  knowledge.
- The **Skill Library** contains focused capabilities. One Skill has one
  responsibility.
- The **Knowledge Base** stores reusable domain knowledge separately from prompts
  and skills.
- The **Evaluation Engine** checks output quality.
- The **Reflection Engine** improves output before delivery.

See [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md) for the
component-level description.

## Working Principles

1. Repository is the source of truth.
2. Documentation comes before implementation.
3. AI models contribute through documented, reviewable changes.
4. Keep the Master Skill focused on orchestration.
5. One Skill = One Responsibility.
6. Keep reusable knowledge separate from prompts.
7. Reuse existing components before creating new ones.
8. Evaluate and reflect on outputs.
9. Record significant architectural decisions as ADRs.

## Documentation-First Workflow

1. Read `PROJECT_CONTEXT.md` and the relevant architecture, principles, and ADRs.
2. Confirm the requirement against the current project tracker.
3. Document new decisions or update affected documentation.
4. Implement the smallest architecture-aligned change.
5. Review and test the change.
6. Update the tracker and other affected repository documents.
7. Commit and push a coherent change set.

## Current Focus

The project completed **Sprint 24 - Repository Integrity Completion**.
`content_integrity.py` automates local Markdown links and anchors, duplicate
anchors, ADR references, retired canonical identities, active-package
placeholders, high-confidence secret signatures, and active Skill/Knowledge
consumer policy. These checks run inside unified repository validation with
structured `ASF-REPOSITORY-006..013` diagnostics. All prior validation and
Runtime planning remain green, with 101 passing unit tests.

The framework still has no Runtime executor or model invocation. Discovery,
validation, and planning are deterministic and offline; no Skill execution,
retrieval, or generation occurs. The next infrastructure priority is
Tool/Connector contract design before execution. See
`PROJECT_TRACKER.md` for the exact deferred gaps.

## Definition of Done

A change is complete when:

- repository documentation and project status are current;
- the change follows the documented architecture and design principles;
- applicable review and tests have passed;
- significant decisions are captured in ADRs;
- the coherent change set is committed and pushed;
- the working tree is clean for the completed scope.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established shared context and contributor rules |
| 0.2 | 2026-07-04 | Set Sprint 2 Knowledge Architecture as current focus |
| 0.3 | 2026-07-04 | Set Sprint 3 AI Skill Specification as current focus |
| 0.4 | 2026-07-04 | Set Sprint 4 Skill Architecture as current focus |
| 0.5 | 2026-07-04 | Set Sprint 5 Workflow Architecture as current focus |
| 0.6 | 2026-07-04 | Set Sprint 6 quality architecture as current focus |
| 0.7 | 2026-07-04 | Set Sprint 7 schema and validation focus |
| 0.8 | 2026-07-04 | Set Sprint 8 validator prototype as current focus |
| 0.9 | 2026-07-04 | Set Sprint 9 CLI architecture as current focus |
| 0.10 | 2026-07-04 | Set Sprint 10 Template Engine as current focus |
| 0.11 | 2026-07-04 | Set Sprint 11 Intermediate Representation as current focus |
| 0.12 | 2026-07-04 | Set Sprint 12 Generator Engine architecture as current focus |
| 0.13 | 2026-07-04 | Set Sprint 13 CLI Design Expansion as current focus |
| 0.14 | 2026-07-04 | Completed Sprint 14 Repository Engineering Review |
| 0.15 | 2026-07-04 | Set Sprint 15 AI Team Architecture as current focus |
| 0.16 | 2026-07-04 | Completed Sprint 16 Validator Roadmap Phase 2 (IR adapters) |
| 0.17 | 2026-07-04 | Completed Sprint 17 Validator Roadmap Phase 3 (Dependency/Version Graph) |
| 0.18 | 2026-07-05 | Completed Sprint 18 Content Creation Skill v1 production package |
| 0.19 | 2026-07-05 | Completed Sprint 19 Research Skill v1 production package |
| 0.20 | 2026-07-05 | Completed Sprint 20 Review Quality Skill v1 production package |
| 0.21 | 2026-07-05 | Completed Sprint 21 IR-level Semantic Validator core |
| 0.22 | 2026-07-05 | Completed Sprint 22 Repository Discovery and initial integrity validation |
| 0.23 | 2026-07-05 | Completed Sprint 23 non-executing Runtime planning foundation |
| 0.24 | 2026-07-05 | Completed Sprint 24 bounded Repository Integrity rules |
