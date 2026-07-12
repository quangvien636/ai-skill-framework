# Golden Sample Intake Plan

Version: 0.1
Status: Active
Last updated: 2026-07-12

This is the Week 2 deliverable of `docs/guides/MONTHLY_OPERATOR_PLAN.md`.
It is a **plan and schema only**: no golden sample has been ingested, no
external content has been fetched, and no directory for storing samples
has been created. Content Trigger A (a real sample provided by an
operator) is what turns this plan into practice, not this document itself.

## 1. Purpose

- Let an operator hand over a video, link, transcript, or other sample
  content in a simple, low-friction way.
- Ensure the AI Skill only ever learns **abstract patterns** from a
  reference — never copies its wording, structure, or identity.
- Standardize the review step a sample goes through before it is ever
  treated as a golden/reference example.
- Prepare the input side of Week 3's `docs/guides/
  CONTENT_BENCHMARK_PLAN.md` — a benchmark is only as trustworthy as the
  references it is scored against.

## 2. Supported Input Types

- A full transcript the operator supplies directly.
- A content summary the operator supplies directly.
- A video link accompanied by the operator's own manual description.
- A local file the operator has already provided and has the rights to
  share.
- A human-approved script/video output produced by this project itself
  (e.g. a reviewed `content-package` from `skill:content-creation` /
  `skill:review-quality`).

Explicit limits:

- **A bare link is not sufficient to analyze** unless it comes with a
  public transcript, caption text, or the operator's own written evidence.
  This plan does not treat "watch the video" as an available capability.
- **No content is scraped or downloaded on the assumption of permission.**
  Only content the operator has explicitly supplied, or explicitly
  confirmed the rights to share, is in scope.
- **A link with no readable content is `INSUFFICIENT_EVIDENCE` by
  definition** — not a prompt to guess at what the video probably
  contains.

## 3. Minimal Operator Input Template

```text
Reference input:

Source:
<link or file path>

Nội dung chính:
<what the video is about, 2-5 lines>

Vì sao hay:
<strong hook / good retention / good example / strong emotional pull>

Muốn AI Skill học:
<opening technique, pacing, structure, visual style, emotional arc...>

Không được copy:
<specific names, exact wording, specific examples, distinctive structure...
if any>
```

This is intentionally short. An operator who only fills in `Source` and
`Nội dung chính` still produces a submission this plan can classify — most
likely as `INSUFFICIENT_EVIDENCE` if that is all the evidence available
(see Section 4).

## 4. Review Gates

Every submission resolves to exactly one of three verdicts:

**`APPROVED`**

- Evidence is sufficient (a transcript, summary, or the operator's own
  detailed description — not just a bare link).
- A pattern can be described at an abstract level (see Section 5).
- No unresolved copying/copyright risk (see Section 6).
- Both `what_can_be_learned` and `what_must_not_be_copied` are filled in
  explicitly — an `APPROVED` record with either field empty is invalid.

**`REJECTED`**

- Content is off-topic for the content-skill domain.
- Copying risk is too high to reduce to a safe abstract pattern.
- Quality is low or the content is misleading.

**`INSUFFICIENT_EVIDENCE`**

- Only a link exists, with no transcript or sufficient description.
- A public page cannot actually be read/verified.
- There is not enough material to describe hook, structure, or pacing
  concretely.
- **A pattern must never be guessed when evidence is insufficient** — this
  is the default, safe outcome when in doubt, not a failure state to
  avoid.

## 5. What Can Be Learned

- Hook type.
- Narrative structure.
- Pacing pattern.
- Emotional arc.
- Retention mechanism.
- Topic framing.
- Visual/caption style, at an abstract level only.
- CTA style, restricted to safe/generic forms.
- Audience promise.
- Contrast/tension pattern.

## 6. What Must Not Be Copied

- Exact wording.
- Overly specific examples.
- Character/brand names, unless structurally necessary.
- Scene order that closely mirrors the original.
- Distinctive jokes/catchphrases.
- Recognizable visual identity or caption style.
- Unverified claims.
- Copyrighted content.
- Misleading content.

## 7. Proposed Metadata Fields

| Field | Type | Description |
| --- | --- | --- |
| `sample_id` | string | Stable identifier for the record. |
| `source_type` | enum | One of the Section 2 supported input types. |
| `source_uri_or_path` | string | Link or local path the operator supplied. |
| `topic_domain` | string | Content domain (e.g. cooking, fitness, tech explainer). |
| `content_summary` | string | Short operator-supplied summary of what the reference contains. |
| `why_it_works` | string | Operator's stated reason the reference is worth learning from. |
| `what_can_be_learned` | list[string] | Abstract patterns, drawn from Section 5's vocabulary. |
| `what_must_not_be_copied` | list[string] | Specific risks, drawn from Section 6's vocabulary. |
| `evidence_status` | enum | `sufficient` \| `insufficient`. |
| `review_status` | enum | `APPROVED` \| `REJECTED` \| `INSUFFICIENT_EVIDENCE`. |
| `reviewer` | string | Who (human or session) made the review call. |
| `created_at` | date | When the record was first submitted. |
| `updated_at` | date | When the record was last reviewed/changed. |
| `risk_notes` | string | Free-text notes on any copying/copyright concern found. |
| `benchmark_eligible` | boolean | `true` only if `review_status == APPROVED`. |

## 8. Schema/Artifact Placement Recommendation

The repository was audited for an existing convention before proposing a
new one. Findings:

- `knowledge/` is schema-validated, IR-extracted, production Knowledge
  content authored *for* Skills to consume as guidance — semantically the
  wrong place for raw external reference material, and mixing the two
  would risk `what_must_not_be_copied` content entering a path designed
  for content Skills are meant to draw directly from.
- `runs/` holds `adapters/ollama_execution`'s own execution reports (e.g.
  `runs/content-workflow-<id>/`) — not reference input.
- `tools/` holds Tool contracts (e.g. `tools/read-file/`) — unrelated.
- `docs/references/` exists but holds internal documentation (currently
  just `GLOSSARY.md`), not external content samples.
- Top-level `assets/`, `examples/`, `prompts/`, `src/`, and `changelog/`
  all exist but are **completely empty** with no README or documented
  purpose (confirmed by directory scan 2026-07-12) — building on an
  unexplained empty directory would itself be a speculative choice, not a
  real convention.

**Recommendation, not yet acted on:** when Content Trigger A actually
fires, create `references/golden-samples/<sample_id>/` holding one
metadata file per sample (the Section 7 fields, likely YAML for
consistency with every other artifact in this repository) plus the
operator-supplied text itself. This is a plan for that moment, not a
directory created now — per this plan's own governance rule (Section 11
and the Monthly Plan's Section 5), schema/checklist work is appropriate
today; creating storage for data that does not exist yet is not.

## 9. Intake Workflow

1. Operator supplies a reference using the Section 3 template.
2. The reviewing session checks evidence sufficiency.
3. The reviewing session classifies the submission `APPROVED`,
   `REJECTED`, or `INSUFFICIENT_EVIDENCE`.
4. If `APPROVED`, extract the abstract pattern(s) only.
5. Record `what_can_be_learned` explicitly.
6. Record `what_must_not_be_copied` explicitly.
7. Only `APPROVED` samples are ever benchmark-eligible or used for
   pattern learning.
8. No sample, regardless of verdict, is ever used to copy content
   directly.

## 10. Relationship to Benchmark Plan

- Golden Sample Intake is the input side of Week 3's `docs/guides/
  CONTENT_BENCHMARK_PLAN.md`.
- Only `APPROVED` samples (`benchmark_eligible: true`) are usable there.
- The benchmark must never claim AI Skill output is better than Claude/
  Anthropic output without real evidence backing that claim.
- Minimum sample counts for a meaningful benchmark (to be confirmed/
  refined when Week 3 is written):
  - Minimum 3 `APPROVED` samples for a smoke-test-level benchmark.
  - 10-20 `APPROVED` samples recommended before treating any result as
    early confidence.
  - Never call the pipeline "production-ready" on fewer samples than that,
    regardless of how strong an early result looks.

## 11. Stop Conditions

Stop and do not proceed if:

- Evidence is not clearly sufficient.
- The input carries a copyright/copying risk that cannot be resolved to a
  safe abstract pattern.
- Human approval is required and has not been given.
- The repository is not clean.
- Validation is red.
- The work would require scraping or downloading content without
  permission.
- A task asks to ingest a real sample but the operator has not actually
  provided one.

## 12. Example Records

These are fictional, generic illustrations for reviewers to calibrate
against — none reference a real video, creator, or brand.

**Example — `APPROVED`**

```yaml
sample_id: "sample-0001"
source_type: "transcript"
source_uri_or_path: "operator-provided transcript, cooking-domain short video"
topic_domain: "cooking"
content_summary: >
  A 45-second short opens on a visible time-pressure problem ("dinner in
  10 minutes"), states one ingredient constraint, then resolves it with a
  single-pan technique shown in three quick beats.
why_it_works: "Strong hook, clear single-constraint structure, fast payoff."
what_can_be_learned:
  - "Hook type: state a time-pressure problem before naming the topic"
  - "Pacing pattern: three-beat resolution, no wasted setup"
what_must_not_be_copied:
  - "The presenter's specific on-screen text style and voice cadence"
  - "The exact ingredient list used as the running example"
evidence_status: "sufficient"
review_status: "APPROVED"
reviewer: "session-2026-07-12"
created_at: "2026-07-12"
updated_at: "2026-07-12"
risk_notes: "None identified; pattern is generic to the short-video format."
benchmark_eligible: true
```

**Example — `INSUFFICIENT_EVIDENCE`**

```yaml
sample_id: "sample-0002"
source_type: "video_link_with_description"
source_uri_or_path: "<link only, no transcript or caption available>"
topic_domain: "unknown"
content_summary: "Operator supplied only a link and no further description."
why_it_works: null
what_can_be_learned: []
what_must_not_be_copied: []
evidence_status: "insufficient"
review_status: "INSUFFICIENT_EVIDENCE"
reviewer: "session-2026-07-12"
created_at: "2026-07-12"
updated_at: "2026-07-12"
risk_notes: "No transcript, caption, or operator description available; cannot analyze without guessing."
benchmark_eligible: false
```

**Example — `REJECTED`**

```yaml
sample_id: "sample-0003"
source_type: "content_summary"
source_uri_or_path: "operator-provided summary"
topic_domain: "finance"
content_summary: >
  Summary describes a short built entirely around a specific,
  unverifiable investment-return claim attributed to a named product.
why_it_works: "Operator noted high engagement, not a content-pattern reason."
what_can_be_learned: []
what_must_not_be_copied:
  - "The unverified return claim itself"
  - "The named product/brand"
evidence_status: "sufficient"
review_status: "REJECTED"
reviewer: "session-2026-07-12"
created_at: "2026-07-12"
updated_at: "2026-07-12"
risk_notes: "Core value of the reference is an unverifiable claim; no safe abstract pattern remains once that is excluded."
benchmark_eligible: false
```

## Related Documents

- `docs/guides/MONTHLY_OPERATOR_PLAN.md` (Section 4, Week 2 — this
  document is that week's deliverable)
- `docs/guides/CONTENT_SKILL_READINESS.md` (Week 1's audit; this plan
  exists because that audit found no golden-sample intake path)
- `skills/content-creation/skill.yaml` (the evaluation contract Week 3's
  benchmark will eventually need to execute against `APPROVED` samples)
- `knowledge/README.md` (the structurally-similar but semantically
  different Knowledge Base, ruled out in Section 8)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Established the Golden Sample Intake Plan: supported input types, minimal operator template, three-verdict review gate, what-can/cannot-be-learned vocabularies, proposed metadata schema, a placement recommendation deferred until a real sample arrives, the intake workflow, its relationship to the Week 3 benchmark, stop conditions, and three fictional example records. No real sample ingested, no scraping, no storage location created |
