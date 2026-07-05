# Content Structures

- **Knowledge ID:** `kb:creative:content:formats:content-structures`
- **Status:** Active
- **Category:** `creative`
- **Domain:** `content`
- **Topic:** `formats`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines the minimum useful structure for each deliverable supported by Content
Creation v1. Retrieve it when selecting sections and packaging a content draft.

## Applies To

- skill:content-creation
- workflow:content-brief-to-package

## Scope

### Includes

- Short video scripts, social posts, article outlines, caption and hashtag sets,
  and title and thumbnail idea sets.
- Required components and practical completeness checks for each format.

### Excludes

- Platform limits, tone selection, factual research, media production, and
  publishing.

## Guidance

Every deliverable has one primary message and one audience action.

For a `short-video-script`, provide an opening hook, beat-by-beat spoken or
on-screen content, a closing action, and production notes. Keep each beat
performable and mark visual directions separately from spoken words.

For a `social-media-post`, provide an opening line, a scannable body, a closing
action, and optional platform-appropriate formatting. Each paragraph should do
one job: establish relevance, deliver value, support the message, or close.

For an `article-outline`, provide a working title, audience promise, thesis,
ordered section headings, section purpose and supporting points, introduction
and conclusion intent, and the desired action. An outline is not a compressed
draft; it must expose the argument's sequence and evidence gaps.

For `caption-hashtags`, provide one complete caption, a closing action, and a
small relevant hashtag set. Hashtags must describe the subject, audience, or
content category and must not introduce unsupported claims.

For `title-thumbnail-ideas`, provide at least three paired concepts. Each pair
contains a title, short thumbnail text or visual premise, the curiosity or value
promise, and a note showing how the content fulfills that promise. Title and
thumbnail must complement rather than repeat each other.

## Decision Rules

1. If the content type is a short video, separate spoken copy from visual or
   editing notes.
2. If the content type is an article outline, identify missing evidence inside
   the relevant section instead of inventing support.
3. If the content type requests hashtags, prefer a small specific set over a
   broad popularity-driven list.
4. If the content type requests ideas, return paired, meaningfully distinct
   concepts rather than cosmetic rewrites.
5. If a required component cannot be completed from the brief, label the gap
   and route it to human review.

## Examples

### Good Example

A short video package has a two-line hook, three numbered beats with spoken
copy, one closing action, and separate notes for on-screen text. A supplied
product fact appears in the script and no additional performance claim is made.

### Counterexample

A title-idea request returns ten near-identical headlines without thumbnail
premises, fulfillment notes, or any distinction in audience promise.

## Limitations and Risks

- Structural completeness does not guarantee that a factual claim is true.
- Exact length and feature availability may change by platform and require
  current human verification.
- A single package does not replace editorial, legal, accessibility, or brand
  review.

## Related Knowledge

## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Content Creation v1 structures. |
