# ADR-0019: Local Markdown Publishing

- **Status:** Proposed
- **Date:** 2026-07-12
- **Decision owners:** Project maintainers

## Context

`publisher_adapters` compiles `ExportDescriptor` values for five targets but
does not execute `PublisherAdapter.publish`. Platform targets require accounts,
credentials, uploads, and external side effects that are outside the approved
scope. The existing `markdown` target can be made real through a bounded local
filesystem export with no credential or network dependency.

## Options

### Add platform SDKs

Rejected for this sprint. YouTube, TikTok, Facebook, and WordPress require
credentials and external upload/publish authority that has not been granted.

### Return rendered Markdown without writing it

Rejected. That remains another descriptor/preview half and would be a stub
disguised as `publish` rather than a real target side effect.

### Publish Markdown to a caller-owned local root

Selected. Python's filesystem primitives are the mature execution target;
PyYAML serializes front matter. No platform client or custom transport is
needed.

## Decision

Implement `PublisherAdapter.publish` for `target == "markdown"` only. The
adapter receives an explicit output root at construction and:

1. derives a safe deterministic filename from the descriptor title;
2. resolves and verifies the destination remains inside the output root;
3. serializes optional front matter with `yaml.safe_dump` and appends the body;
4. creates the file exclusively by default, refusing silent overwrite;
5. returns an immutable result with target, absolute path, and UTF-8 byte
   count.

All platform targets fail before filesystem mutation. The caller may opt into
overwrite explicitly for an already-reviewed local export; no default changes
or platform side effects are implied.

## Build vs Reuse

Python owns path/filesystem semantics and PyYAML owns YAML serialization. ASF
builds only the bounded mapping from its `ExportDescriptor` to a safe Markdown
file/result. There is no scheduler, upload client, CMS SDK, credential store,
or general template engine in this adapter.

## Consequences

- Markdown descriptors now have a real credential-free target.
- Platform descriptors remain useful for planning but fail closed in the
  execute half until separately approved SDK/credential work exists.
- Title-derived filenames are intentionally simple and may collide; exclusive
  create turns collisions into explicit errors rather than silent data loss.
- Local file creation is a real side effect and must only target a caller-owned
  directory.

## Validation Plan

- Unit-test real UTF-8 file creation, deterministic front matter/body, safe
  filenames, root containment, exclusive-create behavior, explicit overwrite,
  blank-slug rejection, and platform fail-closed behavior before mutation.
- Run the complete publisher adapter suite and all mandatory repository
  validations.

## Rollback Plan

Remove the publisher module/exports/tests and PyYAML requirement. Existing
descriptors and binding functions remain unchanged. Any files already created
are caller-owned outputs and are removed only by the caller; rollback code must
not delete arbitrary export roots.

## Related Documents

- ADR-0013
- ADR-0015
- `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`
- `adapters/publisher_adapters/descriptors.py`

