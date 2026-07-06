"""Deterministic, dependency-free scaffolding for optional semantic
(embedding-based) topic-relevance validation.

Everything here is inert by default: :class:`NullEmbeddingProvider` returns
an empty vector, :class:`NullTopicClassifier` never assigns a label, and
:class:`SemanticRelevanceValidator` is constructed with ``enabled=False``.
No network call, no bundled ML model, and no additional runtime dependency
exists anywhere in this module.

Wiring in a real embedding model later
---------------------------------------
1. Implement :class:`EmbeddingProvider` (``embed(text) -> tuple[float,
   ...]``) wrapping a real model or API client (e.g. BGE, E5, MiniLM).
2. Reuse :class:`CosineSimilarity` (pure arithmetic, works for any vector
   size), or implement :class:`SemanticSimilarity` yourself.
3. Construct ``SemanticRelevanceValidator(embedding_provider=...,
   similarity=..., threshold=..., enabled=True)`` and pass it to
   :func:`ollama_execution.topic_relevance.evaluate_topic_relevance` as
   ``semantic_validator``.

``runner.py`` never needs to change for step 3 to take effect: it only
calls ``evaluate_topic_relevance``, which already accepts an optional
semantic validator.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Protocol, Sequence


class EmbeddingProvider(Protocol):
    """Turns text into a fixed-size numeric vector."""

    def embed(self, text: str) -> tuple[float, ...]: ...


class SemanticSimilarity(Protocol):
    """Scores similarity between two embedding vectors, typically in [0, 1]."""

    def similarity(self, a: Sequence[float], b: Sequence[float]) -> float: ...


class TopicClassifier(Protocol):
    """Assigns free text to a single best-matching topic/domain label."""

    def classify(self, text: str) -> Optional[str]: ...


class NullEmbeddingProvider:
    """Deterministic no-op provider: always returns an empty vector.

    The default provider, so the semantic validator never allocates a real
    vector, never calls a network, and never loads a model unless a caller
    deliberately injects a concrete provider.
    """

    def embed(self, text: str) -> tuple[float, ...]:
        return ()


class CosineSimilarity:
    """Real, deterministic cosine similarity -- pure arithmetic, no model."""

    def similarity(self, a: Sequence[float], b: Sequence[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)


class NullTopicClassifier:
    """Deterministic no-op classifier: never assigns a topic label."""

    def classify(self, text: str) -> Optional[str]:
        return None


@dataclass(frozen=True)
class SemanticEvaluation:
    """Raw outcome of one semantic pass, before it is folded into a
    ``TopicRelevanceResult`` by :mod:`.topic_relevance`.
    """

    passed: bool
    score: Optional[float]
    reason: Optional[str] = None


class SemanticRelevanceValidator:
    """Embedding-based relevance check; inert by construction unless enabled.

    Dependency-injected (embedding provider + similarity metric +
    threshold) rather than subclassed: plugging in a real model is a
    constructor argument, never a code change to this class.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider = NullEmbeddingProvider(),
        similarity: SemanticSimilarity = CosineSimilarity(),
        threshold: float = 0.75,
        enabled: bool = False,
    ):
        self.embedding_provider = embedding_provider
        self.similarity = similarity
        self.threshold = threshold
        self.enabled = enabled

    def evaluate(self, topic: str, text: str) -> SemanticEvaluation:
        topic_vector = self.embedding_provider.embed(topic)
        text_vector = self.embedding_provider.embed(text)
        if not topic_vector or not text_vector:
            return SemanticEvaluation(
                passed=True,
                score=None,
                reason="semantic validator has no usable embeddings; skipped",
            )
        score = self.similarity.similarity(topic_vector, text_vector)
        if score < self.threshold:
            return SemanticEvaluation(
                passed=False,
                score=score,
                reason=(
                    f"semantic similarity {score:.3f} is below threshold "
                    f"{self.threshold:.3f}"
                ),
            )
        return SemanticEvaluation(passed=True, score=score)


# Backward-compatible name: earlier revisions exposed a disabled-by-default
# stub under this exact name. Aliasing it to SemanticRelevanceValidator keeps
# existing imports/constructions working (`OptionalSemanticRelevanceValidator()`
# with no arguments still yields a disabled, inert instance) while the
# implementation is now a real (if inert-by-default) validator instead of a
# stub that raises if ever invoked.
OptionalSemanticRelevanceValidator = SemanticRelevanceValidator
