# Model Invokers Adapter

`descriptors.py` compiles immutable provider/model/parameter descriptions and
rejects credential-like parameters. Compilation never invokes a provider.

`invoker.py` implements the execute half for local Ollama only through the
official `ollama` Python SDK. It accepts only HTTP loopback endpoints and fails
closed for OpenAI, Anthropic, and Google descriptors before constructing a
client. It does not read environment credentials, import cloud SDKs, stream,
retry, or call tools.

```python
from model_invokers import ModelInvoker, PreparedPrompt, model_descriptor_from_binding

descriptor = model_descriptor_from_binding(binding)
if descriptor is not None:
    response = ModelInvoker().invoke(descriptor, PreparedPrompt("Summarize this."))
```

See proposed ADR-0018 for the Build-vs-Reuse decision and rollback plan.

