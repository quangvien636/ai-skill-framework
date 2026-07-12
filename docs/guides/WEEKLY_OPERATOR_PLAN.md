# Weekly Operator Plan

Version: 0.3
Status: Active
Last updated: 2026-07-12

This document governs the two standing infrastructure triggers (MCP SDK v2,
SemVer pre-release) only. `docs/guides/MONTHLY_OPERATOR_PLAN.md` is the
higher-level, month-scoped roadmap that sits above it and covers the
separate content-skill readiness push (golden samples, benchmark, video
pipeline integration readiness) with its own triggers — read that document
for anything content-skill-related; it does not change or override
anything below.

## Purpose

Give an autonomous or human operator session a bounded, day-by-day runbook
for the two weeks following ADR-0016 through ADR-0019's acceptance, so a
session with no other instruction can audit repository/governance state,
check the two live Next Actions triggers, prepare (but not act on)
migration/implementation readiness, and refresh operational documentation
without inventing new scope. This document is updated in place each time it
is exercised rather than replaced by a new dated file, consistent with this
repository's existing guardrail against unbounded governance-document growth
(`PROJECT_TRACKER.md`'s Risks and Guardrails table). Week 1 and Week 2 live
in this single file rather than a second file specifically so future
sessions have one authoritative runbook instead of two documents that can
drift out of sync.

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

Week 1 (Days 1-7) is guarded monitoring and readiness only: no code, no
comparator, no migration, regardless of what the triggers show. Week 2
(Days 8-14) is a **conditional implementation window** — it only authorizes
planning or implementation work on a specific day if that day's named
trigger has actually fired; otherwise every Week 2 day degrades to the same
read-only check-and-stop behavior as Week 1.

## How to Use This Document

Each day below names: the day's objective, what work is allowed, what work
is explicitly forbidden, the condition that ends the day's work early
(stop condition), the validation command(s) to run if anything changed, and
the commit rule (where a day's own text does not repeat a commit rule, the
default is: no commit unless that day produced a real, meaningful change).
An operator session should:

1. Identify which day applies by elapsed time and by this document's own
   recorded Status lines / Revision History — not by literal calendar day
   count. Skip ahead if multiple days have passed with nothing to report;
   collapse same-session re-checks into a single pass instead of repeating
   an identical check with a certainly-unchanged result.
2. Do only that day's allowed work.
3. Record findings either inline in this document (if the finding changes
   future guidance) or as a `PROJECT_TRACKER.md` Next Actions edit (if the
   finding changes actionable state) — not both, to avoid duplicated
   sources of truth.
4. Stop cleanly. Do not manufacture additional work to fill session budget,
   and do not re-run a trigger check that was already run minutes or hours
   earlier in the same session with a result that cannot plausibly have
   changed.

**Validation command note:** where a day below says "full pytest" or
similar, this means the full matrix in Appendix B — `python -m unittest
discover -s tests/unit` plus one isolated `python -m pytest` run per
`adapters/<name>/` directory — never a single bare `python -m pytest` at
the repository root. That bare form reliably fails at collection time
(verified 2026-07-12: `ERROR adapters/mcp_tools/tests/test_binding.py`,
`ERROR adapters/publisher_adapters/tests/test_descriptors.py`) because
adapter test packages intentionally share module names across isolated
processes (see `adapters/README.md`); this is a collection-scope artifact,
not a real test failure, and must not be reported as a validation error.

## Week 1 — Guarded Trigger Monitoring & Readiness

Goal: no speculative code. Focus entirely on verifying triggers, auditing
readiness, and preparing migration/test checklists for when a real signal
arrives — never acting on a signal that has not arrived.

### Day 1 — Repo/governance baseline

- **Objective:** Confirm no ADR is `Proposed` and awaiting a human decision;
  confirm `PROJECT_TRACKER.md` Next Actions match real repository state.
- **Allowed:** Run Step 0; read governance and tracker; confirm ADR queue
  status; confirm current Next Actions; update status docs if something
  real has changed.
- **Forbidden:** No MCP migration; no SemVer comparator; no adapter edits
  while a trigger has not fired.
- **Validation:** `python scripts/asf.py doctor`; full pytest (Appendix B);
  `git diff --check`.
- **Stop condition:** Abnormal working tree; governance requires human
  approval; no actionable change found.
- **Status (2026-07-12): Completed.** All 19 real ADRs (`ADR-0001`-`ADR-0019`)
  are `Accepted`; none are `Proposed`. `PROJECT_TRACKER.md` Next Actions
  correctly lists only the MCP SDK v2 and SemVer pre-release triggers.
  `python scripts/asf.py doctor` reported `status: ok`
  (`repository_valid: true`, `schemas: true`, `langgraph: true`). Full
  validation matrix (contracts 23/23, IR 47/47, graph 14/14, semantics 4/4,
  repository 0 errors/0 warnings, core unit tests 168/168) passed.

### Day 2 — MCP SDK v2 public trigger check

- **Objective:** Determine whether MCP Python SDK v2 has shipped as a
  stable (non-prerelease) release.
- **Allowed:** Run `pip index versions mcp` (public, unauthenticated,
  read-only registry lookup — not a paid/cloud API call, not a credential).
  If still `1.x`, record "not actionable" only if that has not already been
  recorded recently. If a `2.x` stable exists, only produce an impact
  assessment/checklist — do not migrate the same day. Check
  `adapters/mcp_tools/binding.py` and its requirements file to confirm the
  real import/type surface (do not assume from memory).
- **Forbidden:** Do not change the `mcp>=1.27,<2` pin without prior
  approval/plan; do not use MCP SDK v2 live; do not edit the adapter the
  same day a trigger is first observed unless this runbook/governance
  explicitly allows it.
- **Validation:** Docs-only change -> `git diff --check` + `python
  scripts/asf.py doctor`. Real code change -> full pytest (Appendix B).
- **Stop condition:** MCP v2 appears -> stop after the impact assessment
  and report that a human decision is needed before migrating. MCP is still
  `1.x` and nothing else changed -> stop clean.
- **Status (2026-07-12, confirmed twice — Day 1 audit and a later same-day
  re-check): Not triggered.** `pip index versions mcp` reported latest
  `1.28.1` both times; no `2.x` release exists yet. Do not re-run this
  check again within the same session once it has already produced this
  result — re-check on or after 2026-07-27, or immediately if an external
  signal indicates v2 shipped, whichever is sooner.

### Day 3 — MCP adapter compatibility audit, offline only

- **Objective:** Keep a ready-made, accurate list of exactly what
  `adapters/mcp_tools/` touches in the `mcp` SDK, so a future migration
  session does not have to re-derive it from scratch once v2 is stable.
- **Allowed:** Audit static imports/usages in `adapters/mcp_tools/`,
  its requirements files, and MCP-related tests; update the compatibility
  checklist (Appendix A) if a real delta is found; add a conditional TODO
  only if governance allows.
- **Forbidden:** Do not install any MCP v2 prerelease; do not make network
  calls beyond a read-only PyPI lookup unless needed; do not write a
  speculative v2 shim.
- **Validation:** `python scripts/asf.py doctor`; MCP-related tests if any
  changed; `git diff --check`.
- **Stop condition:** No delta versus the existing checklist.
- **Status (2026-07-12): Prepared.** See Appendix A. Current SDK surface is
  exactly one import (`mcp.types`) and one type (`types.Tool`); no
  `FastMCP`/`MCPServer` reference exists anywhere in adapter source (only in
  a requirements-file comment describing the *rationale* for the pin) —
  meaning the specific rename ADR-0013/the pin comment warns about may not
  even affect this adapter's actual migration surface.

### Day 4 — SemVer pre-release trigger check

- **Objective:** Determine whether any repository artifact has adopted a
  real pre-release SemVer version (e.g. `1.2.3-alpha.1`, `2.0.0-rc.1`).
- **Allowed:** Grep `*.yaml`/`*.yml`/`*.json` artifact `version:` fields for
  a `-(alpha|beta|rc)` pre-release suffix. If nothing is found, record "not
  actionable" only if that has not already been recorded recently. If a
  real pre-release version is found, analyze impact/test cases only.
- **Forbidden:** Do not implement a comparator without real data; do not
  create a fake version anywhere in source just to trigger work; do not
  change semantics without a real failing/expected test.
- **Validation:** `python scripts/asf.py doctor`. Full pytest only if
  code/tests changed.
- **Stop condition:** No real pre-release version exists.
- **Status (2026-07-12, confirmed twice — Day 1 audit and a later same-day
  re-check): Not triggered.** No `version:` field anywhere in the
  repository matches a pre-release suffix. `version_ir.py`'s documented
  (major, minor, patch)-only comparison remains the correct, non-speculative
  behavior. Do not re-run this grep again within the same session once it
  has already produced this result.

### Day 5 — Test/documentation readiness audit

- **Objective:** Confirm `docs/guides/VALIDATION_GUIDE.md` and Appendix B
  below still name the real, current validation commands with no drift
  against `scripts/`, and that the docs are explicit about when a quick
  check suffices versus when the full matrix is required.
- **Allowed:** Check the command matrix in Appendix B; confirm the docs
  distinguish quick vs. full validation; update the runbook if a real
  command is missing; re-run the documented commands to confirm they still
  work.
- **Forbidden:** No production behavior change; no new dependency.
- **Validation:** Run the documented validation commands; `git diff
  --check`.
- **Stop condition:** Docs are already sufficient and commands run clean.
- **Status (2026-07-12): Confirmed current, no change needed.**
  `docs/guides/VALIDATION_GUIDE.md` is Version 0.8, last updated 2026-07-12
  (Sprint 43), and its documented commands were all re-run today with
  matching results (Appendix B). This session additionally verified and
  documented that a bare root-level `python -m pytest` fails at collection
  (see "How to Use This Document" above) — a real command-accuracy gap that
  is now closed by that note rather than left for a future session to
  rediscover the hard way.

### Day 6 — Tracker/context consistency

- **Objective:** Keep `PROJECT_TRACKER.md`, `PROJECT_CONTEXT.md`, and this
  runbook mutually consistent; ensure Next Actions holds only items that
  are genuinely still waiting on a real signal.
- **Allowed:** Synchronize the three documents; remove or mark stale any
  Next Action that has actually been completed; confirm Next Actions holds
  only real pending-signal items.
- **Forbidden:** Do not change a status without evidence; do not mark
  something actionable when its trigger has not fired.
- **Validation:** `python scripts/asf.py doctor`; `git diff --check`; full
  pytest only if doc tooling requires it.
- **Stop condition:** Tracker/context are already consistent.
- **Status (2026-07-12): Confirmed current, no change needed.** Next
  Actions accurately lists only the two open triggers; the ADR-acceptance
  Revision History entries (`PROJECT_TRACKER.md` and `PROJECT_CONTEXT.md`)
  already record 2026-07-12's decisions without altering earlier entries.

### Day 7 — Weekly closeout

- **Objective:** Summarize Week 1's findings and hand off a short, concrete
  status for whoever picks up Week 2.
- **Allowed:** Compile a summary from Days 1-6; record MCP trigger status,
  SemVer trigger status, validation status, and the next valid re-check
  date/condition; commit docs-only if something real changed.
- **Forbidden:** Do not start a new migration at week's end without a real
  trigger/governance basis; do not invent backlog without evidence.
- **Validation:** Full validation per Appendix B; `git diff --check`.
- **Stop condition:** Week 1 complete, no actionable external trigger.
- **Status (2026-07-12): Complete.** This session's audit covered Days 1-6
  in a single pass because both triggers resolved to "not yet" on first
  check and no code work was authorized; a later same-session pass
  re-confirmed both triggers unchanged without repeating the check a third
  time. Next scheduled full re-check: on or before 2026-07-19, or
  immediately if either trigger fires sooner (MCP v2 stable release, or a
  pre-release version appearing in any artifact).

## Week 2 — Conditional Implementation Window

Goal: if a real trigger has fired, prepare and — only where governance
allows — implement against it. If a trigger has not fired, do only
documentation maintenance and light audit, then stop clean. Every day below
is written as two branches: what is allowed if its named trigger fired, and
what is allowed (much less) if it did not. Do not skip straight to the
"fired" branch without independently re-confirming the trigger this
session; do not skip the "not fired" branch's stop instruction just because
Week 2 sounds more permissive than Week 1 — it is only conditionally so.

### Day 8 — Re-check gate

- **Objective:** Re-establish ground truth on both triggers before any
  Week 2 planning/implementation day proceeds.
- **Allowed:** Re-run the MCP and SemVer trigger checks; compare against
  the most recent recorded result in this document. If the result is
  unchanged **and** the last check was not within the same session/recent
  minutes, record that. If the last check was within the same session with
  a certainly-unchanged result, do not re-run it — just cite the existing
  Status line above.
- **Forbidden:** Do not repeat the same check multiple times within
  minutes; do not spend quota on a no-op loop.
- **Validation:** No full validation needed if no file changed. If docs
  changed: `git diff --check` + `python scripts/asf.py doctor`.
- **Stop condition:** Trigger state unchanged from the most recent record.
- **Status: Gate, evaluated per-session — see the Day 2 / Day 4 Status
  lines above for the most recent recorded result before treating this day
  as due.**

### Day 9 — MCP v2 migration planning, only if trigger fired

- **Allowed if MCP 2.x stable exists (re-confirmed this session, not from
  memory):** Produce an impact assessment; list the real files affected
  (start from Appendix A); list tests that need adding/changing; propose a
  small, reversible migration sequence. Do not migrate the production
  adapter if governance requires human review first.
- **Allowed if MCP has not fired:** Record "not actionable" only if due for
  a re-check per Day 8; otherwise stop clean without writing anything.
- **Forbidden:** Do not bump the dependency without approval; do not
  migrate the same day a trigger is first observed if this runbook says
  not to (it does — see Day 2).
- **Validation:** Docs-only validation, or full pytest if a test actually
  changed.
- **Stop condition:** A human decision is needed (dependency bump,
  migration timing, or backward-compatibility policy).

### Day 10 — MCP compatibility tests, only if approved/actionable

- **Allowed:** Only if governance has approved and the trigger has fired:
  add or adjust tests that exercise compatibility at the offline level,
  using mocks/local fixtures — never a live external MCP service call.
  Only touch adapter source after a real failing test or a documented
  compatibility break exists.
- **Forbidden:** No live connection to an external MCP service; no new
  paid/cloud dependency; do not drop 1.x support without a plan.
- **Validation:** MCP-related tests; full pytest (Appendix B); `python
  scripts/asf.py doctor`; `git diff --check`.
- **Stop condition:** Tests fail for an unclear reason; a decision about
  backward compatibility is needed.

### Day 11 — SemVer implementation planning, only if trigger fired

- **Allowed if a real pre-release version exists (re-confirmed this
  session):** Collect the file(s) that actually carry the pre-release
  version; write expected-ordering test cases from that real data; update
  the plan/test matrix; add failing tests first if governance allows.
- **Allowed if no pre-release version exists:** Stop clean.
- **Forbidden:** Do not create a fake production version to manufacture a
  trigger; do not implement a comparator without a real test built from
  real data.
- **Validation:** Semantic tests if any exist; full pytest if code/tests
  changed.
- **Stop condition:** No real data exists; a human decision on precedence
  policy is needed.

### Day 12 — SemVer comparator/test work, only if approved/actionable

- **Allowed:** Implement a small, test-first change scoped strictly to the
  comparator/semantics involved, only if real pre-release data already
  exists (Day 11) and governance has not raised an objection; update docs
  if behavior changes.
- **Forbidden:** No large refactor; no change to unrelated validation
  behavior.
- **Validation:** Semantic tests; contract/IR/graph tests if related; full
  pytest (Appendix B); `python scripts/asf.py doctor`; `git diff --check`.
- **Stop condition:** A behavior ambiguity needs a human decision.

### Day 13 — Documentation consolidation

- **Allowed:** Update the runbook, tracker, and context with real results;
  fold in new lessons; make sure the next-session prompt is short, clear,
  and reusable; remove real duplication.
- **Forbidden:** No large unnecessary doc rewrite; never change a
  historical record to say something that was not true at the time.
- **Validation:** `python scripts/asf.py doctor`; link/path checks if
  applicable (`python scripts/validate_repository.py`); `git diff --check`;
  full pytest only if doc validation requires it.
- **Stop condition:** Docs are already consistent.

### Day 14 — Two-week closeout

- **Allowed:** Summarize the full two weeks — work done, which trigger(s)
  fired or did not, validation results, remaining Next Actions, and a short
  prompt for the next session. If no trigger fired at all, say plainly that
  the repository is in a clean stop waiting on an external signal.
- **Forbidden:** Do not open a new sprint without a real basis; no
  speculative code on closeout day.
- **Validation:** Full validation per Appendix B; `git diff --check`.
- **Stop condition:** Clean closeout.

## Appendix A — MCP Adapter (`adapters/mcp_tools/`) v1-to-v2 Compatibility Checklist

Prepared 2026-07-12, before any v2 release, so a future migration session
has a verified starting point instead of re-deriving adapter scope from
scratch. This is the reference Day 3 maintains and Day 9/Day 10 consume if
the MCP trigger ever fires.

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
`adapters/README.md` for why they cannot be collected together; a bare
root-level `python -m pytest` fails at collection for exactly this reason,
verified 2026-07-12):

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
`python scripts/asf.py doctor` is a fast read-only health summary, not a
substitute for this matrix — use it for a quick sanity check between full
runs, not as the sole validation before a commit.

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
| 0.2 | 2026-07-12 | Extended in place to a two-week guarded operator plan: regrouped Days 1-7 under Week 1 (Guarded Trigger Monitoring & Readiness, unchanged findings), added Days 8-14 under Week 2 (Conditional Implementation Window — planning/implementation only if a trigger has actually fired, otherwise the same read-only check-and-stop behavior); documented that a bare root-level `python -m pytest` fails at collection and must not be used or reported as a validation failure |
| 0.3 | 2026-07-12 | Added a pointer to the new `docs/guides/MONTHLY_OPERATOR_PLAN.md`, the month-scoped roadmap above this file covering content-skill readiness (golden samples, benchmark, integration readiness) with its own separate triggers; this document's own scope (MCP SDK v2, SemVer pre-release) is unchanged |
