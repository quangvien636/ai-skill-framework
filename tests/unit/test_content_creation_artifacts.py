import json
import unittest

import _bootstrap

from asf_validator.dependency_graph import build_dependency_graph
from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry
from asf_validator.version_graph import build_version_graph


SKILL = "skills/content-creation/skill.yaml"
WORKFLOW = "workflows/content-brief-to-package/workflow.yaml"
RUNTIME = "runtime/content/runtime.yaml"
KNOWLEDGE = {
    "knowledge/creative/content/formats/content-structures.md",
    "knowledge/creative/content/style/tone-guidelines.md",
    "knowledge/creative/content/platforms/publishing-constraints.md",
    "knowledge/creative/content/hooks/hook-formulas.md",
    "knowledge/creative/content/conversion/call-to-action-patterns.md",
}


class ContentCreationProductionArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)

    @staticmethod
    def load_manifest(relative_path):
        return json.loads((_bootstrap.REPO_ROOT / relative_path).read_text(encoding="utf-8"))

    def test_contract_and_ir_cases_reference_canonical_production_manifests(self):
        contract_fixtures = {
            case["fixture"]
            for case in self.load_manifest("tests/fixtures/contracts/cases.json")["cases"]
        }
        ir_fixtures = {
            case["fixture"]
            for case in self.load_manifest("tests/fixtures/ir/cases.json")["cases"]
        }

        self.assertTrue({SKILL, WORKFLOW}.issubset(contract_fixtures))
        self.assertTrue(({SKILL, WORKFLOW} | KNOWLEDGE).issubset(ir_fixtures))

    def test_graph_case_references_complete_canonical_production_package(self):
        cases = self.load_manifest("tests/fixtures/graph/cases.json")["cases"]
        production = next(
            case for case in cases if case["name"] == "content-creation-v1-production-artifacts"
        )
        fixtures = {artifact["fixture"] for artifact in production["artifacts"]}

        self.assertEqual(fixtures, {SKILL, WORKFLOW, RUNTIME} | KNOWLEDGE)
        self.assertEqual(production["expected_codes"], [])

    def test_canonical_production_package_builds_without_graph_diagnostics(self):
        artifacts = [
            ("skill", SKILL),
            *(("knowledge", path) for path in sorted(KNOWLEDGE)),
            ("runtime", RUNTIME),
            ("workflow", WORKFLOW),
        ]
        results = [
            build_ir(kind, _bootstrap.REPO_ROOT / path, self.registry)
            for kind, path in artifacts
        ]

        self.assertTrue(all(result.ok for result in results))
        dependency_graph, dependency_diagnostics = build_dependency_graph(results)
        _version_graph, version_diagnostics = build_version_graph(dependency_graph)
        self.assertEqual(dependency_diagnostics + version_diagnostics, [])


if __name__ == "__main__":
    unittest.main()
