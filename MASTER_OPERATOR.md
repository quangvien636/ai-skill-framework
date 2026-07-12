# Master Operator Manual

Version: 0.1
Status: Active (Foundation)
Last updated: 2026-07-12

## How to Use This Document

This is the entry point for any human or AI contributor session working in
this repository — Claude Code, Codex, Gemini, or any future coding agent.
Read it before making a change. It replaces the need to re-explain this
repository's architecture, governance, and constraints in a new prompt every
session: everything a session needs to operate correctly is either stated
here or reached from here by one link.

This manual does not replace `PROJECT_CONTEXT.md`, the ADRs, the
architecture documents, or any other existing document. It is the
**navigation and governance spine** that sits above them. Where this
document and a more specific document disagree, see
[Repository Truth Hierarchy](#repository-truth-hierarchy) — the specific
document almost always wins; this manual is authoritative for *process and
orientation*, not for facts a more specific document already owns.

Two thin routing files, [`CLAUDE.md`](CLAUDE.md) and [`AGENTS.md`](AGENTS.md),
exist only so tools that auto-load a root file (Claude Code, Codex CLI, and
similar) land here automatically at session start. They carry no authority
of their own.

If you are a session picking up work from the 30-prompt Master Operator
build-out, go straight to [Future Expansion Strategy](#future-expansion-strategy)
and [Complete Table of Contents](#complete-table-of-contents) — they tell
you exactly what to do next and where to put it.

## Vision

Every AI or human session that opens this repository operates with full,
correct context from its first action — without a human re-explaining
architecture, governance, or constraints in a long prompt, and without the
session rediscovering rules by trial and error or by reading conversation
history that ADR-0001 already says is not authoritative.

## Mission

Provide one continuously-maintained, authoritative entry point that:

1. Orients any contributor (human or AI) to this repository's purpose,
   structure, and rules in a single read.
2. Eliminates prompt-repetition — the same standing instructions do not need
   to be retyped into every new session's first message.
3. Organizes the repository's existing documentation into one coherent map
   instead of requiring a session to discover it document by document.
4. Names every gap in that documentation explicitly, so gaps get closed
   deliberately instead of staying invisible.
5. Defines a durable, versioned structure so this manual itself can grow
   from a foundation document into a complete engineering handbook across
   many future sessions without losing coherence or duplicating what
   already exists.

## Philosophy

Principles governing how this manual itself is written and maintained —
distinct from the [Design Principles](docs/principles/DESIGN_PRINCIPLES.md),
which govern the framework's *product* (Skills, Workflows, Knowledge):

1. **Reference, don't duplicate.** If a fact already has an authoritative
   home (an ADR, an architecture document, a schema), this manual links to
   it. Copying it here would create a second place that can go stale.
2. **Synthesize, don't replace.** A chapter in this manual explains *how to
   use* a set of existing documents together — the operator's view — not a
   rewritten version of what they already say.
3. **A manual that lies is worse than no manual.** Every claim here must
   stay checkable against the repository as it exists today. Prefer linking
   to a validator-checked document over restating a fact that can silently
   drift out of sync with it.
4. **Optimize for a cold-start session.** Assume the reader has no memory of
   any prior conversation about this repository — per ADR-0001, it may
   genuinely have none.
5. **Documentation is a dependency, not an afterthought** (Design Principle
   2, applied reflexively to this document): a change to this manual's
   structure ships with the same rigor — commit discipline, validation,
   tracker update — as a change to the framework itself.
6. **Grow deliberately, not speculatively.** The Complete Table of Contents
   names every planned chapter now so no future session invents structure
   ad hoc, but a chapter's *content* is written only when a session actually
   does that work — matching Design Principle 2's "does not mean producing
   speculative documentation for work that has not been selected."

## Repository Truth Hierarchy

When two sources disagree, resolve the conflict in this order — most
authoritative first. This is a synthesis of ADR-0001, ADR-0007, and
`.ai/governance/DECISION_RIGHTS.md`; those documents remain the normative
source if this list and any of them ever appear to differ.

1. **Accepted ADRs** (`docs/adr/ADR-*.md`, `Status: Accepted`) — immutable
   once accepted; a change in direction is a new ADR that supersedes the
   old one, never a silent edit (Version Specification; ADR-0001).
2. **The repository as it currently validates and tests** — the actual
   schemas, code, and passing `python scripts/validate_repository.py` /
   `python -m unittest discover -s tests/unit` output. This is ground truth
   for "what currently works." A document describing behavior that the
   repository no longer exhibits is stale, not authoritative, regardless of
   its own claimed status.
3. **`PROJECT_CONTEXT.md` and `PROJECT_TRACKER.md`** — the current,
   actively maintained record of project state, focus, and sprint history.
4. **Architecture documents** (`docs/architecture/*.md`) — structural
   authority within their own named domain.
5. **Specifications and schemas** (`docs/specifications/*.md`,
   `schemas/*.json`) — contract authority for artifact shape and validation.
6. **Principles** (`docs/principles/*.md`) — cross-cutting design and
   naming authority.
7. **Guides and runbooks** (`docs/guides/*.md`) — operational how-to
   authority, scoped to the task they name.
8. **This manual and its chapters** (`MASTER_OPERATOR.md`,
   `docs/operator/*.md`) — authoritative for onboarding, process, and
   cross-document navigation; never authoritative for a fact a more
   specific source above already owns.
9. **The Knowledge Base** (`knowledge/**`) — domain content authority for
   what Skills consume, scoped to its own category.
10. **Everything else** — conversation history, model memory, an AI
    session's own prior output, `CLAUDE.md`/`AGENTS.md` routing text. Per
    ADR-0001, these are inputs only. They are never authoritative and never
    override anything above, even by omission (a document's silence about
    something is not evidence the rule does not apply).

## Operating Principles

How a session should behave while working in this repository, synthesized
from `PROJECT_CONTEXT.md`'s Working Principles, its Documentation-First
Workflow, and `.ai/playbooks/SPRINT_WORKFLOW.md`:

1. **Read before you write.** Follow the read order this manual and
   `PROJECT_CONTEXT.md` define before touching any artifact.
2. **The repository is the only memory that persists.** Anything worth
   knowing next session must be written down here, not left in this
   conversation.
3. **Ship documentation with the change, not after it.** A durable change
   is not done until affected tracker, context, and reference documents are
   updated in the same commit (`PROJECT_CONTEXT.md`'s Definition of Done).
4. **Prefer the smallest architecture-aligned change.** Do not redesign
   what the task did not ask you to touch.
5. **Never claim something works without evidence.** This repository's own
   sprint history always cites the command and result (test counts,
   validator output) behind a "Done" — match that standard.
6. **Reuse before you build** (Design Principle 8; ADR-0013's Build vs
   Reuse strategy). Check whether an existing Skill, adapter, script, or
   document already does this before creating a new one.
7. **One coherent commit per unit of work, explicit file paths.** Never a
   blind `git add -A`; never an unrelated change folded into the same
   commit as another.
8. **Escalate uncertainty; do not guess on anything hard to reverse.** See
   [Decision Hierarchy](#decision-hierarchy) and
   `.ai/governance/DECISION_RIGHTS.md`'s Escalation rule: an uncertain major
   decision is a hard-stop condition, not a default-to-proceed one.

## Autonomous Development Rules

This repository already runs real unattended/autonomous sessions (see
`docs/guides/WEEKLY_OPERATOR_PLAN.md` and
`docs/guides/MONTHLY_OPERATOR_PLAN.md`, both of which gate action on named
triggers rather than acting speculatively). These rules generalize the
pattern those plans already use so it does not have to be rediscovered per
plan.

### An autonomous or unattended session MUST NOT

- Promote any artifact's lifecycle past `draft` (`.ai/governance/
  DECISION_RIGHTS.md`; ADR-0006's Generator rule).
- Accept, reject, or reverse an ADR — drafting a candidate is fine;
  accepting one is a human decision unless a human has explicitly delegated
  that authority for the session (`.ai/governance/DECISION_RIGHTS.md`).
- Force-push, rewrite shared history, or run any other destructive Git
  operation without the explicit scope of authorization the session was
  given for that specific action.
- Add a cloud or paid API credential path, or otherwise widen network
  access beyond what an accepted ADR already scopes (currently: loopback
  Ollama only — ADR-0013, ADR-0018).
- Act on a plan's named trigger before confirming that trigger has actually
  fired (the Weekly/Monthly Operator Plan pattern).
- Delete or overwrite another session's in-progress or uncommitted work
  without first checking `git status` and preserving it (stash or commit),
  matching this framework's own git-safety expectations.
- Connect a non-production or experimental component to production output
  (e.g. `video_pipeline`) without the explicit human approval the current
  plan already requires.

### An autonomous or unattended session MAY

- Implement an already-accepted architecture's remaining detail
  (Framework Engineer's Decision Right).
- Draft an ADR candidate, a Sprint backlog, or a consistency-review finding
  as a proposal for human review.
- Write or extend documentation, run read-only audits, and run the
  validator or test suite.
- Open a Next Action in `PROJECT_TRACKER.md` for a human or a later session
  to pick up.

### Hard-stop conditions

Treat as a hard stop, not a judgment call, per `.ai/governance/
DECISION_RIGHTS.md`'s Escalation rule: any uncertain major architectural
decision; any task that touches credentials or secrets; any task implying a
destructive Git operation; any trigger-gated action whose trigger has not
fired; any request that would make this manual, an ADR, or the tracker
inconsistent with the repository's actual state.

## Decision Hierarchy

*Who* may decide something, as distinct from the Truth Hierarchy above
(*which document* wins). The full authority is
`.ai/governance/DECISION_RIGHTS.md`; this is its operator-facing summary.

```text
Human maintainer
  -> accepts/rejects ADRs, approves lifecycle promotion, authorizes
     destructive Git operations, sets project direction (ADR-0001)

Chief Architect role
  -> sole approver of a new or superseding ADR candidate's content
     (still requires human acceptance per the row above)

Principal Engineer role
  -> sole authority to open/close a Current Sprint entry in
     PROJECT_TRACKER.md

Framework Engineer role
  -> sole authority over implementation-detail choices inside an
     already-accepted architecture

Quality Engineer role      -> sole authority to block a commit for a
                               consistency violation
Test Engineer role         -> sole authority to mark a schema/spec change
                               "covered" by a fixture
Documentation Engineer role -> sole authority over documentation
                               structure/format conventions
Automation Engineer role   -> sole authority over automated vs. manual
                               checklist items

Any session acting without a clearly applicable role or Decision Right
  -> escalate; do not decide unilaterally (see Autonomous Development
     Rules' hard-stop conditions)
```

One contributor (human or AI) may hold multiple roles in one session — this
repository's history shows exactly that — but each decision still belongs
to the role it falls under (`.ai/standards/COLLABORATION_STANDARDS.md`).
The planned Governance Model chapter (`docs/operator/GOVERNANCE_MODEL.md`,
see the [Complete Table of Contents](#complete-table-of-contents)) will
carry the fully worked-out version of this section with escalation
examples.

## Documentation Strategy

This repository already follows a **hub-and-spoke** documentation pattern
in several places — `docs/specifications/README.md` indexes the
specifications rather than inlining them; `.ai/README.md` indexes roles,
playbooks, standards, and governance the same way; `adapters/README.md`
indexes the six adapter packages. This manual extends that same pattern to
repository-wide operating guidance instead of inventing a new one:

- **`MASTER_OPERATOR.md`** (this file) is the hub: stable, rarely-changing,
  holds the vision/philosophy/hierarchy/principles/rules layer plus the
  complete map of every other document.
- **`docs/operator/*.md`** is the spoke set: one file per planned chapter,
  written progressively, each following `docs/_templates/
  DOCUMENTATION_TEMPLATE.md`'s shape (Purpose, Scope, Definitions, Design,
  Examples, References, Revision History) exactly like every other
  repository document.
- **Every other existing document** (ADRs, architecture, specifications,
  schemas, principles, guides, knowledge, `.ai/`) keeps its existing
  authority, location, and format unchanged. This manual references them;
  it never absorbs them.

See [Documentation Architecture](#documentation-architecture) below for the
concrete mechanics, and [Gap Analysis](#gap-analysis) for what is missing
today.

## Documentation Architecture

### What belongs in `MASTER_OPERATOR.md`

Only content that is true regardless of which chapter a session is working
on: Vision, Mission, Philosophy, Repository Truth Hierarchy, Operating
Principles, Autonomous Development Rules, Decision Hierarchy, Documentation
Strategy and Architecture, Future Expansion Strategy, the Complete Table of
Contents, and the Gap Analysis. This content should change only when the
manual's own structure changes (a new Part or chapter) or a foundational
rule changes — the latter should itself usually be backed by an ADR, since
it is a cross-cutting governance decision.

### What remains in individual documents

Everything normative and domain-specific stays exactly where it already
is: ADRs stay the sole authority for decisions; architecture documents stay
the sole authority for architecture; specifications and schemas stay the
sole authority for artifact contracts; `PROJECT_CONTEXT.md` and
`PROJECT_TRACKER.md` stay the sole authority for live project state and
sprint history. `docs/operator/*.md` chapter files hold synthesized,
operator-facing guidance that cross-references these sources — they never
restate normative content verbatim, and they are never the place a new
architectural rule gets introduced (that is an ADR's job, per the
Governance Model chapter).

### Cross-reference strategy

Every `docs/operator/*.md` chapter's References section links to every
source document it synthesizes. `MASTER_OPERATOR.md`'s Table of Contents
links to a chapter file only once that file exists — an unwritten chapter
is listed with its exact target path and a `Planned` status, never as a
broken link (`python scripts/validate_repository.py` checks every relative
Markdown link and anchor in every `*.md` file in this repository, including
this one, so a link to a not-yet-created file would be a real validation
failure, not just a style problem).

### Update strategy

Adding a new ADR, architecture document, or specification does not require
touching `MASTER_OPERATOR.md` itself unless it changes the Table of
Contents' structure. It should be referenced from whichever
`docs/operator/*.md` chapter's scope already covers it, in that chapter's
own next revision. `MASTER_OPERATOR.md`'s spine changes only for structural
reasons (a new Part/chapter, a corrected Truth or Decision Hierarchy, a
scope change to an existing chapter) — each such change gets one line in
this file's own Revision History.

### Versioning strategy

`MASTER_OPERATOR.md` carries the same Version/Status/Last-updated/Revision
History discipline as every other repository document
(`docs/_templates/DOCUMENTATION_TEMPLATE.md`). Its Revision History records
structural changes to the manual itself ("added Part IV," "rewrote the
Truth Hierarchy") — not the content changes inside an individual
`docs/operator/*.md` chapter, which carries its own independent Version and
Revision History.

## Future Expansion Strategy

This manual is Prompt 01 of a planned 30-prompt build-out. Each future
prompt should:

1. Read this manual's [Complete Table of Contents](#complete-table-of-contents)
   and pick the next unwritten chapter(s) — default order is Part I through
   Part X in sequence, but a session may reprioritize a specific chapter if
   the operator directs it to.
2. Write `docs/operator/<CHAPTER_FILE>.md` following `docs/_templates/
   DOCUMENTATION_TEMPLATE.md`'s shape, synthesizing (never duplicating) the
   source documents that chapter's Gap Analysis row names.
3. Flip that chapter's Table of Contents row from `Planned` to a real link,
   and update its Status.
4. Add one line to this file's Revision History if the change is structural
   (see [Versioning strategy](#versioning-strategy)); otherwise the new
   chapter file's own Revision History is sufficient.
5. Run `python scripts/validate_repository.py` (and the relevant test
   suite if code changed) before committing.
6. Follow the existing `.ai/playbooks/SPRINT_WORKFLOW.md` commit
   discipline: one coherent commit, explicit paths, and a
   `PROJECT_TRACKER.md`/`PROJECT_CONTEXT.md` update in the same change,
   exactly as every other sprint in this repository's history has done.

A genuinely new Part, or a change to a foundational principle in this
file's spine (not just a new chapter under an existing Part), is a
structural documentation decision under the Documentation Engineer's
Decision Right, and — if it changes a cross-cutting rule rather than just
adding content — should be backed by an ADR, per this repository's own
"significant architectural changes require an ADR" rule (ADR-0001, Design
Principle 10).

Stub documents that exist today with no real content
(`docs/guides/GETTING_STARTED.md`, `docs/guides/DEVELOPMENT_GUIDE.md`,
`docs/references/GLOSSARY.md` — see [Gap Analysis](#gap-analysis)) should be
populated as part of whichever chapter depends on them, not as a separate
unscoped effort.

## Complete Table of Contents

Every planned chapter, defined now so no future session has to invent
structure ad hoc. `Status` is `Planned` (file does not exist yet) until a
future prompt writes it, at which point the row gains a real link. No row
here is a placeholder — each already states its scope precisely enough that
a future session can write the chapter without further clarification.

### Part I — Governance & Decision-Making

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 1 | Governance Model | `docs/operator/GOVERNANCE_MODEL.md` | Consolidates `.ai/README.md`, `.ai/roles/*.md`, `DECISION_RIGHTS.md`, and `COLLABORATION_STANDARDS.md` into one operator-facing narrative of who decides what, with worked escalation examples. | Planned |
| 2 | ADR Governance & Lifecycle | `docs/operator/ADR_GOVERNANCE.md` | The full lifecycle of an ADR (candidate -> accepted/superseded), a topic-indexed view of all 19+ ADRs (not just numeric order), and the rule for when a change requires one. | Planned |
| 3 | Human Approval Rules | `docs/operator/HUMAN_APPROVAL_RULES.md` | Expands `DECISION_RIGHTS.md` into a concrete, example-driven decision tree: the exact trigger list requiring human approval (lifecycle promotion, force-push, ADR acceptance, credentials, network/cloud enablement). | Planned |
| 4 | Escalation & Conflict Resolution | `docs/operator/ESCALATION_AND_CONFLICT_RESOLUTION.md` | What a session does when two documents disagree, a role's authority is unclear, or a validator result conflicts with an instruction. | Planned |

### Part II — Repository Lifecycle & Operating Rhythm

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 5 | Session Bootstrap Protocol | `docs/operator/SESSION_BOOTSTRAP_PROTOCOL.md` | The exact ordered reading list and checks a session performs before touching anything, replacing ad hoc prompt instructions. | Planned |
| 6 | Sprint & Repository Lifecycle | `docs/operator/SPRINT_LIFECYCLE.md` | Expands `.ai/playbooks/SPRINT_WORKFLOW.md` into a full runbook with worked examples and the Definition of Done checklist. | Planned |
| 7 | Handover & Continuity Protocol | `docs/operator/HANDOVER_AND_CONTINUITY.md` | Expands `.ai/playbooks/HANDOVER.md` into the full end-of-session and cross-session continuity contract, including quota-exhaustion and hard-stop handling. | Planned |
| 8 | Autonomous Operating Rules (worked examples) | `docs/operator/AUTONOMOUS_OPERATING_RULES.md` | Worked, example-driven expansion of this manual's [Autonomous Development Rules](#autonomous-development-rules), using `WEEKLY_OPERATOR_PLAN.md`/`MONTHLY_OPERATOR_PLAN.md` as case studies. | Planned |

### Part III — Architecture Reference

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 9 | Architecture Index & Component Map | `docs/operator/ARCHITECTURE_INDEX.md` | Single map of all `docs/architecture/*.md` documents, their relationships, and a synthesized dependency diagram. | Planned |
| 10 | Artifact & Contract Model | `docs/operator/ARTIFACT_AND_CONTRACT_MODEL.md` | How Skill/Workflow/Knowledge/Tool/Connector/Runtime Contract/Evaluation/Reflection artifacts relate, tying `docs/specifications/` to `schemas/`. | Planned |
| 11 | Execution & Adapter Boundary | `docs/operator/EXECUTION_ADAPTER_BOUNDARY.md` | Synthesizes ADR-0013's Build vs Reuse strategy and the six `adapters/` packages into one operating picture of what executes and where. | Planned |
| 12 | Architecture Extension Points | `docs/operator/ARCHITECTURE_EXTENSION_POINTS.md` | Where a new architecture document, adapter, or Protocol seam gets added, and the governance gate for doing so. | Planned |

### Part IV — Coding & Engineering Standards

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 13 | Coding Standards | `docs/operator/CODING_STANDARDS.md` | **Gap.** Formalizes the Python conventions already implicit in `scripts/asf_validator`, `scripts/asf_runtime`, and `adapters/` (typing, immutable dataclasses, no module-level mutable state, Protocol seams, docstring policy). | Planned |
| 14 | Repository Structure Standard | `docs/operator/REPOSITORY_STRUCTURE_STANDARD.md` | Canonical map of every top-level directory and what belongs in it, formalizing what is today tribal knowledge across `README.md` and ADR-0007. | Planned |
| 15 | Naming & Metadata Standards | `docs/operator/NAMING_AND_METADATA_STANDARDS.md` | Operator-facing consolidation of `NAMING_CONVENTION.md`, `KNOWLEDGE_NAMING_CONVENTION.md`, `METADATA_SPECIFICATION.md`, and `VERSION_SPECIFICATION.md`. | Planned |
| 16 | Dependency & Package Boundary Rules | `docs/operator/DEPENDENCY_BOUNDARY_RULES.md` | The "adapters never import each other" rule, `requirements-<name>.txt` isolation, and how to add a new adapter package without violating it. | Planned |

### Part V — Documentation Standards & Knowledge Management

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 17 | Documentation Standards | `docs/operator/DOCUMENTATION_STANDARDS.md` | Formalizes `docs/_templates/DOCUMENTATION_TEMPLATE.md` usage, Version/Status/Revision History conventions, and when to create vs. extend a document. | Planned |
| 18 | Documentation Map | `docs/operator/DOCUMENTATION_MAP.md` | **Gap.** Full sitemap of every document in the repository with a one-line purpose, kept current by hand until a validator rule can check it. | Planned |
| 19 | Knowledge Base Management | `docs/operator/KNOWLEDGE_BASE_MANAGEMENT.md` | Operator-facing consolidation of `KNOWLEDGE_ARCHITECTURE.md`, `KNOWLEDGE_CATEGORIES.md`, and the index-maintenance workflow. | Planned |
| 20 | Glossary & Terminology Governance | `docs/operator/GLOSSARY_GOVERNANCE.md` | **Gap.** The process for populating the currently-stub `docs/references/GLOSSARY.md` and keeping terminology consistent repository-wide; this chapter also populates that glossary's real content. | Planned |

### Part VI — Validation, Testing & Quality

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 21 | Validation System Reference | `docs/operator/VALIDATION_SYSTEM_REFERENCE.md` | Operator map over `VALIDATION_GUIDE.md`, `VALIDATOR_ROADMAP.md`, and the `scripts/asf_validator` pipeline stages. | Planned |
| 22 | Testing Standards | `docs/operator/TESTING_STANDARDS.md` | **Gap.** Formalizes `unittest` conventions, `tests/fixtures/contracts` conventions, and the adapter test-isolation policy (documented so far only in Sprint 42's tracker notes). | Planned |
| 23 | Quality Gates & Review Protocol | `docs/operator/QUALITY_GATES_AND_REVIEW.md` | Turns `COLLABORATION_STANDARDS.md`'s three review gates into a step-by-step review checklist. | Planned |
| 24 | Diagnostic Code Reference | `docs/operator/DIAGNOSTIC_CODE_REFERENCE.md` | **Gap.** No single index of every `ASF-*` diagnostic code (`SCHEMA`, `SEMANTIC`, `REPOSITORY`, `RUNTIME-PLAN`, `BINDING`, `PARSE`) exists today; this chapter builds it. | Planned |

### Part VII — AI Skills, Workflows & Runtime

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 25 | Skills Reference | `docs/operator/SKILLS_REFERENCE.md` | Catalog of all production Skills (`content-creation`, `research`, `review-quality`) with lifecycle status and dependency summary. | Planned |
| 26 | Workflows Reference | `docs/operator/WORKFLOWS_REFERENCE.md` | Catalog of all four Workflow packages and the canonical composite compiler (`research-content-review`). | Planned |
| 27 | Runtime Contracts & Bindings Reference | `docs/operator/RUNTIME_CONTRACTS_REFERENCE.md` | Catalog of the five Runtime Contracts, current binding status, and which is active in production. | Planned |
| 28 | Evaluation & Reflection Reference | `docs/operator/EVALUATION_AND_REFLECTION_REFERENCE.md` | Operator map over the Evaluation/Reflection Architecture and Specification, tied to `CONTENT_SKILL_READINESS.md`'s finding that the rubric is validated but never executed. | Planned |

### Part VIII — Content Intelligence & Learning Engine

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 29 | Content Intelligence Strategy | `docs/operator/CONTENT_INTELLIGENCE_STRATEGY.md` | **Gap.** No document today ties `skill:content-creation`'s product goal to a strategic content-quality narrative beyond the Monthly Operator Plan. | Planned |
| 30 | Benchmarking Framework | `docs/operator/BENCHMARKING_FRAMEWORK.md` | Ties to the open Next Action (Content Benchmark Plan, Week 3) and `GOLDEN_SAMPLE_INTAKE_PLAN.md`; written once `docs/guides/CONTENT_BENCHMARK_PLAN.md` exists or alongside it. | Planned |
| 31 | Learning Engine & Continuous Improvement | `docs/operator/LEARNING_ENGINE_AND_CONTINUOUS_IMPROVEMENT.md` | **Gap.** Fully aspirational today: no document describes how Evaluation/Reflection findings would feed back into the Knowledge Base or Skill instructions over time. | Planned |

### Part IX — Release Engineering, Maintenance & Operations

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 32 | Release Engineering | `docs/operator/RELEASE_ENGINEERING.md` | **Gap.** Framework-level versioning/release policy — `changelog/` exists but is empty, and `VERSION_SPECIFICATION.md` governs artifact versions, not the framework's own releases. | Planned |
| 33 | Maintenance & Operator Runbooks | `docs/operator/MAINTENANCE_RUNBOOKS.md` | Consolidates `WEEKLY_OPERATOR_PLAN.md` and `MONTHLY_OPERATOR_PLAN.md` into one index of recurring operator work. | Planned |
| 34 | Disaster Recovery | `docs/operator/DISASTER_RECOVERY.md` | **Gap.** No document today describes recovery from a corrupted working tree, a bad force-push, or a broken validator baseline. | Planned |
| 35 | Security & Secret Handling | `docs/operator/SECURITY_AND_SECRET_HANDLING.md` | **Gap.** The secret-pattern validator rule (`_validate_obvious_secrets` in `scripts/asf_validator/content_integrity.py`) exists in code with no standalone policy document explaining its scope and rationale. | Planned |
| 36 | Incident Response | `docs/operator/INCIDENT_RESPONSE.md` | **Gap.** No document today describes response steps for a misbehaving live Ollama call, a validator regression, or an unauthorized destructive Git operation. | Planned |

### Part X — Long-Term Evolution

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 37 | Long-Term Roadmap Synthesis | `docs/operator/LONG_TERM_ROADMAP_SYNTHESIS.md` | Consolidates `ROADMAP.md`, `VALIDATOR_ROADMAP.md`, and `PROJECT_TRACKER.md`'s Next Actions into one strategic view. | Planned |
| 38 | Self-Improving Documentation Protocol | `docs/operator/SELF_IMPROVING_DOCUMENTATION_PROTOCOL.md` | Meta-chapter: how this manual stays current, who updates the Table of Contents when a chapter lands, and how drift between this manual and reality gets detected. | Planned |
| 39 | Appendices: Command, ADR, and File Index | `docs/operator/APPENDICES_COMMAND_ADR_FILE_INDEX.md` | **Gap.** Single quick-reference appendix of every CLI command, a one-line-per-ADR index, and the full repository file map. | Planned |

## Gap Analysis

Comparing the planned handbook (above) against what exists today.

### Existing knowledge (strong; reference, do not rewrite)

All 19 ADRs (`docs/adr/`); all 15 architecture documents (`docs/architecture/`);
all 9 specifications (`docs/specifications/`) and their backing JSON
Schemas (`schemas/`); `docs/principles/DESIGN_PRINCIPLES.md`,
`NAMING_CONVENTION.md`, and `KNOWLEDGE_NAMING_CONVENTION.md`; the Knowledge
Base governance trio (`knowledge/README.md`, `KNOWLEDGE_CATEGORIES.md`,
`KNOWLEDGE_INDEX.md`); the full `.ai/` governance suite (roles, playbooks,
standards, `DECISION_RIGHTS.md`); `docs/guides/VALIDATION_GUIDE.md`,
`COMPILER_LIFECYCLE.md`, `CONTENT_SKILL_READINESS.md`,
`RUNTIME_PROMOTION_READINESS.md`, `WEEKLY_OPERATOR_PLAN.md`,
`MONTHLY_OPERATOR_PLAN.md`, `GOLDEN_SAMPLE_INTAKE_PLAN.md`;
`docs/roadmaps/ROADMAP.md` and `VALIDATOR_ROADMAP.md`; `PROJECT_CONTEXT.md`,
`PROJECT_TRACKER.md`, and `README.md`. This documentation set is already
well-factored under a one-document-one-concern discipline — no duplication
or contradiction was found while preparing this manual.

### Missing knowledge (real gaps; each mapped to the chapter above that closes it)

| Gap | Evidence | Closed by |
| --- | --- | --- |
| No coding standards document | Conventions exist only as implicit code patterns across `scripts/asf_validator`, `scripts/asf_runtime`, `adapters/` | Chapter 13 |
| No testing standards document | `tests/unit/` and adapter test isolation are consistent in practice but documented only in tracker prose (Sprint 42) | Chapter 22 |
| No diagnostic code index | `ASF-SCHEMA-*`, `ASF-SEMANTIC-*`, `ASF-REPOSITORY-*`, `ASF-RUNTIME-PLAN-*`, `ASF-BINDING-*` codes are defined across many files with no single index | Chapter 24 |
| No documentation sitemap | Discovering "every doc and its purpose" currently requires reading `README.md` plus several `README.md`/index files by hand | Chapter 18 |
| `docs/references/GLOSSARY.md` is a stub | File contains only `TODO` placeholders under every section | Chapter 20 |
| `docs/guides/GETTING_STARTED.md` is a stub | File contains only `TODO` placeholders under every section | Referenced in Chapter 5 (Session Bootstrap Protocol); population deferred to whichever future prompt scopes it explicitly |
| `docs/guides/DEVELOPMENT_GUIDE.md` is a stub | File contains only `TODO` placeholders under every section | Referenced in Chapter 13 (Coding Standards); population deferred similarly |
| No framework-level release/versioning policy | `changelog/` directory exists but is empty; `VERSION_SPECIFICATION.md` governs artifact versions only | Chapter 32 |
| No disaster recovery document | No document describes recovering from a corrupted tree, bad force-push, or broken validator baseline | Chapter 34 |
| No standalone security/secret-handling policy | The rule exists as code (`_validate_obvious_secrets`) with no policy document explaining scope/rationale | Chapter 35 |
| No incident response document | No defined response steps for a misbehaving live call, validator regression, or unauthorized destructive Git op | Chapter 36 |
| No content intelligence strategy document | `skill:content-creation`'s product goal is not tied to a strategic quality narrative beyond the Monthly Operator Plan | Chapter 29 |
| No learning engine / continuous improvement design | Evaluation/Reflection exist as contracts; no document describes closing the loop back into Knowledge/Skills over time | Chapter 31 |
| `DECISION_RIGHTS.md` has no worked decision tree | The rule is narrative prose; no example-driven flowchart exists | Chapter 3 |
| No single ordered session-bootstrap checklist | The read order is implied across `PROJECT_CONTEXT.md` and `SPRINT_WORKFLOW.md` but never stated as one ordered list | Chapter 5 |
| No agent-auto-discovery routing files | No `CLAUDE.md`/`AGENTS.md` existed before this change, so a new session had to be told to read `PROJECT_CONTEXT.md` manually every time | Closed directly by this change (see [Repository Changes](#repository-changes-applied-in-this-revision)) |

### Documents to merge

None. Every existing document already covers a distinct concern with no
found overlap or contradiction; merging any of them would violate the same
one-concern-per-document discipline this repository already applies to
Skills (Design Principle 5). Future `docs/operator/*.md` chapters
synthesize across documents in prose; they do not absorb or replace any of
the source documents they reference.

### Documents to keep separate

All ADRs (immutable, superseded-not-edited per the Version Specification);
all architecture documents; all specifications and schemas;
`PROJECT_CONTEXT.md` and `PROJECT_TRACKER.md` (these remain the live,
frequently-updated operational ledger — a different rate of change and a
different purpose than this manual's stable spine, and must never be
merged into it).

### Documents to deprecate

None outright. The three stub documents (`docs/guides/GETTING_STARTED.md`,
`docs/guides/DEVELOPMENT_GUIDE.md`, `docs/references/GLOSSARY.md`) are
flagged as candidates for either real content (via the chapters above) or a
formal deprecation decision — deciding which is a Documentation Engineer
call this manual does not make unilaterally in its first revision.

### Documents to reference

Effectively the entire existing documentation tree — each is mapped above
to the specific future chapter that will link to it. No new document this
manual creates is intended to be read instead of an existing one; each is
intended to be read as a guide to reading several existing ones together.

## Repository Changes Applied in This Revision

This section records exactly what Prompt 01 changed, so a future session
does not have to reconstruct it from `git log` alone (though `git log`
remains the authoritative record per the Truth Hierarchy).

- Added `MASTER_OPERATOR.md` (this file).
- Added `CLAUDE.md` and `AGENTS.md` — thin, non-authoritative routing files
  so Claude Code and Codex-style tools land on this manual automatically at
  session start.
- Added `docs/adr/ADR-0020-master-operator-manual-and-documentation-hub.md`
  (Status: Proposed) recording the hub-and-spoke decision and the routing
  file addition, since both are cross-cutting governance decisions.
- Added a pointer to this manual in `README.md`, `PROJECT_CONTEXT.md`,
  `PROJECT_TRACKER.md`, `.ai/README.md`, and
  `.ai/playbooks/SPRINT_WORKFLOW.md`'s Step 1, without removing or
  restructuring any existing content or link in those files.
- Recorded this work as Sprint 44 in `PROJECT_TRACKER.md` and
  `PROJECT_CONTEXT.md`, following this repository's existing sprint
  discipline rather than treating the 30-prompt build-out as an
  undocumented parallel process.
- Created no `docs/operator/*.md` chapter files yet — every Table of
  Contents row above is intentionally `Planned`. Writing chapter content is
  explicitly out of scope for Prompt 01 (see Future Expansion Strategy).

## Validation & Consistency

`docs/guides/VALIDATION_GUIDE.md` remains the authority for how this
repository's validator works; this section only states what a session
touching this manual or any `docs/operator/*.md` chapter must run before
committing:

1. `python scripts/validate_repository.py` — checks every relative
   Markdown link and anchor across the entire repository (including this
   file), duplicate headings/anchors within one file, and every `ADR-NNNN`
   reference against a real ADR document. A chapter that links to another
   not-yet-written chapter, or that duplicates a heading text already used
   elsewhere in the same file, fails this check.
2. `python -m unittest discover -s tests/unit` — required only if a change
   touched code, not for a documentation-only change like this one.
3. Confirm `PROJECT_TRACKER.md`'s Current Sprint and `PROJECT_CONTEXT.md`'s
   Current Focus were updated in the same change, per this repository's
   existing Definition of Done.

This revision was validated with `python scripts/validate_repository.py`
before commit; see the Prompt 01 final report for the exact result.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Prompt 01/30: established the Master Operator Manual foundation — Vision, Mission, Philosophy, Repository Truth Hierarchy, Operating Principles, Autonomous Development Rules, Decision Hierarchy, Documentation Strategy and Architecture, Future Expansion Strategy, the complete 39-chapter Table of Contents across ten Parts, and the Gap Analysis. No chapter content written yet. |
