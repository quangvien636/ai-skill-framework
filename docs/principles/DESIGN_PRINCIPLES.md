# AI Skill Framework - Design Principles

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

These principles govern the design and evolution of Skills, Workflows, the
Knowledge Base, templates, quality engines, and the Master Skill. New work must
follow them or document an explicit exception through an ADR.

## 1. Repository Is the Source of Truth

The version-controlled repository is the authoritative record for project
context, architecture, decisions, implementation, knowledge, tests, and status.
Conversation history and AI model memory are temporary inputs, not project state.

**Implications:**

- Durable decisions and knowledge must be committed to the repository.
- Conflicts are resolved in favor of current repository documentation.
- Significant architecture changes require an ADR.

## 2. Documentation First

Documentation is part of the product. Define intent, boundaries, interfaces, and
architectural impact before implementation. Update affected documentation in the
same change set as implementation.

Documentation First means creating enough clarity to guide a change; it does not
mean producing speculative documentation for work that has not been selected.

## 3. AI Models Are Contributors

AI models read, propose, implement, and review changes under the same documented
rules as other contributors. They do not own project context and cannot replace
repository history with remembered conversation.

AI-generated changes must remain inspectable, attributable through Git, and
subject to human direction and review.

## 4. Master Skill Only Orchestrates

The Master Skill stays thin. It understands the request, selects the workflow and
skills, coordinates execution, combines outputs, and invokes quality checks.

Specialized business logic, reusable domain knowledge, and deep task execution
belong in Skills, the Knowledge Base, or dedicated engines, not in the Master
Skill.

## 5. One Skill = One Responsibility

Each Skill performs one cohesive capability with a clear input, output, and
success criterion. A Skill should have one primary reason to change.

A focused Research Skill or Review Skill is valid. A single Skill that researches,
writes, reviews, and publishes is a workflow disguised as a Skill and must be
decomposed.

## 6. Separate Knowledge from Prompts

Reusable facts, policies, examples, patterns, and domain guidance belong in the
Knowledge Base. Prompts should contain only the focused instructions and context
needed to perform a task.

Skills reference shared knowledge rather than duplicating it. This separation
makes knowledge versionable, reusable, reviewable, and independently testable.

## 7. Separate Architectural Responsibilities

- Workflows define execution order.
- Skills perform specialized work.
- The Knowledge Base supplies reusable knowledge.
- The Evaluation Engine measures quality against explicit criteria.
- The Reflection Engine identifies and applies improvements.
- The Master Skill coordinates these components.

No component should absorb another component's core responsibility.

## 8. Design for Reuse and Composition

Prefer composing existing focused components over duplicating logic or creating a
larger component. Skills should be reusable across workflows, and workflows
should express business processes by composing Skills.

## 9. Make Quality Testable

Every reusable module must define its contract and quality expectations. As
applicable, provide:

- defined inputs and outputs;
- validation and failure behavior;
- examples and test cases;
- a review checklist or quality rubric.

Evaluation checks quality; Reflection uses those findings to improve the result.

## 10. Evolve Through Explicit Decisions

Use Git for every meaningful change and ADRs for significant architectural
choices. Prefer small, coherent, reviewable changes. Improve the framework through
the cycle:

```text
Plan -> Document -> Implement -> Evaluate -> Reflect -> Improve -> Release
```

## Decision Checklist

Before accepting a design, confirm:

- Is it consistent with repository documentation and existing ADRs?
- Is the Master Skill limited to orchestration?
- Does each Skill have one responsibility?
- Is reusable knowledge outside the prompt?
- Are component boundaries and quality criteria testable?
- Are affected documents and tracker entries current?

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the framework design principles |
