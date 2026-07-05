# Publishing Constraints

- **Knowledge ID:** `kb:creative:content:platforms:publishing-constraints`
- **Status:** Active
- **Category:** `creative`
- **Domain:** `content`
- **Topic:** `platforms`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines stable, non-numeric adaptation rules for the platforms supported by
Content Creation v1. Retrieve it to package a draft appropriately while
recognizing that exact platform limits and policies change.

## Applies To

- skill:content-creation
- workflow:content-brief-to-package

## Scope

### Includes

- Generic, Instagram, LinkedIn, TikTok, and YouTube packaging guidance.
- Placement, scanability, visual context, and policy-change safeguards.

### Excludes

- Current numeric limits, algorithm optimization claims, paid advertising,
  account configuration, publishing APIs, and legal compliance.

## Guidance

For `generic`, use a portable structure, avoid platform-only features, and state
which publishing decisions remain open.

For `instagram`, make the opening useful before any truncation, use short
paragraphs, ensure the caption adds context beyond the visual, and keep hashtags
specific. Provide alt-text intent in production notes when visuals matter.

For `linkedin`, lead with a professional relevance signal, use whitespace for
scanability, support lessons with concrete experience or supplied facts, and
avoid manufactured vulnerability or engagement bait.

For `tiktok`, make the first spoken or visual beat immediately legible, write
performable short lines, identify on-screen text separately, and ensure the
content fulfills the opening promise quickly.

For `youtube`, align title, thumbnail premise, opening, and delivered value.
Avoid title-thumbnail pairs that imply evidence, results, or conflict absent
from the content. For Shorts, use the short-video structure; for long-form
ideas, expose the content's progression in production notes.

Exact character limits, feature availability, policy requirements, and
recommended technical specifications must be verified against current official
platform documentation before publishing.

## Decision Rules

1. If platform is generic, do not assume hashtags, thumbnails, or platform-only
   interaction patterns.
2. If a platform-dependent numeric limit was not supplied and verified, avoid
   claiming exact compliance and flag it for pre-publication review.
3. If visual context carries meaning, include an accessibility or alt-text note.
4. If a hook or title promises a result, verify that the body directly delivers
   that result.
5. If platform norms conflict with factual integrity or audience trust, preserve
   integrity and document the tradeoff.

## Examples

### Good Example

A TikTok script starts with a clear problem in the first beat, separates spoken
copy from on-screen words, uses three short beats, and notes that final duration
must be checked after recording.

### Counterexample

A LinkedIn post invents a personal failure story for relatability, asks readers
to comment a single word for reach, and claims the format “beats the algorithm.”

## Limitations and Risks

- Platform capabilities, policies, and limits change; this document deliberately
  avoids volatile numeric claims.
- Platform fit is not a promise of distribution or engagement.
- Publishing still requires current policy, accessibility, brand, and legal
  review where applicable.

## Related Knowledge

## Sources

- None - repository-authored stable guidance; verify volatile constraints with
  current official platform documentation before publishing

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Content Creation v1 platform guidance. |
