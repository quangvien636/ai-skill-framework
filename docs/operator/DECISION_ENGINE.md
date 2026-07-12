# Decision Engine

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the deterministic process a session runs to decide whether it may
proceed with a task, and how — combining scope, authorization basis,
reversibility, validation availability, and contract/security/data/
production sensitivity into one ordered set of branches.

## Scope

This is the single decision procedure [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)'s
`planning` state applies. It consumes the outputs of
[Authority Levels](AUTHORITY_LEVELS.md) and
[Risk Classification & Governance Scenarios](RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md)
and produces one of a fixed set of dispositions.

## Design

### The decision flow

```text
1. Is the task within repository scope (C:\AI\ai-skill-framework only,
   this task's stated boundaries)?
     No  -> PROHIBIT
     Yes -> continue

2. Is it supported by evidence: an explicit instruction, a roadmap item,
   an accepted ADR, a PROJECT_TRACKER.md Next Action, or a defect actually
   found this session?
     No  -> DEFER (create a backlog item; do not implement speculatively)
     Yes -> continue

3. Is authority available at the required Level (per Authority Levels)?
     No (task is Level 4-5) -> STOP FOR APPROVAL / PROHIBIT
     Yes -> continue

4. Is the change reversible (per the Risk Classification matrix)?
     No, and risk is High -> STOP FOR APPROVAL
     No, but risk is Low/Medium and a rollback plan exists -> continue,
        with the rollback plan recorded (see Rollback Planning & Risk
        Register)
     Yes -> continue

5. Is required validation available (a validator/test suite that can
   actually confirm correctness)?
     No -> PLAN FIRST (define what "correct" means and how it will be
        checked before implementing) or DEFER if no check is feasible at
        all
     Yes -> continue

6. Does it affect a public contract, security posture, data, a dependency
   with licensing implications, or a production system?
     Yes -> Is an ADR required (per ADR Governance & Decision Rules)?
        Yes -> DRAFT ADR (implementation waits for acceptance, except
           explicitly-authorized non-speculative groundwork)
        No, but human approval is still required per Human vs AI
           Responsibilities -> STOP FOR APPROVAL
     No -> continue

7. PROCEED — enter `implementation` per the Autonomous Development
   Lifecycle.
```

### Branch dispositions

| Disposition | Meaning | What happens next |
| --- | --- | --- |
| PROCEED | All checks passed | Enter `implementation` |
| PLAN FIRST | Feasible, but needs a written Planning Contract or validation strategy before implementing | Return to `planning` with the specific gap named |
| DRAFT ADR | Feasible, but the decision itself needs to be committed as a `Status: Proposed` ADR before substantive implementation | Draft the ADR; implement only explicitly non-speculative groundwork |
| DEFER | Not supported by evidence, or no validation is feasible yet | Record as a `PROJECT_TRACKER.md` Next Action; do not implement |
| STOP FOR APPROVAL | Requires Level 4 human authority | Governance stop per [Autonomous Continuation Rules & Stop Conditions](AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md) |
| PROHIBIT | Out of scope or a Level 5 prohibited action | Hard stop per the same document |

### Worked decision table

| Task | Step 1 | Step 2 | Step 3 | Step 4 | Step 5 | Step 6 | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fix a broken link found during this session | In scope | Evidence: found this session | Level 1 | Reversible | `validate_repository.py` available | No contract/security/data/production impact | PROCEED |
| Write `docs/operator/*.md` chapters per this Batch's mandate | In scope | Evidence: explicit instruction | Level 2 (synthesis, no new rule) | Reversible | `validate_repository.py` available | No | PROCEED |
| Add a new `ASF-SEMANTIC-*` rule enforcing a documented-but-unenforced architecture rule | In scope | Evidence: architecture doc already states the rule | Level 2 | Reversible | Existing semantic validator fixture pattern applies | Touches validator contract, but implements an already-accepted rule, not a new one | PLAN FIRST (write the fixture cases, confirm no unintended breakage), then PROCEED |
| Change which role approves an ADR | In scope | No current evidence this is needed | Level 3-4 | Reversible in principle, but affects all future governance | No existing validator checks this | Governance rule change | DRAFT ADR, STOP FOR APPROVAL on acceptance |
| Add a cloud LLM API call | In scope (repository), but action itself is prohibited | No accepted ADR authorizes this | Level 5 | N/A | N/A | Security/scope | PROHIBIT |
| Bump `mcp` past `<2` before v2 ships | In scope | No — the tracked trigger has not fired | N/A | N/A | N/A | N/A | DEFER (trigger not yet fired) |

## Examples

See the Worked decision table above. Each row traces a real or realistic
task through all six steps to its disposition, rather than asserting a
conclusion without showing the reasoning.

## References

- [Authority Levels](AUTHORITY_LEVELS.md)
- [Risk Classification & Governance Scenarios](RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md)
- [ADR Governance & Decision Rules](ADR_GOVERNANCE.md)
- [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
