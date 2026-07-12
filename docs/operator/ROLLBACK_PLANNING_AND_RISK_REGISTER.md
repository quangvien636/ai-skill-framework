# Rollback Planning and Risk Register

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define minimum rollback requirements by change class, and when a risk must
be formally recorded rather than left implicit.

## Scope

Applies to any change above Level 1 authority (see
[Authority Levels](AUTHORITY_LEVELS.md)). Rollback here means undoing a
change after it has been committed and its consequences discovered to be
wrong — distinct from [Recovery Procedures](RECOVERY_PROCEDURES.md), which
handles interruption/inconsistency before or during a change.

## Design

### Rollback requirements by change class

| Situation | Rollback strategy |
| --- | --- |
| Any documentation or code change | `git revert <commit>` — this repository's entire history is a sequence of coherent, single-purpose commits, so a clean revert is the default expectation for every change class below High risk |
| Feature isolation | A change that adds a new capability without modifying an existing one (e.g., a new `docs/operator/*.md` chapter) — rollback is simply removing the new file(s); nothing else depended on them yet |
| Compatibility fallback | A change to an existing behavior with consumers — confirm before implementing that the prior behavior remains reachable (e.g., via the existing draft/active lifecycle status) until the new behavior is proven |
| Data preservation | No hand-authored data store exists in this repository's current scope; the closest analogue is `knowledge/` content — rollback there means `git revert`, since nothing is generated from it that would need separate regeneration |
| Configuration rollback | `runtime/*/runtime.yaml` lifecycle changes — rollback per ADR-0015's Dependency Resolver behavior: an active-orphan check already prevents an unresolvable state (Sprint 38's own pattern: promoting one Runtime Contract atomically demoted the displaced one back to draft in the same commit) |
| Generated artifact restoration | This repository currently has no committed generator output; when `docs/architecture/GENERATOR_ARCHITECTURE.md`'s Generator exists, this row must be updated to state the regeneration command |
| Documentation rollback | `git revert`; additionally confirm no other document was updated to cross-reference the reverted one in a way that would now dangle — re-run `validate_repository.py` after any revert |
| Post-rollback validation | Always re-run the full applicable validation suite after any revert — a revert can itself introduce inconsistency (e.g., reverting a chapter that other chapters now link to) |

Never prescribe destructive history rewriting (`git reset --hard` on shared
history, `git push --force`) as a rollback mechanism — `git revert` is
always preferred because it preserves history per this repository's Git
Safety Protocol.

### Risk register

A risk must be recorded (in `PROJECT_TRACKER.md`'s Risks and Guardrails
table, or a chapter's own risk note) when it is:

- **Recurring** — has happened before or is structurally likely to happen
  again (e.g., "adapter test suites must stay isolated" is already recorded
  because Sprint 42 found it mattered).
- **Non-obvious** — a future session would not discover it without being
  told (e.g., "this manual's chapters must never link to an unwritten
  chapter" — mechanically enforced, but worth stating so a session
  understands *why* validation fails if it forgets).
- **Consequential** — its materialization would be costly to detect or fix
  late.

Do not record a risk that is purely theoretical with no plausible trigger —
this turns the tracker into unmaintainable noise, which is itself the
"Governance documents grow unbounded" risk `PROJECT_TRACKER.md` already
guards against.

### Risk register entry shape

| Field | Content |
| --- | --- |
| Risk | One sentence |
| Evidence | Why this is a real, not theoretical, risk |
| Likelihood | Low / Medium / High |
| Impact | Low / Medium / High |
| Mitigation | The concrete control already in place or proposed |
| Owner | The role whose Decision Right covers it |
| Trigger | What would indicate the risk has materialized |
| Status | Open / Mitigated / Accepted |
| Last verification | Date last checked |
| Linked task or ADR | Cross-reference |

### This Batch's own risk register additions

| Risk | Evidence | Likelihood | Impact | Mitigation | Owner | Trigger | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/operator/` chapters drift from the authoritative documents they synthesize | This is the single largest maintenance risk a synthesis layer introduces | Medium | Medium | [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)'s audit procedure, run at least once per future Batch | Documentation Engineer | A session finds a chapter contradicting its cited source | Open, mitigated by process (not yet automated) |
| Cross-reference sprawl among `docs/operator/*.md` chapters makes future edits error-prone | This Batch alone created ~30 files with dozens of mutual links | Medium | Low | `validate_repository.py`'s mechanical link/anchor check on every commit | Automation Engineer (existing tooling) | Any broken link | Mitigated (already automated) |
| `docs/operator/` grows without bound across future Batches | This Batch alone added ~30 chapters against an original 39-chapter estimate | Low | Medium | [Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md)'s split/merge thresholds | Documentation Engineer | Navigation becomes genuinely difficult (observed, not assumed) | Open, accepted for now |

## Examples

See this Batch's own risk register additions above — recorded because each
is evidenced by this Batch's own real scale, not hypothetical.

## References

- [Recovery Procedures](RECOVERY_PROCEDURES.md)
- [Work Decomposition, Dependency & Impact Analysis](WORK_DECOMPOSITION_AND_IMPACT_ANALYSIS.md)
- `PROJECT_TRACKER.md` Risks and Guardrails

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
