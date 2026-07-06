"""Generic, config-driven domain detection for topic-relevance scoring.

A "domain" is nothing more than a label (``"ai"``, ``"finance"``,
``"travel"``, ``"medicine"``, ...) mapped to a tuple of indicator phrases in
:class:`~.topic_relevance_config.TopicRelevanceConfig`. This module never
hard-codes a domain name or an indicator phrase -- add, rename, or remove
domains entirely through configuration, and this code does not change.

Matching is substring-based over normalized text rather than token-set
overlap, because indicator phrases are frequently multi-word (e.g. "climate
change", "day trading"); a token-set comparison would miss them.
"""

from __future__ import annotations

from typing import Mapping, Protocol

from .tokenization import strip_diacritics


class DomainClassifier(Protocol):
    """Tags free text with zero or more configured domain labels."""

    def matches(self, text: str) -> frozenset[str]: ...


class NullDomainClassifier:
    """No-op classifier: matches no domain. Safe default when unconfigured."""

    def matches(self, text: str) -> frozenset[str]:
        return frozenset()


class KeywordDomainClassifier:
    """Flags a domain once enough of its indicator phrases occur in text.

    ``domain_terms`` and ``min_occurrences`` are dependency-injected (from
    :class:`~.topic_relevance_config.TopicRelevanceConfig` by default in
    :mod:`.topic_relevance`) rather than hard-coded, so callers can register
    arbitrary domains -- AI, Finance, Travel, Gaming, Medicine, Education,
    Politics, Recipe, Religion, Environment, or anything else -- purely
    through configuration.
    """

    def __init__(
        self,
        domain_terms: Mapping[str, tuple[str, ...]],
        min_occurrences: int = 2,
    ):
        self._domain_terms = domain_terms
        self._min_occurrences = min_occurrences

    def matches(self, text: str) -> frozenset[str]:
        normalized = strip_diacritics(text.casefold())
        matched = {
            domain
            for domain, indicators in self._domain_terms.items()
            if sum(normalized.count(term) for term in indicators)
            >= self._min_occurrences
        }
        return frozenset(matched)
