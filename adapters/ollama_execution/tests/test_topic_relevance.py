"""Tests for the topic-relevance orchestration facade.

These exercise ``evaluate_topic_relevance`` end-to-end (lexical + optional
semantic composition) and the rich ``TopicRelevanceResult`` diagnostics.
Tokenizer, domain classifier, and config-loading internals each have their
own focused test module (test_tokenization.py, test_domain_classification.py,
test_topic_relevance_config.py) so this file stays about orchestration.
"""

import pytest

import _bootstrap  # noqa: F401  (adds scripts/ and adapters/ to sys.path)

from ollama_execution.semantic import (
    CosineSimilarity,
    SemanticRelevanceValidator,
)
from ollama_execution.topic_relevance import (
    LexicalTopicRelevanceValidator,
    OptionalSemanticRelevanceValidator,
    evaluate_topic_relevance,
)
from ollama_execution.topic_relevance_config import DEFAULT_TOPIC_RELEVANCE_CONFIG

_VIETNAMESE_AI_TOPIC = "5 công nghệ AI đáng sợ nhất trong 2 năm tới"
_ENGLISH_AI_TOPIC = "5 scariest AI technologies in the next two years"
_UNRELATED_TOPIC = "Best pasta recipes for a family dinner party"

_ENVIRONMENT_DRIFT_TEXT_EN = (
    "AI technology helps protect the environment and fight climate "
    "change by tracking greenhouse gas emissions and renewable energy."
)


def test_vietnamese_ai_topic_relevant_content_is_accepted():
    text = (
        "5 công nghệ AI đáng sợ nhất: deepfake, AI agent tự động, tấn công "
        "mạng do AI hỗ trợ, giám sát hành vi và thông tin sai lệch quy mô lớn."
    )
    result = evaluate_topic_relevance(_VIETNAMESE_AI_TOPIC, text)
    assert result.passed is True
    assert result.relevant is True  # backward-compatible alias
    assert result.drift_domain is None
    assert result.validator_chain == ("lexical",)


def test_vietnamese_ai_topic_environment_drift_is_rejected():
    text = (
        "Công nghệ AI giúp bảo vệ môi trường và ứng phó biến đổi khí hậu, "
        "theo dõi ô nhiễm và đề xuất năng lượng xanh cho tương lai bền vững."
    )
    result = evaluate_topic_relevance(_VIETNAMESE_AI_TOPIC, text)
    assert result.passed is False
    assert result.drift_domain == "environment"
    assert result.domain_score == 0.0
    assert "off-topic" in result.reason


def test_english_ai_topic_relevant_content_is_accepted():
    text = (
        "The 5 scariest AI technologies include deepfakes, autonomous AI "
        "agents, AI-assisted cyberattacks, surveillance, and misinformation."
    )
    result = evaluate_topic_relevance(_ENGLISH_AI_TOPIC, text)
    assert result.passed is True
    assert result.drift_domain is None
    assert "technologies" in result.matched_keywords


def test_english_ai_topic_environment_drift_is_rejected():
    result = evaluate_topic_relevance(_ENGLISH_AI_TOPIC, _ENVIRONMENT_DRIFT_TEXT_EN)
    assert result.passed is False
    assert result.drift_domain == "environment"


def test_completely_unrelated_non_ai_topic_is_rejected():
    text = (
        "The 5 scariest AI technologies include deepfakes, autonomous AI "
        "agents, AI-assisted cyberattacks, surveillance, and misinformation."
    )
    result = evaluate_topic_relevance(_UNRELATED_TOPIC, text)
    assert result.passed is False
    assert result.drift_domain is None
    assert result.score is not None
    assert result.score < DEFAULT_TOPIC_RELEVANCE_CONFIG.min_relevance_score
    assert result.missing_keywords  # diagnostics explain exactly what's missing


def test_short_ai_keywords_are_not_dropped():
    topic = "AI, ML, RAG, LLM, and IoT trends for the next two years"
    text = "This report covers AI, ML, RAG, LLM, and IoT trends in depth."
    result = evaluate_topic_relevance(topic, text)
    assert result.passed is True
    for expected in ("ai", "ml", "rag", "llm", "iot"):
        assert expected in result.matched_keywords


def test_result_as_dict_is_json_ready_for_structured_logging():
    result = evaluate_topic_relevance(_ENGLISH_AI_TOPIC, _ENVIRONMENT_DRIFT_TEXT_EN)
    payload = result.as_dict()
    assert payload["passed"] is False
    assert payload["drift_domain"] == "environment"
    assert isinstance(payload["matched_keywords"], list)
    assert isinstance(payload["missing_keywords"], list)
    assert isinstance(payload["validator_chain"], list)


def test_lexical_rejection_short_circuits_before_semantic_runs():
    calls: list[str] = []

    class RecordingEmbeddingProvider:
        def embed(self, text: str) -> tuple[float, ...]:
            calls.append(text)
            return (1.0, 0.0)

    semantic_validator = SemanticRelevanceValidator(
        embedding_provider=RecordingEmbeddingProvider(),
        similarity=CosineSimilarity(),
        threshold=0.5,
        enabled=True,
    )
    result = evaluate_topic_relevance(
        _ENGLISH_AI_TOPIC, _ENVIRONMENT_DRIFT_TEXT_EN, semantic_validator=semantic_validator
    )
    assert result.passed is False
    assert result.validator_chain == ("lexical",)
    assert calls == []  # semantic validator must never be invoked


def test_disabled_semantic_validator_never_runs_even_when_lexical_passes():
    class FailingEmbeddingProvider:
        def embed(self, text: str) -> tuple[float, ...]:
            raise AssertionError("disabled semantic validator must not embed anything")

    semantic_validator = SemanticRelevanceValidator(
        embedding_provider=FailingEmbeddingProvider(), enabled=False
    )
    text = (
        "The 5 scariest AI technologies include deepfakes, autonomous AI "
        "agents, AI-assisted cyberattacks, surveillance, and misinformation."
    )
    result = evaluate_topic_relevance(
        _ENGLISH_AI_TOPIC, text, semantic_validator=semantic_validator
    )
    assert result.passed is True
    assert result.validator_chain == ("lexical",)


def test_enabled_semantic_validator_can_veto_a_lexically_passing_result():
    class OppositeVectorEmbeddingProvider:
        """Fake provider: topic and text always embed as opposite vectors."""

        def embed(self, text: str) -> tuple[float, ...]:
            return (1.0, 0.0) if text.startswith("TOPIC:") else (-1.0, 0.0)

    semantic_validator = SemanticRelevanceValidator(
        embedding_provider=OppositeVectorEmbeddingProvider(),
        similarity=CosineSimilarity(),
        threshold=0.5,
        enabled=True,
    )
    text = (
        "The 5 scariest AI technologies include deepfakes, autonomous AI "
        "agents, AI-assisted cyberattacks, surveillance, and misinformation."
    )
    result = evaluate_topic_relevance(
        f"TOPIC:{_ENGLISH_AI_TOPIC}", text, semantic_validator=semantic_validator
    )
    assert result.passed is False
    assert result.validator_chain == ("lexical", "semantic")
    assert result.semantic_score == -1.0


def test_enabled_semantic_validator_with_identical_embeddings_passes():
    class ConstantEmbeddingProvider:
        def embed(self, text: str) -> tuple[float, ...]:
            return (1.0, 1.0, 1.0)

    semantic_validator = SemanticRelevanceValidator(
        embedding_provider=ConstantEmbeddingProvider(),
        similarity=CosineSimilarity(),
        threshold=0.9,
        enabled=True,
    )
    text = (
        "The 5 scariest AI technologies include deepfakes, autonomous AI "
        "agents, AI-assisted cyberattacks, surveillance, and misinformation."
    )
    result = evaluate_topic_relevance(
        _ENGLISH_AI_TOPIC, text, semantic_validator=semantic_validator
    )
    assert result.passed is True
    assert result.semantic_score == pytest.approx(1.0)
    assert result.validator_chain == ("lexical", "semantic")


def test_lexical_validator_can_be_constructed_and_evaluated_directly():
    validator = LexicalTopicRelevanceValidator()
    result = validator.evaluate(_ENGLISH_AI_TOPIC, _ENVIRONMENT_DRIFT_TEXT_EN)
    assert result.passed is False
    assert result.drift_domain == "environment"


def test_optional_semantic_validator_is_disabled_by_default():
    validator = OptionalSemanticRelevanceValidator()
    assert validator.enabled is False
    # Even when a semantic validator is supplied, a disabled one must never
    # run; the lexical drift result below is what decides relevance.
    result = evaluate_topic_relevance(
        _ENGLISH_AI_TOPIC, _ENVIRONMENT_DRIFT_TEXT_EN, semantic_validator=validator
    )
    assert result.passed is False
    assert result.drift_domain == "environment"
