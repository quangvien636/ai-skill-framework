import unittest

import _bootstrap  # noqa: F401  (adds adapters/ to sys.path)

from model_invokers.descriptors import (
    DescriptorError,
    anthropic_descriptor,
    compile_model_descriptor,
    google_descriptor,
    ollama_descriptor,
    openai_descriptor,
)


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


if __name__ == "__main__":
    unittest.main()
