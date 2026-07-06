import _bootstrap  # noqa: F401  (adds scripts/ and adapters/ to sys.path)

from ollama_execution.tokenization import (
    DEFAULT_TOKENIZER,
    DEFAULT_TOKENIZER_REGISTRY,
    TokenizerRegistry,
    WhitespaceRegexTokenizer,
    strip_diacritics,
)


def test_strip_diacritics_normalizes_vietnamese_text():
    assert strip_diacritics("đáng sợ") == "dang so"


def test_strip_diacritics_handles_the_d_stroke_specially():
    # "đ" (U+0111) does not decompose under Unicode NFD like other
    # diacritics, so it needs an explicit translation to a plain "d".
    assert strip_diacritics("đến được để") == "den duoc de"


def test_tokenizer_splits_on_alphanumeric_runs_and_casefolds():
    tokenizer = WhitespaceRegexTokenizer()
    tokens = tokenizer.tokenize("5 Scariest AI-Technologies, Really!")
    assert tokens == ("5", "scariest", "ai", "technologies", "really")


def test_tokenizer_diacritic_stripping_is_deterministic_and_idempotent():
    tokenizer = WhitespaceRegexTokenizer()
    first = tokenizer.tokenize("Công nghệ AI đáng sợ nhất")
    second = tokenizer.tokenize("Công nghệ AI đáng sợ nhất")
    assert first == second
    assert "ai" in first


def test_tokenizer_can_disable_diacritic_stripping():
    tokenizer = WhitespaceRegexTokenizer(strip_diacritics_enabled=False)
    tokens = tokenizer.tokenize("café")
    assert "café" not in tokens  # "é" is not in [a-z0-9], so it splits the word
    assert tokens == ("caf",)


def test_empty_text_tokenizes_to_empty_tuple():
    assert WhitespaceRegexTokenizer().tokenize("") == ()
    assert WhitespaceRegexTokenizer().tokenize("   ") == ()


def test_default_tokenizer_instance_is_a_whitespace_regex_tokenizer():
    assert isinstance(DEFAULT_TOKENIZER, WhitespaceRegexTokenizer)


def test_registry_resolves_known_languages():
    registry = TokenizerRegistry()
    english = WhitespaceRegexTokenizer()
    registry.register("en", english)
    assert registry.get("en") is english


def test_registry_falls_back_to_default_for_unknown_language():
    registry = TokenizerRegistry(default=DEFAULT_TOKENIZER)
    assert registry.get("xx-unknown") is DEFAULT_TOKENIZER
    assert registry.get(None) is DEFAULT_TOKENIZER


def test_registry_language_lookup_is_case_insensitive():
    registry = TokenizerRegistry()
    tokenizer = WhitespaceRegexTokenizer()
    registry.register("EN", tokenizer)
    assert registry.get("en") is tokenizer


def test_default_registry_has_english_and_vietnamese_preregistered():
    assert DEFAULT_TOKENIZER_REGISTRY.get("en") is not None
    assert DEFAULT_TOKENIZER_REGISTRY.get("vi") is not None


def test_future_multilingual_tokenizer_can_be_registered_without_code_changes():
    class ReverseTokenizer:
        """Stand-in for a hypothetical future language-specific tokenizer."""

        def tokenize(self, text: str) -> tuple:
            return tuple(reversed(text.split()))

    registry = TokenizerRegistry()
    registry.register("zz", ReverseTokenizer())
    assert registry.get("zz").tokenize("one two three") == ("three", "two", "one")
