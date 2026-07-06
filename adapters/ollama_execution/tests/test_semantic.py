import _bootstrap  # noqa: F401  (adds scripts/ and adapters/ to sys.path)

from ollama_execution.semantic import (
    CosineSimilarity,
    NullEmbeddingProvider,
    NullTopicClassifier,
    OptionalSemanticRelevanceValidator,
    SemanticRelevanceValidator,
)


def test_null_embedding_provider_returns_empty_vector():
    assert NullEmbeddingProvider().embed("anything") == ()


def test_null_topic_classifier_never_assigns_a_label():
    assert NullTopicClassifier().classify("anything") is None


def test_cosine_similarity_of_identical_vectors_is_one():
    similarity = CosineSimilarity()
    assert similarity.similarity((1.0, 2.0, 3.0), (1.0, 2.0, 3.0)) == 1.0


def test_cosine_similarity_of_orthogonal_vectors_is_zero():
    similarity = CosineSimilarity()
    assert similarity.similarity((1.0, 0.0), (0.0, 1.0)) == 0.0


def test_cosine_similarity_of_opposite_vectors_is_negative_one():
    similarity = CosineSimilarity()
    assert similarity.similarity((1.0, 0.0), (-1.0, 0.0)) == -1.0


def test_cosine_similarity_handles_zero_vector_without_crashing():
    similarity = CosineSimilarity()
    assert similarity.similarity((0.0, 0.0), (1.0, 1.0)) == 0.0


def test_cosine_similarity_handles_mismatched_length_without_crashing():
    similarity = CosineSimilarity()
    assert similarity.similarity((1.0, 0.0), (1.0, 0.0, 0.0)) == 0.0


def test_cosine_similarity_handles_empty_vectors_without_crashing():
    similarity = CosineSimilarity()
    assert similarity.similarity((), ()) == 0.0


def test_semantic_validator_is_disabled_by_default():
    validator = SemanticRelevanceValidator()
    assert validator.enabled is False


def test_disabled_validator_with_null_provider_never_needs_network_or_model():
    # Constructing and evaluating with every default is safe: no network
    # call, no model load, no exception, purely deterministic arithmetic.
    validator = SemanticRelevanceValidator()
    result = validator.evaluate("any topic", "any text")
    assert result.passed is True
    assert result.score is None


def test_enabled_validator_with_fake_provider_passes_above_threshold():
    class FakeEmbeddingProvider:
        def embed(self, text: str) -> tuple:
            return (1.0, 0.0)

    validator = SemanticRelevanceValidator(
        embedding_provider=FakeEmbeddingProvider(),
        similarity=CosineSimilarity(),
        threshold=0.5,
        enabled=True,
    )
    result = validator.evaluate("topic", "text")
    assert result.passed is True
    assert result.score == 1.0


def test_enabled_validator_with_fake_provider_fails_below_threshold():
    class OrthogonalEmbeddingProvider:
        def embed(self, text: str) -> tuple:
            return (1.0, 0.0) if text == "topic" else (0.0, 1.0)

    validator = SemanticRelevanceValidator(
        embedding_provider=OrthogonalEmbeddingProvider(),
        similarity=CosineSimilarity(),
        threshold=0.5,
        enabled=True,
    )
    result = validator.evaluate("topic", "text")
    assert result.passed is False
    assert result.score == 0.0
    assert "below threshold" in result.reason


def test_optional_semantic_relevance_validator_is_an_alias():
    assert OptionalSemanticRelevanceValidator is SemanticRelevanceValidator
