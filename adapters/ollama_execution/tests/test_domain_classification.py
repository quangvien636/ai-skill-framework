import _bootstrap  # noqa: F401  (adds scripts/ and adapters/ to sys.path)

from ollama_execution.domain_classification import (
    KeywordDomainClassifier,
    NullDomainClassifier,
)


def test_null_domain_classifier_never_matches_anything():
    classifier = NullDomainClassifier()
    assert classifier.matches("AI, finance, travel, anything at all") == frozenset()


def test_keyword_domain_classifier_requires_minimum_occurrences():
    classifier = KeywordDomainClassifier(
        domain_terms={"finance": ("stock market", "crypto")},
        min_occurrences=2,
    )
    # Only one indicator occurrence: must not match yet.
    assert classifier.matches("The stock market moved today.") == frozenset()
    # Two occurrences (either the same phrase twice or two different ones).
    assert classifier.matches(
        "The stock market and crypto both moved today."
    ) == frozenset({"finance"})


def test_keyword_domain_classifier_supports_arbitrary_configured_domains():
    domain_terms = {
        "finance": ("stock market", "day trading"),
        "travel": ("flight booking", "travel itinerary"),
        "gaming": ("esports tournament", "battle royale"),
        "medicine": ("clinical trial", "patient diagnosis"),
        "education": ("student curriculum", "classroom lesson"),
        "politics": ("election campaign", "policy debate"),
        "recipe": ("cooking instructions", "recipe ingredients"),
        "religion": ("religious ceremony", "sacred scripture"),
        "environment": ("climate change", "greenhouse gas"),
    }
    classifier = KeywordDomainClassifier(domain_terms, min_occurrences=2)
    text = (
        "This flight booking guide covers travel itinerary planning for "
        "your next trip."
    )
    assert classifier.matches(text) == frozenset({"travel"})


def test_keyword_domain_classifier_can_match_multiple_domains_at_once():
    domain_terms = {
        "finance": ("stock market", "day trading"),
        "gaming": ("esports tournament", "battle royale"),
    }
    classifier = KeywordDomainClassifier(domain_terms, min_occurrences=1)
    text = "The stock market reacted after an esports tournament sponsorship deal."
    assert classifier.matches(text) == frozenset({"finance", "gaming"})


def test_keyword_domain_classifier_matches_are_diacritic_insensitive():
    classifier = KeywordDomainClassifier(
        domain_terms={"environment": ("bien doi khi hau", "moi truong")},
        min_occurrences=1,
    )
    text = "Chúng ta cần ứng phó với biến đổi khí hậu ngay từ bây giờ."
    assert classifier.matches(text) == frozenset({"environment"})


def test_keyword_domain_classifier_with_no_domains_configured_never_matches():
    classifier = KeywordDomainClassifier(domain_terms={}, min_occurrences=1)
    assert classifier.matches("anything") == frozenset()


def test_keyword_domain_classifier_respects_custom_min_occurrences_threshold():
    domain_terms = {"finance": ("money",)}
    lenient = KeywordDomainClassifier(domain_terms, min_occurrences=1)
    strict = KeywordDomainClassifier(domain_terms, min_occurrences=3)
    text = "Money matters, and money talks, but it is still just money."
    assert lenient.matches(text) == frozenset({"finance"})
    assert strict.matches(text) == frozenset({"finance"})  # exactly 3 occurrences
    stricter = KeywordDomainClassifier(domain_terms, min_occurrences=4)
    assert stricter.matches(text) == frozenset()
