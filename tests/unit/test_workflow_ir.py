import unittest

import _bootstrap
import yaml

from asf_validator.workflow_ir import build_workflow_ir


def _load(name: str) -> dict:
    path = _bootstrap.FIXTURES_ROOT / "workflow" / name
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class BuildWorkflowIrTests(unittest.TestCase):
    def test_valid_workflow_builds_ir_with_graph(self):
        doc = _load("valid.yaml")
        workflow, diagnostics = build_workflow_ir(doc, "test")
        self.assertEqual(diagnostics, [])
        self.assertEqual(workflow.entrypoint, "summarize")
        self.assertEqual(len(workflow.steps), 2)
        self.assertEqual(workflow.graph["review"], ("summarize",))
        self.assertEqual(workflow.graph["summarize"], ())

    def test_depends_on_unknown_step_blocks_ir(self):
        doc = _load("invalid_reference.yaml")
        workflow, diagnostics = build_workflow_ir(doc, "test")
        self.assertIsNone(workflow)
        self.assertTrue(any(d.code == "ASF-PARSE-004" for d in diagnostics))

    def test_cycle_blocks_ir(self):
        doc = _load("cycle.yaml")
        workflow, diagnostics = build_workflow_ir(doc, "test")
        self.assertIsNone(workflow)
        self.assertTrue(any(d.code == "ASF-PARSE-006" for d in diagnostics))

    def test_unsupported_schema_version_blocks_ir(self):
        doc = _load("unsupported_version.yaml")
        workflow, diagnostics = build_workflow_ir(doc, "test")
        self.assertIsNone(workflow)
        self.assertTrue(any(d.code == "ASF-PARSE-002" for d in diagnostics))


if __name__ == "__main__":
    unittest.main()
