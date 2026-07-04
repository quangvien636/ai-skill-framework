# ADR-0006: Generator Never Overwrites Content It Cannot Prove Is Its Own

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

The Generator Engine Architecture (Sprint 12) must define what happens when
a generation request targets a file that already exists. Generators in
general are prone to two opposite failure modes: silently overwriting
hand-edited content (destroying reviewed work with no warning), or refusing
to regenerate anything once a file exists (making the Generator useless for
its main purpose — filling templates for new artifacts, and later,
re-running a generator after a template changes).

Because the Git Policy in effect for this project forbids destructive
history rewrites and the repository's own governing decision (ADR-0001)
treats the repository as the sole source of truth, a Generator that
silently discards a committed, human-reviewed file's content would
undermine that guarantee even though Git technically preserves history —
contributors should not need to `git diff` every generation run to discover
what changed.

## Decision

The Generator's Overwrite Policy (`docs/architecture/GENERATOR_ARCHITECTURE.md`)
is safe-by-default and has no unsafe "always overwrite" mode:

1. Missing target path: write it.
2. Existing target path with content identical to what this exact
   template+inputs combination would render (a "safe overwrite"): treat as
   a no-op, not a write.
3. Existing target path with any other content: refuse and report a
   conflict. The Generator never has a flag that skips this check.

Identity conflicts (a requested ID/path already belongs to a different
artifact) are handled the same way: reported, never auto-resolved by
renaming.

The Generator also never promotes an artifact past `status: draft` and
never attempts partial-file (generated-region vs. hand-edited-region)
merging — both would require guessing at intent the Generator cannot
verify, so they are explicitly out of scope rather than solved unsafely.

## Consequences

### Positive

- A generation run can never silently destroy reviewed, committed content;
  the worst case is a reported conflict a human resolves.
- Regeneration after a template change is still useful: unchanged files are
  correctly recognized as a no-op instead of every re-run reporting every
  file as a conflict.
- Contributors do not need to `git diff` after every generation run to
  check for silent damage — a conflict is always surfaced explicitly.

### Costs and Tradeoffs

- There is no fast "just regenerate everything and let me review the diff"
  mode; a contributor who wants to intentionally replace a hand-edited file
  must remove or move it first, then regenerate.
- Detecting a "safe overwrite" requires the Generator to render before
  comparing, which is one extra render+diff step per existing target file
  compared to an unconditional overwrite.

## Enforcement

`docs/architecture/GENERATOR_ARCHITECTURE.md`'s Overwrite Policy and
Conflict Resolution sections MUST NOT be weakened (for example, by adding a
force-overwrite flag that skips the content-identity check) without
superseding this ADR.

## Alternatives Considered

### Always overwrite; rely on Git for recovery

Rejected because it makes silent data loss the default behavior and relies
on every contributor noticing and reverting a bad diff before it is
reviewed or merged, rather than preventing the unsafe write in the first
place.

### Add a `--force` flag that skips the safe-overwrite check

Rejected because a force flag becomes the path of least resistance under
time pressure, reintroducing the exact silent-overwrite risk this decision
exists to prevent. A contributor who truly wants to replace hand-edited
content can remove the file first, which is an explicit, reviewable action.

### Implement generated-region markers for partial-file merging

Rejected as out of scope for now: it adds real complexity (marker syntax,
merge conflict handling within a single file) for a benefit — partial
regeneration of active artifacts — that this framework's lifecycle rules
already discourage (active artifacts are edited by humans, not
regenerated).

## Related Documents

- `docs/architecture/GENERATOR_ARCHITECTURE.md`
- `docs/architecture/IR_ARCHITECTURE.md`
- ADR-0001
- ADR-0005
