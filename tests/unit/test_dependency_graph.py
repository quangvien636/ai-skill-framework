import unittest
from pathlib import Path

import _bootstrap

from asf_validator.dependency_graph import build_dependency_graph
from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry

GRAPH_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph"


class DependencyGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)

    def _load(self, *relative_paths: str, kinds: list[str]):
        results = [
            build_ir(kind, GRAPH_FIXTURES / relative_path, self.schema_registry)
            for kind, relative_path in zip(kinds, relative_paths)
        ]
        return results

    def test_valid_multi_artifact_graph_has_expected_nodes_and_edges(self):
        results = self._load(
            "valid-multi-artifact/skill.yaml",
            "valid-multi-artifact/knowledge.md",
            "valid-multi-artifact/workflow.yaml",
            kinds=["skill", "knowledge", "workflow"],
        )
        graph, diagnostics = build_dependency_graph(results)
        self.assertEqual(diagnostics, [])
        self.assertEqual(
            set(graph.nodes),
            {
                "skill:summarize-document",
                "kb:technical:writing:summarization:brevity",
                "workflow:summarize-document",
            },
        )
        edge_pairs = {(e.source, e.target) for e in graph.edges}
        self.assertIn(
            ("skill:summarize-document", "kb:technical:writing:summarization:brevity"), edge_pairs
        )
        self.assertIn(("workflow:summarize-document", "skill:summarize-document"), edge_pairs)

    def test_valid_tool_and_connector_graph_has_expected_nodes_and_edges(self):
        results = self._load(
            "valid-tool-connector/skill.yaml",
            "valid-tool-connector/tool.yaml",
            "valid-tool-connector/connector.yaml",
            kinds=["skill", "tool", "connector"],
        )
        graph, diagnostics = build_dependency_graph(results)
        self.assertEqual(diagnostics, [])
        self.assertEqual(
            set(graph.nodes),
            {
                "skill:use-tool",
                "tool:read-file",
                "connector:local-fs",
            },
        )
        edge_pairs = {(e.source, e.target) for e in graph.edges}
        self.assertIn(("skill:use-tool", "tool:read-file"), edge_pairs)
        self.assertIn(("tool:read-file", "connector:local-fs"), edge_pairs)

    def test_missing_dependency_is_detected(self):
        results = self._load("missing-dependency/skill.yaml", kinds=["skill"])
        graph, diagnostics = build_dependency_graph(results)
        self.assertEqual(len(graph.edges), 1)
        self.assertTrue(any(d.code == "ASF-GRAPH-001" for d in diagnostics))
        self.assertTrue(all(d.severity.value == "error" for d in diagnostics))  # required dependency

    def test_unresolved_workflow_step_reference_is_detected(self):
        results = self._load(
            "unresolved-workflow-reference/workflow.yaml", kinds=["workflow"]
        )
        graph, diagnostics = build_dependency_graph(results)
        self.assertTrue(any(d.code == "ASF-GRAPH-001" for d in diagnostics))

    def test_cycle_is_detected(self):
        results = self._load(
            "cycle/knowledge-a.md", "cycle/knowledge-b.md", kinds=["knowledge", "knowledge"]
        )
        graph, diagnostics = build_dependency_graph(results)
        self.assertEqual({d.code for d in diagnostics}, {"ASF-GRAPH-002"})

    def test_duplicate_artifact_id_is_detected(self):
        results = self._load(
            "duplicate-id/skill-1.yaml", "duplicate-id/skill-2.yaml", kinds=["skill", "skill"]
        )
        graph, diagnostics = build_dependency_graph(results)
        self.assertTrue(any(d.code == "ASF-GRAPH-003" for d in diagnostics))
        self.assertEqual(len(graph.nodes), 1)  # second duplicate is not added

    def test_dependents_of_query(self):
        results = self._load(
            "valid-multi-artifact/skill.yaml",
            "valid-multi-artifact/knowledge.md",
            "valid-multi-artifact/workflow.yaml",
            kinds=["skill", "knowledge", "workflow"],
        )
        graph, _ = build_dependency_graph(results)
        self.assertEqual(
            graph.dependents_of("skill:summarize-document"), ("workflow:summarize-document",)
        )


if __name__ == "__main__":
    unittest.main()
