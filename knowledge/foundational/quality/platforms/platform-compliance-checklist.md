# Platform Compliance Checklist

- **Knowledge ID:** `kb:foundational:quality:platforms:platform-compliance-checklist`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `quality`
- **Topic:** `platforms`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines stable platform-fit checks while requiring volatile limits and policies
to remain unverified unless supplied by the caller.

## Applies To

- skill:review-quality
- workflow:draft-to-reviewed-package

## Scope

### Includes

- Packaging, scanability, opening, CTA, length intent, pacing intent,
  accessibility notes, and platform-specific constraint traceability.

### Excludes

- Live platform policy lookup, current feature availability, rendered media
  inspection, and account-specific enforcement.

## Guidance

For `generic`, require a self-contained structure without platform-only
assumptions. For LinkedIn, review professional context, scanability, and a
discussion-appropriate CTA. For Instagram, review caption readability, relevant
hashtags, and separation of visual assumptions. For TikTok and YouTube, review
performable openings, spoken-versus-visual directions, pacing intent, and
promise fulfillment.

Treat exact character counts, duration limits, feature availability, policies,
and algorithm claims as volatile. Check them only when a caller supplies the
rule and provenance; otherwise mark them for current human verification.

## Decision Rules

1. A declared caller constraint is reviewable; an assumed current limit is not.
2. Platform fit never excuses unsupported claims or deceptive hooks.
3. Mark recorded duration and visual accessibility not-assessable without the
   rendered artifact.
4. Require one clear CTA appropriate to both platform and objective.
5. Distinguish stable packaging guidance from policy compliance.

## Examples

### Good Example

A TikTok script passes structural pacing review while recorded duration remains
an unresolved verification item.

### Counterexample

A review invents a current platform character limit and rejects the draft.

## Limitations and Risks

- Platform behavior and policies change and require current official review.
- Text-only review cannot verify visuals, captions, audio, or final timing.

## Related Knowledge

## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Review Quality v1 platform checklist. |
