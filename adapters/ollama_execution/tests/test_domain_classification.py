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


def test_single_word_indicator_does_not_match_inside_an_unrelated_word():
    # "car" must not fire on "cartoon"; "net" must not fire on "internet".
    classifier = KeywordDomainClassifier(
        domain_terms={"automotive": ("car",), "networking": ("net",)},
        min_occurrences=1,
    )
    text = "We watched a cartoon about the internet and streaming."
    assert classifier.matches(text) == frozenset()


def test_single_word_indicator_still_matches_as_a_whole_word():
    classifier = KeywordDomainClassifier(
        domain_terms={"automotive": ("car",)},
        min_occurrences=1,
    )
    assert classifier.matches("I need to park the car.") == frozenset({"automotive"})


def test_multi_word_phrase_matching_is_unaffected_by_word_boundaries():
    classifier = KeywordDomainClassifier(
        domain_terms={
            "finance": ("financial market",),
            "ai": ("machine learning",),
        },
        min_occurrences=1,
    )
    text = "The financial market is increasingly shaped by machine learning."
    assert classifier.matches(text) == frozenset({"finance", "ai"})


def test_multi_word_phrase_does_not_match_when_a_word_is_extended():
    # "climate change" must not match "climate changed" (trailing "d" is
    # part of the same word, so there is no boundary after "change").
    classifier = KeywordDomainClassifier(
        domain_terms={"environment": ("climate change",)},
        min_occurrences=1,
    )
    assert classifier.matches("The climate changed drastically.") == frozenset()
    assert classifier.matches("The climate change is drastic.") == frozenset(
        {"environment"}
    )


def test_indicator_terms_with_regex_special_characters_do_not_crash():
    classifier = KeywordDomainClassifier(
        domain_terms={"finance": ("c++ trading", "a/b testing")},
        min_occurrences=1,
    )
    assert classifier.matches("We rely on a/b testing for growth.") == frozenset(
        {"finance"}
    )
    assert classifier.matches("No relevant content here.") == frozenset()
