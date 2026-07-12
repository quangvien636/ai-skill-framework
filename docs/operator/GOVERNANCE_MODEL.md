# Governance Model

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Consolidate `.ai/README.md`, `.ai/roles/*.md`, `.ai/governance/DECISION_RIGHTS.md`,
and `.ai/standards/COLLABORATION_STANDARDS.md` into one operator-facing
narrative of who decides what, with worked escalation examples — without
restating their normative text verbatim, per this manual's "reference, don't
duplicate" philosophy.

## Scope

Covers governance purpose, authority sources, decision categories,
responsibility boundaries, evidence requirements, approval lifecycle,
escalation process, and auditability. The seven `.ai/roles/*.md` files and
`.ai/governance/DECISION_RIGHTS.md` remain the normative source for any
specific role's Decision Right; this chapter is the map, not the territory.

## Design

### Governance purpose

This repository's governance exists to let AI and human contributors work
across many independent sessions without either (a) requiring a human to
approve every routine change, or (b) letting an AI session make a
consequential, hard-to-reverse decision alone. ADR-0001 states the
underlying principle: "AI models are contributors, not owners or sources of
truth."

### Authority sources, ranked

1. **The human maintainer** — ultimate authority; the only party who can
   accept an ADR, approve lifecycle promotion, or authorize a destructive
   Git operation (`.ai/governance/DECISION_RIGHTS.md`).
2. **The seven roles in `.ai/roles/`** — each with one named Decision Right,
   acting *under* human-set direction, not instead of it.
3. **A session holding no specific role** — must escalate anything not
   covered by a generic, already-authorized action (see
   [Authority Levels](AUTHORITY_LEVELS.md) Level 0-1).

### The seven roles, their Decision Right, and their explicit boundaries

| Role | Decision Right | Explicitly does NOT decide |
| --- | --- | --- |
| Chief Architect | Sole approver of a new or superseding ADR | Sprint scope/ordering (Principal Engineer); implementation (Framework Engineer); repository-wide sweeps (Quality Engineer) |
| Principal Engineer | Sole authority to open/close a Current Sprint entry in `PROJECT_TRACKER.md` | ADR acceptance (Chief Architect); direct implementation (though may also act as Framework Engineer in the same session); repository-wide sweeps (Quality Engineer) |
| Framework Engineer | Sole authority over implementation-detail choices within an already-accepted architecture | Deviating from accepted architecture without an ADR; Sprint scope (Principal Engineer); documentation template/format (Documentation Engineer) |
| Quality Engineer | Sole authority to block a commit for a consistency violation | Architecture decisions (routes to Chief Architect as a proposed ADR); fixture coverage (Test Engineer); building automation (Automation Engineer) |
| Test Engineer | Sole authority to mark a schema/spec change "covered" by a fixture | Repository-wide consistency sweeps (Quality Engineer); building the validator script itself (Automation Engineer) |
| Documentation Engineer | Sole authority over documentation structure/format conventions | Content correctness of a specific architecture/specification (its author, reviewed by Chief Architect); periodic consistency sweeps (Quality Engineer) |
| Automation Engineer | Sole authority over what is automated vs. left as a manual checklist | What a check should verify (owned by the architecture/spec/role the check enforces); framework product artifacts (Framework Engineer) |

### One contributor, multiple roles

A single session, human or AI, may hold multiple roles at once — this
repository's entire 44-sprint history has, in practice, been one AI
contributor acting as Principal Engineer, Framework Engineer, Test
Engineer, and Quality Engineer across sprints
(`.ai/standards/COLLABORATION_STANDARDS.md`). Holding multiple roles does
not merge their Decision Rights into one undifferentiated authority — each
decision this Batch's own session makes still belongs to a specific role:
writing `docs/operator/*.md` chapters is a Documentation Engineer decision;
recording Sprint 45 in `PROJECT_TRACKER.md` is a Principal Engineer
decision; proposing ADR-0020's continuation is a Chief-Architect-drafted,
human-pending decision.

### Decision categories

| Category | Example | Who decides |
| --- | --- | --- |
| Architectural decision | Adopting a new cross-cutting rule or boundary | Chief Architect drafts/accepts; human ratifies per Decision Rights |
| Sprint scope | What this session works on next | Principal Engineer |
| Implementation detail | Which equivalent internal data structure to use | Framework Engineer, unilaterally, within accepted architecture |
| Consistency/quality gate | Whether a commit has a broken link or duplicated concept | Quality Engineer, blocking |
| Test coverage sufficiency | Whether a fixture actually exercises a new rule | Test Engineer |
| Documentation structure | What sections a template requires | Documentation Engineer |
| Automation scope | Whether a manual check becomes a script | Automation Engineer |
| Human-reserved decision | ADR acceptance, lifecycle promotion, destructive Git ops, scope expansion | Human maintainer only (see [Authority Levels](AUTHORITY_LEVELS.md) Level 4) |

### Evidence requirements

Every decision above Level 1 (see [Authority Levels](AUTHORITY_LEVELS.md))
must be traceable to evidence, not assertion: a Sprint's backlog table cites
its "Evidence / Output" column; a Quality Engineer block cites the specific
broken reference; a Test Engineer sign-off cites the actual fixture file
and its expected diagnostic. This mirrors `PROJECT_TRACKER.md`'s own
44-sprint convention of always citing the command and result behind a
"Done."

### Approval lifecycle (for an ADR, the highest-weight artifact)

```text
Draft (any role may propose)
  -> Chief Architect review (approve / reject / send back)
  -> Status: Proposed (committed, discoverable, not yet binding)
  -> Human maintainer review
  -> Status: Accepted (binding) or the proposal is abandoned/revised
  -> (later) Status: Superseded by ADR-<NNNN>, if reversed by a new decision
```

An AI session may complete every step through "Status: Proposed." Moving to
"Status: Accepted" requires the human maintainer's explicit review, unless
that authority was explicitly delegated for the session (as
`.ai/governance/DECISION_RIGHTS.md` notes happened for ADR-0002 through
ADR-0007, and as this repository's own Sprint 42 notes happened for
ADR-0016 through ADR-0019).

### Escalation process

1. An implementation disagreement escalates to the Framework Engineer, then
   the Chief Architect.
2. A scope disagreement escalates to the Principal Engineer.
3. A decision that does not clearly belong to any role's Decision Right, or
   that a role is uncertain falls inside or outside its own authority,
   escalates to a human — per `.ai/governance/DECISION_RIGHTS.md`'s
   Escalation rule, uncertainty defaults to escalation, never to proceeding.
4. See [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md)
   for the full escalation procedure and required documentation.

### Auditability

Every governance decision this repository makes is auditable because it is
committed: an ADR's Git history shows exactly when it moved from Proposed
to Accepted and by what commit; `PROJECT_TRACKER.md`'s Sprint History shows
exactly which Principal-Engineer-level scope decisions were made and when;
role boundaries are themselves versioned documents, not verbal
understanding. No governance decision in this repository depends on a
conversation transcript for its record.

## Examples

**Worked escalation example 1 (implementation disagreement):** A session
implementing a new `docs/operator/*.md` chapter must decide whether to name
a table column "Authority" or "Decision Right." This is a documentation
structure choice (Documentation Engineer's Decision Right) — resolved
unilaterally, no escalation, because it does not change any normative rule.

**Worked escalation example 2 (scope disagreement):** A session discovers,
while writing this Batch, that `docs/guides/DEVELOPMENT_GUIDE.md` is a stub
the Documentation Engineer role already owns. Filling it in is not part of
this Batch's assigned scope (Batch 1 is the Master Operator build-out, not
guide population). Per the Principal Engineer's scope authority, this is
recorded as a Next Action rather than opportunistically implemented —
avoiding uncontrolled scope creep even though the fix would be easy.

**Worked escalation example 3 (human-reserved decision):** This same Batch
proposes no new ADR beyond continuing to build on already-proposed
ADR-0020, because no new cross-cutting rule is introduced (see
[ADR Governance & Decision Rules](ADR_GOVERNANCE.md) for why). If a future
Batch did need to introduce one, it would stop at `Status: Proposed` and
record a `PROJECT_TRACKER.md` Next Action asking the human maintainer to
review it — never mark it Accepted unilaterally.

## References

- `.ai/README.md`
- `.ai/roles/*.md`
- `.ai/governance/DECISION_RIGHTS.md`
- `.ai/standards/COLLABORATION_STANDARDS.md`
- ADR-0001, ADR-0008
- [Authority Levels](AUTHORITY_LEVELS.md)
- [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
