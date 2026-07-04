import unittest

import _bootstrap
import yaml

from asf_validator.skill_ir import build_skill_ir


def _load(name: str) -> dict:
    path = _bootstrap.FIXTURES_ROOT / "skill" / name
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class BuildSkillIrTests(unittest.TestCase):
    def test_valid_skill_builds_ir_with_no_diagnostics(self):
        doc = _load("valid.yaml")
        skill, diagnostics = build_skill_ir(doc, "test")
        self.assertEqual(diagnostics, [])
        self.assertEqual(skill.responsibility, "Summarize one document without external research.")
        self.assertEqual(skill.metadata.name, "summarize-document")
        self.assertEqual(len(skill.dependencies.knowledge), 1)
        self.assertEqual(skill.dependencies.knowledge[0].id, "kb:technical:writing:summarization:brevity")
        self.assertEqual(skill.inputs["document"].type, "string")
        self.assertEqual(skill.outputs["summary"].required, True)
        self.assertEqual(skill.evaluation.acceptance.minimum_score, 80)
        self.assertFalse(skill.reflection.enabled)

    def test_unsupported_schema_version_blocks_ir(self):
        doc = _load("unsupported_version.yaml")
        skill, diagnostics = build_skill_ir(doc, "test")
        self.assertIsNone(skill)
        self.assertTrue(any(d.code == "ASF-PARSE-002" for d in diagnostics))

    def test_id_name_mismatch_blocks_ir(self):
        doc = _load("malformed_metadata.yaml")
        skill, diagnostics = build_skill_ir(doc, "test")
        self.assertIsNone(skill)
        self.assertTrue(any(d.code == "ASF-PARSE-005" for d in diagnostics))


if __name__ == "__main__":
    unittest.main()
