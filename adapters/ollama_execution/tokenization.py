"""Deterministic text tokenization for topic-relevance scoring.

Tokenization is intentionally simple and dependency-free: no external NLP
libraries, no network, no model downloads. :class:`WhitespaceRegexTokenizer`
case-folds, strips diacritics, and splits on runs of alphanumeric
characters. That is an acceptable deterministic baseline for both English
and Vietnamese: diacritic stripping is a no-op on ASCII English text, and it
lets Vietnamese words match regardless of accent marks. It is *not* true
word segmentation -- multi-syllable Vietnamese words are still split per
syllable -- which is a known, accepted limitation of a dependency-free
lexical baseline.

Extension point
----------------
Register a smarter tokenizer per language (a real Vietnamese
word-segmenter, a CJK tokenizer, etc.) by implementing the ``Tokenizer``
protocol and calling ``TokenizerRegistry.register(language, tokenizer)``.

Note: :class:`~.topic_relevance.LexicalTopicRelevanceValidator` currently
takes a single ``Tokenizer`` via constructor injection (default
``DEFAULT_TOKENIZER``); it does not yet resolve a tokenizer per-language
through this registry, since nothing upstream currently tracks the
topic/text language. The registry exists so that wiring -- resolve a
language, call ``registry.get(language)``, pass the result as the
``tokenizer=`` argument -- can be added later without changing this
module or the ``Tokenizer`` protocol itself.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Protocol


class Tokenizer(Protocol):
    """Splits text into normalized tokens usable for keyword comparison."""

    def tokenize(self, text: str) -> tuple[str, ...]: ...


_VIETNAMESE_D_STROKE = str.maketrans({"đ": "d", "Đ": "D"})


def strip_diacritics(text: str) -> str:
    """Remove diacritical marks, including the Vietnamese "đ" stroke.

    Vietnamese "đ" (U+0111) does not decompose under Unicode NFD -- it is an
    atomic code point, not "d" plus a combining mark -- so a plain NFD strip
    silently leaves it untouched. That previously made stopwords derived
    from "đ"-initial words (e.g. "được" -> "duoc") impossible to match. It
    is translated to a plain "d" explicitly before the general NFD strip.
    """
    translated = text.translate(_VIETNAMESE_D_STROKE)
    decomposed = unicodedata.normalize("NFD", translated)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


class WhitespaceRegexTokenizer:
    """Default deterministic tokenizer: casefold, optionally strip diacritics,
    then split on runs of ``[a-z0-9]``.
    """

    _TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

    def __init__(self, strip_diacritics_enabled: bool = True):
        self._strip_diacritics_enabled = strip_diacritics_enabled

    def tokenize(self, text: str) -> tuple[str, ...]:
        normalized = text.casefold()
        if self._strip_diacritics_enabled:
            normalized = strip_diacritics(normalized)
        return tuple(self._TOKEN_PATTERN.findall(normalized))


DEFAULT_TOKENIZER = WhitespaceRegexTokenizer()


class TokenizerRegistry:
    """Resolves a language code to a :class:`Tokenizer`, with a safe default.

    Pre-registered with ``en`` and ``vi`` (both using the default
    dependency-free tokenizer today). Adding a future multilingual
    tokenizer -- or a better Vietnamese segmenter -- is a call to
    :meth:`register`; no other module needs to change.
    """

    def __init__(self, default: Tokenizer = DEFAULT_TOKENIZER):
        self._default = default
        self._by_language: dict[str, Tokenizer] = {}

    def register(self, language: str, tokenizer: Tokenizer) -> None:
        self._by_language[language.lower()] = tokenizer

    def get(self, language: str | None) -> Tokenizer:
        if language is None:
            return self._default
        return self._by_language.get(language.lower(), self._default)


DEFAULT_TOKENIZER_REGISTRY = TokenizerRegistry()
DEFAULT_TOKENIZER_REGISTRY.register("en", WhitespaceRegexTokenizer())
DEFAULT_TOKENIZER_REGISTRY.register("vi", WhitespaceRegexTokenizer())
