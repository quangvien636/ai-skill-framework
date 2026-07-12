import asyncio
import unittest
from dataclasses import replace

import _bootstrap

from asf_runtime.binding import build_runtime_binding
from asf_runtime.catalog import build_artifact_catalog
from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry
from mcp_tools.binding import (
    MCPToolRegistry,
    bind_binding_tools,
    bind_runtime_tools,
    tool_ir_to_mcp_tool,
)

FIXTURES = _bootstrap.GRAPH_FIXTURES / "valid-tool-connector"
RUNTIME_FIXTURES = _bootstrap.GRAPH_FIXTURES / "valid-runtime"


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


class MCPBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
        tool_result = build_ir("tool", FIXTURES / "tool.yaml", registry)
        connector_result = build_ir("connector", FIXTURES / "connector.yaml", registry)
        assert tool_result.ok and connector_result.ok, (tool_result.diagnostics, connector_result.diagnostics)
        cls.tool_ir = tool_result.ir
        cls.connector_ir = connector_result.ir

    def test_tool_ir_translates_to_mcp_tool_schema(self):
        mcp_tool = tool_ir_to_mcp_tool(self.tool_ir)

        self.assertEqual(mcp_tool.name, "read-file")
        self.assertEqual(mcp_tool.description, self.tool_ir.responsibility)
        self.assertEqual(mcp_tool.inputSchema["type"], "object")
        self.assertEqual(mcp_tool.inputSchema["properties"]["path"]["type"], "string")
        self.assertIn("path", mcp_tool.inputSchema["required"])
        self.assertEqual(
            mcp_tool.outputSchema["properties"]["content"]["type"],
            "string",
        )
        self.assertIn("content", mcp_tool.outputSchema["required"])

    def test_registry_binds_handler_and_connector_and_dispatches_call(self):
        registry = MCPToolRegistry()

        async def handler(arguments):
            return {"content": f"read {arguments['path']}"}

        registry.bind(self.tool_ir, handler, connector=self.connector_ir)

        listed = registry.list_tools()
        self.assertEqual([t.name for t in listed], ["read-file"])

        bound_connector = registry.connector_for("read-file")
        self.assertEqual(bound_connector.id, "connector:local-fs")
        self.assertEqual(bound_connector.authentication, "none")

        result = asyncio.run(registry.call_tool("read-file", {"path": "/tmp/x"}))
        self.assertEqual(result, {"content": "read /tmp/x"})

    def test_call_tool_without_binding_raises(self):
        registry = MCPToolRegistry()
        with self.assertRaises(KeyError):
            asyncio.run(registry.call_tool("missing-tool", {}))

    def test_bind_runtime_tools_binds_every_enabled_reference(self):
        schema_registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
        runtime_result = build_ir("runtime", RUNTIME_FIXTURES / "runtime.yaml", schema_registry)
        tool_result = build_ir("tool", RUNTIME_FIXTURES / "tool.yaml", schema_registry)
        assert runtime_result.ok and tool_result.ok, (
            runtime_result.diagnostics,
            tool_result.diagnostics,
        )
        self.assertTrue(runtime_result.ir.tools.enabled)

        registry = MCPToolRegistry()

        async def handler(arguments):
            return {"content": f"read {arguments['path']}"}

        bound = bind_runtime_tools(
            registry,
            runtime_result.ir,
            tools_by_id={"tool:read-file": tool_result.ir},
            handlers_by_id={"tool:read-file": handler},
        )
        self.assertEqual(bound, ("read-file",))
        self.assertEqual([t.name for t in registry.list_tools()], ["read-file"])

    def test_bind_runtime_tools_returns_empty_when_disabled(self):
        schema_registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
        runtime_result = build_ir(
            "runtime", RUNTIME_FIXTURES / "runtime-fallback.yaml", schema_registry
        )
        assert runtime_result.ok, runtime_result.diagnostics
        self.assertFalse(runtime_result.ir.tools.enabled)

        registry = MCPToolRegistry()
        bound = bind_runtime_tools(registry, runtime_result.ir, tools_by_id={}, handlers_by_id={})
        self.assertEqual(bound, ())
        self.assertEqual(registry.list_tools(), [])

    def test_bind_binding_tools_binds_every_resolved_tool_without_tools_by_id(self):
        catalog = _runtime_binding_catalog()
        primary = catalog.exact("runtime:primary", "1.0.0").ir
        binding, diagnostics = build_runtime_binding(
            "skill:use-runtime", "1.0.0", primary, catalog
        )
        self.assertEqual(diagnostics, [])
        self.assertEqual(
            [tool.metadata.id for tool in binding.resolved_tools], ["tool:read-file"]
        )

        registry = MCPToolRegistry()

        async def handler(arguments):
            return {"content": f"read {arguments['path']}"}

        bound = bind_binding_tools(
            registry, binding, handlers_by_id={"tool:read-file": handler}
        )
        self.assertEqual(bound, ("read-file",))
        self.assertEqual([t.name for t in registry.list_tools()], ["read-file"])

    def test_bind_binding_tools_returns_empty_when_nothing_in_chain_enables_it(self):
        catalog = _runtime_binding_catalog()
        primary = catalog.exact("runtime:primary", "1.0.0").ir
        binding, diagnostics = build_runtime_binding(
            "skill:use-runtime", "1.0.0", primary, catalog
        )
        self.assertEqual(diagnostics, [])
        no_tools_binding = replace(binding, tools=None)

        registry = MCPToolRegistry()
        bound = bind_binding_tools(registry, no_tools_binding, handlers_by_id={})
        self.assertEqual(bound, ())
        self.assertEqual(registry.list_tools(), [])


if __name__ == "__main__":
    unittest.main()
