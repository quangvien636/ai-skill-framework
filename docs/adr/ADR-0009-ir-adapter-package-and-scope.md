# ADR-0009: IR Adapters Live in scripts/asf_validator/, Metadata/Version Stay Embedded, New ASF-PARSE-* Prefix

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

Sprint 16 implements Validator Roadmap Phase 2: IR adapters that turn a
parsed Skill/Workflow/Knowledge/Evaluation/Reflection document into the
object model `docs/specifications/IR_SPECIFICATION.md` defines. Three
decisions are needed before writing code, none of which the existing
architecture already answers precisely enough to "just implement":

1. **Where does the code live?** The repository has an empty `src/` and an
   empty `runtime/` directory with no document claiming either for a
   specific purpose. The Sprint 8 validator prototype (ADR-0002) already
   established `scripts/` as the home for the Python fixture-conformance
   tooling, pinned to `jsonschema`/`referencing`/`PyYAML`.
2. **Do Metadata and Version get their own adapters?** The Sprint 16 brief
   lists "Skill, Workflow, Knowledge, Evaluation, Reflection, Metadata,
   Version" as artifacts needing adapters. But `docs/guides/VALIDATION_GUIDE.md`
   and `docs/roadmaps/VALIDATOR_ROADMAP.md` already state Metadata and
   Version are shared `$defs`, "not standalone repository artifacts" — there
   is no `metadata.yaml` or `version.yaml` file to parse.
3. **What diagnostic code covers a failure the IR adapter itself detects**
   (malformed YAML, an unsupported `schema_version` major, a Workflow
   `depends_on` pointing at a nonexistent step)? `CLI_ARCHITECTURE.md`'s
   Diagnostics table only allocates `ASF-SCHEMA-*`, `ASF-SEMANTIC-*`,
   `ASF-REPO-*`, `ASF-GEN-*`, and `ASF-CLI-*` — none of which cleanly owns
   "the adapter could not even build an IR object to schema-check."

Per this sprint's explicit instruction, "if the specification is
incomplete, document the gap instead of inventing behavior" — so this ADR
resolves all three before implementation, rather than choosing silently.

## Decision

1. **Location:** IR adapters live in a new Python package,
   `scripts/asf_validator/`, extending the Sprint 8 prototype's language and
   dependency footprint (ADR-0002) rather than claiming `src/`. `src/` and
   `runtime/` remain reserved and untouched — they are candidates for a
   future CLI/Runtime implementation whose language ADR-0003 explicitly
   left undecided; using them now for Python IR-adapter code would
   prejudge that decision.
2. **Metadata and Version scope:** No standalone `MetadataIR`-from-file or
   `VersionIR`-from-file adapter is implemented, because no such file
   exists. Instead:
   - `scripts/asf_validator/metadata_ir.py` exposes `extract_metadata_ir(doc)`,
     a reusable function the Skill and Workflow adapters call to pull the
     common `commonArtifact` fields into a `MetadataIR` dataclass — matching
     the IR Specification's "every Skill IR and Workflow IR includes the
     common artifact fields" description.
   - `scripts/asf_validator/version_ir.py` exposes `parse_version(str)` and
     `parse_version_range(str)`, pure functions with no file I/O, used
     wherever a version or version-range string appears.
   - Both are independently unit-tested as reusable components, satisfying
     "adapters for Metadata and Version" as *shared IR building blocks*
     rather than invented standalone artifact types.
3. **New diagnostic prefix:** `ASF-PARSE-*` is added to
   `CLI_ARCHITECTURE.md`'s Diagnostics table for failures at or before IR
   construction that no existing prefix covers: malformed source
   (`ASF-PARSE-001`), unsupported `schema_version` major
   (`ASF-PARSE-002`), a Knowledge Markdown document missing a section the
   adapter needs to normalize (`ASF-PARSE-003`), an unresolved
   within-document Workflow step reference — `depends_on`, `entrypoint`, or
   an `input_mapping`/`outputs[].from` step reference (`ASF-PARSE-004`), a
   Metadata `id`/`name` self-consistency mismatch (`ASF-PARSE-005`), and a
   cycle in a Workflow's `depends_on` graph (`ASF-PARSE-006`). This is an
   additive table row, not a redefinition of the four existing prefixes or
   of what "valid" means.

### Scope Boundary Made Explicit

The Knowledge Markdown adapter requires all ten canonical `##` sections
(Summary, Applies To, Scope, Guidance, Decision Rules, Examples,
Limitations and Risks, Related Knowledge, Sources, Revision History) and
all seven metadata bullets (Knowledge ID, Status, Category, Domain, Topic,
Version, Last updated) to be physically present to normalize a document at
all (`ASF-PARSE-003` if one is missing) -- this is a parsing-completeness
check, not the deeper "Knowledge ID/taxonomy/path agreement and required
Markdown sections" semantic rule `CONTRACT_VALIDATION_ARCHITECTURE.md`
lists under Phase 3. Cross-file checks (does this ID appear in the
Knowledge Index, does the category/domain/topic match the file's actual
path) remain unimplemented Phase 3/4 work.

The Workflow IR adapter builds and validates the step graph described by
`IR_SPECIFICATION.md`'s Workflow IR section (resolved step IDs, acyclic
dependency graph) because the specification already names this as part of
Workflow IR, not a Phase 3 semantic rule. It does **not** resolve
cross-artifact references (a Skill ID inside a Workflow step, a Knowledge
ID inside a Skill's dependencies) against the rest of the repository — that
is the Dependency Graph, explicitly Phase 3/4 work, and remains
unimplemented after this sprint. An IR adapter builds one artifact's IR
from its own document only.

## Consequences

### Positive

- No new dependency, language, or top-level directory is introduced; the
  change is additive to an already-accepted decision (ADR-0002).
- Metadata/Version are testable, reusable units without a fictional file
  format being invented for them.
- Future adapters (a Generator IR adapter, a Runtime loader) have one place
  to import from (`scripts/asf_validator`) instead of duplicating parsing.

### Costs and Tradeoffs

- `scripts/asf_validator/` growing into a real package means `scripts/`
  is no longer "one script plus one wrapper" (ADR-0002's original shape);
  future contributors should expect a package there, not a single file.
- The `ASF-PARSE-*` prefix sits logically "before" `ASF-SCHEMA-*` in the
  pipeline but was allocated after it numerically in the table; this is a
  cosmetic ordering inconsistency accepted rather than renumbering
  existing, already-referenced prefixes.

## Enforcement

Any future code that parses a Skill/Workflow/Knowledge/Evaluation/
Reflection document MUST go through `scripts/asf_validator`'s existing
loader/adapters rather than re-implementing parsing, per the IR
Architecture's "one IR, many consumers" rule (ADR-0005). A new artifact
kind's adapter MUST follow the same `(ir_or_none, diagnostics)` return
shape established here.

## Alternatives Considered

### Put IR adapters in `src/`

Rejected because no document claims `src/` for Python tooling specifically,
and doing so now would informally decide the future CLI/Runtime's language
is Python before ADR-0003's deferred decision is actually made.

### Invent a `metadata.yaml` / `version.yaml` file format to adapt

Rejected because it contradicts the already-documented fact that Metadata
and Version are shared `$defs`, not standalone artifacts — inventing a file
format for them would be exactly the kind of "invented behavior" this
sprint's instructions ask to avoid.

### Reuse `ASF-SCHEMA-*` for all pre-schema-validation failures

Rejected because it would make `ASF-SCHEMA-*` mean two different things
(the document doesn't parse at all vs. the document parses but fails
Draft 2020-12 validation), reducing a Reporter's ability to distinguish
them.

## Related Documents

- `docs/architecture/IR_ARCHITECTURE.md`
- `docs/specifications/IR_SPECIFICATION.md`
- `docs/architecture/CLI_ARCHITECTURE.md`
- `docs/roadmaps/VALIDATOR_ROADMAP.md`
- ADR-0002
- ADR-0005
