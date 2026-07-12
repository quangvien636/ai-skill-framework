# ADR-0018: Local Ollama Model Invocation

- **Status:** Accepted
- **Date:** 2026-07-12
- **Decision owners:** Project maintainers

## Context

`model_invokers` compiles provider-neutral `ModelDescriptor` values but has no
`ModelInvoker.invoke` execute half. This sprint must invoke a real provider
without enabling cloud calls, credentials, or a second hand-written Ollama HTTP
transport. The existing `ollama_execution` adapter proves the local API path,
but adapter isolation forbids one adapter package importing another.

## Options

### Import `ollama_execution.OllamaClient`

Rejected. It reuses code but violates the established rule that adapters do not
import other adapter packages and couples a general descriptor seam to the
canonical workflow executor.

### Copy the standard-library HTTP client

Rejected. It duplicates transport/error behavior and conflicts with ADR-0013's
requirement to reuse provider SDKs instead of adding another hand-written model
client.

### Use the official Ollama Python SDK

Selected. It owns transport, request serialization, provider errors, and API
compatibility. The ASF adapter remains a narrow descriptor/prompt/result
translation layer and can inject a client double for deterministic tests.

Cloud-provider SDKs are not selected in this sprint because using them would
require credentials and external paid/cloud access outside the approved scope.

## Decision

Implement `ModelInvoker.invoke` for `provider == "ollama"` only using the
official `ollama` Python SDK. The invoker:

1. rejects every non-Ollama descriptor before constructing a client;
2. requires an HTTP loopback endpoint (`localhost`, `127.0.0.1`, or `::1`);
3. accepts an immutable prepared prompt and descriptor parameters;
4. calls the SDK's synchronous `generate` API;
5. returns an immutable response containing provider, model, and generated
   text;
6. converts unavailable-server, missing-model/provider, and malformed-response
   failures into explicit adapter exceptions without hiding their cause.

No API key, environment credential lookup, cloud SDK, streaming, tool call,
retry loop, or response-schema enforcement is introduced.

## Build vs Reuse

The official Ollama SDK owns all provider transport and protocol behavior. ASF
builds only validation and translation around the already-stable
`ModelDescriptor` seam. Existing `ollama_execution` remains independent and is
not refactored in this sprint; consolidating transports would require a future
cross-adapter architecture decision rather than an incidental import.

## Consequences

- `ModelDescriptor` from a real `RuntimeBinding` can now invoke local Ollama as
  a reusable adapter capability, not only through the canonical StepExecutor.
- The package gains the official `ollama` dependency.
- Cloud descriptors intentionally fail closed at invocation time; their
  execute halves remain unimplemented.
- Synchronous invocation is the first bounded contract. Async/streaming remain
  deferred until a real consumer requires them.

## Validation Plan

- Unit-test real request mapping with an injected client, binding-to-invocation
  composition, non-Ollama rejection before client use, non-loopback rejection,
  blank prompts, provider errors, and malformed responses.
- Run an opt-in live test against the installed local `llama3` model and report
  the truthful result.
- Run full repository validation and all model-invoker tests.

## Rollback Plan

Remove the invoker module/exports/tests and official SDK requirement. Descriptor
compilation and both Runtime/RuntimeBinding conversion functions remain
unchanged, restoring the package to its prior describe-only behavior.

## Related Documents

- ADR-0013
- ADR-0015
- `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`
- `adapters/ollama_execution/`

