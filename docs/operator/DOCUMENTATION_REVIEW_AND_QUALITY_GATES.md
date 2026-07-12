# Documentation Review Workflow and Quality Gates

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the documentation review procedure (lightweight and full levels),
the Validation Report and Commit Report standards, and the quality gates
that must fail a document — separated from warning-level issues that do not
block.

## Scope

Applies to every documentation change. Complements
[Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)'s
audit procedures (which find defects) with a review workflow (which
prevents them from being committed).

## Design

### Documentation review workflow

1. Verify factual accuracy against code and repository state (not against
   memory or assumption).
2. Verify authority — does the document correctly state whether it is
   normative, descriptive, or a proposal?
3. Check terminology — matches
   [Documentation & Writing Standards](DOCUMENTATION_AND_WRITING_STANDARDS.md)'s
   established terms.
4. Check links — every relative link resolves; run
   `python scripts/validate_repository.py`.
5. Check duplicate guidance — per
   [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md).
6. Check contradiction — does this document disagree with a more
   authoritative source per the Truth Hierarchy?
7. Check current/planned distinction — no claim implies something exists
   that does not.
8. Check actionability — could a cold-start session actually act on this?
9. Check examples — at least one concrete worked example for any normative
   content.
10. Run automated validators (`validate_repository.py`, and the relevant
    test suite if code changed).
11. Correct defects found by any of the above.
12. Record verification (a Validation Report if the change class requires
    one, per
    [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)).

### Review levels

| Level | When to use | What it covers |
| --- | --- | --- |
| Lightweight | Level 1 documentation-only changes (typo, broken link, stale tracker row) | Steps 4, 10 only |
| Full | Any new document, any Level 2+ change, any document a future session will rely on for a process decision | All 12 steps |

### Documentation Quality Gates (blocking)

A document MUST fail review and MUST NOT be committed if it contains:

- A false current-state claim (asserts something exists/works that does
  not, verified).
- A broken authoritative link (caught mechanically by
  `validate_repository.py`).
- An undefined decision authority (a rule with no stated "who decides").
- Conflicting normative rules within the same document.
- An unsupported "complete" claim (a Definition of Done claimed without
  the evidence that satisfies it).
- A placeholder (`TODO`, `TBD`, bracketed instruction text) left in an
  *active* document — a template's own bracketed instructions are the one
  legitimate exception, since the template is not itself "active content,"
  it is a form to be filled.
- A command known not to work (never document a command without having
  verified it, or without clearly labeling it as illustrative/future).
- Missing safety guidance for a destructive-adjacent operation (e.g., a
  runbook step involving `git` history rewriting without an explicit
  warning).
- A stale status field (a document actively treated as authoritative but
  still marked `Draft`, or vice versa).
- Duplicated authoritative instructions with no stated hierarchy (two
  documents both claiming to be "the" answer for the same specific rule).

### Warning-level issues (do not block, but must be recorded)

- A document's Last-updated date has not changed despite a substantive
  edit (a hygiene issue, not a correctness one — fix opportunistically).
- A cross-reference that could usefully exist but does not yet (missed
  navigation convenience, not an error).
- A table that could be more concise (a style improvement).
- An example that is correct but not maximally illustrative.

### Validation Report Standard

A Validation Report records:

| Field | Content |
| --- | --- |
| Repository and branch | Absolute path and branch name |
| HEAD before / after | Commit hashes |
| Commands run | The exact commands, verbatim |
| Environment | Python version, OS, any relevant tool versions |
| Results | Pass/fail per command |
| Pass/fail counts | Numeric, e.g. "168/168" |
| Skipped checks | What was not run and why (e.g., an opt-in live-service test with no server available) |
| Known warnings | Any non-blocking finding |
| Limitations | What this validation does NOT prove |
| Artifacts | Any generated report file |
| Conclusion | Whether the change is safe to commit, stated plainly |

**Prohibited:** reporting unexecuted validation as passed. If a command was
not run, the report states that explicitly — never infer or assume a
result.

### Commit Report Standard

A final work report (per
[Multi-Session Continuity, Handover & Completion Checklist](MULTI_SESSION_CONTINUITY_AND_HANDOVER.md))
records: scope, repository, branch, HEAD transition, files changed (each
with its role, not just its path), behavior changed, validation evidence,
commit hashes and messages, push state, out-of-scope items intentionally
preserved, blockers, next eligible work. Internal Git plumbing identifiers
(tree hashes, index state) are omitted unless specifically useful for
debugging a reported problem — the report must be auditable, not merely
verbose.

## Examples

This Batch's own final report (produced at the end of all four phases) is
required to be a Commit Report per the standard above — including the
actual `validate_repository.py` pass/fail counts run against the fully
consolidated state, not a claim of "should pass."

## References

- [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)
- [Documentation & Writing Standards](DOCUMENTATION_AND_WRITING_STANDARDS.md)
- [Multi-Session Continuity, Handover & Completion Checklist](MULTI_SESSION_CONTINUITY_AND_HANDOVER.md)
- `docs/operator/_templates/VALIDATION_REPORT_TEMPLATE.md`

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 4) |
