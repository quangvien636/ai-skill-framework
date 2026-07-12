# Validation and Repair Loop

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the loop a session runs between the `validation` and `repair` states
of the [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md),
and the failure taxonomy that determines whether a session may continue,
must repair first, or must escalate.

## Scope

Covers classifying validation failures and the response each class
requires. It does not re-document what each individual validator checks —
`docs/guides/VALIDATION_GUIDE.md` remains authoritative for that; this
document is about *what to do* with a failure once one occurs.

## Design

### The loop

```text
Run applicable validation
  -> classify each failure (see taxonomy below)
  -> determine whether caused by the current change
  -> repair current-change-caused failures immediately
  -> investigate (do not silently fix) pre-existing failures
  -> document evidence for every failure, fixed or deferred
  -> re-run the specific validation that failed
  -> run the broader regression suite before commit
```

"Applicable validation" for this repository, as verified in this session,
currently means one or more of: `python scripts/validate_repository.py`
(repository-wide integrity, links, anchors, ADR references/status,
placeholders, secrets, lifecycle orphans), `python scripts/validate_contracts.py`
(schema fixture conformance), `python scripts/build_ir.py` /
`build_graph.py` / `build_semantics.py` (IR/graph/semantic fixture
conformance), `python -m unittest discover -s tests/unit` (core unit
tests), and each `adapters/<name>/tests/` suite run in its own isolated
process (per Sprint 42's documented isolation requirement — see
[Repository Architecture Map](REPOSITORY_ARCHITECTURE_MAP.md)). A
documentation-only change requires only `validate_repository.py`; a code
change requires the relevant subset plus `validate_repository.py`.

### Failure classification

| Class | Definition | Expected response | Continuation allowed? | Commit allowed? | Escalation required? |
| --- | --- | --- | --- | --- | --- |
| Syntax | File does not parse (Markdown link regex aside, this mainly means Python/YAML/JSON syntax errors) | Fix immediately; this is always in scope | No, until fixed | No | No |
| Formatting | Style-only issue with no behavior change (this repository has no dedicated formatter configured today — treat any future one as authoritative once added) | Fix if trivial and in scope; otherwise note as a gap | Yes if not blocking | Yes if unrelated to current change | No |
| Schema | `ASF-SCHEMA-*` diagnostic from `validate_contracts.py` or the pipeline | Fix the artifact (or, rarely, the schema itself as its own classified change) | No, until fixed | No | Only if the schema itself appears wrong, not just the artifact |
| Contract | `ASF-SEMANTIC-*` / `ASF-BINDING-*` diagnostic — a structurally valid artifact violating a cross-artifact rule | Fix the artifact or its dependency graph edges | No, until fixed | No | If the fix would require changing an accepted ADR's rule |
| Unit test | A `tests/unit/*.py` failure | Diagnose root cause; fix code or, if the test's expectation was wrong, fix the test with justification recorded | No, until fixed or diagnosed as pre-existing | No, unless pre-existing and unrelated (see below) | If the fix touches a contract another Skill/Workflow depends on |
| Integration/adapter test | A `adapters/<name>/tests/` failure, run in its own isolated process | Same as unit test; remember adapter suites must not be collected together (Sprint 42) | No, until fixed or diagnosed as pre-existing | No, unless pre-existing and unrelated | If it involves a live-service opt-in test (e.g., `ASF_TEST_OLLAMA=1`) failing for environment reasons, not code reasons |
| Graph | `ASF-DEP-*`/`ASF-VER-*`-family diagnostic from `build_graph.py` or dependency/version graph validation | Fix the dependency/version declaration causing the cycle, missing edge, or duplicate id | No, until fixed | No | No |
| Repository policy | `ASF-REPOSITORY-*` diagnostic (broken link, duplicate anchor, invalid ADR reference/status, placeholder, secret pattern, lifecycle orphan) | Fix the specific violation named by the diagnostic's `location` | No, until fixed | No | Secret-pattern hits always escalate even if a false positive, to confirm before dismissing |
| Documentation | A `docs/operator/*.md` or other document found to contradict a more authoritative source during this session's own review | Correct it in the same change per the Truth Hierarchy | Yes, this is not blocking unless the contradiction is itself the task | Yes | No, unless the contradiction reveals an unresolved governance question |
| Broken links | Same mechanism as Repository policy above; called out separately because it is the most common Batch-1-relevant failure | Fix the relative path or anchor, or remove the premature link | No, until fixed | No | No |
| Stale generated artifacts | Not currently applicable — this repository has no generator producing committed output yet (`docs/architecture/GENERATOR_ARCHITECTURE.md` describes a future capability) | N/A today; when a Generator exists, define here | N/A | N/A | N/A |
| Flaky/nondeterministic | A test that fails intermittently with no code change between runs | Re-run to confirm; if confirmed flaky, this is itself a defect — record it, do not simply re-run until green and ignore it | Yes, but only after re-run confirms it is not a real regression | No, until root-caused or explicitly tracked as a known-flaky Next Action | Yes, flakiness in a validated framework is a quality-gate concern |
| Environment limitation | A check requires a tool/service not available in the current environment (e.g., no local Ollama installed for an opt-in live test) | Skip only the specific opt-in check; do not skip core validation; record the limitation | Yes | Yes, if only the environment-gated opt-in check is affected | No, this is an expected, already-documented pattern (dry-run default, `ASF_TEST_OLLAMA=1` opt-in) |
| External dependency failure | A check depends on something outside the repository's control failing (e.g., `git fetch` with no network) | Treat per [Session Bootstrap Protocol](SESSION_BOOTSTRAP_PROTOCOL.md) step 3's fallback; does not block local-only work | Yes for non-push-dependent work | Yes | Only if the task specifically requires the unavailable dependency |

### Determining "caused by current change" vs. pre-existing

1. Run the failing validator/test on `HEAD` (before your uncommitted
   changes, e.g. via `git stash` or by checking the last known-green
   `PROJECT_TRACKER.md` exit criteria for the current sprint).
2. If it also fails on `HEAD`, it is pre-existing — document it, do not
   silently claim credit for fixing it unless fixing it was the task, and
   do not let it block unrelated work.
3. If it passes on `HEAD` and fails with your changes applied, it is
   current-change-caused — repair before proceeding to `documentation`.
4. If step 1 is impractical (e.g., a slow suite), reason from the most
   recent sprint's recorded exit criteria in `PROJECT_TRACKER.md` instead —
   but prefer the direct check when the cost is low, since a stale tracker
   entry is itself a class of failure this loop must not blindly trust.

### Repeated-failure threshold

If the same repair attempt fails twice for the same root cause, stop
repairing blindly and re-diagnose from evidence (re-read the diagnostic's
exact message, location, and suggestion fields) rather than trying a third
variation. If a third attempt also fails, this is an escalation condition —
the session's understanding of the problem is likely wrong, not just the
fix.

## Examples

A change to `docs/operator/RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md`
introduces a link to a chapter that does not exist yet.
`validate_repository.py` reports `ASF-REPOSITORY-006` (link target missing)
— classified as Repository policy / Broken links, caused by the current
change, must be fixed before commit. The fix: remove the markdown link
syntax and reference the planned chapter by name in plain text instead
(matching [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)'s
"never link to an unwritten chapter" rule), then re-run
`validate_repository.py` to confirm 0 errors before proceeding.

## References

- `docs/guides/VALIDATION_GUIDE.md`
- [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)
- [Repository Architecture Map](REPOSITORY_ARCHITECTURE_MAP.md) (adapter
  test isolation)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 1) |
