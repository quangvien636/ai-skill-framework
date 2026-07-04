# Knowledge Categories

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define the canonical top-level categories for reusable knowledge. This file owns
category identifiers and boundaries; it does not duplicate topic content or index
individual documents.

## Category Registry

| ID | Category | Includes | Excludes |
| --- | --- | --- | --- |
| `foundational` | Foundational | Cross-domain reasoning, communication, research, and general quality principles | Framework governance and domain-specific practice |
| `technical` | Technical | Software engineering, data, infrastructure, security, and computing technologies | Product strategy and organization policy |
| `product` | Product | Product discovery, strategy, design, delivery, and measurement | General writing and implementation-specific engineering |
| `business` | Business | Operations, finance, marketing, sales, and organizational practices | Product-specific delivery and technical implementation |
| `creative` | Creative | Writing, storytelling, visual communication, and content craft | General communication principles and product design |
| `compliance` | Compliance | Legal, regulatory, privacy, safety, and policy knowledge requiring explicit governance | General security implementation and non-normative ethics discussion |

## Selection Standard

Choose the category that owns the subject's primary body of knowledge, not the
category of the Skill consuming it. A technical writing Skill, for example, may
consume both `technical` and `creative` documents without creating a hybrid
category.

Use this decision order:

1. Is the subject a governed legal, regulatory, privacy, safety, or policy
   obligation? Use `compliance`.
2. Is it primarily about computing systems or software practice? Use `technical`.
3. Is it primarily about discovering, designing, delivering, or measuring a
   product? Use `product`.
4. Is it primarily about operating or growing an organization? Use `business`.
5. Is it primarily a creative craft or content form? Use `creative`.
6. Is it reusable across domains and none of the above owns it? Use
   `foundational`.

When a subject spans categories, keep one canonical document under its primary
category and link to it from related documents or consumers. Do not copy it.

## Adding or Changing a Category

A proposal must:

- show that no existing category can own the subject without ambiguity;
- define its inclusion and exclusion boundaries;
- identify expected domains and cross-category effects;
- update the Knowledge Architecture, this registry, and affected index entries;
- receive architecture review before merge.

Renaming, merging, or removing a category is an architectural change and may
require an ADR when it changes established decisions or compatibility.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the initial category registry |
