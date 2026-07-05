import asyncio
import unittest

import _bootstrap

from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry
from mcp_tools.binding import MCPToolRegistry, tool_ir_to_mcp_tool

FIXTURES = _bootstrap.GRAPH_FIXTURES / "valid-tool-connector"


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


if __name__ == "__main__":
    unittest.main()
