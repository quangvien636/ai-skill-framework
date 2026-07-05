"""Declarative model-provider descriptors (describe, never invoke).

See docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md and ADR-0013.
"""

from .descriptors import (
    SUPPORTED_PROVIDERS,
    DescriptorError,
    ModelDescriptor,
    anthropic_descriptor,
    compile_model_descriptor,
    google_descriptor,
    ollama_descriptor,
    openai_descriptor,
)

__all__ = [
    "SUPPORTED_PROVIDERS",
    "DescriptorError",
    "ModelDescriptor",
    "anthropic_descriptor",
    "compile_model_descriptor",
    "google_descriptor",
    "ollama_descriptor",
    "openai_descriptor",
]
