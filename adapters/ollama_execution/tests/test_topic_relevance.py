import json

import _bootstrap  # noqa: F401  (adds scripts/ and adapters/ to sys.path)

from ollama_execution.topic_relevance import (
    LexicalTopicRelevanceValidator,
    OptionalSemanticRelevanceValidator,
    evaluate_topic_relevance,
)
from ollama_execution.topic_relevance_config import (
    DEFAULT_TOPIC_RELEVANCE_CONFIG,
    load_topic_relevance_config,
)

_VIETNAMESE_AI_TOPIC = "5 công nghệ AI đáng sợ nhất trong 2 năm tới"
_ENGLISH_AI_TOPIC = "5 scariest AI technologies in the next two years"
_UNRELATED_TOPIC = "Best pasta recipes for a family dinner party"


def test_vietnamese_ai_topic_relevant_content_is_accepted():
    text = (
        "5 công nghệ AI đáng sợ nhất: deepfake, AI agent tự động, tấn công "
        "mạng do AI hỗ trợ, giám sát hành vi và thông tin sai lệch quy mô lớn."
    )
    result = evaluate_topic_relevance(_VIETNAMESE_AI_TOPIC, text)
    assert result.relevant is True
    assert result.drift_domain is None


def test_vietnamese_ai_topic_environment_drift_is_rejected():
    text = (
        "Công nghệ AI giúp bảo vệ môi trường và ứng phó biến đổi khí hậu, "
        "theo dõi ô nhiễm và đề xuất năng lượng xanh cho tương lai bền vững."
    )
    result = evaluate_topic_relevance(_VIETNAMESE_AI_TOPIC, text)
    assert result.relevant is False
    assert result.drift_domain == "environmental-protection"


def test_english_ai_topic_relevant_content_is_accepted():
    text = (
        "The 5 scariest AI technologies include deepfakes, autonomous AI "
        "agents, AI-assisted cyberattacks, surveillance, and misinformation."
    )
    result = evaluate_topic_relevance(_ENGLISH_AI_TOPIC, text)
    assert result.relevant is True
    assert result.drift_domain is None


def test_english_ai_topic_environment_drift_is_rejected():
    text = (
        "AI technology helps protect the environment and fight climate "
        "change by tracking greenhouse gas emissions and renewable energy."
    )
    result = evaluate_topic_relevance(_ENGLISH_AI_TOPIC, text)
    assert result.relevant is False
    assert result.drift_domain == "environmental-protection"


def test_completely_unrelated_non_ai_topic_is_rejected():
    text = (
        "The 5 scariest AI technologies include deepfakes, autonomous AI "
        "agents, AI-assisted cyberattacks, surveillance, and misinformation."
    )
    result = evaluate_topic_relevance(_UNRELATED_TOPIC, text)
    assert result.relevant is False
    assert result.drift_domain is None
    assert result.score is not None
    assert result.score < DEFAULT_TOPIC_RELEVANCE_CONFIG.min_relevance_score


def test_short_ai_keywords_are_not_dropped():
    topic = "AI, ML, RAG, LLM, and IoT trends for the next two years"
    validator = LexicalTopicRelevanceValidator()
    keywords = validator._extract_keywords(topic)
    for expected in ("ai", "ml", "rag", "llm", "iot"):
        assert expected in keywords

    text = "This report covers AI, ML, RAG, LLM, and IoT trends in depth."
    result = evaluate_topic_relevance(topic, text)
    assert result.relevant is True


def test_missing_config_falls_back_to_default(monkeypatch):
    monkeypatch.delenv("ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG", raising=False)
    config = load_topic_relevance_config()
    assert config == DEFAULT_TOPIC_RELEVANCE_CONFIG


def test_config_override_merges_instead_of_replacing(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps(
            {
                "min_relevance_score": 0.5,
                "short_keyword_allowlist": ["xr"],
                "offtopic_drift_terms": {
                    "finance-crypto": ["bitcoin", "crypto trading"]
                },
            }
        ),
        encoding="utf-8",
    )
    config = load_topic_relevance_config(str(override))
    assert config.min_relevance_score == 0.5
    assert "xr" in config.short_keyword_allowlist
    assert "ai" in config.short_keyword_allowlist  # union, not replaced
    assert "finance-crypto" in config.offtopic_drift_terms
    assert "environmental-protection" in config.offtopic_drift_terms  # still present


def test_config_override_missing_file_raises(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    try:
        load_topic_relevance_config(str(missing))
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("expected FileNotFoundError for a missing override path")


def test_optional_semantic_validator_is_disabled_by_default():
    validator = OptionalSemanticRelevanceValidator()
    assert validator.enabled is False
    text = (
        "AI technology helps protect the environment and fight climate "
        "change by tracking greenhouse gas emissions and renewable energy."
    )
    # Even when a semantic validator is supplied, a disabled one must never
    # run; the lexical drift result below is what decides relevance.
    result = evaluate_topic_relevance(
        _ENGLISH_AI_TOPIC, text, semantic_validator=validator
    )
    assert result.relevant is False
    assert result.drift_domain == "environmental-protection"
