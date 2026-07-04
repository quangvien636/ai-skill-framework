import unittest

import _bootstrap

from asf_validator.knowledge_ir import build_knowledge_ir


def _read(name: str) -> str:
    path = _bootstrap.FIXTURES_ROOT / "knowledge" / name
    return path.read_text(encoding="utf-8")


class BuildKnowledgeIrTests(unittest.TestCase):
    def test_valid_document_normalizes_every_field(self):
        text = _read("valid.md")
        knowledge, diagnostics = build_knowledge_ir(text, "test")
        self.assertEqual(diagnostics, [])
        self.assertEqual(knowledge.id, "kb:technical:databases:indexing:index-selection")
        self.assertEqual(knowledge.title, "Index Selection")
        self.assertEqual(knowledge.status, "draft")
        self.assertEqual(knowledge.category, "technical")
        self.assertIn("skill:optimize-query", knowledge.applies_to)
        self.assertIn("Single-column and composite index selection.", knowledge.scope_includes)
        self.assertIn("Storage-engine-specific index tuning.", knowledge.scope_excludes)
        self.assertEqual(len(knowledge.decision_rules), 2)
        self.assertTrue(knowledge.examples_good.startswith("Measuring a slow query"))
        self.assertTrue(knowledge.examples_counterexample.startswith("Indexing every column"))
        self.assertEqual(len(knowledge.revision_history), 1)
        self.assertEqual(knowledge.revision_history[0].version, "0.1.0")

    def test_normalized_dict_matches_schema_field_names(self):
        text = _read("valid.md")
        knowledge, _ = build_knowledge_ir(text, "test")
        normalized = knowledge.as_normalized_dict()
        for key in (
            "id", "title", "status", "category", "domain", "topic", "version",
            "last_updated", "summary", "applies_to", "scope", "guidance",
            "decision_rules", "examples", "limitations_and_risks",
            "related_knowledge", "sources", "revision_history",
        ):
            self.assertIn(key, normalized)

    def test_missing_section_blocks_ir(self):
        text = _read("missing_required.md")
        knowledge, diagnostics = build_knowledge_ir(text, "test")
        self.assertIsNone(knowledge)
        self.assertTrue(any(d.code == "ASF-PARSE-003" for d in diagnostics))

    def test_status_bullet_is_lowercased(self):
        text = _read("valid.md")
        self.assertIn("**Status:** Draft", text)  # source keeps title case
        knowledge, _ = build_knowledge_ir(text, "test")
        self.assertEqual(knowledge.status, "draft")  # normalized to schema enum


if __name__ == "__main__":
    unittest.main()
