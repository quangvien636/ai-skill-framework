# Research, Content, and Review

This active composite Workflow is ASF's canonical compile-only production path:

```text
Research -> Content Creation -> Review Quality -> Reviewed Content Package
```

Every transfer is declared in `workflow.yaml`. The Research Skill's
`research-brief` becomes Content Creation's `research-brief`; the generated
`content-package` becomes Review Quality's `draft`. Workflow inputs supply
caller-owned evidence directly to Research and Review without hidden state.

The final workflow output envelope retains the research brief and quality
report, the content package and quality report, and the review report and
reviewed content package. For short video, the nested content draft carries
title, hook, script, scenes, voice-over text, on-screen text, image prompts,
CTA, hashtags, and metadata. ASF stops at this reviewed editorial artifact.
Rendering and publishing belong to external adapters and systems.

Compile without execution:

```bash
python scripts/asf.py compile --workflow workflow:research-content-review --inputs "{}"
```

See [the representative example](examples/representative.yaml) for the
canonical input and expected artifact shape.
