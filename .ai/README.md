# AI Team

Governance documents describing how human and AI contributors collaborate
on the AI Skill Framework repository itself. This is documentation, not an
executable Skill or agent system — see ADR-0008.

## Roles

| Role | One Decision Right |
| --- | --- |
| [Chief Architect](roles/CHIEF_ARCHITECT.md) | Sole approver of a new or superseding ADR |
| [Principal Engineer](roles/PRINCIPAL_ENGINEER.md) | Sole authority to open/close a Sprint entry in `PROJECT_TRACKER.md` |
| [Framework Engineer](roles/FRAMEWORK_ENGINEER.md) | Sole authority over implementation-detail choices within an already-accepted architecture |
| [Quality Engineer](roles/QUALITY_ENGINEER.md) | Sole authority to block a commit for a consistency violation |
| [Test Engineer](roles/TEST_ENGINEER.md) | Sole authority to mark a schema/spec change "covered" by a fixture |
| [Documentation Engineer](roles/DOCUMENTATION_ENGINEER.md) | Sole authority over documentation structure/format conventions |
| [Automation Engineer](roles/AUTOMATION_ENGINEER.md) | Sole authority over what is automated vs. left as a manual checklist |

## Playbooks

- [Sprint Workflow](playbooks/SPRINT_WORKFLOW.md) — the Understand -> Plan ->
  Design -> Implement -> Review -> Validate -> Commit -> Push loop this
  repository's sprints already follow.
- [Handover](playbooks/HANDOVER.md) — what a session must leave behind for
  the next one.

## Standards

- [Collaboration Standards](standards/COLLABORATION_STANDARDS.md) — how
  roles interact, escalate, and share ADR/tracker ownership.

## Governance

- [Decision Rights](governance/DECISION_RIGHTS.md) — human vs. AI authority,
  consistent with ADR-0001's "AI models are contributors, not owners."

## Relationship to the Rest of the Repository

Roles describe *how contributors work on this repository*; they are not
Skills, Workflows, or Runtime components, and they do not appear in
`skills/` or `workflows/`. A role has no `skill.yaml`, is never selected by
a Master Skill, and is never invoked by the framework it governs — see
ADR-0008 for why that boundary is deliberate.
