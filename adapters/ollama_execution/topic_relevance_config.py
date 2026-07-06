"""Configuration for the Ollama adapter's deterministic topic-relevance gate.

``TopicRelevanceConfig`` is the single source of truth for every tunable in
the subsystem: the relevance threshold, the short-keyword allowlist, the
stopword list, and the domain vocabulary used for off-topic drift detection.
Nothing downstream (tokenizer, domain classifier, lexical/semantic
validators) hard-codes a domain name, threshold, or keyword list -- they all
read from an instance of this dataclass.

Overriding defaults
--------------------
Point the ``ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG`` environment variable at a
JSON file, or pass an explicit path to :func:`load_topic_relevance_config`.
Any key you omit falls back to the built-in default. List-valued keys
(``short_keyword_allowlist``, ``stopwords``) are unioned with the defaults
rather than replacing them, and ``domain_terms`` domains are merged
key-by-key, so a small override cannot silently drop built-in coverage.
Example override file::

    {
      "config_version": "1",
      "min_relevance_score": 0.25,
      "short_keyword_allowlist": ["rag", "llm"],
      "domain_terms": {
        "finance": ["bitcoin", "crypto trading", "day trading"],
        "travel": ["flight booking", "travel itinerary", "visa requirements"]
      }
    }

Domains are arbitrary labels chosen entirely by configuration (AI, Finance,
Travel, Gaming, Medicine, Education, Politics, Recipe, Religion, Environment,
...); adding a new one never requires a code change. ``offtopic_drift_terms``
is still accepted as a deprecated alias for ``domain_terms`` so older
override files keep working.

No external dependency is required: overrides are plain JSON read with the
standard library.
"""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

_ENV_VAR = "ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG"
_SUPPORTED_CONFIG_VERSIONS = frozenset({"1"})
_LEGACY_DOMAIN_TERMS_KEY = "offtopic_drift_terms"
_KNOWN_OVERRIDE_KEYS = frozenset(
    {
        "config_version",
        "min_relevance_score",
        "min_domain_indicator_occurrences",
        "semantic_similarity_threshold",
        "short_keyword_allowlist",
        "stopwords",
        "domain_terms",
        _LEGACY_DOMAIN_TERMS_KEY,
    }
)


class TopicRelevanceConfigError(ValueError):
    """Raised when a topic-relevance configuration value is invalid.

    Covers both malformed override files and out-of-range values, so callers
    can catch one type instead of guessing between ``ValueError``,
    ``TypeError``, and ``KeyError``.
    """


class TopicRelevanceConfigNotFoundError(TopicRelevanceConfigError, FileNotFoundError):
    """Raised when an explicit override path does not exist.

    Subclasses ``FileNotFoundError`` too, so existing ``except
    FileNotFoundError`` call sites keep working unchanged.
    """


@dataclass(frozen=True)
class TopicRelevanceConfig:
    """Deterministic rules used to judge whether output stays on-topic.

    Instances are immutable and safe to share across calls. Build a new one
    with :func:`load_topic_relevance_config` or ``dataclasses.replace``
    rather than mutating fields in place.
    """

    config_version: str
    min_relevance_score: float
    min_domain_indicator_occurrences: int
    semantic_similarity_threshold: float
    short_keyword_allowlist: frozenset[str]
    stopwords: frozenset[str]
    domain_terms: Mapping[str, tuple[str, ...]]

    def __post_init__(self) -> None:
        _require(
            self.config_version in _SUPPORTED_CONFIG_VERSIONS,
            "config_version",
            self.config_version,
            f"one of {sorted(_SUPPORTED_CONFIG_VERSIONS)}",
        )
        _require(
            0.0 <= self.min_relevance_score <= 1.0,
            "min_relevance_score",
            self.min_relevance_score,
            "a float between 0.0 and 1.0",
        )
        _require(
            isinstance(self.min_domain_indicator_occurrences, int)
            and self.min_domain_indicator_occurrences >= 1,
            "min_domain_indicator_occurrences",
            self.min_domain_indicator_occurrences,
            "an integer >= 1",
        )
        _require(
            0.0 <= self.semantic_similarity_threshold <= 1.0,
            "semantic_similarity_threshold",
            self.semantic_similarity_threshold,
            "a float between 0.0 and 1.0",
        )


def _require(condition: bool, field_name: str, value: object, expected: str) -> None:
    if not condition:
        raise TopicRelevanceConfigError(
            f"Invalid topic-relevance config field '{field_name}': "
            f"got {value!r}, expected {expected}."
        )


_DEFAULT_SHORT_KEYWORD_ALLOWLIST = frozenset(
    {"ai", "ml", "vr", "ar", "5g", "iot", "llm", "rag", "nlp", "gpt"}
)

_DEFAULT_STOPWORDS = frozenset(
    {
        # english
        "the", "and", "for", "with", "that", "this", "from", "are", "was",
        "were", "have", "has", "will", "about", "into", "your", "you", "not",
        "but", "can", "its", "video", "script",
        # vietnamese (diacritics stripped by the tokenizer before matching)
        "trong", "nhung", "mot", "nay", "cho", "duoc", "cua", "voi", "den",
        "khi", "hay", "hon", "toi", "nhat", "nam", "cac", "la", "va", "de",
        "co", "se", "tu", "ve", "sao", "nao", "gi", "bang", "theo", "tren",
        "duoi", "truoc", "sau", "con", "neu", "thi", "hoac", "cung", "rat",
        "qua", "chi", "luon", "nhieu",
    }
)

_DEFAULT_DOMAIN_TERMS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "environment": (
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
)

DEFAULT_TOPIC_RELEVANCE_CONFIG = TopicRelevanceConfig(
    config_version="1",
    min_relevance_score=0.2,
    min_domain_indicator_occurrences=2,
    semantic_similarity_threshold=0.75,
    short_keyword_allowlist=_DEFAULT_SHORT_KEYWORD_ALLOWLIST,
    stopwords=_DEFAULT_STOPWORDS,
    domain_terms=_DEFAULT_DOMAIN_TERMS,
)


def load_topic_relevance_config(
    path: str | Path | None = None,
) -> TopicRelevanceConfig:
    """Load topic-relevance rules, falling back to built-in defaults.

    Resolution order: an explicit ``path`` argument, then the
    ``ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG`` environment variable, then the
    built-in defaults. This keeps the adapter fully functional with zero
    external configuration, and raises :class:`TopicRelevanceConfigError`
    (or its :class:`TopicRelevanceConfigNotFoundError` subclass) with a
    precise, actionable message instead of letting a malformed override
    crash deep inside validation logic.
    """
    resolved = path or os.environ.get(_ENV_VAR)
    if not resolved:
        return DEFAULT_TOPIC_RELEVANCE_CONFIG
    overrides = _read_overrides(Path(resolved))
    return _merge_overrides(DEFAULT_TOPIC_RELEVANCE_CONFIG, overrides)


def _read_overrides(path: Path) -> Mapping[str, object]:
    if not path.is_file():
        raise TopicRelevanceConfigNotFoundError(
            f"Topic relevance config not found: {path}"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise TopicRelevanceConfigError(
            f"Topic relevance config at '{path}' is not valid JSON: {error}"
        ) from error
    if not isinstance(payload, Mapping):
        raise TopicRelevanceConfigError(
            f"Topic relevance config at '{path}' must contain a JSON object, "
            f"got {type(payload).__name__}."
        )
    return payload


def _merge_overrides(
    base: TopicRelevanceConfig, overrides: Mapping[str, object]
) -> TopicRelevanceConfig:
    _warn_unknown_keys(overrides)
    updates: dict[str, object] = {}
    if "config_version" in overrides:
        updates["config_version"] = str(overrides["config_version"])
    if "min_relevance_score" in overrides:
        updates["min_relevance_score"] = _as_float(
            overrides["min_relevance_score"], "min_relevance_score"
        )
    if "min_domain_indicator_occurrences" in overrides:
        updates["min_domain_indicator_occurrences"] = _as_int(
            overrides["min_domain_indicator_occurrences"],
            "min_domain_indicator_occurrences",
        )
    if "semantic_similarity_threshold" in overrides:
        updates["semantic_similarity_threshold"] = _as_float(
            overrides["semantic_similarity_threshold"],
            "semantic_similarity_threshold",
        )
    if "short_keyword_allowlist" in overrides:
        updates["short_keyword_allowlist"] = base.short_keyword_allowlist | frozenset(
            str(item).lower() for item in overrides["short_keyword_allowlist"]
        )
    if "stopwords" in overrides:
        updates["stopwords"] = base.stopwords | frozenset(
            str(item).lower() for item in overrides["stopwords"]
        )
    domain_terms = _merge_domain_terms(base.domain_terms, overrides)
    if domain_terms is not None:
        updates["domain_terms"] = domain_terms
    try:
        return replace(base, **updates)
    except TopicRelevanceConfigError:
        raise
    except (TypeError, ValueError) as error:
        raise TopicRelevanceConfigError(
            f"Invalid topic-relevance config override: {error}"
        ) from error


def _merge_domain_terms(
    base_terms: Mapping[str, tuple[str, ...]], overrides: Mapping[str, object]
) -> Mapping[str, tuple[str, ...]] | None:
    raw_new = overrides.get("domain_terms")
    raw_legacy = overrides.get(_LEGACY_DOMAIN_TERMS_KEY)
    if raw_new is None and raw_legacy is None:
        return None

    merged = {domain.casefold(): terms for domain, terms in base_terms.items()}
    if raw_legacy is not None:
        warnings.warn(
            f"'{_LEGACY_DOMAIN_TERMS_KEY}' is a deprecated alias for "
            "'domain_terms' and may be removed in a future config_version; "
            "rename the key in your override file.",
            DeprecationWarning,
            stacklevel=3,
        )
        legacy_terms = _normalize_domain_terms(raw_legacy, _LEGACY_DOMAIN_TERMS_KEY)
        merged.update(legacy_terms)
    if raw_new is not None:
        new_terms = _normalize_domain_terms(raw_new, "domain_terms")
        if raw_legacy is not None:
            reshadowed = sorted(set(new_terms) & set(legacy_terms))
            if reshadowed:
                warnings.warn(
                    f"Domain(s) {reshadowed} defined in both 'domain_terms' "
                    f"and deprecated '{_LEGACY_DOMAIN_TERMS_KEY}'; the "
                    "'domain_terms' definition wins.",
                    UserWarning,
                    stacklevel=3,
                )
        merged.update(new_terms)
    return MappingProxyType(merged)


def _normalize_domain_terms(
    raw: object, source_label: str
) -> dict[str, tuple[str, ...]]:
    if not isinstance(raw, Mapping):
        raise TopicRelevanceConfigError(
            f"'{source_label}' must be a JSON object mapping domain name to "
            f"a list of indicator phrases, got {type(raw).__name__}."
        )
    normalized: dict[str, tuple[str, ...]] = {}
    original_names: dict[str, str] = {}
    for domain, terms in raw.items():
        key = str(domain).casefold()
        if key in original_names and original_names[key] != domain:
            raise TopicRelevanceConfigError(
                f"Duplicate domain definition in '{source_label}': "
                f"'{domain}' and '{original_names[key]}' both normalize to "
                f"the same domain label '{key}'. Use one consistent name."
            )
        original_names[key] = domain
        normalized[key] = tuple(str(term).lower() for term in terms)
    return normalized


def _warn_unknown_keys(overrides: Mapping[str, object]) -> None:
    unknown = sorted(set(overrides) - _KNOWN_OVERRIDE_KEYS)
    if unknown:
        warnings.warn(
            f"Unknown topic-relevance config field(s) ignored: {unknown}. "
            f"Recognized fields: {sorted(_KNOWN_OVERRIDE_KEYS)}.",
            UserWarning,
            stacklevel=3,
        )


def _as_float(value: object, field_name: str) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise TopicRelevanceConfigError(
            f"Field '{field_name}' must be a number, got {value!r}."
        ) from error


def _as_int(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TopicRelevanceConfigError(
            f"Field '{field_name}' must be an integer, got {value!r}."
        )
    return value
