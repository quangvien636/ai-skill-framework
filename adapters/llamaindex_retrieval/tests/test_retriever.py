import unittest

import _bootstrap

from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry
from llamaindex_retrieval import (
    KnowledgeRetriever,
    LocalHashingEmbedding,
    compile_retrieval_config,
)


KNOWLEDGE_DOCS = (
    _bootstrap.REPO_ROOT
    / "knowledge/creative/content/formats/content-structures.md",
    _bootstrap.REPO_ROOT
    / "knowledge/creative/content/style/tone-guidelines.md",
)


def _config(top_k=2):
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    results = [build_ir("knowledge", path, registry) for path in KNOWLEDGE_DOCS]
    assert all(result.ok for result in results)
    return compile_retrieval_config(
        [result.ir for result in results], similarity_top_k=top_k
    )


class KnowledgeRetrieverTests(unittest.TestCase):
    def test_real_index_ranks_relevant_document_and_preserves_metadata(self):
        result = KnowledgeRetriever().query(
            _config(), "tone audience voice clear conversational style"
        )

        self.assertEqual(len(result.matches), 2)
        self.assertEqual(
            result.matches[0].document_id,
            "kb:creative:content:style:tone-guidelines",
        )
        self.assertEqual(
            result.matches[0].metadata["id"], result.matches[0].document_id
        )
        self.assertIn("Tone Guidelines", result.matches[0].text)
        self.assertIsInstance(result.matches[0].score, float)

    def test_similarity_top_k_limits_real_retrieval(self):
        result = KnowledgeRetriever().query(
            _config(top_k=1), "content format structure"
        )
        self.assertEqual(len(result.matches), 1)
        self.assertEqual(
            result.matches[0].document_id,
            "kb:creative:content:formats:content-structures",
        )

    def test_retrieval_is_deterministic(self):
        retriever = KnowledgeRetriever()
        first = retriever.query(_config(), "tone voice")
        second = retriever.query(_config(), "tone voice")
        self.assertEqual(first, second)

    def test_empty_config_returns_empty_result_without_index(self):
        empty = compile_retrieval_config([])
        result = KnowledgeRetriever().query(empty, "anything")
        self.assertEqual(result.matches, ())

    def test_blank_query_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must not be blank"):
            KnowledgeRetriever().query(_config(), "  ")

    def test_local_embedding_is_content_sensitive_and_fixed_size(self):
        embedding = LocalHashingEmbedding(dimensions=256)
        first = embedding.get_text_embedding("tone and audience")
        second = embedding.get_text_embedding("vector database indexing")
        self.assertEqual(len(first), 256)
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()

