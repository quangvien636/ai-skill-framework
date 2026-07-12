import unittest
from dataclasses import replace

import _bootstrap

from asf_runtime.binding import build_runtime_binding
from asf_runtime.catalog import build_artifact_catalog
from asf_validator.pipeline import build_ir
from asf_validator.runtime_ir import build_runtime_ir
from asf_validator.schema_registry import build_schema_registry
from model_invokers.descriptors import (
    DescriptorError,
    anthropic_descriptor,
    compile_model_descriptor,
    google_descriptor,
    model_descriptor_from_binding,
    model_descriptor_from_runtime,
    ollama_descriptor,
    openai_descriptor,
)

RUNTIME_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph" / "valid-runtime"


def _runtime_binding_catalog():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    results = [
        build_ir("skill", RUNTIME_FIXTURES / "skill.yaml", registry),
        build_ir("runtime", RUNTIME_FIXTURES / "runtime.yaml", registry),
        build_ir("runtime", RUNTIME_FIXTURES / "runtime-fallback.yaml", registry),
        build_ir("tool", RUNTIME_FIXTURES / "tool.yaml", registry),
        build_ir("knowledge", RUNTIME_FIXTURES / "knowledge.md", registry),
    ]
    assert all(result.ok for result in results), [
        (result.artifact, result.diagnostics) for result in results if not result.ok
    ]
    return build_artifact_catalog(results)

_RUNTIME_DOC_BASE = {
    "schema_version": "1.0.0",
    "id": "runtime:simple",
    "name": "simple",
    "display_name": "Simple Runtime",
    "description": "Minimal single-model runtime",
    "version": "1.0.0",
    "status": "draft",
    "owners": ["me"],
    "responsibility": "Bind a Skill to a single model",
    "execution_profile": "sync",
    "retriever": {"enabled": False, "knowledge": []},
    "tools": {"enabled": False, "refs": []},
    "publisher": {"enabled": False},
    "timeout_policy": {"timeout_seconds": 30, "on_timeout": "fail"},
    "retry_policy": {"max_attempts": 1, "backoff": "none"},
    "safety_profile": {"content_filter": "standard"},
    "audit_profile": {"log_level": "basic"},
    "concurrency_profile": {"max_parallel_steps": 1, "max_parallel_tool_calls": 1},
    "fallback_profile": {"enabled": False, "max_fallback_depth": 1},
}


def _runtime(model_doc):
    doc = dict(_RUNTIME_DOC_BASE, model=model_doc)
    runtime, diagnostics = build_runtime_ir(doc, "runtime/simple/runtime.yaml")
    assert runtime is not None, diagnostics
    return runtime


class ModelDescriptorTests(unittest.TestCase):
    def test_openai_descriptor_is_declarative_only(self):
        descriptor = openai_descriptor("gpt-4o", temperature=0.2, max_tokens=512)
        self.assertEqual(descriptor.provider, "openai")
        self.assertEqual(descriptor.model, "gpt-4o")
        self.assertEqual(descriptor.parameters["temperature"], 0.2)
        self.assertIsNone(descriptor.endpoint)

    def test_anthropic_descriptor(self):
        descriptor = anthropic_descriptor("claude-sonnet-5", max_tokens=1024)
        self.assertEqual(descriptor.provider, "anthropic")
        self.assertEqual(descriptor.parameters["max_tokens"], 1024)

    def test_google_descriptor(self):
        descriptor = google_descriptor("gemini-2.5-pro", temperature=0.5)
        self.assertEqual(descriptor.provider, "google")

    def test_ollama_descriptor_defaults_local_endpoint(self):
        descriptor = ollama_descriptor("llama3")
        self.assertEqual(descriptor.provider, "ollama")
        self.assertEqual(descriptor.endpoint, "http://localhost:11434")

    def test_ollama_descriptor_accepts_custom_endpoint(self):
        descriptor = ollama_descriptor("llama3", endpoint="http://gpu-box:11434")
        self.assertEqual(descriptor.endpoint, "http://gpu-box:11434")

    def test_unsupported_provider_is_rejected(self):
        with self.assertRaises(DescriptorError):
            compile_model_descriptor("azure", "gpt-4o")

    def test_empty_model_is_rejected(self):
        with self.assertRaises(DescriptorError):
            compile_model_descriptor("openai", "")

    def test_credential_like_parameter_is_rejected(self):
        for key in ("api_key", "API-KEY", "token", "Authorization", "secret"):
            with self.assertRaises(DescriptorError):
                compile_model_descriptor("openai", "gpt-4o", {key: "sk-not-really-a-secret"})

    def test_descriptor_parameters_are_immutable(self):
        descriptor = openai_descriptor("gpt-4o", temperature=0.2)
        with self.assertRaises(TypeError):
            descriptor.parameters["temperature"] = 1.0

    def test_model_descriptor_from_runtime_binds_enabled_model(self):
        runtime = _runtime(
            {
                "enabled": True,
                "provider": "anthropic",
                "model": "claude-sonnet-5",
                "parameters": {"temperature": 0.2},
            }
        )
        descriptor = model_descriptor_from_runtime(runtime)
        self.assertIsNotNone(descriptor)
        self.assertEqual(descriptor.provider, "anthropic")
        self.assertEqual(descriptor.model, "claude-sonnet-5")
        self.assertEqual(descriptor.parameters["temperature"], 0.2)

    def test_model_descriptor_from_runtime_returns_none_when_disabled(self):
        runtime = _runtime({"enabled": False})
        self.assertIsNone(model_descriptor_from_runtime(runtime))

    def test_model_descriptor_from_binding_binds_effective_model(self):
        catalog = _runtime_binding_catalog()
        primary = catalog.exact("runtime:primary", "1.0.0").ir
        binding, diagnostics = build_runtime_binding(
            "skill:use-runtime", "1.0.0", primary, catalog
        )
        self.assertEqual(diagnostics, [])
        descriptor = model_descriptor_from_binding(binding)
        self.assertIsNotNone(descriptor)
        self.assertEqual(descriptor.provider, "anthropic")
        self.assertEqual(descriptor.model, "claude-sonnet-5")

    def test_model_descriptor_from_binding_returns_none_when_nothing_in_chain_enables_it(self):
        catalog = _runtime_binding_catalog()
        primary = catalog.exact("runtime:primary", "1.0.0").ir
        binding, diagnostics = build_runtime_binding(
            "skill:use-runtime", "1.0.0", primary, catalog
        )
        self.assertEqual(diagnostics, [])
        no_model_binding = replace(binding, model=None)
        self.assertIsNone(model_descriptor_from_binding(no_model_binding))


if __name__ == "__main__":
    unittest.main()
