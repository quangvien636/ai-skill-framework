# Handover

What a session (human or AI) must leave behind so the next session can
continue without re-deriving context, per ADR-0001's "conversation history
is not authoritative" rule.

## Before Ending a Session

Confirm each of the following is true, or explicitly note why not:

1. `git status` is clean, or any uncommitted work is clearly the next
   session's in-progress task, not accidentally abandoned.
2. `PROJECT_TRACKER.md`'s Current Sprint reflects reality: either completed
   and folded into Sprint History, or still open with an accurate backlog.
3. `PROJECT_CONTEXT.md`'s Current Focus names the actual next sprint, not a
   stale one.
4. Every new architectural decision has an ADR; no decision was made and
   left undocumented "for later."
5. `python scripts/validate_contracts.py` (or the current equivalent check)
   passes.
6. Any known inconsistency, technical debt, or deferred decision is listed
   in `PROJECT_TRACKER.md`'s Next Actions, not only mentioned in
   conversation.

## Handover Report

When a session ends (quota exhaustion, a natural stopping point, or a hard
stop condition), it should produce a report covering:

- Completed sprints/milestones this session, with commit hashes.
- Files created and modified.
- New ADRs, and what each decided.
- Remaining backlog and technical debt.
- Any hard-stop condition hit and why.
- A recommended next sprint.

This mirrors the "Final Engineering Report" instruction pattern this
repository's own autonomous-mode sessions have used; recording it here
makes the expectation independent of any one session's specific prompt.
