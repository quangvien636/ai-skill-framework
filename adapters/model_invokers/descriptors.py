"""Declarative model-provider descriptions. Priority 3 scope: describe, never
invoke.

This module builds immutable ``ModelDescriptor`` values naming a provider,
model, and generation parameters. It makes no network call, imports no
provider SDK, and actively rejects any parameter that looks like a
credential -- "no API keys" is enforced here, not just documented. Actually
calling a provider (``ModelInvoker.invoke`` in
docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md) is unimplemented; when
it is built, each provider's official SDK (openai, anthropic, google-genai)
or Ollama's local API is the reuse target, never a hand-rolled HTTP client,
per ADR-0013.

``model_descriptor_from_runtime`` binds a resolved Runtime Contract's
``model`` section (ADR-0014) to a ``ModelDescriptor`` -- binding only, no
invocation. It returns ``None`` when the contract's model is disabled,
mirroring how a Runtime Contract can decline a capability rather than omit
its section (ADR-0014's `enabled` pattern).
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Optional

from asf_validator.runtime_ir import RuntimeIR

SUPPORTED_PROVIDERS = ("openai", "anthropic", "google", "ollama")

_CREDENTIAL_LIKE_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "key",
        "token",
        "secret",
        "authorization",
        "auth",
        "password",
        "credential",
        "credentials",
        "access_token",
        "bearer",
    }
)


class DescriptorError(ValueError):
    """Raised when a declarative model descriptor is invalid or would carry
    a credential."""


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_")


def _validate_parameters(parameters: Mapping[str, Any]) -> None:
    for key in parameters:
        if _normalize_key(key) in _CREDENTIAL_LIKE_KEYS:
            raise DescriptorError(
                f"parameter '{key}' looks like a credential; model_invokers is "
                "declarative-only and must never carry secrets (Priority 3: "
                "\"No API keys\")"
            )


@dataclass(frozen=True)
class ModelDescriptor:
    """A non-executing description of which model to call and how.

    ``endpoint`` is a plain configuration string (e.g. a local Ollama host)
    -- storing it performs no network I/O.
    """

    provider: str
    model: str
    parameters: Mapping[str, Any]
    endpoint: Optional[str] = None


def compile_model_descriptor(
    provider: str,
    model: str,
    parameters: Optional[Mapping[str, Any]] = None,
    endpoint: Optional[str] = None,
) -> ModelDescriptor:
    """Compile a declarative ``ModelDescriptor``. Never calls a network or
    imports a provider SDK.
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise DescriptorError(
            f"unsupported provider '{provider}' (supported: {SUPPORTED_PROVIDERS})"
        )
    if not model:
        raise DescriptorError("model must not be empty")

    params = dict(parameters or {})
    _validate_parameters(params)

    return ModelDescriptor(
        provider=provider,
        model=model,
        parameters=MappingProxyType(params),
        endpoint=endpoint,
    )


def openai_descriptor(model: str, **parameters: Any) -> ModelDescriptor:
    return compile_model_descriptor("openai", model, parameters)


def anthropic_descriptor(model: str, **parameters: Any) -> ModelDescriptor:
    return compile_model_descriptor("anthropic", model, parameters)


def google_descriptor(model: str, **parameters: Any) -> ModelDescriptor:
    return compile_model_descriptor("google", model, parameters)


def ollama_descriptor(
    model: str, endpoint: str = "http://localhost:11434", **parameters: Any
) -> ModelDescriptor:
    return compile_model_descriptor("ollama", model, parameters, endpoint=endpoint)


def model_descriptor_from_runtime(runtime: RuntimeIR) -> Optional[ModelDescriptor]:
    """Bind a resolved Runtime Contract's ``model`` section to a
    ``ModelDescriptor``. Binding only -- no invocation.

    Returns ``None`` when ``runtime.model.enabled`` is false, matching
    ADR-0014's `enabled` pattern: a Runtime Contract can decline the model
    capability rather than omit the section entirely. Semantic validation
    (``ASF-SEMANTIC-010``) already guarantees that an enabled model section
    has a non-empty ``model.model``, so this function does not re-check it.
    """
    if not runtime.model.enabled:
        return None
    return compile_model_descriptor(
        provider=runtime.model.provider,
        model=runtime.model.model,
        parameters=runtime.model.parameters,
        endpoint=runtime.model.endpoint,
    )
