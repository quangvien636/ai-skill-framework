"""Configuration for the Ollama adapter's deterministic topic-relevance gate.

The denylist, threshold, and short-keyword allowlist used to be hard-coded
inside runner.py. They now live in one place (this module) so new domains,
keywords, or thresholds can be added without touching validation logic.

To override defaults without editing this file, point the
``ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG`` environment variable at a JSON file, or
pass an explicit path to :func:`load_topic_relevance_config`. Any key you
omit falls back to the built-in default. List-valued keys
(``short_keyword_allowlist``, ``stopwords``) are unioned with the defaults
rather than replacing them, and ``offtopic_drift_terms`` domains are merged
key-by-key, so a small override cannot silently drop built-in coverage.
Example override file::

    {
      "min_relevance_score": 0.25,
      "short_keyword_allowlist": ["rag", "llm"],
      "offtopic_drift_terms": {
        "finance-crypto": ["bitcoin", "crypto trading", "day trading"]
      }
    }

No external dependency is required: overrides are plain JSON read with the
standard library.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Mapping

_ENV_VAR = "ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG"


@dataclass(frozen=True)
class TopicRelevanceConfig:
    """Deterministic rules used to judge whether output stays on-topic."""

    min_relevance_score: float
    short_keyword_allowlist: frozenset[str]
    stopwords: frozenset[str]
    offtopic_drift_terms: Mapping[str, tuple[str, ...]]


_DEFAULT_SHORT_KEYWORD_ALLOWLIST = frozenset(
    {"ai", "ml", "vr", "ar", "5g", "iot", "llm", "rag", "nlp", "gpt"}
)

_DEFAULT_STOPWORDS = frozenset(
    {
        # english
        "the", "and", "for", "with", "that", "this", "from", "are", "was",
        "were", "have", "has", "will", "about", "into", "your", "you", "not",
        "but", "can", "its", "video", "script",
        # vietnamese (diacritics stripped by _normalize_text before matching)
        "trong", "nhung", "mot", "nay", "cho", "duoc", "cua", "voi", "den",
        "khi", "hay", "hon", "toi", "nhat", "nam", "cac", "la", "va", "de",
        "co", "se", "tu", "ve", "sao", "nao", "gi", "bang", "theo", "tren",
        "duoi", "truoc", "sau", "con", "neu", "thi", "hoac", "cung", "rat",
        "qua", "chi", "luon", "nhieu",
    }
)

_DEFAULT_OFFTOPIC_DRIFT_TERMS: Mapping[str, tuple[str, ...]] = {
    "environmental-protection": (
        "moi truong",
        "bien doi khi hau",
        "khi thai",
        "o nhiem",
        "sinh thai",
        "nang luong xanh",
        "environment",
        "environmental",
        "climate change",
        "greenhouse gas",
        "sustainability",
        "renewable energy",
        "global warming",
    ),
}

DEFAULT_TOPIC_RELEVANCE_CONFIG = TopicRelevanceConfig(
    min_relevance_score=0.2,
    short_keyword_allowlist=_DEFAULT_SHORT_KEYWORD_ALLOWLIST,
    stopwords=_DEFAULT_STOPWORDS,
    offtopic_drift_terms=_DEFAULT_OFFTOPIC_DRIFT_TERMS,
)


def load_topic_relevance_config(
    path: str | Path | None = None,
) -> TopicRelevanceConfig:
    """Load topic-relevance rules, falling back to built-in defaults.

    Resolution order: an explicit ``path`` argument, then the
    ``ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG`` environment variable, then the
    built-in defaults. This keeps the adapter fully functional with zero
    external configuration.
    """
    resolved = path or os.environ.get(_ENV_VAR)
    if not resolved:
        return DEFAULT_TOPIC_RELEVANCE_CONFIG
    overrides = _read_overrides(Path(resolved))
    return _merge_overrides(DEFAULT_TOPIC_RELEVANCE_CONFIG, overrides)


def _read_overrides(path: Path) -> Mapping[str, object]:
    if not path.is_file():
        raise FileNotFoundError(f"Topic relevance config not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("Topic relevance config file must contain a JSON object.")
    return payload


def _merge_overrides(
    base: TopicRelevanceConfig, overrides: Mapping[str, object]
) -> TopicRelevanceConfig:
    updates: dict[str, object] = {}
    if "min_relevance_score" in overrides:
        updates["min_relevance_score"] = float(overrides["min_relevance_score"])
    if "short_keyword_allowlist" in overrides:
        updates["short_keyword_allowlist"] = base.short_keyword_allowlist | frozenset(
            str(item).lower() for item in overrides["short_keyword_allowlist"]
        )
    if "stopwords" in overrides:
        updates["stopwords"] = base.stopwords | frozenset(
            str(item).lower() for item in overrides["stopwords"]
        )
    if "offtopic_drift_terms" in overrides:
        merged_terms = dict(base.offtopic_drift_terms)
        raw_terms = overrides["offtopic_drift_terms"]
        if not isinstance(raw_terms, Mapping):
            raise ValueError("offtopic_drift_terms override must be a JSON object.")
        for domain, terms in raw_terms.items():
            merged_terms[domain] = tuple(str(term).lower() for term in terms)
        updates["offtopic_drift_terms"] = merged_terms
    return replace(base, **updates)
