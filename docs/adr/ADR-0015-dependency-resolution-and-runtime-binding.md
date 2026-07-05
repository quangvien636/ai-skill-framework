# ADR-0015: Dependency Resolution and Runtime Binding

- **Status:** Accepted
- **Date:** 2026-07-05
- **Decision owners:** Project maintainers

## Context

ADR-0014 gave Runtime Contracts a schema, IR, graph edges, semantic rules,
and a first planner resolution pass (`asf_runtime.planner._resolve_runtime`),
plus five adapter binding functions that each take a raw `RuntimeIR` and
inspect its fields directly (`model.enabled`, `retriever.knowledge`, ...).
That resolution is intentionally minimal: it walks exactly one
`fallback_profile.fallback_runtime` edge for graph/planning purposes and
never combines a Runtime Contract with its fallback chain into one
effective view.

This milestone asks for a **Dependency Resolver** and **Runtime Binding**
layer sitting between Runtime Contracts and the adapters, supporting
"inheritance," "overrides," and a full fallback chain walk — while
explicitly forbidding any redesign of the now-stable Contracts, IR,
Validation, Runtime Contract schema, or existing adapter functions. Four
design questions have no existing answer:

1. **What do "inheritance" and "overrides" mean** given the Runtime
   Contract schema (`schemas/runtime.schema.json`) cannot change?
2. **Is Binding a new discovered artifact kind**, or computed data? Phase 7
   says "extend discovery... if required" and "do not duplicate Runtime
   discovery" — a real either/or.
3. **What does each of the seven new validation rule names concretely
   check**, and do they belong under `ASF-SEMANTIC-*` or a new prefix,
   given the Validation checklist lists "Semantic validation" and "Binding
   validation" as two separate items to run?
4. **How do adapters "consume RuntimeBinding" without redesigning their
   stable, already-shipped `*_from_runtime` functions** (ADR-0014 Phase 6)?

## Decision

### 1. Inheritance and overrides, without touching the schema

A Runtime Contract's four capability sections (`model`, `retriever`,
`tools`, `publisher`) each carry `enabled: bool` (ADR-0014). The Dependency
Resolver treats a *disabled* section as "nothing declared here — look at my
fallback chain," and an *enabled* section as an explicit, final value that
is never overridden by anything else in the chain:

- **Inheritance**: walking `runtime` then its `fallback_profile.fallback_runtime`
  chain (primary first), the first chain member with a capability
  `enabled: true` supplies that capability's effective value.
- **Override**: a capability enabled directly on `runtime` itself always
  wins over anything reachable through its fallback chain — closer always
  beats farther, with no ambiguity to resolve.

This requires no schema change: `enabled` and `fallback_profile` already
exist. It also gives Phase 8's five example flavors real, distinct
semantics (a `simple` binding needs no chain; an `inherited` binding
disables a capability its fallback provides; a `hybrid` binding enables
everything itself, so nothing is inherited).

`timeout_policy`, `retry_policy`, `safety_profile`, `audit_profile`, and
`concurrency_profile` are **not** inherited — they are always-required,
non-optional sections on every contract (ADR-0014), so there is no "gap" to
fill; the primary Runtime Contract's own values are the binding's effective
values.

### 2. `RuntimeBinding` (engine output) vs. `BindingIR` (serializable record)

Two types, not one, split by purpose:

- **`RuntimeBinding`** (`scripts/asf_runtime/binding.py`): the rich,
  in-memory result adapters and the planner actually consume. Holds the
  full resolved `RuntimeIR`/`ToolIR`/`KnowledgeIR` objects the binding
  needs, plus which chain member supplied each inherited capability.
- **`BindingIR`**: a flattened, JSON-serializable summary derived from a
  `RuntimeBinding` (canonical ids/versions only, no embedded IR objects),
  carrying its own `diagnostics: list[Diagnostic]` — matching this
  repository's established `(ir_or_none, diagnostics)` adapter shape
  (ADR-0009) and giving Binding a `.as_dict()` matching `KnowledgeIR`'s
  precedent.

Both live in `scripts/asf_runtime/`, extending the existing non-executing
Runtime Planning package (ADR-0011) rather than a new top-level location —
Binding is Runtime Planning's output, not a new architectural layer.

### 3. Binding is computed, not discovered (Phase 7)

No new discoverable artifact kind, no new file format, no new canonical
path. A `RuntimeBinding`/`BindingIR` is produced by resolving already-
discovered Skill/Runtime/Knowledge/Tool artifacts — identical in kind to
how `ExecutionPlan` is computed from already-discovered Workflow/Skill
artifacts, never itself discovered. This satisfies "do not duplicate
Runtime discovery" by construction: nothing new is scanned from disk.

### 4. New diagnostic prefix `ASF-BINDING-*`

The Validation checklist names "Semantic validation" and "Binding
validation" separately, and none of the seven requested rules are
single-artifact IR checks in the sense `ASF-SEMANTIC-*` owns (ADR-0009) —
they are chain-resolution outcomes. A new prefix is allocated, reusing the
existing `Diagnostic`/`Severity` shape and runner pattern
(`scripts/build_bindings.py` mirrors `build_semantics.py`) rather than
inventing new infrastructure:

| Code | Rule | Concrete trigger |
| --- | --- | --- |
| `ASF-BINDING-001` | missing runtime binding | `Skill.dependencies.runtime` is non-empty but no Runtime Contract in it resolves at all |
| `ASF-BINDING-002` | cyclic runtime fallback | Walking `fallback_profile.fallback_runtime` revisits a runtime id already seen, scoped precisely to the fallback subgraph (distinct from the Dependency Graph's whole-repository `ASF-GRAPH-002`, which would also fire but without fallback-chain-specific framing) |
| `ASF-BINDING-003` | unresolved dependency chain | A primary binding resolved, but a `required: true` `retriever.knowledge`/`tools.refs` reference remains unresolved after exhausting the fallback chain to `max_fallback_depth` |
| `ASF-BINDING-004` | invalid inheritance | An inherited capability's source runtime is not `status: active` |
| `ASF-BINDING-005` | duplicate binding ids | Within one resolution batch, two `BindingIR`s compute the same canonical id (`binding:<skill_id>@<runtime_id>`) but differ in resolved content — a determinism violation |
| `ASF-BINDING-006` | incompatible descriptor combinations | Effective `retriever.enabled` is true while effective `model.enabled` is false (retrieval with nothing to reason over it) |
| `ASF-BINDING-007` | conflicting override rules | Two chain members both explicitly enable the *same* capability with *different* configured content (e.g. two different `publisher.target` values) — legal under override precedence, but almost certainly an authoring mistake worth flagging |

### 5. Adapters gain `*_from_binding` functions; nothing existing changes

Each adapter's already-shipped `*_from_runtime` function (ADR-0014 Phase 6)
is untouched. A new, additive `*_from_binding(binding: RuntimeBinding)`
function is added alongside it, taking the fully resolved `RuntimeBinding`
instead of a raw `RuntimeIR` — satisfying "adapters should not inspect
Skills directly" (already true) and "consume RuntimeBinding" without
redesigning a stable, already-documented contract.

## Consequences

### Positive

- Every "missing X" / "cyclic X" concept in the milestone brief has a
  precise, testable trigger instead of an invented generic rule.
- No schema, IR, or existing adapter function changes — fully additive,
  matching "do NOT redesign" for the stable layers.
- The fallback chain becomes genuinely useful (inheritance) rather than
  only a graph edge and a timeout-routing flag.

### Costs and Tradeoffs

- Two related types (`RuntimeBinding`, `BindingIR`) for one concept adds a
  small amount of conceptual overhead versus a single class; accepted
  because "immutable, serializable, structured diagnostics" (`BindingIR`)
  and "the resolved data adapters need" (`RuntimeBinding`) are genuinely
  different shapes with different consumers.
- `ASF-BINDING-002`'s fallback-cycle check necessarily overlaps with the
  Dependency Graph's existing generic `ASF-GRAPH-002`; both may fire for
  the same cycle. This is accepted rather than suppressed, since the two
  serve different audiences (a Binding-specific report vs. whole-repository
  graph validation) and ADR-0010 already established that graph cycle
  detection is generic across all edge kinds.

## Enforcement

No change to `schemas/runtime.schema.json`, `scripts/asf_validator/runtime_ir.py`,
the Dependency Graph's existing edge kinds, or any existing adapter
function's signature or behavior. All new code is additive: new functions,
new types, new diagnostics, new fixtures. `scripts/asf_runtime/` and every
`adapters/*/` package remain free of any execution-backend dependency and
never call `execute()`/`invoke()`/`query()`/`publish()`.

## Build vs Reuse

Fallback-chain-with-inheritance-and-override is a common *pattern* (CSS
cascade, DNS CNAME chains, Kubernetes admission chains, Python's MRO) but no
mature OSS library exists for this narrow, ASF-specific declarative shape
(a bounded chain of a bespoke contract type with four independently
enableable capabilities). Building roughly 150 lines of deterministic
chain-walking logic is not "reinventing a solved problem" in the sense
ADR-0013 warns against — there is no reuse target, and the Binding layer is
explicitly named ASF intellectual property in this milestone's brief.

## Related Documents

- `docs/adr/ADR-0009-ir-adapter-package-and-scope.md`
- `docs/adr/ADR-0011-runtime-planning-precedes-execution.md`
- `docs/adr/ADR-0014-runtime-contract-schema-and-scope.md`
- `docs/architecture/RUNTIME_ARCHITECTURE.md`
- `docs/architecture/RUNTIME_CONTRACT_ARCHITECTURE.md`
- `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`
