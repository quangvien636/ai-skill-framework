# ADR-0008: The AI Team Is Governance Documentation, Not an Executable Skill/Agent System

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

Sprint 15 asks for an AI Team: roles (Chief Architect, Principal Engineer,
Framework Engineer, Quality Engineer, Test Engineer, Documentation
Engineer, Automation Engineer), playbooks, standards, and governance for
how contributors collaborate on this repository. There are two structurally
different ways to build this:

1. As Markdown governance documents under `.ai/`, describing responsibility,
   inputs, outputs, and decision rights for each role — read by contributors
   (human or AI) the same way `PROJECT_CONTEXT.md` or an ADR is read.
2. As executable Skills under `skills/`, each with a `skill.yaml`, so a
   future Runtime or Master Skill could literally invoke a "Quality
   Engineer" Skill.

Option 2 is tempting because the framework already has a mature Skill
contract (AI Skill Specification, Skill Architecture) that could be reused.
But a "role" as scoped here (Chief Architect, Principal Engineer, etc.)
describes *who is accountable for what decision on this repository's own
governance* — it is not a reusable task capability with a bounded input/
output contract the way `skill:summarize-document` is. Conflating the two
would give a role a `skill.yaml` it does not need and would blur One Skill
= One Responsibility (Design Principle 5): a "Framework Engineer" is not one
cohesive task, it is an accountability boundary spanning many tasks.

## Decision

The AI Team lives entirely under `.ai/` as Markdown governance documents:
`.ai/README.md`, `.ai/roles/*.md`, `.ai/playbooks/*.md`,
`.ai/standards/*.md`, `.ai/governance/*.md`. None of these are Skills:
none has a `skill.yaml`, none is discoverable by a Master Skill or
Workflow, and none is ever invoked by the framework's Runtime. They are
read the same way `PROJECT_CONTEXT.md`, the Design Principles, or an ADR
is read — by a contributor deciding how to act, not by the framework
executing a task.

Each role document follows the same shape: one responsibility statement,
inputs it consumes, outputs it owns, one decision right, and explicit
boundaries naming which other role owns what it does not. This mirrors One
Skill = One Responsibility applied to accountability rather than task
execution.

## Consequences

### Positive

- Roles stay clearly separate from Skills, avoiding a confusing situation
  where `skills/` contains both "do a task" Skills and "who's allowed to
  decide X" roles.
- A role document can name a Decision Right precisely without needing an
  input/output schema, a lifecycle, or contract tests — the machinery a
  real Skill requires but a governance role does not.
- Human oversight (ADR-0001's "AI models are contributors, not owners") is
  easier to reason about when roles are documentation a human reads and can
  override, not code a Runtime executes autonomously.

### Costs and Tradeoffs

- There is no automated enforcement of a role's Decision Right (for
  example, nothing currently blocks an AI session from editing
  `PROJECT_TRACKER.md`'s Current Sprint outside the Principal Engineer's
  described process) — enforcement is presently a review convention, not a
  validator rule.
- If the framework later wants an actual automated multi-agent workflow
  (distinct AI sessions each bounded to one role), that would need new
  architecture — this ADR deliberately does not design that; it only
  establishes that today's `.ai/` content is not it.

## Enforcement

`.ai/roles/*.md` files MUST NOT gain a `skill.yaml`, MUST NOT be referenced
from a Workflow's `steps[].skill.id`, and MUST NOT be treated as resolvable
by the Dependency Graph the same way a Skill or Knowledge document is. A
future proposal to make roles executable requires a new ADR superseding
this one, not a quiet addition of a manifest file.

## Alternatives Considered

### Model each role as a Skill under `skills/`

Rejected because a role is an accountability boundary over many tasks, not
one cohesive responsibility with a bounded input/output contract; forcing
it into the Skill contract would either produce an overly broad Skill
(violating Design Principle 5) or an empty one (a `skill.yaml` with no real
procedure).

### Skip formalizing roles at all; rely on ad hoc session instructions

Rejected because this repository has already been developed across many
sessions with repeated, similar autonomous-mode instructions (visible in
this session's own operating prompt); writing the underlying responsibility
split down once, in the repository, is exactly what ADR-0001 asks for
instead of leaving it "trapped in conversations."

## Related Documents

- `.ai/README.md`
- `.ai/roles/`
- ADR-0001
- `docs/principles/DESIGN_PRINCIPLES.md`
