# Runtime Promotion Readiness

Version: 1.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the evidence required before a local Ollama-backed Runtime Contract is
promoted from `draft` to `active` and used by an active production Skill. This
checklist records approval; it does not itself change lifecycle state.

## Approved Promotion Scope

On 2026-07-12, the human maintainer explicitly approved one bounded promotion:

- Runtime Contract: `runtime:offline@1.0.0`;
- production consumer: `skill:content-creation@1.0.0`;
- execution backend: a local Ollama server on a loopback endpoint only;
- side effects: model text generation only, stopping at ASF's declared output
  boundary; no rendering, TTS, upload, publishing, or cloud API;
- delivery: readiness was recorded separately; wiring and lifecycle promotion
  were explicitly approved as one atomic sprint because production planning
  resolves active Runtime Contracts only.

This approval does not accept ADR-0016, promote any other artifact, authorize a
cloud provider, authorize credentials, or authorize MCP SDK v2 work.

## Promotion Gates

All gates below must pass before `runtime:offline` changes to `active`.

| Gate | Required evidence | Sprint 37 baseline |
| --- | --- | --- |
| Human authority | Durable scoped approval record | Pass — atomic promotion approved 2026-07-12 |
| Contract validity | Contract, IR, graph, semantic, and repository validation | Pass |
| Production consumer | The approved Skill resolves `runtime:offline` through its declared dependency and `RuntimeBinding` | Pass |
| Real execution path | Existing adapter consumes the resolved binding; no stub or bypass | Pass |
| Local-only transport | Endpoint validation rejects non-loopback hosts | Pass — adapter test coverage |
| Model configuration | Model comes from the Runtime Contract or an explicit local override; no credential or source-code-only model selection | Pass — `llama3` from binding |
| Failure behavior | Unavailable server and missing model return structured diagnostics | Pass — adapter test coverage |
| Live readiness | A real local Ollama server lists the configured model and the approved path completes its live test without fake output | Pass — `llama3:latest` listed; opt-in compiled-binding live test passed |
| Safety boundary | No cloud call, API key, TTS, rendering, upload, or publishing | Pass |
| Regression safety | Full required validation plus affected adapter tests pass | Pass |

## Promotion Procedure

1. Wire only `skill:content-creation@1.0.0` to
   `runtime:offline@1.0.0` through its manifest and existing binding path.
2. Run static validation and the affected RuntimeBinding/Ollama adapter tests.
3. Probe local Ollama only through the existing loopback-only client. Confirm
   that the Runtime Contract's configured model is installed.
4. Run the opt-in live test and retain its truthful pass/fail/skip result in the
   sprint evidence. A skip or unavailable model blocks promotion.
5. Only after all gates pass, change `runtime:offline` from `draft` to `active`.
6. Run full validation again, update project status, commit, and push.

## Promotion Result

Sprint 38 completed the approved atomic transition. `skill:content-creation`
now requires `runtime:offline`, `runtime:offline` is `active`, and the former
`runtime:content` contract returned to `draft` because otherwise it would be an
active lifecycle orphan after losing its only consumer. Production planning
resolves exactly one active `runtime:offline`; controlled tests prove draft and
ambiguous active candidates fail closed.

## Rollback

If wiring validation fails before promotion, revert only the wiring sprint and
leave `runtime:offline` as `draft`. If a regression is discovered after
promotion, restore the Skill's prior Runtime dependency and return
`runtime:offline` to `draft` in a reviewed corrective commit; do not silently
substitute a cloud runtime or bypass model availability checks.

## References

- [Decision Rights](../../.ai/governance/DECISION_RIGHTS.md)
- [Skill Architecture](../architecture/SKILL_ARCHITECTURE.md)
- [Execution Adapter Architecture](../architecture/EXECUTION_ADAPTER_ARCHITECTURE.md)
- [Compiler Lifecycle](COMPILER_LIFECYCLE.md)
- [Ollama Execution Adapter](../../adapters/ollama_execution/README.md)
