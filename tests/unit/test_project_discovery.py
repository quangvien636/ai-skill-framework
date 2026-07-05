import tempfile
import unittest
from pathlib import Path

import _bootstrap

from asf_validator.project_discovery import discover_project


class ProjectDiscoveryTests(unittest.TestCase):
    def test_real_repository_index_has_canonical_artifact_counts(self):
        index = discover_project(_bootstrap.REPO_ROOT)
        self.assertEqual(len(index.by_kind("skill")), 3)
        self.assertEqual(len(index.by_kind("workflow")), 3)
        self.assertEqual(len(index.by_kind("knowledge")), 18)
        self.assertEqual(len(index.by_kind("evaluation")), 3)
        self.assertEqual(len(index.by_kind("reflection")), 3)
        self.assertEqual(len(index.by_kind("example")), 12)
        self.assertEqual(len(index.by_kind("tool")), 0)
        self.assertEqual(len(index.by_kind("connector")), 0)

    def test_evaluation_and_reflection_are_embedded_skill_locations(self):
        index = discover_project(
            _bootstrap.REPO_ROOT, kinds=("evaluation", "reflection")
        )
        self.assertTrue(index.artifacts)
        self.assertTrue(all(artifact.is_embedded for artifact in index.artifacts))
        self.assertEqual(
            {artifact.embedded_section for artifact in index.artifacts},
            {"evaluation", "reflection"},
        )
        self.assertTrue(
            all(artifact.path.name == "skill.yaml" for artifact in index.artifacts)
        )

    def test_kind_selection_is_lazy_and_does_not_add_other_kinds(self):
        index = discover_project(_bootstrap.REPO_ROOT, kinds=("workflow",))
        self.assertEqual(len(index.artifacts), 3)
        self.assertTrue(all(artifact.kind == "workflow" for artifact in index.artifacts))
        self.assertEqual(index.by_kind("skill"), ())

    def test_knowledge_excludes_templates_and_navigation_documents(self):
        index = discover_project(_bootstrap.REPO_ROOT, kinds=("knowledge",))
        relative = {index.relative_path(artifact).as_posix() for artifact in index.artifacts}
        self.assertNotIn("knowledge/_templates/KNOWLEDGE_TEMPLATE.md", relative)
        self.assertNotIn("knowledge/KNOWLEDGE_INDEX.md", relative)
        self.assertIn(
            "knowledge/foundational/research/briefs/research-brief-structure.md",
            relative,
        )

    def test_examples_exclude_readmes_and_are_deterministic(self):
        first = discover_project(_bootstrap.REPO_ROOT, kinds=("example",))
        second = discover_project(_bootstrap.REPO_ROOT, kinds=("example",))
        self.assertEqual(first, second)
        self.assertTrue(
            all(artifact.path.name != "README.md" for artifact in first.artifacts)
        )

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            discover_project(_bootstrap.REPO_ROOT, kinds=("fake_kind",))

    def test_discovery_enumerates_without_parsing_invalid_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "broken" / "skill.yaml"
            skill.parent.mkdir(parents=True)
            skill.write_text(": not valid: yaml: [", encoding="utf-8")
            index = discover_project(root, kinds=("skill",))
            self.assertEqual([artifact.path for artifact in index.artifacts], [skill])


if __name__ == "__main__":
    unittest.main()
