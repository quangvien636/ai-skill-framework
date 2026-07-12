# Ollama Execution Adapter

This adapter is ASF's first intentionally narrow execution path. It runs only
`workflow:research-content-review`, sequentially, through a local Ollama
endpoint and stops at Reviewed Content Package.

It owns:

- serializable per-step and whole-run execution reports;
- deterministic prompt assembly from validated Skill IR;
- loopback-only Ollama transport;
- structured unavailable-server, missing-model, HTTP, and malformed-output
  diagnostics;
- artifact checks after Research, Content Creation, and Review Quality;
- deterministic report persistence under `runs/<execution-id>/`.

It does not provide a runtime engine, arbitrary workflow execution, scheduling,
queues, background workers, publishing, or rendering. Dry-run mode never
constructs or calls an Ollama client.

`skill:content-creation@1.0.0` resolves its production local model through the
active `runtime:offline@1.0.0` contract. The adapter consumes that
`RuntimeBinding` directly, so an explicit model override is not required for
that Skill. Other canonical Skills still use non-Ollama bindings and require
an explicit local model override when the full three-step composite is run
live.

See [TOPIC_RELEVANCE.md](TOPIC_RELEVANCE.md) for how the artifact checks
decide whether generated output actually stays on-topic (lexical scoring,
domain-drift detection, configuration, and the optional semantic extension
point).
