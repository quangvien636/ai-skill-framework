import unittest

import _bootstrap
from asf_validator.diagnostics import Severity
from asf_validator.tool_ir import build_tool_ir


class BuildToolIrTests(unittest.TestCase):
    def test_build_tool_ir_valid(self):
        doc = {
            "schema_version": "1.0.0",
            "id": "tool:read-file",
            "name": "read-file",
            "display_name": "Read File",
            "description": "Reads a file",
            "version": "1.0.0",
            "status": "draft",
            "owners": ["me"],
            "responsibility": "Read content",
            "inputs": {
                "path": {
                    "type": "string",
                    "required": True,
                    "description": "Path to file"
                }
            },
            "outputs": {
                "content": {
                    "type": "string",
                    "required": True,
                    "description": "File content"
                }
            },
            "dependencies": {
                "connectors": []
            },
            "constraints": {
                "side_effects": "none",
                "requires_network": False,
                "requires_local_filesystem": True
            }
        }

        tool, diagnostics = build_tool_ir(doc, "tools/read-file/tool.yaml")
        self.assertIsNotNone(tool)
        self.assertEqual(len(diagnostics), 0)
        self.assertEqual(tool.metadata.id, "tool:read-file")
        self.assertEqual(tool.responsibility, "Read content")
        self.assertEqual(len(tool.inputs), 1)
        self.assertIn("path", tool.inputs)
        self.assertEqual(len(tool.outputs), 1)
        self.assertEqual(len(tool.dependencies.connectors), 0)
        self.assertEqual(tool.constraints.side_effects, "none")
        self.assertEqual(tool.constraints.requires_local_filesystem, True)

    def test_build_tool_ir_invalid_metadata(self):
        doc = {
            "schema_version": "1.0.0",
            "id": "skill:read-file",
            "name": "read-file",
            "display_name": "Read File",
            "description": "Reads a file",
            "version": "1.0.0",
            "status": "draft",
            "owners": ["me"],
            "responsibility": "Read content",
            "inputs": {},
            "outputs": {},
            "dependencies": {"connectors": []},
            "constraints": {"side_effects": "none"}
        }

        tool, diagnostics = build_tool_ir(doc, "tools/read-file/tool.yaml")
        self.assertIsNone(tool)
        self.assertGreater(len(diagnostics), 0)
        self.assertEqual(diagnostics[0].severity, Severity.ERROR)

if __name__ == "__main__":
    unittest.main()
