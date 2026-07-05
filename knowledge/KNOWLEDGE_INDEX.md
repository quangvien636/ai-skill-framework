# Knowledge Index

Version: 0.3
Status: Active
Last updated: 2026-07-05

## Purpose

Provide the canonical discovery registry for Knowledge Base documents. Each
knowledge ID maps to exactly one repository path.

## How to Use This Index

- Search by ID, title, category, domain, topic, status, or summary.
- Load only documents relevant to the current Skill responsibility.
- Treat only `Active` entries as approved for normal consumption.
- Follow a deprecated entry's replacement instead of selecting it for new work.

## Registry

| Knowledge ID | Title | Category | Domain | Topic | Status | Path | Summary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `kb:creative:content:conversion:call-to-action-patterns` | Call-to-Action Patterns | creative | content | conversion | Active | `knowledge/creative/content/conversion/call-to-action-patterns.md` | Proportional patterns for choosing one clear audience action. |
| `kb:creative:content:formats:content-structures` | Content Structures | creative | content | formats | Active | `knowledge/creative/content/formats/content-structures.md` | Required structure for every deliverable supported by Content Creation v1. |
| `kb:creative:content:hooks:hook-formulas` | Hook Formulas | creative | content | hooks | Active | `knowledge/creative/content/hooks/hook-formulas.md` | Honest opening patterns that establish relevance and a fulfilled promise. |
| `kb:creative:content:platforms:publishing-constraints` | Publishing Constraints | creative | content | platforms | Active | `knowledge/creative/content/platforms/publishing-constraints.md` | Stable packaging guidance for generic, Instagram, LinkedIn, TikTok, and YouTube content. |
| `kb:creative:content:style:tone-guidelines` | Tone Guidelines | creative | content | style | Active | `knowledge/creative/content/style/tone-guidelines.md` | Observable tone and style choices for audience-appropriate content. |
| `kb:foundational:research:briefs:research-brief-structure` | Research Brief Structure | foundational | research | briefs | Active | `knowledge/foundational/research/briefs/research-brief-structure.md` | Required structure and traceability rules for a decision-useful research brief. |
| `kb:foundational:research:citations:citation-expectations` | Citation Expectations | foundational | research | citations | Active | `knowledge/foundational/research/citations/citation-expectations.md` | Minimum identity, locator, consistency, and honesty rules for citations. |
| `kb:foundational:research:evidence:claim-evidence-mapping` | Claim Evidence Mapping | foundational | research | evidence | Active | `knowledge/foundational/research/evidence/claim-evidence-mapping.md` | Atomic claim mapping to supporting, contradicting, or missing evidence. |
| `kb:foundational:research:sources:source-reliability-criteria` | Source Reliability Criteria | foundational | research | sources | Active | `knowledge/foundational/research/sources/source-reliability-criteria.md` | Explainable fitness assessment for supplied research sources. |
| `kb:foundational:research:uncertainty:uncertainty-language` | Uncertainty Language | foundational | research | uncertainty | Active | `knowledge/foundational/research/uncertainty/uncertainty-language.md` | Calibrated language for confidence, inference, disagreement, and unknowns. |
| `kb:foundational:research:verification:fact-checking-checklist` | Fact Checking Checklist | foundational | research | verification | Active | `knowledge/foundational/research/verification/fact-checking-checklist.md` | Pre-delivery checks for material claims against supplied research records. |

## Registration Rules

1. Create the document from `_templates/KNOWLEDGE_TEMPLATE.md`.
2. Validate taxonomy against `KNOWLEDGE_CATEGORIES.md`.
3. Validate names and ID against the Knowledge Naming Convention.
4. Add exactly one row, sorted lexicographically by Knowledge ID.
5. Use a repository-relative path beginning with `knowledge/`.
6. Keep the summary concise and useful for retrieval.
7. Update status, path, or summary when the canonical document changes.

The index must not contain aliases or duplicate rows. Cross-references belong in
knowledge documents; replacements are declared in the deprecated document.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the empty canonical registry |
| 0.2 | 2026-07-05 | Registered five Content Creation v1 Knowledge documents. |
| 0.3 | 2026-07-05 | Registered six Research v1 methodology documents. |
