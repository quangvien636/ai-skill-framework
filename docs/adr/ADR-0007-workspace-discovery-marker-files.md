# ADR-0007: Workspace Discovery Uses PROJECT_CONTEXT.md + PROJECT_TRACKER.md, Not .git

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

The CLI Design Expansion (Sprint 13) needs a concrete Workspace Discovery
rule: given a working directory anywhere under a checkout of this
repository, how does `AISkill.CLI` find the repository root so it can
resolve artifact paths and load repository configuration? The obvious
default — walk upward for a `.git` directory — is what most CLIs (npm,
cargo, git itself) already do, so it needs an explicit reason to deviate
from it.

Two considerations argue against `.git` alone: this framework's own
identity is defined by its Markdown governance documents
(`PROJECT_CONTEXT.md`, `PROJECT_TRACKER.md`), not by which VCS manages the
checkout (ADR-0001 treats the repository's content, not its VCS, as the
source of truth); and a `.git` marker would misidentify the root in a
nested-repository layout (a framework checkout vendored inside another
project's own `.git`-managed repo) or fail entirely in a non-Git checkout
(a downloaded archive, a Git-less deployment copy).

## Decision

Workspace Discovery walks parent directories from the current working
directory and selects the nearest ancestor directory containing **both**
`PROJECT_CONTEXT.md` and `PROJECT_TRACKER.md`. Requiring both files (not
either alone) avoids a false-positive match against an unrelated directory
that happens to contain a similarly-named file for some other reason.
`.git` is not consulted by Workspace Discovery.

If no such directory is found within a bounded number of parent directories,
discovery fails with a startup error naming the directory where the search
began. There is no silent fallback to the current working directory as a
pseudo-root.

## Consequences

### Positive

- The CLI works identically in a Git checkout, a nested vendored copy, or a
  Git-less archive extraction, because it depends only on this framework's
  own governance files.
- Requiring both marker files makes an accidental false-positive match
  (some unrelated directory with one similarly named file) very unlikely.
- The rule is consistent with ADR-0001: the repository's authoritative
  content, not its VCS metadata, defines the project.

### Costs and Tradeoffs

- Deviates from the common `.git`-root convention contributors coming from
  other tools may expect; this must be documented clearly in CLI help/error
  text, not just in this ADR.
- If a future restructuring ever renames or removes `PROJECT_CONTEXT.md` or
  `PROJECT_TRACKER.md`, Workspace Discovery breaks until updated — the
  marker files are now load-bearing for tooling, not just documentation.

## Enforcement

Any future CLI implementation's Workspace Discovery MUST require both
marker files, MUST NOT fall back to `.git`-based discovery as a primary
strategy, and MUST fail with an explicit error (naming the search start
directory) rather than defaulting to the current directory.

## Alternatives Considered

### Discover the workspace root via `.git`

Rejected because it is VCS-specific rather than framework-specific, breaks
for non-Git checkouts, and can misidentify the root in a nested-repository
layout where an outer `.git` belongs to a different, unrelated project.

### Require a single marker file (just `PROJECT_CONTEXT.md`)

Rejected because a single common filename is more likely to coincidentally
exist in an unrelated directory than the specific pair this framework
always creates together (per the Sprint 1 Foundation), making the pair a
cheap, effectively free extra safety check.

### Support both `.git` and marker-file discovery, preferring whichever is found first

Rejected as unnecessary complexity: it would make Workspace Discovery's
behavior depend on which check happens to run first in two different
checkout layouts, producing behavior that is harder to explain and test
than one deterministic rule.

## Related Documents

- `docs/architecture/CLI_ARCHITECTURE.md`
- ADR-0001
- ADR-0003
