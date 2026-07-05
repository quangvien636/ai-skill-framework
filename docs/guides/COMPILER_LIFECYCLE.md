# ASF Compiler Lifecycle

Version: 1.0  
Status: Active  
Last updated: 2026-07-05

## Purpose

Define the canonical production path proved by the ASF compiler and the exact
boundary where external execution begins.

## Canonical Lifecycle

```text
Topic
  -> Research
  -> Content Creation
  -> Review Quality
  -> Reviewed Content Package
  -> External Adapter
  -> Video System
  -> Publishing Platform
```

ASF owns everything through **Reviewed Content Package**. It validates
contracts, resolves dependencies and Runtime Contracts, creates
`RuntimeBinding`/`BindingIR`, plans deterministic batches, and compiles a
LangGraph `StateGraph`. Compilation never executes a graph node.

External systems own Skill invocation, retrieval, model calls, media
generation, voice synthesis, subtitle rendering, video editing, encoding,
uploading, and publishing. CapCut, Remotion, FFmpeg, or another video system
may consume the reviewed package; none is part of ASF.

## Composite Workflow

The canonical manifest is
[`workflow:research-content-review`](../../workflows/research-content-review/README.md).
It composes existing Skills without copying their logic:

| Step | Skill | Declared predecessor |
| --- | --- | --- |
| `research-topic` | `skill:research` | none |
| `create-content` | `skill:content-creation` | `research-topic` |
| `review-content` | `skill:review-quality` | `create-content` |

Artifact flow is explicit:

```text
steps.research-topic.outputs.research-brief
  -> steps.create-content.inputs.research-brief

steps.create-content.outputs.content-package
  -> steps.review-content.inputs.draft
```

Workflow inputs remain explicit sources for caller-owned evidence,
constraints, platform, audience, and the editorial brief. There is no implicit
global state or hidden transfer.

## Reviewed Content Package

The workflow output envelope is ASF's canonical production artifact. It
retains:

- research brief and research quality report;
- content package and content quality report;
- review report and reviewed content package.

For `short-video-script`, the content package's primary content carries title,
hook, script, scenes, voice-over text, on-screen text, image prompts, CTA,
hashtags, and metadata. The review artifacts carry the final disposition,
required corrections, unresolved items, safety review, and quality findings.

This is editorial and production-planning data. It is not a rendered video,
audio file, subtitle file, thumbnail binary, upload receipt, or platform post.

## Compile-Only Proof

```bash
python scripts/asf.py compile content-workflow
python scripts/asf.py snapshot
python scripts/asf.py inspect
python scripts/asf.py explain
```

`compile content-workflow` uses the canonical workflow and representative
inputs unless the caller supplies `--inputs`. The other commands expose the
five golden snapshots, resolved workflow contract, artifact transfers, and ASF
boundary. None has an execution path.

## Golden Snapshots

The canonical snapshots live under
[`workflows/research-content-review/snapshots/`](../../workflows/research-content-review/snapshots/README.md):

1. composite workflow;
2. composite binding;
3. composite execution plan;
4. compiled StateGraph;
5. reviewed content package shape.

The reviewed package snapshot is deliberately marked `revise`: it demonstrates
shape without pretending that research, generation, review, or fact-checking
ran.

## Local Ollama Execution Milestone

The first execution milestone is implemented in
[`adapters/ollama_execution/`](../../adapters/ollama_execution/README.md).
It leaves the compiler unchanged and:

1. consumes the immutable `ExecutionPlan`, Skill IR, Knowledge IR, and resolved
   Runtime bindings;
2. invokes only a loopback Ollama endpoint with no API key;
3. executes only the canonical three-step workflow, sequentially;
4. validates research, content, and reviewed-package artifact boundaries;
5. persists JSON, human-readable, and per-step reports under `runs/`;
6. stops at Reviewed Content Package.

Dry-run remains the default and does not construct an Ollama executor.
Live-local requires both an explicit mode and model:

```bash
python scripts/asf.py run content-workflow --topic "Local AI" --mode dry-run
python scripts/asf.py run content-workflow --topic "Local AI" --mode live-local --model llama3
```

Rendering and publishing remain separate, unimplemented external milestones.
