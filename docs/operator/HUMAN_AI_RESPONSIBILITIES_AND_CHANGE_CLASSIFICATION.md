# Human vs. AI Responsibilities and Change Classification

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Assign responsibility for concrete activity types as deterministic rules
rather than "ask when uncertain" prose, and define a change taxonomy with,
per class, the authority/design/validation/rollback/documentation/commit/
push requirements.

## Scope

Operationalizes `.ai/governance/DECISION_RIGHTS.md` for the specific
activity list this Batch's mandate names. Where an activity is not listed,
apply [Authority Levels](AUTHORITY_LEVELS.md)'s classification procedure
instead of treating the absence as permission.

## Design

### Responsibility table

| Activity | Responsible party | Basis |
| --- | --- | --- |
| Bug fixes (non-contract) | AI session (Level 1-2) | Framework Engineer Decision Right |
| Regression tests | AI session (Level 1-2) | Test Engineer Decision Right |
| Documentation updates matching current code/decisions | AI session (Level 1-2) | Documentation Engineer Decision Right |
| Refactoring (reversible, contract-free) | AI session (Level 2) | Framework Engineer Decision Right |
| Accepted-roadmap implementation | AI session (Level 2) | Framework Engineer Decision Right, within Principal-Engineer-scoped sprint |
| ADR drafting | AI session (Level 3, draft only) | Any role may propose (`.ai/standards/COLLABORATION_STANDARDS.md`) |
| ADR approval | Human maintainer (Level 4) | `.ai/governance/DECISION_RIGHTS.md` |
| Dependency upgrades (non-breaking, pinned range) | AI session (Level 2), with validation | Framework Engineer, provided `requirements-*.txt` pins are respected |
| Dependency upgrades (breaking / major version) | Human approval (Level 4) | Treated as a breaking change, see Change Classification below |
| Breaking changes to a public contract | Human approval (Level 4) | Requires an accepted ADR before implementation |
| External API usage (new) | Human approval (Level 4) | Section 2.7-class prohibition unless explicitly authorized by existing governance (currently: none authorized beyond local loopback Ollama, per ADR-0013/0018) |
| Credential management | Human approval (Level 4); creation is Level 5 (prohibited) for a session acting alone | Section 2.7; `.ai/governance/DECISION_RIGHTS.md` |
| Licensing decisions (adopting a new dependency's license) | Human approval (Level 4) | Not currently delegated to any role |
| Production deployment | Human approval (Level 4) | No production environment currently exists in this repository's scope; would require new governance before this row could ever apply |
| Public release / tagging a release | Human approval (Level 4) | Section 2.7 explicitly prohibits this unless permitted |
| Data migration | Human approval (Level 4) | No data-migration capability currently exists in this repository; treat any future instance as Level 4 by default until governed otherwise |
| Repository scope expansion (new top-level capability) | Human approval (Level 4) | `.ai/governance/DECISION_RIGHTS.md`'s general escalation rule |
| Security-sensitive changes (secret handling, auth) | Human approval (Level 4) | Section 2.7; no such capability currently exists in scope |
| Project-goal changes (Vision/Mission) | Human approval (Level 4) | These are foundational, ADR-0001-adjacent; changing them is definitionally a Level 3-4 architectural decision |

### Change classification

| Class | Authority required | Design requirement | Validation scope | Rollback requirement | Documentation requirement | Commit strategy | Push restrictions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Documentation-only | Level 1-2 | None, or a lightweight plan | `validate_repository.py` | `git revert` is always sufficient | The document itself; tracker/context if a sprint deliverable | One commit per coherent topic | Push freely once green |
| Test-only | Level 1-2 | None | The specific suite touched | `git revert` | None beyond the test file itself | One commit | Push freely once green |
| Internal non-breaking implementation | Level 2 | Lightweight plan | Full applicable suite for the area | `git revert`; confirm no downstream artifact depended on the internal detail | Tracker/context; architecture doc only if the internal detail is documented there | One commit per coherent unit | Push once green |
| Public contract change (schema/specification) | Level 3 (design), Level 4 (acceptance if it changes an accepted contract) | Full Planning Contract; ADR if the contract is already accepted elsewhere | Schema fixtures, IR, graph, semantic validation, full unit suite | Must state what downstream artifacts break and how they migrate | ADR, specification update, schema update, all in the same or clearly sequenced changes | Coherent multi-file commit, contract + fixtures + docs together | Push only after human-approved ADR if one was required |
| Data or schema migration | Level 4 | Full design + rollback plan | Full suite plus migration-specific verification | Explicit, tested rollback path required before proceeding | ADR plus a runbook | N/A until governed | Never without explicit human approval |
| Dependency change | Level 2 (pinned-range) / Level 4 (major/breaking) | Lightweight (pinned-range) or full ADR (breaking) | Full suite for the affected package's consumers | Pin revert | `requirements-*.txt` change plus, if breaking, an ADR | One commit | Push once green (pinned-range only) |
| Architecture change | Level 3 | Full Planning Contract, ADR | Full applicable suite | ADR's own Alternatives Considered informs rollback | ADR plus architecture doc update | Proposal committed separately from any narrow enabling groundwork | Proposal may push; substantive implementation waits for acceptance |
| Security change | Level 4 | Full design, explicit threat consideration | Full suite plus the secret-pattern check (`_validate_obvious_secrets` in `scripts/asf_validator/content_integrity.py`) and manual review — a dedicated Security & Secret Handling chapter is planned for a later Batch but not yet written | Explicit rollback, tested | ADR required | N/A until authorized | Never without explicit human approval |
| Operational change (runbook/process, no code) | Level 1-2 | Lightweight plan | `validate_repository.py` | `git revert` | The runbook/chapter itself | One commit | Push once green |
| Release change | Level 4 | Full design | Full suite, full regression | Explicit rollback/tag policy | Release notes per a future Release Engineering chapter (planned) | N/A until authorized | Never without explicit human approval |
| Experimental work | Level 2-3 depending on blast radius | Lightweight plan, explicitly labeled experimental | Whatever the experiment itself needs to be evaluable | Must be easy to discard entirely | An Investigation Report (see [Template Framework](TEMPLATE_FRAMEWORK.md), planned) if the result is worth keeping | Isolated commit(s), clearly labeled | Push only the report/conclusion, not necessarily the experimental code itself |

### Deterministic, not "ask when uncertain"

Every row above states a rule, not a suggestion to check with a human. The
only genuinely open cases are ones this table does not cover — for those,
apply [Authority Levels](AUTHORITY_LEVELS.md)'s classification procedure,
and if still ambiguous after that, treat as Level 4 (the conservative
default), which itself is a deterministic rule, not an ad hoc question back
to the operator.

## Examples

A session is asked to bump `mcp` from `>=1.27,<2` to allow `2.x` once MCP
Python SDK v2 ships (the repository's own tracked Next Action). This is a
Dependency change, and because it crosses a major version boundary that
`adapters/mcp_tools/` was explicitly pinned against, it is the
"major/breaking" branch of that row: Level 4, requiring human approval and
likely its own ADR, not a routine pin bump — exactly matching
`PROJECT_TRACKER.md`'s own existing Next Action framing ("update the pin
deliberately rather than incidentally").

## References

- `.ai/governance/DECISION_RIGHTS.md`
- [Authority Levels](AUTHORITY_LEVELS.md)
- [Risk Classification & Governance Scenarios](RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
