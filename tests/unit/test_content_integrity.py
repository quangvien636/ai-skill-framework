import tempfile
import unittest
from pathlib import Path

import _bootstrap

from asf_validator.content_integrity import validate_content_integrity
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import ProjectIndex, discover_project
from asf_validator.schema_registry import build_schema_registry


class ContentIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)

    def empty_index(self, root):
        return ProjectIndex(Path(root).resolve(), ())

    def test_missing_link_anchor_duplicate_anchor_and_adr_are_structured(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "doc.md").write_text(
                "# Same\n\n## Same\n\n[missing](missing.md)\n"
                "[anchor](#not-present)\nADR-9999\n",
                encoding="utf-8",
            )
            codes = {
                item.code
                for item in validate_content_integrity(self.empty_index(root), [])
            }
            self.assertEqual(
                codes,
                {
                    "ASF-REPOSITORY-006",
                    "ASF-REPOSITORY-007",
                    "ASF-REPOSITORY-008",
                    "ASF-REPOSITORY-009",
                },
            )

    def test_valid_relative_file_and_section_links_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "target.md").write_text("# Target Heading\n", encoding="utf-8")
            (root / "source.md").write_text(
                "[target](target.md#target-heading)\n", encoding="utf-8"
            )
            self.assertEqual(
                validate_content_integrity(self.empty_index(root), []), []
            )

    def test_obvious_secret_and_stale_reference_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            secret = "AKIA" + "A" * 16
            stale = "kb:research:" + "methodology:old"
            (root / "data.txt").write_text(f"{secret}\n{stale}\n", encoding="utf-8")
            codes = {
                item.code
                for item in validate_content_integrity(self.empty_index(root), [])
            }
            self.assertEqual(
                codes, {"ASF-REPOSITORY-011", "ASF-REPOSITORY-013"}
            )

    def test_active_orphan_skill_and_shipped_todo_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "skills" / "mapping-target"
            package.mkdir(parents=True)
            source = (
                _bootstrap.REPO_ROOT
                / "tests/fixtures/semantic/mapping-skill.yaml"
            ).read_text(encoding="utf-8")
            source = source.replace('status: "draft"', 'status: "active"')
            manifest = package / "skill.yaml"
            manifest.write_text(source, encoding="utf-8")
            (package / "README.md").write_text("# Final\n\nTODO\n", encoding="utf-8")
            index = discover_project(root, kinds=("skill", "example"))
            result = build_ir("skill", manifest, self.registry)
            codes = {
                item.code
                for item in validate_content_integrity(index, [result])
            }
            self.assertEqual(
                codes, {"ASF-REPOSITORY-010", "ASF-REPOSITORY-012"}
            )

    def test_active_orphan_runtime_contract_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "runtime" / "orphan"
            package.mkdir(parents=True)
            source = (
                _bootstrap.REPO_ROOT / "tests/fixtures/contracts/runtime/valid.yaml"
            ).read_text(encoding="utf-8")
            source = source.replace('status: "draft"', 'status: "active"')
            manifest = package / "runtime.yaml"
            manifest.write_text(source, encoding="utf-8")
            index = discover_project(root, kinds=("runtime",))
            result = build_ir("runtime", manifest, self.registry)
            codes = {item.code for item in validate_content_integrity(index, [result])}
            self.assertIn("ASF-REPOSITORY-012", codes)

    def test_runtime_referenced_as_fallback_is_not_orphan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = (
                _bootstrap.REPO_ROOT / "tests/fixtures/contracts/runtime/valid.yaml"
            ).read_text(encoding="utf-8")
            active_source = source.replace('status: "draft"', 'status: "active"')

            primary = root / "runtime" / "primary" / "runtime.yaml"
            primary.parent.mkdir(parents=True)
            primary.write_text(
                active_source.replace(
                    'fallback_profile:\n  enabled: false\n  max_fallback_depth: 1\n',
                    'fallback_profile:\n  enabled: true\n  fallback_runtime:\n'
                    '    id: "runtime:target"\n    version: "1.0.0"\n    required: true\n'
                    '  max_fallback_depth: 1\n',
                ),
                encoding="utf-8",
            )
            target = root / "runtime" / "target" / "runtime.yaml"
            target.parent.mkdir(parents=True)
            target.write_text(
                active_source.replace('runtime:simple', 'runtime:target').replace(
                    'name: "simple"', 'name: "target"'
                ),
                encoding="utf-8",
            )

            index = discover_project(root, kinds=("runtime",))
            results = [
                build_ir("runtime", primary, self.registry),
                build_ir("runtime", target, self.registry),
            ]
            self.assertTrue(all(result.ok for result in results))
            diagnostics = validate_content_integrity(index, results)
            orphaned_ids = {
                d.artifact for d in diagnostics if d.code == "ASF-REPOSITORY-012"
            }
            # "runtime:primary" has no consumer either and is expected to be
            # flagged; the point of this test is that "runtime:target" is not,
            # because it is referenced as another active Runtime's fallback.
            self.assertNotIn("runtime:target", orphaned_ids)

    def test_draft_artifact_placeholder_is_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "skills" / "mapping-target" / "skill.yaml"
            manifest.parent.mkdir(parents=True)
            source = (
                _bootstrap.REPO_ROOT
                / "tests/fixtures/semantic/mapping-skill.yaml"
            ).read_text(encoding="utf-8")
            manifest.write_text(source, encoding="utf-8")
            (manifest.parent / "README.md").write_text("# Draft\n\nTODO\n", encoding="utf-8")
            index = discover_project(root, kinds=("skill",))
            result = build_ir("skill", manifest, self.registry)
            diagnostics = validate_content_integrity(index, [result])
            self.assertNotIn(
                "ASF-REPOSITORY-010",
                {diagnostic.code for diagnostic in diagnostics},
            )


if __name__ == "__main__":
    unittest.main()
