# Authority Levels

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Give a practical, ordered authority scale (Level 0-5) that synthesizes
`.ai/governance/DECISION_RIGHTS.md` and the seven roles in `.ai/roles/`
into a single classification a session can apply quickly to any task.

## Scope

This is a **descriptive synthesis**, not a new rule: it reorganizes
existing Decision Rights into a scale for convenience. It carries no
authority beyond what `.ai/governance/DECISION_RIGHTS.md` and the role
documents already grant — where this scale and those documents disagree,
they win (per the Repository Truth Hierarchy's Authority category, see
[Truth Hierarchy & Conflict Resolution](TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md)).
Making this scale an *enforced* gate (e.g., a validator rule) rather than a
descriptive one would be a new rule requiring its own ADR, per
[ADR Governance & Decision Rules](ADR_GOVERNANCE.md) — not done here.

## Design

### The scale

| Level | Name | Examples | Permitted actions | Prohibited actions | Documentation required | Validation required | Commit/push rules | Escalation condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Read-only inspection | Reading files, running `git status`, running the validator without changes | Any read or non-mutating command | Any write | None | N/A | N/A | Never — always permitted |
| 1 | Routine corrective maintenance | Fixing a broken link, a typo, a stale tracker row for already-completed work, adding a missing regression test for an understood defect | Small, reversible, contract-free edits | Changing a schema, ADR, or public contract | Update the specific document touched | The specific validator covering that area | Commit freely; push per [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md) push rules | Only if the "small fix" turns out to touch a contract once inspected |
| 2 | Bounded implementation within accepted architecture | Implementing a Framework Engineer's Decision Right: an implementation-detail choice inside an already-accepted architecture or specification | Write new code/docs that realize an existing, accepted design | Deviate from the accepted design without an ADR | Update tracker/context plus the relevant architecture doc if the implementation reveals a documentation gap | Full applicable validation for the area touched | Commit freely; push per Change Classification rules | The implementation reveals the accepted design itself is wrong or ambiguous |
| 3 | Design changes requiring an ADR | A new cross-cutting boundary, a new contract, a reversal of a prior decision's rationale | Draft the ADR candidate (`Status: Proposed`); draft the design; may implement only what is explicitly authorized by an already-accepted parent decision | Mark the ADR `Accepted`; implement the substance of a not-yet-accepted design as if it were final | The ADR itself, plus a `PROJECT_TRACKER.md` Next Action naming the pending review | Validation for whatever narrow, non-speculative groundwork is implemented alongside the proposal | Commit the proposal; do not push implementation that assumes acceptance | Always, for the acceptance step itself |
| 4 | Human approval required | ADR acceptance; lifecycle promotion past `draft`; adding a credential/cloud path; force-push or history rewrite; production/release actions | Prepare the request with full evidence | Make the decision | A clear, evidence-backed request (see [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)) | All validation must already be green before requesting | Never self-authorize; wait for explicit approval | Always |
| 5 | Prohibited | Deleting historical evidence; bypassing failing validation to force a commit; claiming completion without evidence; unauthorized destructive Git operations; calling a paid/cloud API without authorization | None | The action itself | A hard-stop report per [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md) | N/A | Never | Always — this is a Hard Stop, not an escalation-and-wait |

### How to classify a task

1. Does it write anything? No -> Level 0.
2. Is it reversible, contract-free, and already covered by existing
   validation? Yes -> Level 1.
3. Does it realize an already-accepted design without deviating from it?
   Yes -> Level 2.
4. Does it introduce or change a cross-cutting rule, contract, or prior
   decision? Yes -> Level 3 (draft only; acceptance is Level 4).
5. Does it require a human-reserved decision per
   `.ai/governance/DECISION_RIGHTS.md` (ADR acceptance, lifecycle
   promotion, destructive Git op, credential/scope expansion)? Yes -> Level
   4.
6. Does it match a Section-2.7-style prohibited-action class (destructive,
   evidence-destroying, validation-bypassing, unauthorized external call)?
   Yes -> Level 5, hard stop.

When a task is ambiguous between two levels, classify at the **higher**
(more restrictive) level — matching `.ai/governance/DECISION_RIGHTS.md`'s
own Escalation rule that uncertainty defaults to caution.

## Examples

**Level 1:** Correcting a broken relative link found in
`docs/guides/COMPILER_LIFECYCLE.md`.

**Level 2:** Adding a new `ASF-REPOSITORY-*` diagnostic implementing a rule
that `docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md` already
describes but `scripts/asf_validator/content_integrity.py` does not yet
enforce.

**Level 3:** Writing this Batch's own governance chapters is, per
[ADR Governance & Decision Rules](ADR_GOVERNANCE.md), classified as
synthesis (Level 2, bounded implementation within already-accepted
governance), not Level 3 — no new rule is introduced. Had this Batch
instead proposed *changing* which role approves an ADR, that would be
Level 3.

**Level 4:** Promoting a `docs/operator/*.md` chapter set from this
session's own draft status to being treated as binding process (rather
than descriptive synthesis) would require human review, matching how
lifecycle promotion past `draft` already requires it for any other
artifact.

**Level 5:** Force-pushing over `origin/main` to "clean up" this Batch's
commit history without explicit authorization.

## References

- `.ai/governance/DECISION_RIGHTS.md`
- [Governance Model](GOVERNANCE_MODEL.md)
- [MASTER_OPERATOR.md](../../MASTER_OPERATOR.md) — Autonomous Development
  Rules
- [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
