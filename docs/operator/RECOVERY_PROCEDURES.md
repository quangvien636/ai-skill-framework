# Recovery Procedures

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define detailed, safe recovery procedures for every interruption or
inconsistency class a session might find at boot, so recovery is a lookup,
not an improvisation, and so evidence is never destroyed before ownership is
determined.

## Scope

Covers detection, preservation, inspection, safe recovery, validation,
documentation, and escalation conditions for each listed situation. Never
recommends destructive cleanup before preservation. Applies whether the
interrupted session was this repository's own or a different agent's.

## Design

### General rule

For every procedure below: **detect -> preserve -> inspect -> recover ->
validate -> document -> escalate if needed.** Never skip "preserve." A
`git stash` (not `git checkout .` or `git clean -f`) is the default
preservation move for uncommitted changes whose ownership is unclear.

### Procedures

| Situation | Detection | Preservation | Inspection | Safe recovery | Validation | Documentation | Escalate when |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Quota exhaustion | Session ends abruptly, no closing report | N/A (happened already) | Next session's boot sequence finds the state | If mid-implementation with no commit: assess whether the partial change is safe to commit as-is, complete, or must be reverted | Run full applicable validation before deciding | Record in `PROJECT_TRACKER.md` that the prior session was interrupted, with the partial state's disposition | Partial state is ambiguous or looks unsafe to keep |
| Interrupted session (any cause) | Uncommitted changes at boot with no matching recent commit | `git stash push -u -m "recovered-<date>"` if disposition is unclear | Read the stashed diff; compare to `PROJECT_TRACKER.md`'s last Current Sprint | If it matches an incomplete task: `git stash pop` and resume from `planning` or `implementation`; if it looks abandoned/wrong: leave stashed, document, ask before dropping | Run validation on both the stashed-out and stashed-in states to compare | Note the recovery in session notes and, if resumed, in the eventual commit message | The stash cannot be confidently attributed |
| Terminal closure | Same as "Interrupted session" | Same | Same | Same | Same | Same | Same |
| Machine restart | Same as "Interrupted session"; also check for stale lock files | Same | Same, plus check `.git/index.lock` | Same, plus see "Stale lock files" row | Same | Same | Same |
| Partial implementation | A file matches part of a plan but not all of it | Do not delete; do not "finish guessing" | Compare against the Planning Contract (if written) or the task description | Resume implementation from where the plan left off | Full validation before commit | Note in commit message that the change resumes prior partial work | The original plan cannot be reconstructed with confidence |
| Partially updated documentation | Some but not all Definition-of-Done documents reflect a change | Do not revert the code to "match" stale docs | Diff the code/behavior against every doc the change should have touched (tracker, context, architecture, ADR) | Finish the documentation update; this is normal `documentation`-state work, not a special recovery case | `validate_repository.py` (links/anchors) | The completing session's own commit documents the completion | The original change's intent is unclear from code alone |
| Validation failure (found at boot, not caused by this session) | Step 13 of [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md) shows nonzero errors before any new change | N/A | Read every diagnostic's artifact/location/message | Do not fix opportunistically as part of an unrelated task unless trivial and clearly safe; otherwise record as a Next Action | Re-run after any fix | Add to `PROJECT_TRACKER.md` Next Actions with the diagnostic code | The failure suggests repository corruption rather than a simple content defect |
| Incomplete commit (staged but not committed, or committed but message is malformed/truncated) | `git status` shows staged changes with no new commit, or `git log -1` shows a suspicious message | Do not amend blindly | Check whether the staged diff is complete and coherent | If complete: commit properly. If incomplete: unstage, treat as "Partial implementation" | Full validation before commit | N/A beyond the eventual proper commit | The staged diff mixes unrelated concerns |
| Failed push | `git push` errors (rejected, network failure, auth failure) | Commits remain local; never force-push to work around a rejection | `git status` for ahead/behind; `git log origin/<branch> -1` for what the remote actually has | If rejected due to remote having new commits: `git fetch` then evaluate `git merge` or `git rebase` against a **clean, cheap-to-verify** basis — never force-push over remote history | Full validation after any merge/rebase, before re-attempting push | Report the exact failure and the chosen resolution | Remote history is materially different from what was expected (see "Remote branch movement") |
| Remote branch movement | `git rev-list --left-right --count origin/<branch>...HEAD` shows both sides nonzero | Do not force-push | `git log origin/<branch>` vs local `git log` to see what changed remotely | Merge or rebase onto the new remote tip using ordinary (non-destructive) Git operations; resolve conflicts per "Merge conflict" row | Full validation after resolution | Note in the eventual commit/PR why history briefly diverged | Remote commits conflict with the local session's own understanding of the current sprint (possible concurrent session) |
| Merge conflict | Git reports conflict markers during merge/rebase | Do not discard either side blindly | Read both versions; determine which (or a combination) is correct per the Truth Hierarchy and the task's own plan | Resolve manually, preserving intent from both sides where both are valid | Full validation after resolution, before completing the merge/rebase | Note the resolution rationale in the merge commit or session notes | The conflict is in a normative document (ADR, schema) where the "correct" resolution is a judgment call, not mechanical |
| Detached HEAD | `git branch --show-current` returns empty | Do not commit on a detached HEAD as if it were a branch | `git log --oneline -5` to see what's checked out and why | `git switch -c <recovery-branch>` if there is unique work to save, then decide whether to merge it into `main`; otherwise `git switch main` | N/A until resolved | Note how the detached state arose if determinable | Unique, valuable commits exist only on the detached HEAD |
| Accidental work on the wrong branch | Boot step 2 shows a branch inconsistent with the task's expectation (this repository currently works directly on `main`; a feature-branch policy would change this row) | Do not delete the branch or its commits | Confirm what actually changed and whether it is safe on `main` | If safe and intended for `main`: continue. If not: create a properly named branch, move the commits (`git switch -c`, or cherry-pick), reset the wrong branch only after the work is safely preserved elsewhere | Full validation | Note the correction | Any doubt about whether commits are duplicated or lost during the move |
| Stale lock files | `.git/index.lock` or similar exists with no active Git process | Do not delete without confirming no other process is running | Check for a running `git` process before removing the lock | Remove the lock file only after confirming no process holds it | `git status` should work normally afterward | N/A unless it recurs, which would indicate a different problem | The lock reappears immediately (suggests a real concurrent process, not a stale artifact) |
| Abandoned generated files | Untracked files matching a known output pattern (e.g., under `runs/`) with no corresponding recent task | Do not delete without checking `.gitignore` intent and whether they are referenced by any doc/test | Check whether they are reproducible (i.e., safe to delete and regenerate) or unique evidence | If reproducible and not referenced: safe to leave alone (they are typically gitignored); if referenced: preserve | N/A | N/A unless they turn out to matter | The files appear to be evidence for an open investigation |
| Interrupted rebase or merge | `.git/MERGE_HEAD` or `.git/rebase-merge`/`rebase-apply` exists | Do not run `git rebase --abort` reflexively — check whether the in-progress work is worth finishing first | `git status` describes exactly what's mid-flight | Finish the operation (resolve remaining conflicts) if the intent is clear and safe; otherwise `git rebase --abort` / `git merge --abort` only after confirming no unique unpreserved work would be lost | Full validation after completion or abort | Note the outcome | The in-progress operation's original intent cannot be reconstructed |
| Worktree containing unrelated changes | Boot step 5/8 finds uncommitted changes matching no known task | `git stash push -u` before doing anything else | Read the diff; check `PROJECT_TRACKER.md` and recent commit history for any matching context | Attribute if possible and proceed accordingly; if not attributable, leave stashed and report | N/A until attributed | Report as a possible-concurrent-work finding | Always, if attribution fails — this is Hard Stop 15.1 territory per [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md) |

## Examples

A session boots and finds `git status --porcelain` listing a modified
`skills/research/instructions.md` with no corresponding entry in
`PROJECT_TRACKER.md`'s Current Sprint and no recent commit touching that
file. Per the "Worktree containing unrelated changes" row: the session
stashes the change (`git stash push -u -m "recovered-2026-07-12-unattributed-research-instructions"`),
inspects the diff, finds it does not match any documented task, and reports
it as a possible-concurrent-work finding rather than either discarding it
or building on top of it.

## References

- [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md)
- [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md)
- Git Safety Protocol (this session's own operating instructions: never
  force-push, never skip hooks, never discard uncommitted work without
  investigation)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 1) |
