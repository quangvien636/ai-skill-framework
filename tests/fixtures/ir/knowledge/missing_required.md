# Index Selection

- **Knowledge ID:** `kb:technical:databases:indexing:index-selection`
- **Status:** Draft
- **Category:** `technical`
- **Domain:** `databases`
- **Topic:** `indexing`
- **Version:** 0.1.0
- **Last updated:** 2026-07-04

## Summary

Explains how to choose which columns to index based on observed query
patterns rather than guessing.

## Applies To

- skill:optimize-query

## Scope

### Includes

- Single-column and composite index selection.

### Excludes

- Storage-engine-specific index tuning.

## Guidance

Add an index only after measuring a slow query.

## Decision Rules

1. If a query filters on one column, add a single-column index.

## Examples

### Good Example

Measuring a slow query, then adding an index.

### Counterexample

Indexing every column without measuring.

## Limitations and Risks

- Extra indexes slow down writes.

## Related Knowledge

- kb:technical:databases:query-optimization:index-selection

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1.0 | 2026-07-04 | Initial draft. |
