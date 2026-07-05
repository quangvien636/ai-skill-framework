# Review Quality

`skill:review-quality` evaluates a supplied content package, research brief, or
generic draft before downstream use. It reviews clarity, structure, logic,
tone, platform fit, CTA, length, pacing, evidence and citation alignment,
unsupported claims, and safety, then recommends `approve`, `revise`, or
`reject`.

Review v1 uses only caller-supplied artifacts and evidence. It does not execute
an LLM, browse, externally fact-check, retrieve policy, or publish.

See [`examples/`](examples/) for approve, revise, reject, and invalid/refusal
cases. Use the
[`draft-to-reviewed-package`](../../workflows/draft-to-reviewed-package/README.md)
Workflow for the canonical end-to-end process.
