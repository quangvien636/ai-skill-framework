# ADR Governance and Decision Rules

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the full ADR lifecycle, a topic-indexed view of the 20 ADRs this
repository has produced, and precise rules for when an ADR is mandatory,
when it is unnecessary, and how drafting differs from approving.

## Scope

Extends `docs/adr/ADR_TEMPLATE.md` and `.ai/governance/DECISION_RIGHTS.md`
with operational rules. Does not change any ADR's content or status — that
remains the Chief Architect's and human maintainer's authority.

## Design

### Lifecycle

```text
Context identified (a real, evidenced decision is needed)
  -> Draft (any role may propose; Chief-Architect-role session drafts the
     candidate document under docs/adr/ADR-<NNNN>-<slug>.md)
  -> Status: Proposed (committed; discoverable; not yet binding)
  -> Human maintainer review
  -> Status: Accepted (binding from this point forward)
     OR the proposal is revised and re-reviewed
     OR the proposal is abandoned (left Proposed with no further action,
        or -- if it must be formally closed -- superseded by a new ADR
        that says so explicitly)
  -> (later, if direction changes) a NEW ADR is drafted that supersedes it
  -> Old ADR's Status becomes "Superseded by ADR-<NNNN>"
```

An accepted ADR is immutable — its Decision, Consequences, and Alternatives
Considered sections are never edited after acceptance, per the Version
Specification's "superseded, not edited" rule for ADRs specifically (ADRs
are the one artifact class explicitly excluded from normal in-place
versioning). Only its `Status:` field changes, to record supersession.

### When an ADR is mandatory

An ADR is required when a decision:

- Establishes or changes a cross-cutting architectural boundary (e.g.,
  ADR-0013's Build vs Reuse strategy).
- Commits the framework to a durable contract or interface future code must
  respect (e.g., ADR-0007's Workspace Discovery rule).
- Selects between materially different technical approaches with long-term
  consequences (e.g., ADR-0017's LlamaIndex + local hashing embeddings
  choice).
- Introduces or changes a governance rule itself (e.g., ADR-0008's "AI Team
  is documentation, not executable").
- Is irreversible or expensive to reverse once other work depends on it.
- Authorizes a new execution capability (e.g., ADR-0018's local Ollama
  invocation, ADR-0019's local Markdown publishing) — this repository's own
  pattern of pairing every new "execute" capability with its own ADR is
  itself a precedent this rule generalizes.

### When an ADR is unnecessary

- A small bug fix with no architectural implication.
- A documentation correction (fixing a stale claim, a broken link, a typo).
- An implementation detail already inside an accepted architecture's scope
  (the Framework Engineer's Decision Right covers this without an ADR).
- A reversible refactor with no contract change.
- Adding regression test coverage for an already-understood defect.
- Writing a `docs/operator/*.md` chapter that synthesizes and cross-
  references existing authoritative decisions without introducing a new
  rule — **this is exactly this Batch's own situation**: Batch 1 documents
  and operationalizes existing governance, authority, and process; it does
  not introduce a new binding rule beyond what ADR-0020 (Prompt 01) already
  proposed. No new ADR is drafted in this Batch for that reason. If a
  future Batch needs to introduce a genuinely new cross-cutting rule (for
  example, formally binding the Authority Levels model as enforceable
  rather than descriptive), that specific change would need its own ADR at
  that time.

### Drafting vs. approving

| Activity | Who may do it | Result |
| --- | --- | --- |
| Identify that a decision is needed | Any role | A `PROJECT_TRACKER.md` Next Action or direct drafting |
| Write the ADR's Context/Decision/Consequences/Alternatives | Any role, typically acting as Chief Architect or Framework Engineer | `docs/adr/ADR-<NNNN>-*.md`, `Status: Proposed` |
| Accept the ADR (`Status: Accepted`) | Human maintainer, or a session with explicit delegated authority for that session | Binding decision |
| Reject the ADR | Human maintainer | Recorded outside the ADR file itself (or the ADR is revised/abandoned); an AI session does not delete a Proposed ADR unilaterally on the assumption it will be rejected |
| Supersede an Accepted ADR | A new ADR, drafted the same way, accepted the same way | Old ADR's Status updated to `Superseded by ADR-<NNNN>` |
| Amend an Accepted ADR's substance | Not permitted — see Lifecycle above; a substantive change is always a new, superseding ADR | N/A |

### Implementation tracking

An ADR's Related Documents section and `PROJECT_TRACKER.md`'s Sprint History
together provide the implementation trail: the ADR states the decision, the
tracker states which sprint(s) implemented it, and — for schema/contract
ADRs — `docs/specifications/README.md` or the relevant schema file provides
the machine-checkable link. `ASF-REPOSITORY-014` mechanically validates
that every canonical ADR's own `Status:` field is well-formed
(`Proposed`, `Accepted`, or `Superseded by ADR-<NNNN>` naming a real ADR).

### Topic index (as verified this session)

| Topic | ADRs |
| --- | --- |
| Repository governance / source of truth | ADR-0001, ADR-0007, ADR-0008 |
| Validation tooling | ADR-0002, ADR-0009, ADR-0010 |
| CLI | ADR-0003, ADR-0016 |
| Templates/Generator | ADR-0004, ADR-0006 |
| IR / shared object model | ADR-0005 |
| Runtime planning and contracts | ADR-0011, ADR-0014, ADR-0015 |
| Tool/Connector contracts | ADR-0012 |
| Execution strategy (Build vs Reuse) | ADR-0013 |
| Local execution adapters | ADR-0017 (LlamaIndex retrieval), ADR-0018 (Ollama invocation), ADR-0019 (Markdown publishing) |
| Documentation architecture (this manual) | ADR-0020 (Proposed, Prompt 01) |

This table is a navigation aid, not a substitute for reading the ADR
itself; if it ever disagrees with an ADR's own content, the ADR wins per
the Repository Truth Hierarchy.

## Examples

A session in a future Batch discovers that Authority Levels (see
[Authority Levels](AUTHORITY_LEVELS.md)) should become an enforced gate
rather than a descriptive synthesis — for example, wiring a validator rule
that blocks a commit exceeding a session's stated Authority Level. That
*would* be a new cross-cutting rule (an enforcement mechanism, not just
documentation of an existing one) and would require its own ADR, drafted
and left `Proposed` for human review, not silently implemented.

## References

- `docs/adr/ADR_TEMPLATE.md`
- `.ai/governance/DECISION_RIGHTS.md`
- `docs/specifications/VERSION_SPECIFICATION.md`
- [Governance Model](GOVERNANCE_MODEL.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 3) |
