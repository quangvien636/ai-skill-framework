"""Version IR: parse SemVer and version-range strings into structured values.

Not a standalone file adapter -- Version has no source file of its own
(docs/guides/VALIDATION_GUIDE.md's Schema Selection table). These are pure,
reusable functions the Skill and Workflow adapters call wherever a version
or version-range string appears (ADR-0009).

Resolving whether a given exact version satisfies a range is Validator
Roadmap Phase 3 ("version rules") and is intentionally not implemented here;
this module only parses and structures the strings schemas already validate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

_SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

_COMPARATOR_RE = re.compile(r"(>=|<=|>|<|=)([0-9]+\.[0-9]+\.[0-9]+)")


@dataclass(frozen=True)
class VersionIR:
    raw: str
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None


@dataclass(frozen=True)
class VersionComparatorIR:
    operator: str
    version: VersionIR


@dataclass(frozen=True)
class VersionRangeIR:
    raw: str
    comparators: tuple[VersionComparatorIR, ...]


def parse_version(raw: str) -> tuple[Optional[VersionIR], Optional[str]]:
    """Parse an exact SemVer string. Returns (VersionIR, None) or (None, error)."""
    match = _SEMVER_RE.match(raw)
    if not match:
        return None, f"'{raw}' is not a valid Semantic Version."
    return (
        VersionIR(
            raw=raw,
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=match.group("prerelease"),
            build=match.group("build"),
        ),
        None,
    )


def parse_version_range(raw: str) -> tuple[Optional[VersionRangeIR], Optional[str]]:
    """Parse an exact version or comparator range into structured comparators."""
    exact, error = parse_version(raw)
    if exact is not None:
        return VersionRangeIR(raw=raw, comparators=(VersionComparatorIR("=", exact),)), None

    comparators: list[VersionComparatorIR] = []
    for operator, version_text in _COMPARATOR_RE.findall(raw):
        version, version_error = parse_version(version_text)
        if version is None:  # pragma: no cover - regex already constrains this
            return None, version_error
        comparators.append(VersionComparatorIR(operator, version))

    if not comparators:
        return None, f"'{raw}' is not a valid version or comparator range."
    return VersionRangeIR(raw=raw, comparators=tuple(comparators)), None
