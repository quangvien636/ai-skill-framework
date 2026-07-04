import unittest

import _bootstrap

from asf_validator.dependency_graph import build_dependency_graph
from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry
from asf_validator.version_graph import build_version_graph

GRAPH_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph"


class VersionGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)

    def _load(self, *relative_paths: str, kinds: list[str]):
        return [
            build_ir(kind, GRAPH_FIXTURES / relative_path, self.schema_registry)
            for kind, relative_path in zip(kinds, relative_paths)
        ]

    def test_valid_graph_has_no_version_diagnostics(self):
        results = self._load(
            "valid-multi-artifact/skill.yaml",
            "valid-multi-artifact/knowledge.md",
            "valid-multi-artifact/workflow.yaml",
            kinds=["skill", "knowledge", "workflow"],
        )
        dependency_graph, _ = build_dependency_graph(results)
        _version_graph, diagnostics = build_version_graph(dependency_graph)
        self.assertEqual(diagnostics, [])

    def test_incompatible_version_is_detected(self):
        results = self._load(
            "version-unsatisfiable/skill.yaml",
            "version-unsatisfiable/workflow.yaml",
            kinds=["skill", "workflow"],
        )
        dependency_graph, _ = build_dependency_graph(results)
        _version_graph, diagnostics = build_version_graph(dependency_graph)
        self.assertTrue(any(d.code == "ASF-GRAPH-004" for d in diagnostics))

    def test_ambiguous_version_reference_is_detected(self):
        results = self._load("ambiguous-version/skill.yaml", kinds=["skill"])
        dependency_graph, _ = build_dependency_graph(results)
        _version_graph, diagnostics = build_version_graph(dependency_graph)
        self.assertTrue(any(d.code == "ASF-GRAPH-006" for d in diagnostics))

    def test_deprecated_dependency_is_a_warning(self):
        results = self._load(
            "deprecated-dependency/skill.yaml",
            "deprecated-dependency/knowledge.md",
            kinds=["skill", "knowledge"],
        )
        dependency_graph, _ = build_dependency_graph(results)
        _version_graph, diagnostics = build_version_graph(dependency_graph)
        deprecated = [d for d in diagnostics if d.code == "ASF-GRAPH-005"]
        self.assertEqual(len(deprecated), 1)
        self.assertEqual(deprecated[0].severity.value, "warning")

    def test_required_dependency_on_archived_artifact_is_an_error(self):
        results = self._load(
            "archived-dependency-required/skill.yaml",
            "archived-dependency-required/knowledge.md",
            kinds=["skill", "knowledge"],
        )
        dependency_graph, _ = build_dependency_graph(results)
        _version_graph, diagnostics = build_version_graph(dependency_graph)
        archived = [d for d in diagnostics if d.code == "ASF-GRAPH-005"]
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0].severity.value, "error")

    def test_self_contradictory_range_is_detected_without_also_reporting_unsatisfiable(self):
        results = self._load(
            "self-contradictory-range/skill.yaml",
            "self-contradictory-range/workflow.yaml",
            kinds=["skill", "workflow"],
        )
        dependency_graph, _ = build_dependency_graph(results)
        _version_graph, diagnostics = build_version_graph(dependency_graph)
        codes = {d.code for d in diagnostics}
        self.assertIn("ASF-GRAPH-007", codes)
        self.assertNotIn("ASF-GRAPH-004", codes)

    def test_known_version_lookup(self):
        results = self._load(
            "valid-multi-artifact/skill.yaml",
            "valid-multi-artifact/knowledge.md",
            "valid-multi-artifact/workflow.yaml",
            kinds=["skill", "knowledge", "workflow"],
        )
        dependency_graph, _ = build_dependency_graph(results)
        version_graph, _ = build_version_graph(dependency_graph)
        version = version_graph.known_version("skill:summarize-document")
        self.assertEqual((version.major, version.minor, version.patch), (1, 0, 0))
        self.assertIsNone(version_graph.known_version("skill:does-not-exist"))


if __name__ == "__main__":
    unittest.main()
