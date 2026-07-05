# Research

`skill:research` turns a topic and caller-supplied evidence into a structured,
traceable research brief. It supports research questions, source requirements,
evidence notes, reliability ranking, claim extraction and mapping, synthesis,
uncertainty, gaps, citations, and next steps.

Research v1 does not browse or fetch external sources. A request without enough
evidence still produces useful questions, source requirements, and gap records,
but it must not manufacture findings.

See [`examples/`](examples/) for representative, minimal-evidence, contradictory,
and invalid-source cases. Use the
[`research-topic-to-brief`](../../workflows/research-topic-to-brief/README.md)
Workflow for the end-to-end framework process.
