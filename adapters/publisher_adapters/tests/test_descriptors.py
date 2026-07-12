import unittest
from dataclasses import replace

import _bootstrap

from asf_runtime.binding import build_runtime_binding
from asf_runtime.catalog import build_artifact_catalog
from asf_validator.pipeline import build_ir
from asf_validator.runtime_ir import PublisherBindingIR, build_runtime_ir
from asf_validator.schema_registry import build_schema_registry
from publisher_adapters.descriptors import (
    DescriptorError,
    compile_export_descriptor,
    export_descriptor_from_binding,
    export_descriptor_from_runtime,
    facebook_export,
    markdown_export,
    tiktok_export,
    wordpress_export,
    youtube_export,
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
    "model": {"enabled": False},
    "retriever": {"enabled": False, "knowledge": []},
    "tools": {"enabled": False, "refs": []},
    "timeout_policy": {"timeout_seconds": 30, "on_timeout": "fail"},
    "retry_policy": {"max_attempts": 1, "backoff": "none"},
    "safety_profile": {"content_filter": "standard"},
    "audit_profile": {"log_level": "basic"},
    "concurrency_profile": {"max_parallel_steps": 1, "max_parallel_tool_calls": 1},
    "fallback_profile": {"enabled": False, "max_fallback_depth": 1},
}


def _runtime(publisher_doc):
    doc = dict(_RUNTIME_DOC_BASE, publisher=publisher_doc)
    runtime, diagnostics = build_runtime_ir(doc, "runtime/simple/runtime.yaml")
    assert runtime is not None, diagnostics
    return runtime


class ExportDescriptorTests(unittest.TestCase):
    def test_youtube_export_is_declarative_only(self):
        descriptor = youtube_export(
            "Title", "Description", tags=("ai", "skills"), category="Education"
        )
        self.assertEqual(descriptor.target, "youtube")
        self.assertEqual(descriptor.metadata["tags"], ("ai", "skills"))
        self.assertEqual(descriptor.metadata["privacy_status"], "private")

    def test_tiktok_export(self):
        descriptor = tiktok_export("Title", "Caption", hashtags=("fyp",))
        self.assertEqual(descriptor.target, "tiktok")
        self.assertEqual(descriptor.metadata["hashtags"], ("fyp",))

    def test_facebook_export(self):
        descriptor = facebook_export("Title", "Message", link="https://example.com")
        self.assertEqual(descriptor.target, "facebook")
        self.assertEqual(descriptor.metadata["link"], "https://example.com")

    def test_wordpress_export_defaults_to_draft_status(self):
        descriptor = wordpress_export("Title", "Content")
        self.assertEqual(descriptor.metadata["status"], "draft")

    def test_markdown_export_never_writes_a_file(self):
        descriptor = markdown_export("Title", "# Body", front_matter={"date": "2026-07-05"})
        self.assertEqual(descriptor.target, "markdown")
        self.assertEqual(descriptor.metadata["front_matter"]["date"], "2026-07-05")

    def test_unsupported_target_is_rejected(self):
        with self.assertRaises(DescriptorError):
            compile_export_descriptor("instagram", "Title", "Body")

    def test_empty_title_is_rejected(self):
        with self.assertRaises(DescriptorError):
            compile_export_descriptor("markdown", "", "Body")

    def test_credential_like_metadata_key_is_rejected(self):
        for key in ("api_key", "Access-Token", "cookie", "session_id"):
            with self.assertRaises(DescriptorError):
                compile_export_descriptor("wordpress", "Title", "Body", {key: "value"})

    def test_credential_like_key_nested_in_front_matter_is_rejected(self):
        with self.assertRaises(DescriptorError):
            markdown_export("Title", "Body", front_matter={"api_key": "sk-not-real"})

    def test_descriptor_metadata_is_immutable(self):
        descriptor = youtube_export("Title", "Description")
        with self.assertRaises(TypeError):
            descriptor.metadata["privacy_status"] = "public"

    def test_export_descriptor_from_runtime_binds_enabled_publisher(self):
        runtime = _runtime({"enabled": True, "target": "wordpress", "metadata": {"status": "draft"}})
        descriptor = export_descriptor_from_runtime(runtime, "Title", "Body")
        self.assertIsNotNone(descriptor)
        self.assertEqual(descriptor.target, "wordpress")
        self.assertEqual(descriptor.title, "Title")
        self.assertEqual(descriptor.body, "Body")
        self.assertEqual(descriptor.metadata["status"], "draft")

    def test_export_descriptor_from_runtime_returns_none_when_disabled(self):
        runtime = _runtime({"enabled": False})
        self.assertIsNone(export_descriptor_from_runtime(runtime, "Title", "Body"))

    def test_export_descriptor_from_binding_returns_none_when_nothing_in_chain_enables_it(self):
        catalog = _runtime_binding_catalog()
        primary = catalog.exact("runtime:primary", "1.0.0").ir
        binding, diagnostics = build_runtime_binding(
            "skill:use-runtime", "1.0.0", primary, catalog
        )
        self.assertEqual(diagnostics, [])
        self.assertIsNone(binding.publisher)
        self.assertIsNone(export_descriptor_from_binding(binding, "Title", "Body"))

    def test_export_descriptor_from_binding_binds_effective_publisher(self):
        catalog = _runtime_binding_catalog()
        primary = catalog.exact("runtime:primary", "1.0.0").ir
        primary_with_publisher = replace(
            primary,
            publisher=PublisherBindingIR(
                enabled=True, target="wordpress", metadata={"status": "draft"}
            ),
        )
        binding, diagnostics = build_runtime_binding(
            "skill:use-runtime", "1.0.0", primary_with_publisher, catalog
        )
        self.assertEqual(diagnostics, [])

        descriptor = export_descriptor_from_binding(binding, "Title", "Body")
        self.assertIsNotNone(descriptor)
        self.assertEqual(descriptor.target, "wordpress")
        self.assertEqual(descriptor.title, "Title")
        self.assertEqual(descriptor.body, "Body")
        self.assertEqual(descriptor.metadata["status"], "draft")


if __name__ == "__main__":
    unittest.main()
