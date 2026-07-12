# Master Operator Manual

Version: 0.2
Status: Active
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

If you are a session picking up work from the Master Operator build-out, go
straight to [Future Expansion Strategy](#future-expansion-strategy) and
[Complete Table of Contents](#complete-table-of-contents) — they tell you
exactly what to do next and where to put it. If you need the concrete
session-start procedure right now rather than this manual's own narrative,
go directly to `docs/operator/SESSION_BOOTSTRAP_PROTOCOL.md`.

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
source if this list and any of them ever appear to differ. For the fully
worked-out, category-based version of this hierarchy with concrete conflict
examples, see `docs/operator/TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md`.

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
plan. The full deterministic lifecycle, decision engine, and worked
governance scenarios these rules summarize now live under
`docs/operator/` — start at `docs/operator/AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md`
and `docs/operator/DECISION_ENGINE.md` for the complete, example-driven
version.

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
The fully worked-out version of this section, with escalation examples, now
lives at `docs/operator/GOVERNANCE_MODEL.md`; the practical Level 0-5
authority scale it implies is formalized at
`docs/operator/AUTHORITY_LEVELS.md`.

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
failure, not just a style problem). Reusable process document shapes
(design proposals, implementation plans, investigation/validation/incident
reports, and others) live under `docs/operator/_templates/`, indexed from
`docs/operator/TEMPLATE_FRAMEWORK.md`, following the same colocated-
`_templates/`-directory convention `docs/_templates/`,
`knowledge/_templates/`, `templates/skill/`, and `templates/workflow/`
already establish.

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

This manual began as Prompt 01's foundation (spine only, no chapters) and
was substantially built out by a Batch 1 continuous execution (originally
scoped as combined Prompts 02-05) that wrote 30 chapters across five Parts
plus a 12-file template library — the Autonomous Operating System,
Governance & Decision Rights, Autonomous Planning, Repository Knowledge
Architecture, and Documentation Framework Parts below. Roughly 24 chapters
across seven further Parts remain `Planned` for future Batches. Each future
session extending this manual should:

1. Read this manual's [Complete Table of Contents](#complete-table-of-contents)
   and pick the next unwritten chapter(s) — default order is the next
   `Planned` Part in sequence, but a session may reprioritize a specific
   chapter if the operator directs it to.
2. Write `docs/operator/<CHAPTER_FILE>.md` following `docs/_templates/
   DOCUMENTATION_TEMPLATE.md`'s shape, synthesizing (never duplicating) the
   source documents that chapter's Gap Analysis row names. Follow
   `docs/operator/DOCUMENT_CREATION_RULES.md`'s pre-creation checklist
   before creating any new file.
3. Flip that chapter's Table of Contents row from `Planned` to a real link,
   and update its Status.
4. Add one line to this file's Revision History if the change is structural
   (see [Versioning strategy](#versioning-strategy)); otherwise the new
   chapter file's own Revision History is sufficient.
5. Run `python scripts/validate_repository.py` (and the relevant test
   suite if code changed) before committing — see
   `docs/operator/VALIDATION_AND_REPAIR_LOOP.md` for the full procedure.
6. Follow the existing `.ai/playbooks/SPRINT_WORKFLOW.md` commit
   discipline, made fully deterministic by
   `docs/operator/AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md`: one coherent commit,
   explicit paths, and a `PROJECT_TRACKER.md`/`PROJECT_CONTEXT.md` update in
   the same change, exactly as every other sprint in this repository's
   history has done.

A genuinely new Part, or a change to a foundational principle in this
file's spine (not just a new chapter under an existing Part), is a
structural documentation decision under the Documentation Engineer's
Decision Right, and — if it changes a cross-cutting rule rather than just
adding content — should be backed by an ADR, per this repository's own
"significant architectural changes require an ADR" rule (ADR-0001, Design
Principle 10). See `docs/operator/ADR_GOVERNANCE.md` for exactly when this
applies to a documentation change specifically.

Stub documents that exist today with no real content
(`docs/guides/GETTING_STARTED.md`, `docs/guides/DEVELOPMENT_GUIDE.md`,
`docs/references/GLOSSARY.md` — see [Gap Analysis](#gap-analysis)) should be
populated as part of whichever chapter depends on them, not as a separate
unscoped effort. None was populated in Batch 1; this remains open.

## Complete Table of Contents

Every chapter, written or planned, defined so no future session has to
invent structure ad hoc. `Status` is `Written` (real link, file exists and
is validated) or `Planned` (file does not exist yet; target path already
named). No `Planned` row is a placeholder — each already states its scope
precisely enough that a future session can write the chapter without
further clarification. Parts I-V were written in Batch 1 (a continuous
execution originally scoped as combined Prompts 02-05); Parts VI-XIII
remain for future Batches.

### Part I — Autonomous Operating System [Batch 1 — Written]

| # | Chapter | File | Scope | Status |
| - | --- | --- | --- | --- |
| 1 | Session Bootstrap Protocol | [docs/operator/SESSION_BOOTSTRAP_PROTOCOL.md](docs/operator/SESSION_BOOTSTRAP_PROTOCOL.md) | The 18-step ordered repository boot sequence and the Session Initialization Contract. | Written |
| 2 | Context Restoration | [docs/operator/CONTEXT_RESTORATION.md](docs/operator/CONTEXT_RESTORATION.md) | Deterministic reconstruction of project context from repository state, and disagreement handling between sources. | Written |
| 3 | Autonomous Development Lifecycle | [docs/operator/AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md](docs/operator/AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md) | The full session state machine (ready -> planning -> implementation -> validation -> ... -> completed), the Planning Contract, and Implementation Rules. | Written |
| 4 | Validation and Repair Loop | [docs/operator/VALIDATION_AND_REPAIR_LOOP.md](docs/operator/VALIDATION_AND_REPAIR_LOOP.md) | Failure classification and required response per class, and how to tell current-change-caused from pre-existing failures. | Written |
| 5 | Autonomous Continuation Rules and Stop Conditions | [docs/operator/AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md](docs/operator/AUTONOMOUS_CONTINUATION_AND_STOP_CONDITIONS.md) | When a session must keep working automatically, and the five stop-condition classes (hard/governance/external-wait/temporary/clean-completion). | Written |
| 6 | Recovery Procedures | [docs/operator/RECOVERY_PROCEDURES.md](docs/operator/RECOVERY_PROCEDURES.md) | Detect-preserve-inspect-recover-validate-document procedures for 15 interruption/inconsistency situations. | Written |
| 7 | Multi-Session Continuity and Handover | [docs/operator/MULTI_SESSION_CONTINUITY_AND_HANDOVER.md](docs/operator/MULTI_SESSION_CONTINUITY_AND_HANDOVER.md) | What must persist in the repository (never a transcript) for a different session or tool to resume, plus the Session Completion Checklist. | Written |

### Part II — Governance and Decision Rights [Batch 1 — Written]

| # | Chapter | File | Scope | Status |
| - | --- | --- | --- | --- |
| 8 | Governance Model | [docs/operator/GOVERNANCE_MODEL.md](docs/operator/GOVERNANCE_MODEL.md) | Consolidates `.ai/README.md`, `.ai/roles/*.md`, `DECISION_RIGHTS.md`, and `COLLABORATION_STANDARDS.md` into one narrative of who decides what, with worked escalation examples. Supersedes Prompt 01's planned "Governance Model" and "Escalation & Conflict Resolution" rows. | Written |
| 9 | ADR Governance and Decision Rules | [docs/operator/ADR_GOVERNANCE.md](docs/operator/ADR_GOVERNANCE.md) | The full ADR lifecycle, a topic-indexed view of all 20 ADRs, and mandatory-vs-unnecessary rules. | Written |
| 10 | Authority Levels | [docs/operator/AUTHORITY_LEVELS.md](docs/operator/AUTHORITY_LEVELS.md) | A descriptive Level 0-5 authority scale synthesizing Decision Rights for quick task classification. | Written |
| 11 | Human vs. AI Responsibilities and Change Classification | [docs/operator/HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md](docs/operator/HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md) | Deterministic responsibility table for ~20 activity types, plus a Change Classification table (authority/design/validation/rollback/documentation/commit/push per class). Supersedes Prompt 01's planned "Human Approval Rules" row. | Written |
| 12 | Risk Classification and Governance Scenarios | [docs/operator/RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md](docs/operator/RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md) | A blast-radius/reversibility risk matrix and a worked scenario table covering 12 realistic governance situations. | Written |

### Part III — Autonomous Planning [Batch 1 — Written]

| # | Chapter | File | Scope | Status |
| - | --- | --- | --- | --- |
| 13 | Decision Engine | [docs/operator/DECISION_ENGINE.md](docs/operator/DECISION_ENGINE.md) | The deterministic seven-step "may I proceed, and how" flow, with dispositions and a worked decision table. | Written |
| 14 | Priority and Autonomous Planning Engine | [docs/operator/PRIORITY_AND_PLANNING_ENGINE.md](docs/operator/PRIORITY_AND_PLANNING_ENGINE.md) | A 14-tier priority ordering, tie-breakers, and the planning loop pseudo-algorithm. | Written |
| 15 | Work Decomposition, Dependency, and Impact Analysis | [docs/operator/WORK_DECOMPOSITION_AND_IMPACT_ANALYSIS.md](docs/operator/WORK_DECOMPOSITION_AND_IMPACT_ANALYSIS.md) | When to split vs. keep atomic, dependency types and handling, minimum impact analysis by Change Classification. | Written |
| 16 | Rollback Planning and Risk Register | [docs/operator/ROLLBACK_PLANNING_AND_RISK_REGISTER.md](docs/operator/ROLLBACK_PLANNING_AND_RISK_REGISTER.md) | Rollback strategy by situation, and when/how a risk must be formally recorded. | Written |
| 17 | Blocker Classification and Escalation | [docs/operator/BLOCKER_CLASSIFICATION_AND_ESCALATION.md](docs/operator/BLOCKER_CLASSIFICATION_AND_ESCALATION.md) | 11 blocker classes with required evidence/handling, and deterministic resolve-independently-vs-escalate rules. Supersedes Prompt 01's planned "Escalation & Conflict Resolution" row (the conflict-resolution half now lives in Chapter 19). | Written |

### Part IV — Repository Knowledge Architecture [Batch 1 — Written]

| # | Chapter | File | Scope | Status |
| - | --- | --- | --- | --- |
| 18 | Repository Architecture Map | [docs/operator/REPOSITORY_ARCHITECTURE_MAP.md](docs/operator/REPOSITORY_ARCHITECTURE_MAP.md) | Purpose/ownership/lifecycle for every top-level directory, verified against the repository, not invented. Supersedes Prompt 01's planned "Repository Structure Standard" row. | Written |
| 19 | Truth Hierarchy and Conflict Resolution (Detailed) | [docs/operator/TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md](docs/operator/TRUTH_HIERARCHY_AND_CONFLICT_RESOLUTION.md) | Category-based (not just positional) conflict resolution with worked examples; the full expansion of this manual's own Repository Truth Hierarchy. | Written |
| 20 | Documentation Placement Rules | [docs/operator/DOCUMENTATION_PLACEMENT_RULES.md](docs/operator/DOCUMENTATION_PLACEMENT_RULES.md) | A 10-step placement decision procedure and the embed/summarize/reference/extract/merge/deprecate/archive action table. | Written |
| 21 | Knowledge Classification, Lifecycle, and Capture | [docs/operator/KNOWLEDGE_CLASSIFICATION_AND_LIFECYCLE.md](docs/operator/KNOWLEDGE_CLASSIFICATION_AND_LIFECYCLE.md) | 13 knowledge classes with storage/ownership/obsolescence, the discovery-to-archival lifecycle, and the promotion threshold. | Written |
| 22 | Duplication, Staleness, and Conflict Detection | [docs/operator/DUPLICATION_AND_STALENESS_DETECTION.md](docs/operator/DUPLICATION_AND_STALENESS_DETECTION.md) | Repeatable audit procedures for duplicated guidance, stale documents, and unresolved conflicts. | Written |
| 23 | Context, Tracker, Roadmap Responsibilities, and Naming Standards | [docs/operator/CONTEXT_TRACKER_ROADMAP_AND_NAMING_STANDARDS.md](docs/operator/CONTEXT_TRACKER_ROADMAP_AND_NAMING_STANDARDS.md) | Unambiguous split between `PROJECT_CONTEXT.md`/`PROJECT_TRACKER.md`/roadmaps, plus `docs/operator/*.md` metadata/naming conventions. | Written |
| 24 | Deprecation, Archival, and Repository Evolution Strategy | [docs/operator/DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md](docs/operator/DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md) | Deprecation/archival mechanics, and split/merge/index-maintenance thresholds for `docs/operator/` and `PROJECT_TRACKER.md`. | Written |

### Part V — Documentation Framework [Batch 1 — Written]

| # | Chapter | File | Scope | Status |
| - | --- | --- | --- | --- |
| 25 | Documentation and Writing Standards | [docs/operator/DOCUMENTATION_AND_WRITING_STANDARDS.md](docs/operator/DOCUMENTATION_AND_WRITING_STANDARDS.md) | Required qualities by document type, and writing-level standards (voice, tense, normative terms). Supersedes Prompt 01's planned "Documentation Standards" row. | Written |
| 26 | Markdown, Cross-Link, and Status Standards | [docs/operator/MARKDOWN_CROSSLINK_AND_STATUS_STANDARDS.md](docs/operator/MARKDOWN_CROSSLINK_AND_STATUS_STANDARDS.md) | Markdown formatting grounded in what `content_integrity.py` actually enforces, cross-link rules, and the full Document Status Model. | Written |
| 27 | Required Sections by Document Type | [docs/operator/REQUIRED_SECTIONS_BY_DOCUMENT_TYPE.md](docs/operator/REQUIRED_SECTIONS_BY_DOCUMENT_TYPE.md) | Section requirements for 11 document types, scaled so small documents are not bloated. | Written |
| 28 | Template Framework | [docs/operator/TEMPLATE_FRAMEWORK.md](docs/operator/TEMPLATE_FRAMEWORK.md) | Indexes 5 existing templates plus 12 new ones under `docs/operator/_templates/` (design proposal, implementation plan, investigation/validation/incident/recovery report, retrospective, knowledge capture, roadmap item, blocker report, session handoff, release-readiness review). | Written |
| 29 | Documentation Review Workflow and Quality Gates | [docs/operator/DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md](docs/operator/DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md) | The 12-step review procedure, lightweight vs. full review levels, blocking Quality Gates vs. warning-level issues, and the Validation/Commit Report standards. | Written |
| 30 | Future Document Creation Rules | [docs/operator/DOCUMENT_CREATION_RULES.md](docs/operator/DOCUMENT_CREATION_RULES.md) | The pre-creation checklist preventing orphaned or redundant documents. | Written |

### Part VI — Architecture Reference [Planned]

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 31 | Architecture Index and Component Map | `docs/operator/ARCHITECTURE_INDEX.md` | Single map of all `docs/architecture/*.md` documents, their relationships, and a synthesized dependency diagram. | Planned |
| 32 | Artifact and Contract Model | `docs/operator/ARTIFACT_AND_CONTRACT_MODEL.md` | How Skill/Workflow/Knowledge/Tool/Connector/Runtime Contract/Evaluation/Reflection artifacts relate, tying `docs/specifications/` to `schemas/`. | Planned |
| 33 | Execution and Adapter Boundary | `docs/operator/EXECUTION_ADAPTER_BOUNDARY.md` | Synthesizes ADR-0013's Build vs Reuse strategy and the six `adapters/` packages into one operating picture of what executes and where. | Planned |
| 34 | Architecture Extension Points | `docs/operator/ARCHITECTURE_EXTENSION_POINTS.md` | Where a new architecture document, adapter, or Protocol seam gets added, and the governance gate for doing so. | Planned |

### Part VII — Coding and Engineering Standards [Planned]

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 35 | Coding Standards | `docs/operator/CODING_STANDARDS.md` | **Gap.** Formalizes the Python conventions already implicit in `scripts/asf_validator`, `scripts/asf_runtime`, and `adapters/` (typing, immutable dataclasses, no module-level mutable state, Protocol seams, docstring policy). | Planned |
| 36 | Naming and Metadata Standards (artifact-level) | `docs/operator/NAMING_AND_METADATA_STANDARDS.md` | Operator-facing consolidation of `NAMING_CONVENTION.md`, `KNOWLEDGE_NAMING_CONVENTION.md`, `METADATA_SPECIFICATION.md`, and `VERSION_SPECIFICATION.md` for Skill/Workflow/Knowledge artifacts. Distinct from Chapter 23, which covers `docs/operator/` chapter and tracker/context/roadmap naming only. | Planned |
| 37 | Dependency and Package Boundary Rules | `docs/operator/DEPENDENCY_BOUNDARY_RULES.md` | The "adapters never import each other" rule, `requirements-<name>.txt` isolation, and how to add a new adapter package without violating it. | Planned |

### Part VIII — Validation, Testing, and Quality Reference [Planned]

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 38 | Validation System Reference | `docs/operator/VALIDATION_SYSTEM_REFERENCE.md` | Operator map over `VALIDATION_GUIDE.md`, `VALIDATOR_ROADMAP.md`, and the `scripts/asf_validator` pipeline stages. Distinct from Chapter 4, which covers the autonomous session's repair loop, not the validator's own architecture. | Planned |
| 39 | Testing Standards | `docs/operator/TESTING_STANDARDS.md` | **Gap.** Formalizes `unittest` conventions, `tests/fixtures/contracts` conventions, and the adapter test-isolation policy (documented so far only in Sprint 42's tracker notes). | Planned |
| 40 | Quality Gates and Review Protocol (commit-level) | `docs/operator/QUALITY_GATES_AND_REVIEW.md` | Turns `COLLABORATION_STANDARDS.md`'s three review gates (Quality/Test/Chief-Architect) into a step-by-step commit review checklist. Distinct from Chapter 29, which covers documentation-specific review only. | Planned |
| 41 | Diagnostic Code Reference | `docs/operator/DIAGNOSTIC_CODE_REFERENCE.md` | **Gap.** No single index of every `ASF-*` diagnostic code (`SCHEMA`, `SEMANTIC`, `REPOSITORY`, `RUNTIME-PLAN`, `BINDING`, `PARSE`) exists today; this chapter builds it. | Planned |

### Part IX — Documentation Map, Glossary, and Product Knowledge Base [Planned]

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 42 | Documentation Map | `docs/operator/DOCUMENTATION_MAP.md` | **Gap.** Full sitemap of every document in the repository with a one-line purpose, kept current by hand until a validator rule can check it. | Planned |
| 43 | Glossary and Terminology Governance | `docs/operator/GLOSSARY_GOVERNANCE.md` | **Gap.** The process for populating the currently-stub `docs/references/GLOSSARY.md` and keeping terminology consistent repository-wide; this chapter also populates that glossary's real content. | Planned |
| 44 | Knowledge Base Management (product) | `docs/operator/KNOWLEDGE_BASE_MANAGEMENT.md` | Operator-facing consolidation of `KNOWLEDGE_ARCHITECTURE.md`, `KNOWLEDGE_CATEGORIES.md`, and the index-maintenance workflow for `knowledge/` (Skill-consumed domain content — distinct from Chapter 21's repository-internal knowledge taxonomy). | Planned |

### Part X — AI Skills, Workflows, and Runtime [Planned]

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 45 | Skills Reference | `docs/operator/SKILLS_REFERENCE.md` | Catalog of all production Skills (`content-creation`, `research`, `review-quality`) with lifecycle status and dependency summary. | Planned |
| 46 | Workflows Reference | `docs/operator/WORKFLOWS_REFERENCE.md` | Catalog of all four Workflow packages and the canonical composite compiler (`research-content-review`). | Planned |
| 47 | Runtime Contracts and Bindings Reference | `docs/operator/RUNTIME_CONTRACTS_REFERENCE.md` | Catalog of the five Runtime Contracts, current binding status, and which is active in production. | Planned |
| 48 | Evaluation and Reflection Reference | `docs/operator/EVALUATION_AND_REFLECTION_REFERENCE.md` | Operator map over the Evaluation/Reflection Architecture and Specification, tied to `CONTENT_SKILL_READINESS.md`'s finding that the rubric is validated but never executed. | Planned |

### Part XI — Content Intelligence and Learning Engine [Planned]

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 49 | Content Intelligence Strategy | `docs/operator/CONTENT_INTELLIGENCE_STRATEGY.md` | **Gap.** No document today ties `skill:content-creation`'s product goal to a strategic content-quality narrative beyond the Monthly Operator Plan. | Planned |
| 50 | Benchmarking Framework | `docs/operator/BENCHMARKING_FRAMEWORK.md` | Ties to the open Next Action (Content Benchmark Plan, Week 3) and `GOLDEN_SAMPLE_INTAKE_PLAN.md`; written once `docs/guides/CONTENT_BENCHMARK_PLAN.md` exists or alongside it. | Planned |
| 51 | Learning Engine and Continuous Improvement | `docs/operator/LEARNING_ENGINE_AND_CONTINUOUS_IMPROVEMENT.md` | **Gap.** Fully aspirational today: no document describes how Evaluation/Reflection findings would feed back into the Knowledge Base or Skill instructions over time. | Planned |

### Part XII — Release Engineering, Maintenance, and Operations [Planned]

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 52 | Release Engineering | `docs/operator/RELEASE_ENGINEERING.md` | **Gap.** Framework-level versioning/release policy — `changelog/` exists but is empty, and `VERSION_SPECIFICATION.md` governs artifact versions, not the framework's own releases. | Planned |
| 53 | Maintenance and Operator Runbooks | `docs/operator/MAINTENANCE_RUNBOOKS.md` | Consolidates `WEEKLY_OPERATOR_PLAN.md` and `MONTHLY_OPERATOR_PLAN.md` into one index of recurring operator work. | Planned |
| 54 | Disaster Recovery | `docs/operator/DISASTER_RECOVERY.md` | **Partially addressed by Chapter 6** (session/Git-level recovery: interrupted sessions, merge conflicts, detached HEAD, stale locks). This chapter remains for catastrophic/repository-corruption scenarios Chapter 6 does not cover — not yet applicable at this repository's current scale, written when a real scenario or a production environment makes it concrete. | Planned |
| 55 | Security and Secret Handling | `docs/operator/SECURITY_AND_SECRET_HANDLING.md` | **Gap.** The secret-pattern validator rule (`_validate_obvious_secrets` in `scripts/asf_validator/content_integrity.py`) exists in code with no standalone policy document explaining its scope and rationale. | Planned |
| 56 | Incident Response | `docs/operator/INCIDENT_RESPONSE.md` | **Partially addressed by Chapter 17's Security blocker class and the Incident Report template.** This chapter remains for the detection/triage/containment procedure itself (e.g., a misbehaving live Ollama call, a validator regression). | Planned |

### Part XIII — Long-Term Evolution [Planned]

| # | Chapter | Target file | Scope | Status |
| - | --- | --- | --- | --- |
| 57 | Long-Term Roadmap Synthesis | `docs/operator/LONG_TERM_ROADMAP_SYNTHESIS.md` | Consolidates `ROADMAP.md`, `VALIDATOR_ROADMAP.md`, and `PROJECT_TRACKER.md`'s Next Actions into one strategic view. | Planned |
| 58 | Self-Improving Documentation Protocol | `docs/operator/SELF_IMPROVING_DOCUMENTATION_PROTOCOL.md` | Meta-chapter: how this manual stays current, who updates the Table of Contents when a chapter lands, and how drift between this manual and reality gets detected — building on Chapter 22's audit procedures at the whole-manual scale. | Planned |
| 59 | Appendices: Command, ADR, and File Index | `docs/operator/APPENDICES_COMMAND_ADR_FILE_INDEX.md` | **Gap.** Single quick-reference appendix of every CLI command, a one-line-per-ADR index, and the full repository file map. | Planned |

## Gap Analysis

Comparing the planned handbook against what exists today, updated after
Batch 1.

### Existing knowledge (strong; reference, do not rewrite)

All 20 ADRs (`docs/adr/`, including proposed ADR-0020); all 15 architecture
documents (`docs/architecture/`); all 9 specifications
(`docs/specifications/`) and their backing JSON Schemas (`schemas/`);
`docs/principles/DESIGN_PRINCIPLES.md`, `NAMING_CONVENTION.md`, and
`KNOWLEDGE_NAMING_CONVENTION.md`; the Knowledge Base governance trio
(`knowledge/README.md`, `KNOWLEDGE_CATEGORIES.md`, `KNOWLEDGE_INDEX.md`);
the full `.ai/` governance suite (roles, playbooks, standards,
`DECISION_RIGHTS.md`); `docs/guides/VALIDATION_GUIDE.md`,
`COMPILER_LIFECYCLE.md`, `CONTENT_SKILL_READINESS.md`,
`RUNTIME_PROMOTION_READINESS.md`, `WEEKLY_OPERATOR_PLAN.md`,
`MONTHLY_OPERATOR_PLAN.md`, `GOLDEN_SAMPLE_INTAKE_PLAN.md`;
`docs/roadmaps/ROADMAP.md` and `VALIDATOR_ROADMAP.md`; `PROJECT_CONTEXT.md`,
`PROJECT_TRACKER.md`, and `README.md`. This documentation set was already
well-factored under a one-document-one-concern discipline before Batch 1 —
no duplication or contradiction was found while preparing it.

**Added by Batch 1:** 30 `docs/operator/*.md` chapters (Parts I-V above)
and a 12-file template library under `docs/operator/_templates/` — now
themselves part of this repository's existing, reference-don't-rewrite
knowledge for any future Batch.

### Missing knowledge (real gaps; each row states its Batch 1 outcome)

| Gap | Evidence | Batch 1 outcome |
| --- | --- | --- |
| No coding standards document | Conventions exist only as implicit code patterns across `scripts/asf_validator`, `scripts/asf_runtime`, `adapters/` | Still open — Chapter 35 (Part VII, Planned) |
| No testing standards document | `tests/unit/` and adapter test isolation are consistent in practice but documented only in tracker prose (Sprint 42) | Still open — Chapter 39 (Part VIII, Planned) |
| No diagnostic code index | `ASF-SCHEMA-*`, `ASF-SEMANTIC-*`, `ASF-REPOSITORY-*`, `ASF-RUNTIME-PLAN-*`, `ASF-BINDING-*` codes are defined across many files with no single index | Still open — Chapter 41 (Part VIII, Planned) |
| No documentation sitemap | Discovering "every doc and its purpose" currently requires reading `README.md` plus several index files by hand | Still open — Chapter 42 (Part IX, Planned) |
| `docs/references/GLOSSARY.md` is a stub | File contains only `TODO` placeholders under every section | Still open — Chapter 43 (Part IX, Planned) |
| `docs/guides/GETTING_STARTED.md` is a stub | File contains only `TODO` placeholders under every section | Still open — not populated this Batch |
| `docs/guides/DEVELOPMENT_GUIDE.md` is a stub | File contains only `TODO` placeholders under every section | Still open — not populated this Batch |
| No framework-level release/versioning policy | `changelog/` directory exists but is empty; `VERSION_SPECIFICATION.md` governs artifact versions only | Still open — Chapter 52 (Part XII, Planned) |
| No disaster recovery document | No document described recovering from a corrupted tree, bad force-push, or broken validator baseline | **Substantially closed** for session/Git-level scenarios by written Chapter 6 (`RECOVERY_PROCEDURES.md`, 15 situations covered); catastrophic/production-scale recovery remains Chapter 54 (Planned) |
| No standalone security/secret-handling policy | The rule exists as code (`_validate_obvious_secrets`) with no policy document explaining scope/rationale | Still open — Chapter 55 (Part XII, Planned); referenced but not authored this Batch |
| No incident response document | No defined response steps for a misbehaving live call, validator regression, or unauthorized destructive Git op | **Partially closed** — Chapter 17 (`BLOCKER_CLASSIFICATION_AND_ESCALATION.md`) defines the Security blocker class and escalation path, and the Incident Report template exists; the detection/triage/containment procedure itself remains Chapter 56 (Planned) |
| No content intelligence strategy document | `skill:content-creation`'s product goal is not tied to a strategic quality narrative beyond the Monthly Operator Plan | Still open — Chapter 49 (Part XI, Planned) |
| No learning engine / continuous improvement design | Evaluation/Reflection exist as contracts; no document describes closing the loop back into Knowledge/Skills over time | Still open — Chapter 51 (Part XI, Planned) |
| `DECISION_RIGHTS.md` has no worked decision tree | The rule was narrative prose; no example-driven flowchart existed | **Closed** — written Chapter 13 (`DECISION_ENGINE.md`) and Chapter 12 (`RISK_CLASSIFICATION_AND_GOVERNANCE_SCENARIOS.md`'s scenario table) |
| No single ordered session-bootstrap checklist | The read order was implied across `PROJECT_CONTEXT.md` and `SPRINT_WORKFLOW.md` but never stated as one ordered list | **Closed** — written Chapter 1 (`SESSION_BOOTSTRAP_PROTOCOL.md`) |
| No agent-auto-discovery routing files | No `CLAUDE.md`/`AGENTS.md` existed before Prompt 01 | Closed in Prompt 01 |

**New gaps this Batch's own audit found and closed within scope:**
Repository Structure Standard (an original gap) is now closed by written
Chapter 18 (`REPOSITORY_ARCHITECTURE_MAP.md`), verified directory-by-
directory rather than asserted; Human Approval Rules and Escalation &
Conflict Resolution (two original planned rows) are closed by written
Chapters 11, 17, and 19; Documentation Standards (an original planned row)
is closed by written Chapters 25-26.

### Documents to merge

None. Every existing document (including this Batch's 30 new chapters)
covers a distinct concern with no found overlap or contradiction; merging
any of them would violate the same one-concern-per-document discipline this
repository already applies to Skills (Design Principle 5). Where two
chapters could appear to overlap (e.g., Chapter 4's repair loop vs. Chapter
38's planned Validation System Reference), each Table of Contents row above
states the distinction explicitly to prevent future duplication.

### Documents to keep separate

All ADRs (immutable, superseded-not-edited per the Version Specification);
all architecture documents; all specifications and schemas;
`PROJECT_CONTEXT.md` and `PROJECT_TRACKER.md` (these remain the live,
frequently-updated operational ledger — a different rate of change and a
different purpose than this manual's stable spine, and must never be
merged into it); every `docs/operator/*.md` chapter (one file per concern,
per `docs/operator/DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md`'s
merge threshold, which this Batch's own chapter set does not meet).

### Documents to deprecate

None outright. The three stub documents (`docs/guides/GETTING_STARTED.md`,
`docs/guides/DEVELOPMENT_GUIDE.md`, `docs/references/GLOSSARY.md`) remain
flagged as candidates for either real content (via Chapters 43 and future
population) or a formal deprecation decision — deciding which is a
Documentation Engineer call this manual does not make unilaterally.

### Documents to reference

Effectively the entire existing documentation tree, plus this Batch's own
30 chapters going forward — each is mapped above to the specific chapter
that links to or will link to it. No document this manual creates is
intended to be read instead of an existing one; each is intended to be read
as a guide to reading several existing ones together.

## Repository Changes Applied, by Revision

This section records exactly what each revision changed, so a future
session does not have to reconstruct it from `git log` alone (though
`git log` remains the authoritative record per the Truth Hierarchy). Per
this manual's own Knowledge Classification chapter, this is historical
evidence — each revision's entry is appended, never rewritten.

### Revision 0.1 (Prompt 01)

- Added `MASTER_OPERATOR.md` (this file) as a spine with no chapters yet.
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
  `PROJECT_CONTEXT.md`.
- Created no `docs/operator/*.md` chapter files — every Table of Contents
  row was `Planned`, by design.

### Revision 0.2 (Batch 1 — combined Prompts 02-05 scope, one continuous execution)

- Added 30 `docs/operator/*.md` chapter files across five new Parts
  (Autonomous Operating System, Governance and Decision Rights, Autonomous
  Planning, Repository Knowledge Architecture, Documentation Framework —
  see [Complete Table of Contents](#complete-table-of-contents)).
- Added a 12-file template library under `docs/operator/_templates/`,
  indexed from `docs/operator/TEMPLATE_FRAMEWORK.md`.
- Rewrote this manual's Complete Table of Contents (now 13 Parts, 59
  chapters: 30 Written, 29 Planned) and Gap Analysis to reflect actual
  Batch 1 output, removing rows Batch 1 genuinely superseded
  (Repository Structure Standard, Human Approval Rules, Escalation &
  Conflict Resolution, Documentation Standards) and renumbering the
  remaining originally-planned rows into Parts VI-XIII without dropping
  any of them.
- Updated the Repository Truth Hierarchy, Decision Hierarchy, Autonomous
  Development Rules, and Documentation Architecture sections with pointers
  to the new detailed chapters, without changing their substance.
- Wrote no new ADR: per `docs/operator/ADR_GOVERNANCE.md`'s own "when an
  ADR is unnecessary" rule, Batch 1 synthesizes and operationalizes
  existing governance rather than introducing a new cross-cutting one.
- Recorded this work as Sprint 45 in `PROJECT_TRACKER.md` and
  `PROJECT_CONTEXT.md`.
- Made no code change, called no external service, promoted no artifact
  lifecycle, and accepted no ADR.

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

Every revision recorded in
[Repository Changes Applied, by Revision](#repository-changes-applied-by-revision)
was validated with `python scripts/validate_repository.py` before commit;
see each revision's own final report for the exact result.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Prompt 01: established the Master Operator Manual foundation — Vision, Mission, Philosophy, Repository Truth Hierarchy, Operating Principles, Autonomous Development Rules, Decision Hierarchy, Documentation Strategy and Architecture, Future Expansion Strategy, the complete 39-chapter Table of Contents across ten Parts, and the Gap Analysis. No chapter content written yet. |
| 0.2 | 2026-07-12 | Batch 1 (combined Prompts 02-05, one continuous execution): wrote 30 `docs/operator/*.md` chapters across five new Parts (Autonomous Operating System, Governance and Decision Rights, Autonomous Planning, Repository Knowledge Architecture, Documentation Framework) plus a 12-file template library; rewrote the Complete Table of Contents (13 Parts, 59 chapters total) and Gap Analysis; updated Truth/Decision Hierarchy and Autonomous Development Rules sections with pointers to the new detailed chapters. No new ADR; no code change. |
