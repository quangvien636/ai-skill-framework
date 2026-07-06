"""Generic, config-driven domain detection for topic-relevance scoring.

A "domain" is nothing more than a label (``"ai"``, ``"finance"``,
``"travel"``, ``"medicine"``, ...) mapped to a tuple of indicator phrases in
:class:`~.topic_relevance_config.TopicRelevanceConfig`. This module never
hard-codes a domain name or an indicator phrase -- add, rename, or remove
domains entirely through configuration, and this code does not change.

Matching is word-boundary-anchored over normalized text rather than a bare
substring search or token-set overlap: indicator phrases are frequently
multi-word (e.g. "climate change", "day trading"), which a token-set
comparison would miss, but a bare substring search would also let a
single-word indicator like "car" or "net" match inside unrelated words such
as "cartoon" or "internet". Anchoring both ends of each indicator with
``\\b`` keeps multi-word phrase matching working exactly as before while
eliminating that class of accidental partial-word match.
"""

from __future__ import annotations

import re
from typing import Mapping, Protocol

from .tokenization import strip_diacritics


class DomainClassifier(Protocol):
    """Tags free text with zero or more configured domain labels."""

    def matches(self, text: str) -> frozenset[str]: ...


class NullDomainClassifier:
    """No-op classifier: matches no domain. Safe default when unconfigured."""

    def matches(self, text: str) -> frozenset[str]:
        return frozenset()


def _compile_term_pattern(term: str) -> re.Pattern[str]:
    """Word-boundary-anchor one indicator phrase for whole-word matching."""
    return re.compile(rf"\b{re.escape(term)}\b")


class KeywordDomainClassifier:
    """Flags a domain once enough of its indicator phrases occur in text.

    ``domain_terms`` and ``min_occurrences`` are dependency-injected (from
    :class:`~.topic_relevance_config.TopicRelevanceConfig` by default in
    :mod:`.topic_relevance`) rather than hard-coded, so callers can register
    arbitrary domains -- AI, Finance, Travel, Gaming, Medicine, Education,
    Politics, Recipe, Religion, Environment, or anything else -- purely
    through configuration. Indicator patterns are compiled once per
    instance rather than on every :meth:`matches` call.
    """

    def __init__(
        self,
        domain_terms: Mapping[str, tuple[str, ...]],
        min_occurrences: int = 2,
    ):
        self._min_occurrences = min_occurrences
        self._domain_patterns: dict[str, tuple[re.Pattern[str], ...]] = {
            domain: tuple(_compile_term_pattern(term) for term in terms)
            for domain, terms in domain_terms.items()
        }

    def matches(self, text: str) -> frozenset[str]:
        normalized = strip_diacritics(text.casefold())
        matched = {
            domain
            for domain, patterns in self._domain_patterns.items()
            if sum(len(pattern.findall(normalized)) for pattern in patterns)
            >= self._min_occurrences
        }
        return frozenset(matched)
