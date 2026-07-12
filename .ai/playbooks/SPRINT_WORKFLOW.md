# Sprint Workflow

The loop every Sprint in this repository's history (Sprints 1-14) has
followed, made explicit so future sessions — human or AI — repeat it
without rediscovering it from Git history.

```text
Understand -> Plan -> Design -> Implement -> Review -> Validate -> Commit -> Push
```

1. **Understand** — read `MASTER_OPERATOR.md`, `PROJECT_CONTEXT.md`,
   `PROJECT_TRACKER.md`'s Current Sprint and Next Actions, and every
   document the sprint's scope touches. Do not restate what is already
   established; build on it.
2. **Plan** — confirm the sprint's goal and backlog against the roadmap
   ([Principal Engineer](../roles/PRINCIPAL_ENGINEER.md)). For a
   non-trivial change, this is where a plan-mode style proposal belongs.
3. **Design** — for a new architectural decision, draft it as an ADR
   candidate ([Chief Architect](../roles/CHIEF_ARCHITECT.md) approves).
   Reuse an existing document/section instead of creating a new one where
   one already covers the concept.
4. **Implement** — produce the durable artifact: architecture doc, schema,
   template, fixture, or script
   ([Framework Engineer](../roles/FRAMEWORK_ENGINEER.md),
   [Test Engineer](../roles/TEST_ENGINEER.md)).
5. **Review** — check the change against Design Principles, Naming
   Convention, and existing ADRs; check for duplication with an existing
   document ([Quality Engineer](../roles/QUALITY_ENGINEER.md)).
6. **Validate** — run `python scripts/validate_contracts.py` (or the
   relevant check) and confirm it still passes before committing.
7. **Commit** — one coherent commit per sprint, explicit file paths (never
   a blind `git add -A`), a message describing what changed and why.
8. **Push** — push to `origin/main` (or open a PR, depending on the
   repository's current branch policy) so the change is durable per
   ADR-0001.

## Definition of Done for One Sprint

A sprint is done only when, per `PROJECT_CONTEXT.md`:

- the durable artifact exists in the repository;
- affected tracker, context, and navigation documents are updated in the
  same change;
- a significant decision is captured in an ADR;
- the validator (or relevant check) passes;
- the working tree is clean and the change is pushed.
