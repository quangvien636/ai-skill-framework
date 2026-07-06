"""Pluggable topic-relevance validation for generated Ollama step output.

Two validators compose to decide whether generated text stayed on-topic:

- ``LexicalTopicRelevanceValidator``: deterministic keyword-overlap and
  known-domain-drift detection. No network, no model, no randomness. Always
  runs.
- ``OptionalSemanticRelevanceValidator``: a disabled-by-default stub. To wire
  in a real embedding model later (e.g. BGE, E5, MiniLM), subclass it (or
  implement the ``TopicRelevanceValidator`` protocol directly), embed
  ``topic`` and ``text``, threshold a cosine-similarity score into a
  ``TopicRelevanceResult``, then set ``enabled = True`` and pass the
  instance to :func:`evaluate_topic_relevance` as ``semantic_validator``.
  Nothing else in the adapter needs to change. Left disabled here so the
  adapter stays dependency-free, network-free, and fast by default.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional, Protocol

from .topic_relevance_config import DEFAULT_TOPIC_RELEVANCE_CONFIG, TopicRelevanceConfig


@dataclass(frozen=True)
class TopicRelevanceResult:
    relevant: bool
    reason: Optional[str] = None
    drift_domain: Optional[str] = None
    score: Optional[float] = None


class TopicRelevanceValidator(Protocol):
    """Interface any relevance validator (lexical or semantic) implements."""

    def evaluate(self, topic: str, text: str) -> TopicRelevanceResult: ...


def _normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


class LexicalTopicRelevanceValidator:
    """Deterministic keyword-overlap and known-drift-domain detector."""

    def __init__(self, config: TopicRelevanceConfig = DEFAULT_TOPIC_RELEVANCE_CONFIG):
        self._config = config

    def _extract_keywords(self, text: str) -> set[str]:
        normalized = _normalize_text(text)
        tokens = re.findall(r"[a-z0-9]+", normalized)
        keywords: set[str] = set()
        for token in tokens:
            if token in self._config.short_keyword_allowlist:
                keywords.add(token)
            elif len(token) >= 3 and token not in self._config.stopwords:
                keywords.add(token)
        return keywords

    def _detect_offtopic_drift(self, topic: str, text: str) -> Optional[str]:
        topic_normalized = _normalize_text(topic)
        text_normalized = _normalize_text(text)
        for domain, indicators in self._config.offtopic_drift_terms.items():
            if any(term in topic_normalized for term in indicators):
                continue
            occurrences = sum(text_normalized.count(term) for term in indicators)
            if occurrences >= 2:
                return domain
        return None

    def evaluate(self, topic: str, text: str) -> TopicRelevanceResult:
        drift = self._detect_offtopic_drift(topic, text)
        if drift is not None:
            return TopicRelevanceResult(
                relevant=False,
                reason=(
                    f"drifted to an off-topic '{drift}' subject unrelated to "
                    f"the requested topic '{topic}'"
                ),
                drift_domain=drift,
            )
        topic_keywords = self._extract_keywords(topic)
        if not topic_keywords:
            return TopicRelevanceResult(relevant=True, score=None)
        text_normalized = _normalize_text(text)
        hits = sum(1 for keyword in topic_keywords if keyword in text_normalized)
        score = hits / len(topic_keywords)
        if score < self._config.min_relevance_score:
            return TopicRelevanceResult(
                relevant=False,
                reason=(
                    "does not appear relevant to the requested topic "
                    f"'{topic}' (keyword overlap too low)"
                ),
                score=score,
            )
        return TopicRelevanceResult(relevant=True, score=score)


class OptionalSemanticRelevanceValidator:
    """Disabled-by-default hook for an embedding-based relevance check.

    Wire in a real model by subclassing this (or implementing
    ``TopicRelevanceValidator`` directly): override ``evaluate`` to embed
    ``topic`` and ``text`` with a model such as BGE/E5/MiniLM, threshold
    cosine similarity, and return a ``TopicRelevanceResult``. Then set
    ``enabled = True`` on the instance and pass it to
    :func:`evaluate_topic_relevance` as ``semantic_validator``. Left as a
    no-op stub so the adapter never calls a network or loads a heavy model
    unless a caller explicitly opts in.
    """

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def evaluate(self, topic: str, text: str) -> TopicRelevanceResult:
        raise NotImplementedError(
            "OptionalSemanticRelevanceValidator is a stub; enable it only "
            "after subclassing with a concrete embedding-based evaluate()."
        )


def evaluate_topic_relevance(
    topic: str,
    text: str,
    config: TopicRelevanceConfig = DEFAULT_TOPIC_RELEVANCE_CONFIG,
    semantic_validator: Optional[OptionalSemanticRelevanceValidator] = None,
) -> TopicRelevanceResult:
    """Run lexical validation, then optional semantic validation if enabled.

    The lexical pass is always deterministic and always runs. The semantic
    validator only runs when a caller supplies one *and* it reports
    ``enabled = True``; by default no semantic check happens at all.
    """
    result = LexicalTopicRelevanceValidator(config).evaluate(topic, text)
    if not result.relevant:
        return result
    if semantic_validator is not None and semantic_validator.enabled:
        return semantic_validator.evaluate(topic, text)
    return result
