# <Skill Display Name> Instructions

## Responsibility

<Restate the single responsibility from `skill.yaml`.>

## Procedure

1. Validate only the declared inputs.
2. Apply the focused task instructions and resolved Knowledge.
3. Produce only the declared outputs.
4. Stop safely when a constraint cannot be satisfied.

## Boundaries

- Do not invoke another Skill or select a Workflow.
- Do not embed reusable Knowledge.
- Do not use undeclared inputs, dependencies, tools, or side effects.
