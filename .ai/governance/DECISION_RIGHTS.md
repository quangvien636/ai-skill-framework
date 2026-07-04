# Decision Rights

Human vs. AI authority for this repository, consistent with ADR-0001: "AI
models are contributors, not owners or sources of truth... Human
contributors remain responsible for project direction and approval."

## What an AI Contributor May Decide Unilaterally

Acting under one or more roles in `.ai/roles/`, within a session:

- Implementation-detail choices inside an already-accepted architecture
  (Framework Engineer's Decision Right).
- Fixture/test coverage sufficiency for a schema change (Test Engineer's
  Decision Right).
- Documentation structure and format conventions (Documentation Engineer's
  Decision Right).
- What becomes an automated script vs. a manual checklist item (Automation
  Engineer's Decision Right).
- Drafting an ADR candidate, a Sprint's backlog, or a consistency-review
  finding — these are proposals, not final decisions (see below).

## What Requires Human Direction or Approval

Per ADR-0001, project direction and approval remain with human
contributors. In practice, for this repository, that means:

- **Accepting an ADR** is drafted under the Chief Architect role, but a
  human maintainer's approval is the actual acceptance — an AI session
  marking an ADR "Accepted" in a document is a proposal for human review,
  not a final decision, unless the human operating the session has
  explicitly delegated that authority for the session (as the autonomous
  sessions that produced ADR-0002 through ADR-0007 were explicitly
  instructed to do).
- **Promoting an artifact's lifecycle** past `draft` (to `active`,
  `deprecated`, or `archived`) is a human/reviewed decision; no role's
  Decision Right includes self-promoting an artifact it authored, matching
  the Generator Architecture's rule that a Generator never promotes an
  artifact past `draft` (ADR-0006).
- **Pushing to a shared branch, force-pushing, or any destructive Git
  operation** requires the explicit scope of authorization the operating
  session was given — never assumed from a prior approval.
- **Reversing an accepted ADR's decision** requires a new ADR and the same
  human-approval path as accepting the original one.

## Escalation

A role that is uncertain whether a decision falls in "may decide
unilaterally" or "requires human direction" should treat it as requiring
human direction — per this repository's own operating instructions, an
uncertain major architectural decision is a hard-stop condition, not a
default-to-proceed one.

## Related Documents

- ADR-0001
- `standards/COLLABORATION_STANDARDS.md`
- `docs/adr/ADR-0006-generator-safe-overwrite-policy.md`
