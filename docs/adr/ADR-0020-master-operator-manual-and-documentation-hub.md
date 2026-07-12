# ADR-0020: Master Operator Manual as a Hub-and-Spoke Documentation Layer

- **Status:** Proposed
- **Date:** 2026-07-12
- **Decision owners:** Project maintainers

## Context

Every AI session working in this repository has, in practice, needed a
long standing prompt re-explaining architecture, governance, and
constraints, because that context was scattered across `PROJECT_CONTEXT.md`,
19 ADRs, 15 architecture documents, 9 specifications, `.ai/` governance
documents, and several guides — real and non-duplicative, but not
navigable from one place. A 30-prompt initiative was started to build a
single operating manual, `MASTER_OPERATOR.md`, intended to grow into a
200-400-page-equivalent engineering handbook over many future sessions.

Two structurally different ways to build it exist:

1. **Monolith:** write all handbook content directly into one large
   `MASTER_OPERATOR.md` file, growing without bound.
2. **Hub-and-spoke:** `MASTER_OPERATOR.md` stays a stable spine (vision,
   philosophy, truth/decision hierarchies, operating rules, and a complete
   table of contents); actual chapter content lives in individual files
   under a new `docs/operator/` directory, written progressively.

This repository already uses hub-and-spoke successfully in several places
— `docs/specifications/README.md`, `.ai/README.md`, and `adapters/README.md`
each index a set of documents rather than inlining them. A monolith would
also directly contradict this repository's own "no duplication" review gate
(`.ai/standards/COLLABORATION_STANDARDS.md`) once any handbook content
started restating what an ADR, architecture document, or specification
already says, and would make a single file spanning hundreds of pages hard
to review, diff, and keep internally consistent (duplicate-anchor and
link-target checks in `scripts/asf_validator/content_integrity.py` already
scan every Markdown file in the repository, including this one).

Separately, no `CLAUDE.md` or `AGENTS.md` existed at the repository root.
Claude Code and Codex-style agent tools auto-load a root file with those
names at session start; without one, a session had no way to discover
`MASTER_OPERATOR.md` except being told about it in a prompt — which is the
exact repetition this initiative exists to eliminate.

## Decision

`MASTER_OPERATOR.md` is a hub: it holds Vision, Mission, Philosophy,
Repository Truth Hierarchy, Operating Principles, Autonomous Development
Rules, Decision Hierarchy, Documentation Strategy and Architecture, Future
Expansion Strategy, a complete Table of Contents naming every planned
chapter, and a Gap Analysis. It does not hold chapter content.

Chapter content lives under a new `docs/operator/` directory, one file per
chapter, each following `docs/_templates/DOCUMENTATION_TEMPLATE.md`'s
existing shape, added progressively as future prompts complete them. A
Table of Contents row is listed as `Planned` with its exact target path
until the file exists, and becomes a real link only once it does — never a
link to a file that does not yet exist, so repository link validation
always passes.

`CLAUDE.md` and `AGENTS.md` are added at the repository root as thin,
non-authoritative routing files. Each states, in a few lines, "read
`MASTER_OPERATOR.md` first" and nothing else of substance — they carry no
independent authority and sit outside `MASTER_OPERATOR.md`'s own Repository
Truth Hierarchy (they are explicitly named there as "everything else,"
alongside conversation history and model memory).

## Consequences

### Positive

- No existing document is duplicated, merged, or restructured; every
  existing ADR, architecture document, specification, schema, principle,
  and guide keeps its current authority and location unchanged.
- A future prompt has an unambiguous unit of work (one Table-of-Contents
  row, one target file) instead of an open-ended "add more to the big
  file" task.
- `MASTER_OPERATOR.md` itself stays small enough to read in full every
  session, matching its own "optimize for a cold-start session" philosophy.
- Claude Code and Codex-style sessions now discover the operating manual
  automatically, without depending on the human operator to mention it.

### Costs and Tradeoffs

- The full handbook is now spread across many files instead of one; a
  reader wanting "everything" must follow the Table of Contents rather
  than scrolling one document.
- `docs/operator/` is a new top-level documentation category alongside
  `docs/architecture/`, `docs/guides/`, etc., and must be kept from
  drifting into duplicating any of them — the "reference, don't duplicate"
  rule in `MASTER_OPERATOR.md`'s Philosophy section is the safeguard, but
  it is a review discipline, not (yet) an automated check.
- `CLAUDE.md` and `AGENTS.md` are a second and third place (beyond
  `MASTER_OPERATOR.md`) that must keep saying the same narrow thing; kept
  deliberately minimal to bound that risk.

## Enforcement

`python scripts/validate_repository.py` already mechanically enforces that
every relative Markdown link (including any `docs/operator/*.md` link from
`MASTER_OPERATOR.md`) resolves to a real file and a real anchor, and that no
file has a duplicate heading/anchor — this catches a Table-of-Contents row
linked before its chapter file exists. A future Automation Engineer
decision may add a dedicated check that every `docs/operator/*.md` file is
referenced from `MASTER_OPERATOR.md`'s Table of Contents, but none exists
yet; today this is a review-time discipline, matching how ADR-0008 accepted
the same tradeoff for `.ai/` role enforcement.

## Alternatives Considered

### Single monolithic `MASTER_OPERATOR.md` file

Rejected: would duplicate content already authoritative elsewhere, would
violate the existing no-duplication review gate as soon as any chapter
restated an ADR or architecture document, and would produce a single file
difficult to review, diff, or keep anchor-consistent at the targeted
200-400-page-equivalent scale.

### Put operator content inside `PROJECT_CONTEXT.md`

Rejected: `PROJECT_CONTEXT.md` is a frequently-updated live operational
ledger (sprint-by-sprint focus and revision history); mixing it with a
stable governance spine would make both harder to maintain and would blur
the Truth Hierarchy this ADR itself establishes.

### Per-tool duplicated instruction files (a separate long prompt per tool) instead of a shared manual

Rejected: this is exactly the repetition the 30-prompt initiative exists to
eliminate; a shared manual with thin per-tool routing files achieves the
same auto-discovery without duplicating the substance per tool.

## Related Documents

- `MASTER_OPERATOR.md`
- ADR-0001
- ADR-0006
- ADR-0008
- `.ai/governance/DECISION_RIGHTS.md`
- `.ai/standards/COLLABORATION_STANDARDS.md`
- `docs/_templates/DOCUMENTATION_TEMPLATE.md`
