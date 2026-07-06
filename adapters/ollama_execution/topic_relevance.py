"""Composable, deterministic topic-relevance validation for generated Ollama
step output.

Architecture
------------
Two validators compose to decide whether generated text stayed on-topic:

1. :class:`LexicalTopicRelevanceValidator` -- deterministic keyword-overlap
   scoring plus config-driven domain-drift detection (see
   :mod:`.domain_classification`). No network, no model. Always runs, and
   always decides the outcome on its own if it rejects the text.
2. An optional semantic validator (see :mod:`.semantic`) -- disabled by
   default. Only runs when the lexical pass accepts the text *and* a caller
   supplies a validator with ``enabled=True``.

:func:`evaluate_topic_relevance` is the single public entry point other
modules (``runner.py``) call. It never needs to change to support a new
tokenizer, a new domain, or a real embedding model later: those are all
supplied through :class:`~.topic_relevance_config.TopicRelevanceConfig` or
constructor injection.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Optional, Protocol

from .domain_classification import DomainClassifier, KeywordDomainClassifier
from .semantic import (
    CosineSimilarity,
    EmbeddingProvider,
    NullEmbeddingProvider,
    NullTopicClassifier,
    OptionalSemanticRelevanceValidator,
    SemanticEvaluation,
    SemanticRelevanceValidator,
    SemanticSimilarity,
    TopicClassifier,
)
from .tokenization import DEFAULT_TOKENIZER, Tokenizer
from .topic_relevance_config import DEFAULT_TOPIC_RELEVANCE_CONFIG, TopicRelevanceConfig

__all__ = [
    "TopicRelevanceResult",
    "TopicRelevanceValidator",
    "LexicalTopicRelevanceValidator",
    "SemanticRelevanceValidator",
    "OptionalSemanticRelevanceValidator",
    "EmbeddingProvider",
    "SemanticSimilarity",
    "TopicClassifier",
    "CosineSimilarity",
    "NullEmbeddingProvider",
    "NullTopicClassifier",
    "DomainClassifier",
    "KeywordDomainClassifier",
    "Tokenizer",
    "evaluate_topic_relevance",
]


@dataclass(frozen=True)
class TopicRelevanceResult:
    """Rich diagnostics for one topic-relevance evaluation.

    ``passed`` is the only field a caller *must* consult to gate execution;
    every other field exists for observability (structured logs, dashboards,
    postmortems) and is safe to ignore. ``relevant`` is kept as a read-only
    alias of ``passed`` for backward compatibility with earlier revisions.
    """

    passed: bool
    score: Optional[float] = None
    lexical_score: Optional[float] = None
    semantic_score: Optional[float] = None
    domain_score: Optional[float] = None
    matched_keywords: frozenset[str] = frozenset()
    missing_keywords: frozenset[str] = frozenset()
    detected_domains: frozenset[str] = frozenset()
    drift_domain: Optional[str] = None
    reason: Optional[str] = None
    validator_chain: tuple[str, ...] = ()
    confidence: Optional[float] = None

    @property
    def relevant(self) -> bool:
        """Backward-compatible alias of :attr:`passed`."""
        return self.passed

    def as_dict(self) -> dict[str, object]:
        """Structured form for logging/observability. Never logs itself."""
        return {
            "passed": self.passed,
            "score": self.score,
            "lexical_score": self.lexical_score,
            "semantic_score": self.semantic_score,
            "domain_score": self.domain_score,
            "matched_keywords": sorted(self.matched_keywords),
            "missing_keywords": sorted(self.missing_keywords),
            "detected_domains": sorted(self.detected_domains),
            "drift_domain": self.drift_domain,
            "reason": self.reason,
            "validator_chain": list(self.validator_chain),
            "confidence": self.confidence,
        }


class TopicRelevanceValidator(Protocol):
    """Interface any relevance validator (lexical or semantic) implements."""

    def evaluate(self, topic: str, text: str) -> TopicRelevanceResult: ...


class LexicalTopicRelevanceValidator:
    """Deterministic keyword-overlap + config-driven domain-drift detector.

    Composed from (not inherited from) a :class:`Tokenizer` and a
    :class:`DomainClassifier`, both dependency-injected with defaults built
    from ``config`` so most callers never construct those directly.
    """

    def __init__(
        self,
        config: TopicRelevanceConfig = DEFAULT_TOPIC_RELEVANCE_CONFIG,
        tokenizer: Tokenizer = DEFAULT_TOKENIZER,
        domain_classifier: Optional[DomainClassifier] = None,
    ):
        self._config = config
        self._tokenizer = tokenizer
        self._domain_classifier = domain_classifier or KeywordDomainClassifier(
            config.domain_terms, config.min_domain_indicator_occurrences
        )

    def _keywords(self, text: str) -> frozenset[str]:
        allowlist = self._config.short_keyword_allowlist
        stopwords = self._config.stopwords
        return frozenset(
            token
            for token in self._tokenizer.tokenize(text)
            if token in allowlist or (len(token) >= 3 and token not in stopwords)
        )

    def evaluate(self, topic: str, text: str) -> TopicRelevanceResult:
        topic_domains = self._domain_classifier.matches(topic)
        text_domains = self._domain_classifier.matches(text)
        drifted = text_domains - topic_domains
        if drifted:
            drift_domain = min(drifted)
            return TopicRelevanceResult(
                passed=False,
                domain_score=0.0,
                detected_domains=text_domains,
                drift_domain=drift_domain,
                reason=(
                    f"drifted to an off-topic '{drift_domain}' subject "
                    f"unrelated to the requested topic '{topic}'"
                ),
                validator_chain=("lexical",),
            )
        return self._score_keyword_overlap(topic, text, text_domains)

    def _score_keyword_overlap(
        self, topic: str, text: str, detected_domains: frozenset[str]
    ) -> TopicRelevanceResult:
        topic_keywords = self._keywords(topic)
        if not topic_keywords:
            return TopicRelevanceResult(
                passed=True,
                domain_score=1.0,
                detected_domains=detected_domains,
                validator_chain=("lexical",),
            )
        text_keywords = self._keywords(text)
        matched = topic_keywords & text_keywords
        missing = topic_keywords - text_keywords
        lexical_score = len(matched) / len(topic_keywords)
        passed = lexical_score >= self._config.min_relevance_score
        return TopicRelevanceResult(
            passed=passed,
            score=lexical_score,
            lexical_score=lexical_score,
            domain_score=1.0,
            matched_keywords=matched,
            missing_keywords=missing,
            detected_domains=detected_domains,
            confidence=lexical_score,
            reason=(
                None
                if passed
                else (
                    "does not appear relevant to the requested topic "
                    f"'{topic}' (keyword overlap too low)"
                )
            ),
            validator_chain=("lexical",),
        )


def evaluate_topic_relevance(
    topic: str,
    text: str,
    config: TopicRelevanceConfig = DEFAULT_TOPIC_RELEVANCE_CONFIG,
    semantic_validator: Optional[SemanticRelevanceValidator] = None,
) -> TopicRelevanceResult:
    """Run lexical validation, then optional semantic validation if enabled.

    The lexical pass is always deterministic and always runs. If it
    rejects the text, that result is returned immediately -- the semantic
    validator never runs on text already known to be off-topic. If a
    semantic validator is supplied *and* reports ``enabled=True``, its
    result is folded into the returned diagnostics; otherwise no semantic
    check happens at all.
    """
    lexical_result = LexicalTopicRelevanceValidator(config).evaluate(topic, text)
    if not lexical_result.passed:
        return lexical_result
    if semantic_validator is None or not semantic_validator.enabled:
        return lexical_result
    return _fold_semantic_result(lexical_result, semantic_validator.evaluate(topic, text))


def _fold_semantic_result(
    lexical_result: TopicRelevanceResult, semantic: SemanticEvaluation
) -> TopicRelevanceResult:
    validator_chain = lexical_result.validator_chain + ("semantic",)
    if semantic.passed:
        return dataclasses.replace(
            lexical_result,
            semantic_score=semantic.score,
            validator_chain=validator_chain,
        )
    return TopicRelevanceResult(
        passed=False,
        score=semantic.score if semantic.score is not None else lexical_result.score,
        lexical_score=lexical_result.lexical_score,
        semantic_score=semantic.score,
        domain_score=lexical_result.domain_score,
        matched_keywords=lexical_result.matched_keywords,
        missing_keywords=lexical_result.missing_keywords,
        detected_domains=lexical_result.detected_domains,
        reason=semantic.reason,
        confidence=semantic.score,
        validator_chain=validator_chain,
    )
