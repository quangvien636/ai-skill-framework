import unittest

import _bootstrap
from asf_validator.diagnostics import Severity
from asf_validator.runtime_ir import build_runtime_ir


def _valid_doc(**overrides):
    doc = {
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
        "model": {
            "enabled": True,
            "provider": "anthropic",
            "model": "claude-sonnet-5",
            "parameters": {"temperature": 0.2},
        },
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
    doc.update(overrides)
    return doc


class BuildRuntimeIrTests(unittest.TestCase):
    def test_build_runtime_ir_valid(self):
        runtime, diagnostics = build_runtime_ir(_valid_doc(), "runtime/simple/runtime.yaml")
        self.assertIsNotNone(runtime)
        self.assertEqual(len(diagnostics), 0)
        self.assertEqual(runtime.metadata.id, "runtime:simple")
        self.assertEqual(runtime.execution_profile, "sync")
        self.assertTrue(runtime.model.enabled)
        self.assertEqual(runtime.model.provider, "anthropic")
        self.assertEqual(runtime.model.parameters["temperature"], 0.2)
        self.assertFalse(runtime.retriever.enabled)
        self.assertEqual(runtime.retriever.similarity_top_k, 5)
        self.assertFalse(runtime.tools.enabled)
        self.assertEqual(runtime.tools.refs, ())
        self.assertFalse(runtime.publisher.enabled)
        self.assertIsNone(runtime.publisher.target)
        self.assertEqual(runtime.timeout_policy.timeout_seconds, 30)
        self.assertEqual(runtime.retry_policy.max_attempts, 1)
        self.assertEqual(runtime.safety_profile.content_filter, "standard")
        self.assertEqual(runtime.audit_profile.log_level, "basic")
        self.assertEqual(runtime.concurrency_profile.max_parallel_steps, 1)
        self.assertFalse(runtime.fallback_profile.enabled)
        self.assertIsNone(runtime.fallback_profile.fallback_runtime)

    def test_build_runtime_ir_with_retriever_tools_and_fallback(self):
        doc = _valid_doc(
            retriever={
                "enabled": True,
                "knowledge": [
                    {
                        "id": "kb:creative:content:formats:content-structures",
                        "version": "1.0.0",
                        "required": True,
                        "purpose": "Structure guidance",
                    }
                ],
                "similarity_top_k": 3,
            },
            tools={
                "enabled": True,
                "refs": [{"id": "tool:read-file", "version": "1.0.0", "required": True}],
            },
            fallback_profile={
                "enabled": True,
                "fallback_runtime": {"id": "runtime:offline", "version": "1.0.0", "required": True},
                "max_fallback_depth": 2,
            },
        )
        runtime, diagnostics = build_runtime_ir(doc, "runtime/hybrid/runtime.yaml")
        self.assertIsNotNone(runtime)
        self.assertEqual(len(diagnostics), 0)
        self.assertEqual(len(runtime.retriever.knowledge), 1)
        self.assertEqual(runtime.retriever.similarity_top_k, 3)
        self.assertEqual(len(runtime.tools.refs), 1)
        self.assertEqual(runtime.tools.refs[0].id, "tool:read-file")
        self.assertTrue(runtime.fallback_profile.enabled)
        self.assertEqual(runtime.fallback_profile.fallback_runtime.id, "runtime:offline")
        self.assertEqual(runtime.fallback_profile.max_fallback_depth, 2)

    def test_build_runtime_ir_invalid_metadata(self):
        doc = _valid_doc(id="skill:simple")
        runtime, diagnostics = build_runtime_ir(doc, "runtime/simple/runtime.yaml")
        self.assertIsNone(runtime)
        self.assertGreater(len(diagnostics), 0)
        self.assertEqual(diagnostics[0].severity, Severity.ERROR)


if __name__ == "__main__":
    unittest.main()
