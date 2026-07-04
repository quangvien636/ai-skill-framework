# Principal Engineer

## Responsibility

Translate the roadmap and backlog into one Sprint at a time: define its
goal, backlog, and exit criteria, drive it through the
[Sprint Workflow](../playbooks/SPRINT_WORKFLOW.md), and close it out in
`PROJECT_TRACKER.md`. The Principal Engineer is the role most sessions of
this framework's own development have been operating as.

## Inputs

- `PROJECT_TRACKER.md`'s Sprint History and Next Actions.
- `docs/roadmaps/*.md`.
- Chief Architect decisions (accepted ADRs) that unblock or constrain a
  Sprint's scope.

## Outputs

- `PROJECT_TRACKER.md` Current Sprint section (goal, backlog, exit
  criteria) and its move into Sprint History on completion.
- `PROJECT_CONTEXT.md`'s Current Focus section.
- Sprint-level decisions about what is in scope vs. deferred to Next
  Actions.

## Decision Right

The Principal Engineer is the sole authority to open a new Current Sprint
entry in `PROJECT_TRACKER.md` and to mark it Completed and fold it into
Sprint History.

## Boundaries

- Does not accept ADRs — that is the [Chief Architect](CHIEF_ARCHITECT.md);
  the Principal Engineer proposes them alongside the Framework Engineer.
- Does not implement the sprint's artifacts directly, though in practice
  (as in a single-contributor AI session) the same session may act as both
  Principal Engineer and Framework Engineer — the roles remain distinct
  responsibilities even when one contributor holds both.
- Does not run the repository-wide consistency sweep that closes out a
  Repository Engineering Review sprint — that is the
  [Quality Engineer](QUALITY_ENGINEER.md).
