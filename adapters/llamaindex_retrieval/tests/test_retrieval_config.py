import unittest

import _bootstrap

from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry
from llamaindex_retrieval.retrieval_config import (
    compile_retrieval_config,
    knowledge_ir_to_document,
    retrieval_config_from_runtime,
)

KNOWLEDGE_DOCS = (
    _bootstrap.REPO_ROOT / "knowledge" / "creative" / "content" / "formats" / "content-structures.md",
    _bootstrap.REPO_ROOT / "knowledge" / "creative" / "content" / "style" / "tone-guidelines.md",
)

RUNTIME_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph" / "valid-runtime"


def _load_knowledge(path):
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    result = build_ir("knowledge", path, registry)
    assert result.ok, result.diagnostics
    return result.ir


class RetrievalConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.knowledge_docs = [_load_knowledge(path) for path in KNOWLEDGE_DOCS]

    def test_knowledge_ir_translates_to_document_with_stable_text(self):
        knowledge = self.knowledge_docs[0]
        doc = knowledge_ir_to_document(knowledge)

        self.assertEqual(doc.doc_id, knowledge.id)
        self.assertIn(knowledge.title, doc.text)
        self.assertIn(knowledge.guidance, doc.text)
        self.assertEqual(doc.metadata["category"], knowledge.category)
        self.assertEqual(doc.metadata["domain"], knowledge.domain)
        self.assertEqual(doc.metadata["topic"], knowledge.topic)

        # Deterministic: compiling twice from the same IR yields identical text.
        self.assertEqual(knowledge_ir_to_document(knowledge).text, doc.text)

    def test_compile_retrieval_config_preserves_order_and_top_k(self):
        config = compile_retrieval_config(self.knowledge_docs, similarity_top_k=3)

        self.assertEqual(config.knowledge_ids, tuple(k.id for k in self.knowledge_docs))
        self.assertEqual([d.doc_id for d in config.documents], list(config.knowledge_ids))
        self.assertEqual(config.similarity_top_k, 3)

    def test_compile_retrieval_config_defaults_top_k(self):
        config = compile_retrieval_config(self.knowledge_docs)
        self.assertEqual(config.similarity_top_k, 5)

    def test_rejects_non_positive_top_k(self):
        with self.assertRaises(ValueError):
            compile_retrieval_config(self.knowledge_docs, similarity_top_k=0)

    def test_empty_knowledge_docs_compiles_to_empty_config(self):
        config = compile_retrieval_config([])
        self.assertEqual(config.knowledge_ids, ())
        self.assertEqual(config.documents, ())

    def test_retrieval_config_from_runtime_binds_enabled_retriever(self):
        registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
        runtime_result = build_ir("runtime", RUNTIME_FIXTURES / "runtime.yaml", registry)
        assert runtime_result.ok, runtime_result.diagnostics
        brevity = _load_knowledge(RUNTIME_FIXTURES / "knowledge.md")

        config = retrieval_config_from_runtime(runtime_result.ir, [brevity])
        self.assertIsNotNone(config)
        self.assertEqual(config.knowledge_ids, (brevity.id,))
        self.assertEqual(
            config.similarity_top_k, runtime_result.ir.retriever.similarity_top_k
        )

    def test_retrieval_config_from_runtime_returns_none_when_disabled(self):
        registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
        runtime_result = build_ir(
            "runtime", RUNTIME_FIXTURES / "runtime-fallback.yaml", registry
        )
        assert runtime_result.ok, runtime_result.diagnostics
        self.assertFalse(runtime_result.ir.retriever.enabled)
        self.assertIsNone(retrieval_config_from_runtime(runtime_result.ir, []))


if __name__ == "__main__":
    unittest.main()
