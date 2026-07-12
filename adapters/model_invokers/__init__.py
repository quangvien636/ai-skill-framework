"""Model descriptors and local Ollama invocation.

See docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md and ADR-0013.
"""

from .descriptors import (
    SUPPORTED_PROVIDERS,
    DescriptorError,
    ModelDescriptor,
    anthropic_descriptor,
    compile_model_descriptor,
    google_descriptor,
    model_descriptor_from_binding,
    model_descriptor_from_runtime,
    ollama_descriptor,
    openai_descriptor,
)
from .invoker import (
    InvocationError,
    ModelInvoker,
    ModelResponse,
    PreparedPrompt,
    UnsupportedInvocationError,
)

__all__ = [
    "SUPPORTED_PROVIDERS",
    "DescriptorError",
    "ModelDescriptor",
    "anthropic_descriptor",
    "compile_model_descriptor",
    "google_descriptor",
    "model_descriptor_from_binding",
    "model_descriptor_from_runtime",
    "ollama_descriptor",
    "openai_descriptor",
    "InvocationError",
    "ModelInvoker",
    "ModelResponse",
    "PreparedPrompt",
    "UnsupportedInvocationError",
]
