# Weekly Operator Plan

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Give an autonomous or human operator session a bounded, day-by-day runbook
for the week following ADR-0016 through ADR-0019's acceptance, so a session
with no other instruction can audit repository/governance state, check the
two live Next Actions triggers, and refresh operational documentation
without inventing new scope. This document is updated in place each time it
is exercised rather than replaced by a new dated file, consistent with this
repository's existing guardrail against unbounded governance-document growth
(`PROJECT_TRACKER.md`'s Risks and Guardrails table).

## Scope

This plan covers **only** the two open Next Actions in `PROJECT_TRACKER.md`
as of 2026-07-12:

1. MCP Python SDK v2 stable release (target date 2026-07-27).
2. SemVer pre-release precedence in `scripts/asf_validator/version_ir.py`
   (Sprint 17's documented simplification), gated on a real pre-release
   version being adopted somewhere in the repository.

Both are **read-only audit triggers**, not standing work. Neither
authorizes code changes until its trigger condition is independently
confirmed true. No other backlog item exists outside these two as of this
document's last update — see `PROJECT_TRACKER.md`'s Next Actions section for
the current authoritative list.

## How to Use This Document

Each day below names: the day's objective, what work is allowed, what work
is explicitly forbidden, the condition that ends the day's work early
(stop condition), the validation command(s) to run if anything changed, and
the commit rule. An operator session should:

1. Identify which day applies (by elapsed time since the last entry in this
   document's Revision History, not by calendar day count alone — skip
   ahead if multiple days have passed with nothing to report).
2. Do only that day's allowed work.
3. Record findings either inline in this document (if the finding changes
   future guidance) or as a `PROJECT_TRACKER.md` Next Actions edit (if the
   finding changes actionable state) — not both, to avoid duplicated
   sources of truth.
4. Stop cleanly. Do not manufacture additional work to fill session budget.

## Day-by-Day Plan

### Day 1 — Repository/governance audit, confirm ADR queue closed

- **Objective:** Confirm no ADR is `Proposed` and awaiting a human decision;
  confirm `PROJECT_TRACKER.md` Next Actions match real repository state.
- **Allowed work:** Read `.ai/governance/DECISION_RIGHTS.md`,
  `PROJECT_TRACKER.md`, `PROJECT_CONTEXT.md`, every `docs/adr/*.md` Status
  field; run `python scripts/asf.py doctor` and the full validation matrix
  (Appendix B) as a read-only health check.
- **Forbidden work:** Any ADR Status edit without a human decision already
  given; any code change.
- **Stop condition:** Any ADR found `Proposed` -> report and wait for human
  decision (do not self-accept, per `DECISION_RIGHTS.md`).
- **Validation command:** Full matrix, Appendix B (read-only; no source
  changes expected).
- **Commit rule:** No commit unless a real doc drift is found.
- **Status (2026-07-12): Completed.** All 19 real ADRs (`ADR-0001`-`ADR-0019`)
  are `Accepted`; none are `Proposed`. `PROJECT_TRACKER.md` Next Actions
  correctly lists only the MCP SDK v2 and SemVer pre-release triggers.
  `python scripts/asf.py doctor` reported `status: ok`
  (`repository_valid: true`, `schemas: true`, `langgraph: true`). Full
  validation matrix (contracts 23/23, IR 47/47, graph 14/14, semantics 4/4,
  repository 0 errors/0 warnings, core unit tests 168/168) passed.

### Day 2 — MCP SDK v2 readiness audit (read-only)

- **Objective:** Determine whether MCP Python SDK v2 has shipped as a
  stable (non-prerelease) release.
- **Allowed work:** Query the public PyPI index for the installed/available
  `mcp` package versions (e.g. `pip index versions mcp`) — a free,
  unauthenticated, read-only registry lookup, not a paid/cloud API call and
  not a credential. Compare the highest version against `2.0.0`.
- **Forbidden work:** Installing or pinning to any `2.x` version; editing
  `adapters/mcp_tools/requirements-mcp-tools.txt` or any adapter source;
  assuming stability from a pre-release/rc tag.
- **Stop condition:** If a `2.x` stable version is found, do **not** migrate
  same-day. Record the finding in `PROJECT_TRACKER.md` Next Actions as
  newly actionable and hand off to Day 3's checklist for the actual
  migration decision.
- **Validation command:** None (no source changes expected). If the finding
  changes tracker text, rerun `python scripts/validate_repository.py`.
- **Commit rule:** No commit unless the trigger fired (see Day 3) or a
  meaningful "last checked" note is added.
- **Status (2026-07-12, first pass during Day 1 audit): Not triggered.**
  `pip index versions mcp` reported latest `1.28.1`; no `2.x` release
  exists yet. Re-check on or after 2026-07-27, or whenever this document is
  next exercised, whichever is sooner.

### Day 3 — MCP adapter compatibility checklist (no migration)

- **Objective:** Keep a ready-made, accurate list of exactly what
  `adapters/mcp_tools/` touches in the `mcp` SDK, so a future migration
  session does not have to re-derive it from scratch once v2 is stable.
- **Allowed work:** Grep/read `adapters/mcp_tools/` for SDK usage; update
  Appendix A below if the adapter's SDK surface has changed since the last
  update.
- **Forbidden work:** Renaming any `FastMCP`/`MCPServer` reference; bumping
  the pin; editing `binding.py`'s import or type usage; any speculative
  v2-shaped code.
- **Stop condition:** None expected while v2 is unreleased — this is a
  standing reference, refreshed opportunistically. If v2 has shipped
  (Day 2 fired), this checklist becomes the scope statement for a
  **separate**, explicitly-triggered migration session — still not
  performed same-day.
- **Validation command:** None for the checklist itself (docs only).
- **Commit rule:** Only if Appendix A's content actually changes.
- **Status (2026-07-12): Prepared.** See Appendix A. Current SDK surface is
  exactly one import (`mcp.types`) and one type (`types.Tool`); no
  `FastMCP`/`MCPServer` reference exists anywhere in adapter source (only in
  a requirements-file comment describing the *rationale* for the pin) —
  meaning the specific rename ADR-0013/the pin comment warns about may not
  even affect this adapter's actual migration surface.

### Day 4 — SemVer pre-release readiness audit

- **Objective:** Determine whether any repository artifact has adopted a
  real pre-release SemVer version (e.g. `1.2.3-alpha.1`, `2.0.0-rc.1`).
- **Allowed work:** Grep `*.yaml`/`*.yml`/`*.json` artifact `version:`
  fields for a `-` pre-release suffix per the SemVer 2.0.0 grammar already
  encoded in `scripts/asf_validator/version_ir.py`'s `_VERSION_PATTERN`.
- **Forbidden work:** Writing or modifying any pre-release comparison logic
  in `version_ir.py` without a real adopted version driving it; speculative
  comparator implementation "just in case."
- **Stop condition:** If a real pre-release version is found adopted,
  do not implement the comparator inline. Record it as a newly-triggered
  Next Action requiring its own scoped sprint (with a Build-vs-Reuse ADR if
  the fix is non-trivial, per this repository's established pattern).
- **Validation command:** None if nothing found (read-only). If found,
  no code change this session — only a `PROJECT_TRACKER.md` Next Actions
  update, validated with `python scripts/validate_repository.py`.
- **Commit rule:** No commit unless the trigger fired and the tracker
  needs updating to reflect it.
- **Status (2026-07-12, first pass during Day 1 audit): Not triggered.** No
  `version:` field anywhere in the repository matches a pre-release suffix.
  `version_ir.py`'s documented (major, minor, patch)-only comparison remains
  the correct, non-speculative behavior.

### Day 5 — Validation matrix refresh / document test commands

- **Objective:** Confirm `docs/guides/VALIDATION_GUIDE.md` (and Appendix B
  below) still names the real, current validation commands with no drift
  against `scripts/`.
- **Allowed work:** Cross-check the guide's documented commands against the
  actual contents of `scripts/`; run each documented command to confirm it
  still behaves as described; update the guide only if real drift is found.
- **Forbidden work:** Restructuring the guide's philosophy/sections;
  documenting hypothetical future commands that do not exist yet.
- **Stop condition:** None expected; this is a confirm-or-fix day.
- **Validation command:** Full matrix, Appendix B.
- **Commit rule:** No commit unless real drift is found and fixed.
- **Status (2026-07-12): Confirmed current, no change needed.**
  `docs/guides/VALIDATION_GUIDE.md` is Version 0.8, last updated 2026-07-12
  (Sprint 43), and its documented commands were all re-run today with
  matching results (Appendix B).

### Day 6 — Cleanup stale tracker wording (docs-only, only if a real gap exists)

- **Objective:** Find and fix genuinely stale **current-state** claims in
  `PROJECT_TRACKER.md`/`PROJECT_CONTEXT.md` (e.g. a Next Action describing
  a decision that has since been made).
- **Allowed work:** Read both files' Current Focus / Next Actions /
  most-recent state sections for accuracy against today's real repository
  state.
- **Forbidden work:** Rewriting **historical** Sprint narrative text (e.g.
  Sprint 36/39/40/41's "pending human acceptance" phrasing) to imply a
  later decision applied retroactively — those entries correctly describe
  what was true when each sprint closed, and this repository's established
  practice (set when ADR-0016-0019 were accepted) is to append a new
  Revision History entry recording the later decision, never rewrite prior
  entries. Any wording change that would alter a decision's meaning, not
  just fix staleness, is out of scope for unilateral action.
- **Stop condition:** A wording gap that turns out to encode a real
  undecided question (not just stale phrasing) -> stop and report as
  requiring human direction, per `DECISION_RIGHTS.md`'s escalation rule.
- **Validation command:** `python scripts/validate_repository.py` (link/
  anchor integrity) if any content changes.
- **Commit rule:** Only if a real gap is found and fixed.
- **Status (2026-07-12): Confirmed current, no change needed.** Next
  Actions accurately lists only the two open triggers; the ADR-acceptance
  Revision History entries (`PROJECT_TRACKER.md` and `PROJECT_CONTEXT.md`)
  already record 2026-07-12's decision without altering earlier entries.

### Day 7 — Final weekly report, next trigger prompt

- **Objective:** Summarize the week's findings and hand off a short,
  concrete prompt for whichever session picks up next.
- **Allowed work:** Compile a summary from Days 1-6's Status notes above;
  update this document's Revision History; update `PROJECT_TRACKER.md`'s
  Next Actions only if a trigger fired during the week.
- **Forbidden work:** Opening any new unscoped work item.
- **Stop condition:** None — this is the wrap-up day.
- **Validation command:** Full matrix, Appendix B, as a clean-stop
  confirmation.
- **Commit rule:** One `docs:` commit for this document's updates, separate
  from any other change.
- **Status (2026-07-12): This session's audit doubled as Days 1-6 read-only
  checks in a single pass** because both triggers resolved to "not yet" on
  first check and no code work was authorized. Next scheduled full re-check:
  on or before 2026-07-19 (one week from this document's Last Updated date),
  or immediately if either trigger fires sooner (MCP v2 stable release, or a
  pre-release version appearing in any artifact).

## Appendix A — MCP Adapter (`adapters/mcp_tools/`) v1-to-v2 Compatibility Checklist

Prepared 2026-07-12, before any v2 release, so a future migration session
has a verified starting point instead of re-deriving adapter scope from
scratch.

| Surface | Location | Note |
| --- | --- | --- |
| `import mcp.types as types` | `adapters/mcp_tools/binding.py:17` | Sole SDK import in the package. |
| `types.Tool` | `adapters/mcp_tools/binding.py:56,63,103,119` | Sole SDK type referenced. |
| `mcp.server.lowlevel.Server` | `adapters/mcp_tools/binding.py:98` (docstring only) | Named only in a comment describing the shape `MCPToolRegistry` is duck-type-compatible with; **not imported or instantiated** anywhere in this adapter. |
| `FastMCP` / `MCPServer` | `adapters/mcp_tools/requirements-mcp-tools.txt:2` (comment only) | The v1->v2 rename ADR-0013's pin comment warns about does not appear to affect this adapter's actual code, since it never imports the high-level `FastMCP` convenience class. Re-verify against the real v2 changelog once released — this is a documented expectation, not a tested fact, since v2 does not exist yet to test against. |
| Pin | `adapters/mcp_tools/requirements-mcp-tools.txt:4` | `mcp>=1.27,<2`. Do not widen until v2 stable is confirmed **and** the adapter test suite (`adapters/mcp_tools`, 7/7 as of 2026-07-12) passes against it. |

Migration (when triggered) must still: read the real v2 changelog, update
the pin deliberately, rerun `adapters/mcp_tools`'s test suite unmodified
first to see what actually breaks, then fix only what breaks — not
speculatively rewrite working code.

## Appendix B — Validation Command Matrix (confirmed current 2026-07-12)

```text
python scripts/validate_contracts.py       # 23/23
python scripts/build_ir.py                 # 47/47
python scripts/build_graph.py               # 14/14
python scripts/build_semantics.py           # 4/4
python scripts/validate_repository.py       # 0 errors, 0 warnings
python -m unittest discover -s tests/unit   # 168/168
```

Adapter suites (each in its own isolated process — see
`adapters/README.md` for why they cannot be collected together):

```text
adapters/mcp_tools            python -m pytest -q   # 7/7
adapters/llamaindex_retrieval python -m pytest -q   # 15/15
adapters/model_invokers       python -m pytest -q   # 20/20 (+1 opt-in skip)
adapters/publisher_adapters   python -m pytest -q   # 20/20
adapters/langgraph_runtime    python -m pytest -q   # 23/23 (+1 opt-in skip)
adapters/ollama_execution     python -m pytest -q   # 107/107 (+1 opt-in skip)
```

Opt-in skips require `ASF_TEST_OLLAMA=1` (or equivalent) and a real local
Ollama server; they are intentionally not run by default. This matrix is
the authoritative source for validation commands; `docs/guides/
VALIDATION_GUIDE.md` covers the underlying design and diagnostic shape.

## Related Documents

- `PROJECT_TRACKER.md` (Next Actions — authoritative live trigger list)
- `PROJECT_CONTEXT.md` (Current Focus, Revision History)
- `.ai/governance/DECISION_RIGHTS.md`
- `docs/guides/VALIDATION_GUIDE.md`
- `docs/guides/RUNTIME_PROMOTION_READINESS.md` (precedent for a bounded,
  gated readiness document)
- ADR-0013 (Build vs Reuse — governs the MCP pin rationale)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Established the weekly operator plan; Day 1 audit confirmed all 19 ADRs Accepted and both Next Actions triggers not yet fired (MCP SDK latest 1.28.1, no pre-release version adopted); prepared the MCP compatibility checklist and confirmed the validation matrix current |
