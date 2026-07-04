# ADR-0001: Repository Is the Source of Truth

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

The AI Skill Framework may be developed with multiple human contributors, AI
models, tools, and conversation sessions. Their local context is incomplete and
temporary. Without one durable authority, architecture, requirements, reusable
knowledge, and project status can diverge or become trapped in model memory and
chat history.

The framework also follows Documentation First. Its decisions must therefore be
discoverable, reviewable, and versioned before downstream implementation relies
on them.

## Decision

The Git repository is the authoritative source for project state.

The following durable artifacts must live in the repository:

- project context, architecture, and design principles;
- accepted architectural decisions;
- skills, workflows, prompts, templates, and implementation;
- reusable Knowledge Base content;
- tests, examples, quality criteria, and project status.

AI models are contributors. They must read the relevant repository artifacts,
follow accepted decisions, and express durable changes through reviewable
repository updates. Conversation history, model memory, generated output, and
external notes are inputs only; they are not authoritative until intentionally
captured in the repository.

When an external statement conflicts with the repository, contributors follow the
repository or propose a documented change. Significant architectural changes are
recorded in a new ADR; accepted ADRs are not silently rewritten to reverse a
decision.

## Consequences

### Positive

- Contributors can recover project context from a single versioned location.
- Changes are traceable, reviewable, and reproducible.
- AI models can collaborate without depending on shared conversational memory.
- Documentation, implementation, knowledge, and project status can evolve
  together.

### Costs and Tradeoffs

- Contributors must update documentation and tracker artifacts as part of their
  work.
- Repository documentation requires ongoing review to avoid becoming stale.
- Decisions may take slightly longer because they must be made explicit.

## Enforcement

A change is not complete until affected durable context is represented in the
repository. Reviews must check consistency with:

- `PROJECT_CONTEXT.md`;
- `docs/architecture/SYSTEM_ARCHITECTURE.md`;
- `docs/principles/DESIGN_PRINCIPLES.md`;
- accepted ADRs;
- `PROJECT_TRACKER.md`.

## Alternatives Considered

### Conversation history as the source of truth

Rejected because conversations are session-specific, difficult to review as a
coherent system, and not reliably available to every contributor.

### An AI model's memory as the source of truth

Rejected because models have incomplete, non-durable context and may interpret or
recall decisions inconsistently.

### Separate external documentation as the source of truth

Rejected for the foundation stage because it creates synchronization and access
risks. External tools may support collaboration later, but accepted durable state
must still be captured in the repository.

## Related Documents

- `PROJECT_CONTEXT.md`
- `PROJECT_TRACKER.md`
- `docs/architecture/SYSTEM_ARCHITECTURE.md`
- `docs/principles/DESIGN_PRINCIPLES.md`
