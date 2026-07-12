"""Local-only real model invocation through the official Ollama SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import urlparse

import ollama

from .descriptors import ModelDescriptor


class InvocationError(RuntimeError):
    """Raised when a supported local provider invocation fails."""


class UnsupportedInvocationError(InvocationError):
    """Raised before any client is built for providers outside local scope."""


class OllamaGenerateClient(Protocol):
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: str | None = None,
        stream: bool = False,
        options: Mapping[str, Any] | None = None,
    ) -> Any: ...


@dataclass(frozen=True)
class PreparedPrompt:
    text: str
    system: str | None = None


@dataclass(frozen=True)
class ModelResponse:
    provider: str
    model: str
    text: str


def _official_client(endpoint: str) -> OllamaGenerateClient:
    return ollama.Client(host=endpoint)


class ModelInvoker:
    """Invoke an Ollama descriptor; all cloud descriptors fail closed."""

    def __init__(
        self,
        client_factory: Callable[[str], OllamaGenerateClient] = _official_client,
    ) -> None:
        self._client_factory = client_factory

    def invoke(
        self, descriptor: ModelDescriptor, prompt: PreparedPrompt
    ) -> ModelResponse:
        if descriptor.provider != "ollama":
            raise UnsupportedInvocationError(
                f"provider '{descriptor.provider}' invocation is unavailable; "
                "this execute half supports local Ollama only"
            )
        text = prompt.text.strip()
        if not text:
            raise ValueError("prompt text must not be blank")

        endpoint = descriptor.endpoint or "http://localhost:11434"
        _validate_loopback_endpoint(endpoint)
        client = self._client_factory(endpoint)
        try:
            response = client.generate(
                descriptor.model,
                text,
                system=prompt.system,
                stream=False,
                options=dict(descriptor.parameters),
            )
        except (ollama.RequestError, ollama.ResponseError, ConnectionError) as error:
            raise InvocationError(f"local Ollama invocation failed: {error}") from error

        generated = _response_text(response)
        return ModelResponse("ollama", descriptor.model, generated)


def _validate_loopback_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        raise UnsupportedInvocationError(
            "Ollama invocation requires a local HTTP loopback endpoint"
        )


def _response_text(response: Any) -> str:
    value = (
        response.get("response")
        if isinstance(response, Mapping)
        else getattr(response, "response", None)
    )
    if not isinstance(value, str) or not value.strip():
        raise InvocationError("local Ollama returned no generated text")
    return value

