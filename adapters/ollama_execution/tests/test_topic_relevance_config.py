import json

import pytest

import _bootstrap  # noqa: F401  (adds scripts/ and adapters/ to sys.path)

from ollama_execution.topic_relevance_config import (
    DEFAULT_TOPIC_RELEVANCE_CONFIG,
    TopicRelevanceConfig,
    TopicRelevanceConfigError,
    TopicRelevanceConfigNotFoundError,
    load_topic_relevance_config,
)


def test_missing_env_and_path_falls_back_to_default(monkeypatch):
    monkeypatch.delenv("ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG", raising=False)
    config = load_topic_relevance_config()
    assert config == DEFAULT_TOPIC_RELEVANCE_CONFIG


def test_env_var_is_used_when_no_explicit_path_given(tmp_path, monkeypatch):
    override = tmp_path / "topic_relevance.json"
    override.write_text(json.dumps({"min_relevance_score": 0.42}), encoding="utf-8")
    monkeypatch.setenv("ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG", str(override))
    config = load_topic_relevance_config()
    assert config.min_relevance_score == 0.42


def test_explicit_path_takes_precedence_over_env_var(tmp_path, monkeypatch):
    env_override = tmp_path / "env.json"
    env_override.write_text(json.dumps({"min_relevance_score": 0.11}), encoding="utf-8")
    monkeypatch.setenv("ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG", str(env_override))

    explicit_override = tmp_path / "explicit.json"
    explicit_override.write_text(
        json.dumps({"min_relevance_score": 0.33}), encoding="utf-8"
    )
    config = load_topic_relevance_config(str(explicit_override))
    assert config.min_relevance_score == 0.33


def test_config_override_merges_instead_of_replacing(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps(
            {
                "min_relevance_score": 0.5,
                "short_keyword_allowlist": ["xr"],
                "domain_terms": {
                    "finance": ["bitcoin", "crypto trading"],
                },
            }
        ),
        encoding="utf-8",
    )
    config = load_topic_relevance_config(str(override))
    assert config.min_relevance_score == 0.5
    assert "xr" in config.short_keyword_allowlist
    assert "ai" in config.short_keyword_allowlist  # union, not replaced
    assert "finance" in config.domain_terms
    assert "environment" in config.domain_terms  # built-in domain still present


def test_legacy_offtopic_drift_terms_key_still_works(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps(
            {"offtopic_drift_terms": {"travel": ["flight booking", "visa requirements"]}}
        ),
        encoding="utf-8",
    )
    config = load_topic_relevance_config(str(override))
    assert "travel" in config.domain_terms
    assert "environment" in config.domain_terms


def test_arbitrary_domains_can_be_added_purely_through_configuration(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps(
            {
                "domain_terms": {
                    "finance": ["stock market", "crypto trading"],
                    "gaming": ["esports tournament", "battle royale"],
                    "medicine": ["clinical trial", "patient diagnosis"],
                }
            }
        ),
        encoding="utf-8",
    )
    config = load_topic_relevance_config(str(override))
    for domain in ("finance", "gaming", "medicine", "environment"):
        assert domain in config.domain_terms


def test_missing_override_file_raises_not_found_error(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    with pytest.raises(FileNotFoundError):
        load_topic_relevance_config(str(missing))
    with pytest.raises(TopicRelevanceConfigNotFoundError):
        load_topic_relevance_config(str(missing))


def test_invalid_json_raises_clear_config_error(tmp_path):
    broken = tmp_path / "broken.json"
    broken.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(TopicRelevanceConfigError, match="not valid JSON"):
        load_topic_relevance_config(str(broken))


def test_non_object_json_raises_clear_config_error(tmp_path):
    not_an_object = tmp_path / "list.json"
    not_an_object.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(TopicRelevanceConfigError, match="JSON object"):
        load_topic_relevance_config(str(not_an_object))


def test_out_of_range_min_relevance_score_raises_clear_config_error(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(json.dumps({"min_relevance_score": 1.5}), encoding="utf-8")
    with pytest.raises(TopicRelevanceConfigError, match="min_relevance_score"):
        load_topic_relevance_config(str(override))


def test_unsupported_config_version_raises_clear_config_error(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(json.dumps({"config_version": "999"}), encoding="utf-8")
    with pytest.raises(TopicRelevanceConfigError, match="config_version"):
        load_topic_relevance_config(str(override))


def test_non_integer_min_domain_indicator_occurrences_raises_clear_config_error(
    tmp_path,
):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps({"min_domain_indicator_occurrences": "two"}), encoding="utf-8"
    )
    with pytest.raises(
        TopicRelevanceConfigError, match="min_domain_indicator_occurrences"
    ):
        load_topic_relevance_config(str(override))


def test_domain_terms_wrong_type_raises_clear_config_error(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(json.dumps({"domain_terms": ["not", "a", "mapping"]}), encoding="utf-8")
    with pytest.raises(TopicRelevanceConfigError, match="domain_terms"):
        load_topic_relevance_config(str(override))


def test_config_is_immutable_and_hashable_fields_are_frozensets():
    with pytest.raises(Exception):
        DEFAULT_TOPIC_RELEVANCE_CONFIG.min_relevance_score = 0.9  # type: ignore[misc]
    assert isinstance(DEFAULT_TOPIC_RELEVANCE_CONFIG.short_keyword_allowlist, frozenset)
    assert isinstance(DEFAULT_TOPIC_RELEVANCE_CONFIG.stopwords, frozenset)


def test_out_of_range_semantic_similarity_threshold_raises_via_override(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps({"semantic_similarity_threshold": -0.1}), encoding="utf-8"
    )
    with pytest.raises(TopicRelevanceConfigError, match="semantic_similarity_threshold"):
        load_topic_relevance_config(str(override))


def test_unknown_top_level_field_is_ignored_but_warns(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps({"min_relevance_score": 0.3, "totally_made_up_field": 42}),
        encoding="utf-8",
    )
    with pytest.warns(UserWarning, match="totally_made_up_field"):
        config = load_topic_relevance_config(str(override))
    # The known field still applies; the unknown one is ignored, not fatal.
    assert config.min_relevance_score == 0.3


def test_no_warning_when_every_field_is_recognized(tmp_path, recwarn):
    override = tmp_path / "topic_relevance.json"
    override.write_text(json.dumps({"min_relevance_score": 0.3}), encoding="utf-8")
    load_topic_relevance_config(str(override))
    assert len(recwarn) == 0


def test_legacy_key_usage_emits_a_deprecation_warning(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps({"offtopic_drift_terms": {"travel": ["flight booking"]}}),
        encoding="utf-8",
    )
    with pytest.warns(DeprecationWarning, match="offtopic_drift_terms"):
        load_topic_relevance_config(str(override))


def test_duplicate_domain_definition_within_one_source_raises(tmp_path):
    override = tmp_path / "topic_relevance.json"
    # "Finance" and "finance" normalize to the same domain label -- ambiguous
    # which one should win, so this must fail loudly rather than pick one.
    override.write_text(
        json.dumps(
            {
                "domain_terms": {
                    "Finance": ["stock market"],
                    "finance": ["crypto trading"],
                }
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(TopicRelevanceConfigError, match="Duplicate domain"):
        load_topic_relevance_config(str(override))


def test_domain_defined_in_both_legacy_and_new_key_warns_and_new_wins(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps(
            {
                "offtopic_drift_terms": {"finance": ["old indicator"]},
                "domain_terms": {"finance": ["new indicator"]},
            }
        ),
        encoding="utf-8",
    )
    with pytest.warns(UserWarning, match="finance"):
        config = load_topic_relevance_config(str(override))
    assert config.domain_terms["finance"] == ("new indicator",)


def test_domain_key_casing_is_normalized_against_built_in_domains(tmp_path):
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps({"domain_terms": {"Environment": ["extra indicator"]}}),
        encoding="utf-8",
    )
    config = load_topic_relevance_config(str(override))
    # "Environment" folds onto the built-in "environment" domain rather than
    # creating a separate, near-duplicate entry.
    assert "Environment" not in config.domain_terms
    assert "extra indicator" in config.domain_terms["environment"]


def test_direct_construction_validates_invariants():
    with pytest.raises(TopicRelevanceConfigError):
        TopicRelevanceConfig(
            config_version="1",
            min_relevance_score=2.0,  # out of [0, 1] range
            min_domain_indicator_occurrences=2,
            semantic_similarity_threshold=0.75,
            short_keyword_allowlist=frozenset(),
            stopwords=frozenset(),
            domain_terms={},
        )
