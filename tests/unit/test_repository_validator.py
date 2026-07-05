import tempfile
import unittest
from pathlib import Path

import _bootstrap

from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import (
    ArtifactLocation,
    ProjectIndex,
    discover_project,
)
from asf_validator.repository_validator import validate_repository
from asf_validator.schema_registry import build_schema_registry


class RepositoryValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)

    def test_real_repository_has_no_integrity_diagnostics(self):
        index = discover_project(_bootstrap.REPO_ROOT)
        results = [
            build_ir(artifact.kind, artifact.path, self.registry)
            for artifact in index.artifacts
            if artifact.kind in ("skill", "workflow", "knowledge")
        ]
        self.assertTrue(all(result.ok for result in results))
        self.assertEqual(validate_repository(index, results), [])

    def test_noncanonical_skill_path_and_missing_package_files_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "wrong-directory" / "skill.yaml"
            skill.parent.mkdir(parents=True)
            source = _bootstrap.REPO_ROOT / "tests/fixtures/semantic/mapping-skill.yaml"
            skill.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            index = discover_project(root, kinds=("skill",))
            result = build_ir("skill", skill, self.registry)
            codes = {item.code for item in validate_repository(index, [result])}
            self.assertEqual(
                codes, {"ASF-REPOSITORY-001", "ASF-REPOSITORY-002"}
            )

    def test_missing_knowledge_index_registration_is_reported(self):
        artifact = next(
            artifact
            for artifact in discover_project(
                _bootstrap.REPO_ROOT, kinds=("knowledge",)
            ).artifacts
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relative = artifact.path.relative_to(_bootstrap.REPO_ROOT)
            target = root / relative
            target.parent.mkdir(parents=True)
            target.write_text(artifact.path.read_text(encoding="utf-8"), encoding="utf-8")
            index = discover_project(root, kinds=("knowledge",))
            result = build_ir("knowledge", target, self.registry)
            codes = {item.code for item in validate_repository(index, [result])}
            self.assertIn("ASF-REPOSITORY-003", codes)

    def test_case_collision_is_reported_for_synthetic_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            first = ArtifactLocation("example", root / "A.yaml")
            second = ArtifactLocation("example", root / "a.yaml")
            index = ProjectIndex(root, (first, second))
            diagnostics = validate_repository(index, [])
            self.assertEqual(
                {diagnostic.code for diagnostic in diagnostics},
                {"ASF-REPOSITORY-005"},
            )


if __name__ == "__main__":
    unittest.main()
