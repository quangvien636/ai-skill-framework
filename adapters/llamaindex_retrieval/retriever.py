"""Real, local LlamaIndex retrieval from an ASF ``RetrievalConfig``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import MetadataMode
from pydantic import PrivateAttr
from sklearn.feature_extraction.text import HashingVectorizer

from .retrieval_config import RetrievalConfig


class LocalHashingEmbedding(BaseEmbedding):
    """Deterministic, stateless local embeddings backed by scikit-learn."""

    _vectorizer: HashingVectorizer = PrivateAttr()

    def __init__(self, dimensions: int = 4096) -> None:
        if dimensions < 128:
            raise ValueError("dimensions must be at least 128")
        super().__init__(model_name="sklearn-hashing-vectorizer")
        self._vectorizer = HashingVectorizer(
            n_features=dimensions,
            alternate_sign=False,
            norm="l2",
            ngram_range=(1, 2),
            lowercase=True,
        )

    def _embed(self, texts: Sequence[str]) -> list[list[float]]:
        matrix = self._vectorizer.transform(texts)
        return matrix.toarray().astype(float).tolist()

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._embed((query,))[0]

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._embed((text,))[0]

    def _get_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts)


@dataclass(frozen=True)
class RetrievalMatch:
    document_id: str
    text: str
    metadata: Mapping[str, Any]
    score: float | None


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    matches: tuple[RetrievalMatch, ...]


class KnowledgeRetriever:
    """Build and query a real in-memory LlamaIndex vector index locally."""

    def __init__(self, embed_model: BaseEmbedding | None = None) -> None:
        self._embed_model = embed_model or LocalHashingEmbedding()

    def query(self, config: RetrievalConfig, query: str) -> RetrievalResult:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must not be blank")
        if not config.documents:
            return RetrievalResult(normalized_query, ())

        index = VectorStoreIndex.from_documents(
            list(config.documents),
            embed_model=self._embed_model,
            show_progress=False,
        )
        retriever = index.as_retriever(
            similarity_top_k=config.similarity_top_k
        )
        nodes = retriever.retrieve(normalized_query)
        matches = tuple(
            RetrievalMatch(
                document_id=(
                    str(item.node.ref_doc_id)
                    if item.node.ref_doc_id
                    else str(item.node.metadata.get("id", item.node.node_id))
                ),
                text=item.node.get_content(metadata_mode=MetadataMode.NONE),
                metadata=dict(item.node.metadata),
                score=float(item.score) if item.score is not None else None,
            )
            for item in nodes
        )
        return RetrievalResult(normalized_query, matches)

