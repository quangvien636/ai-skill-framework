# Priority and Autonomous Planning Engine

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define a deterministic task-priority ordering and the planning loop a
session uses to select, decompose, and sequence work from
`PROJECT_TRACKER.md`'s Next Actions and the roadmap, so "what should I do
next" always has a derivable answer.

## Scope

Feeds [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md) step 16
(determine the next eligible task) and the `ready -> planning` transition in
[Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md).

## Design

### Priority ordering

Adapted from this Batch's own mandate to this repository's actual shape
(a documentation/validator/contract framework with no production traffic,
no live users, and a small, currently-green test suite):

1. Repository safety and corruption risks (data loss, broken working tree).
2. Security defects (a committed secret, an unauthorized capability).
3. Failing validation caused by the current or most recent session's own
   change.
4. Regressions (something that used to pass and no longer does).
5. Broken accepted contracts (a schema/specification violated by an
   existing artifact).
6. Blocking defects (something that prevents a Next Action from being
   attempted at all).
7. Governance-required documentation (an ADR whose Enforcement section
   names a document that must exist, and does not yet).
8. Milestone-critical work (the current sprint's stated backlog).
9. Missing regression coverage for an already-understood defect.
10. Reliability and recovery gaps (this Batch's own Recovery Procedures
    class of work).
11. Documentation consistency (staleness, duplication — see
    [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)).
12. Approved technical debt (a Next Action explicitly deferred earlier).
13. Performance improvements supported by evidence (not currently a live
    concern for this repository's offline validator/documentation scope,
    but the slot is retained for when it becomes one).
14. Optional polish.

### Tie-breakers

When two eligible tasks tie at the same priority tier:

1. **Unblock value** — does completing this task unblock other blocked
   work? Prefer the one that does.
2. **User impact** — for this repository, "user" means the next AI or
   human session; prefer what most reduces their re-derivation cost.
3. **Dependency count** — prefer the task fewer other open items depend on
   being done first is *not* right; prefer the task that is itself a
   dependency for the most other items (do it first to unblock them).
4. **Risk** — prefer lower risk when value is otherwise equal (per
   [Risk Classification & Governance Scenarios](RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md)).
5. **Reversibility** — prefer more reversible when value is otherwise equal.
6. **Validation availability** — prefer the task whose correctness can
   actually be checked over one that cannot yet.
7. **Effort** — prefer lower effort only after all of the above are equal;
   this repository's own guidance is explicit that easy cosmetic work must
   never be prioritized over important blocked milestones merely to show
   activity.
8. **Roadmap order** — final tie-break: `docs/roadmaps/ROADMAP.md`'s stated
   sequence.

### The planning loop

```text
Load eligible work
  -> remove blocked tasks (open trigger not fired; see Blocker
     Classification & Escalation) and unauthorized tasks (Level 4-5 per
     Authority Levels, without existing approval)
  -> identify dependencies (see Work Decomposition, Dependency & Impact
     Analysis)
  -> score remaining tasks by the Priority ordering above, tie-broken as
     above
  -> select the highest-scoring safe task
  -> decompose it if it exceeds a single coherent commit's worth of change
  -> identify validation strategy
  -> identify documentation updates required
  -> define the commit boundary
  -> execute (Autonomous Development Lifecycle)
  -> update planning state (PROJECT_TRACKER.md Next Actions: remove
     completed, add newly discovered)
  -> repeat
```

### Avoiding endless planning without execution

A session must not loop in `planning` indefinitely refining a plan. Concrete
guard: if a task has already passed the [Decision Engine](DECISION_ENGINE.md)
with a PROCEED disposition and has a stated Planning Contract (or is
explicitly Level 0-1 and exempt from requiring one), it must move to
`implementation` within the same planning pass — re-planning is only
justified by *new* information (a validation failure, a scope discovery),
not by continued deliberation over already-settled facts.

### Avoiding manufactured work

Per [MASTER_OPERATOR.md](../../MASTER_OPERATOR.md)'s Autonomous Development
Rules, a session must not implement a speculative feature merely because no
task is immediately assigned. The planning loop's "Load eligible work" step
draws only from: an explicit instruction for the current session, an open
`PROJECT_TRACKER.md` Next Action, or a roadmap item already marked "Next."
If none of these yield an eligible task, this is a legitimate Clean
Completion Stop (see
[Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md)),
not a license to invent one.

## Examples

At the start of this Batch, the planning loop's input was a single explicit
instruction spanning four phases. Eligible work was decomposed per
[Work Decomposition, Dependency & Impact Analysis](WORK_DECOMPOSITION_AND_IMPACT_ANALYSIS.md)
into per-chapter units, each independently scored as priority tier 8
(milestone-critical, the current sprint's stated backlog) with tie-breaks
resolved by the phase order the instruction itself specified.

## References

- [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md)
- [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)
- [Work Decomposition, Dependency & Impact Analysis](WORK_DECOMPOSITION_AND_IMPACT_ANALYSIS.md)
- [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
