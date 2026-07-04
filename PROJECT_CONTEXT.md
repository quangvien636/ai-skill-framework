# AI Skill Framework - Project Context

Version: 0.2
Status: Active
Last updated: 2026-07-04

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

The project is in **Sprint 2 - Knowledge Architecture**. The focus is establishing
the scalable hierarchy, taxonomy, document contract, discovery index, and naming
rules for reusable knowledge. See `PROJECT_TRACKER.md` for current progress and
`docs/architecture/KNOWLEDGE_ARCHITECTURE.md` for the detailed design.

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
