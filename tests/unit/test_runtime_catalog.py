import unittest

import _bootstrap

from asf_runtime.catalog import build_artifact_catalog
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry
from asf_validator.skill_ir import SkillIR
from asf_validator.version_ir import parse_version_range


def production_results():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    index = discover_project(
        _bootstrap.REPO_ROOT, kinds=("skill", "workflow", "knowledge")
    )
    return [
        build_ir(artifact.kind, artifact.path, registry)
        for artifact in index.artifacts
    ]


class RuntimeCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = production_results()
        cls.catalog = build_artifact_catalog(cls.results)

    def test_catalog_contains_all_loadable_production_artifacts(self):
        self.assertEqual(len(self.catalog.artifacts), 24)
        self.assertEqual(len(self.catalog.candidates("skill:content-creation")), 1)
        self.assertEqual(
            len(self.catalog.candidates("workflow:research-topic-to-brief")), 1
        )

    def test_exact_resolution_returns_active_artifact(self):
        artifact = self.catalog.exact("workflow:draft-to-reviewed-package", "1.0.0")
        self.assertEqual(artifact.kind, "workflow")
        self.assertEqual(artifact.status, "active")

    def test_range_resolution_uses_shared_version_rules(self):
        version_range, error = parse_version_range(">=1.0.0 <2.0.0")
        self.assertIsNone(error)
        artifact = self.catalog.resolve("skill:research", version_range)
        self.assertEqual(artifact.version.raw, "1.0.0")

    def test_invalid_ir_results_are_not_cataloged(self):
        invalid = build_ir(
            "skill",
            _bootstrap.REPO_ROOT / "tests/fixtures/ir/skill/missing_required.yaml",
            build_schema_registry(_bootstrap.SCHEMA_ROOT),
        )
        catalog = build_artifact_catalog([invalid])
        self.assertEqual(catalog.artifacts, ())

    def test_missing_exact_version_fails_resolution(self):
        with self.assertRaises(LookupError):
            self.catalog.exact("skill:research", "2.0.0")

    def test_duplicate_catalog_identity_is_rejected(self):
        result = next(
            result
            for result in self.results
            if result.ok
            and isinstance(result.ir, SkillIR)
            and result.ir.metadata.id == "skill:research"
        )
        with self.assertRaises(ValueError):
            build_artifact_catalog([result, result])


if __name__ == "__main__":
    unittest.main()
