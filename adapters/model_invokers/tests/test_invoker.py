import os
import unittest

import pytest

import _bootstrap

from asf_runtime.binding import resolve_skill_runtime_binding
from asf_runtime.catalog import build_artifact_catalog
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry
from model_invokers import (
    InvocationError,
    ModelInvoker,
    PreparedPrompt,
    UnsupportedInvocationError,
    model_descriptor_from_binding,
    ollama_descriptor,
    openai_descriptor,
)


class RecordingClient:
    def __init__(self, response=None, error=None):
        self.response = response or {"response": "local answer"}
        self.error = error
        self.calls = []

    def generate(self, model, prompt, **kwargs):
        self.calls.append((model, prompt, kwargs))
        if self.error:
            raise self.error
        return self.response


def _production_binding():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    index = discover_project(
        _bootstrap.REPO_ROOT,
        kinds=("skill", "knowledge", "runtime"),
    )
    results = [build_ir(item.kind, item.path, registry) for item in index.artifacts]
    assert all(result.ok for result in results)
    catalog = build_artifact_catalog(results)
    skill = catalog.exact("skill:content-creation", "1.0.0").ir
    binding, diagnostics = resolve_skill_runtime_binding(skill, catalog)
    assert binding is not None and not diagnostics
    return binding


class ModelInvokerTests(unittest.TestCase):
    def test_official_client_contract_maps_descriptor_prompt_and_parameters(self):
        client = RecordingClient()
        endpoints = []
        invoker = ModelInvoker(
            client_factory=lambda endpoint: endpoints.append(endpoint) or client
        )

        response = invoker.invoke(
            ollama_descriptor("llama3", temperature=0.2),
            PreparedPrompt("Explain local AI.", system="Be concise."),
        )

        self.assertEqual(endpoints, ["http://localhost:11434"])
        self.assertEqual(
            client.calls,
            [
                (
                    "llama3",
                    "Explain local AI.",
                    {
                        "system": "Be concise.",
                        "stream": False,
                        "options": {"temperature": 0.2},
                    },
                )
            ],
        )
        self.assertEqual(response.text, "local answer")
        self.assertEqual(response.provider, "ollama")

    def test_production_runtime_binding_composes_with_invoker(self):
        descriptor = model_descriptor_from_binding(_production_binding())
        self.assertIsNotNone(descriptor)
        client = RecordingClient()
        response = ModelInvoker(client_factory=lambda _endpoint: client).invoke(
            descriptor, PreparedPrompt("Return one word.")
        )
        self.assertEqual(response.model, "llama3")
        self.assertEqual(client.calls[0][0], "llama3")

    def test_cloud_descriptor_fails_before_client_construction(self):
        constructed = []
        invoker = ModelInvoker(
            client_factory=lambda endpoint: constructed.append(endpoint)
        )
        with self.assertRaises(UnsupportedInvocationError):
            invoker.invoke(openai_descriptor("gpt-4o"), PreparedPrompt("hello"))
        self.assertEqual(constructed, [])

    def test_non_loopback_endpoint_is_rejected(self):
        with self.assertRaises(UnsupportedInvocationError):
            ModelInvoker().invoke(
                ollama_descriptor("llama3", endpoint="https://example.com"),
                PreparedPrompt("hello"),
            )

    def test_blank_prompt_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must not be blank"):
            ModelInvoker().invoke(
                ollama_descriptor("llama3"), PreparedPrompt("  ")
            )

    def test_provider_failure_is_explicit(self):
        client = RecordingClient(error=ConnectionError("refused"))
        with self.assertRaisesRegex(InvocationError, "refused"):
            ModelInvoker(client_factory=lambda _endpoint: client).invoke(
                ollama_descriptor("llama3"), PreparedPrompt("hello")
            )

    def test_malformed_response_is_rejected(self):
        client = RecordingClient(response={"response": ""})
        with self.assertRaisesRegex(InvocationError, "no generated text"):
            ModelInvoker(client_factory=lambda _endpoint: client).invoke(
                ollama_descriptor("llama3"), PreparedPrompt("hello")
            )


@pytest.mark.skipif(
    os.environ.get("ASF_TEST_OLLAMA") != "1",
    reason="set ASF_TEST_OLLAMA=1 for real local Ollama invocation",
)
def test_live_local_ollama_invocation():
    model = os.environ.get("ASF_OLLAMA_MODEL", "llama3")
    result = ModelInvoker().invoke(
        ollama_descriptor(model),
        PreparedPrompt("Reply with exactly the word LOCAL."),
    )
    assert result.text.strip()
    assert result.model == model


if __name__ == "__main__":
    unittest.main()

