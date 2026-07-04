"""Version IR: parse SemVer and version-range strings into structured values,
and (Sprint 17 / Phase 3) check whether a version satisfies a range.

Not a standalone file adapter -- Version has no source file of its own
(docs/guides/VALIDATION_GUIDE.md's Schema Selection table). These are pure,
reusable functions the Skill and Workflow adapters, and the Version Graph,
call wherever a version or version-range string appears (ADR-0009).

Version comparison uses (major, minor, patch) only -- SemVer 2.0.0's
pre-release precedence algorithm is not implemented, a documented
simplification (ADR-0010). `range_is_self_contradictory` is a coarse check:
it catches a lower bound exceeding an upper bound (e.g. ">=2.0.0 <1.0.0")
but does not detect a range that excludes every version by squeezing
between two adjacent versions with no integer triple between them (e.g.
">1.0.0 <1.0.1"); that is out of scope for this sprint.
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


def _core(version: VersionIR) -> tuple[int, int, int]:
    return (version.major, version.minor, version.patch)


def _comparator_holds(operator: str, candidate: tuple[int, int, int], bound: tuple[int, int, int]) -> bool:
    if operator == "=":
        return candidate == bound
    if operator == ">=":
        return candidate >= bound
    if operator == ">":
        return candidate > bound
    if operator == "<=":
        return candidate <= bound
    if operator == "<":
        return candidate < bound
    raise ValueError(f"unknown comparator operator: {operator!r}")  # pragma: no cover


def version_satisfies_range(version: VersionIR, version_range: VersionRangeIR) -> bool:
    """True if `version` satisfies every comparator in `version_range` (AND semantics)."""
    candidate = _core(version)
    return all(
        _comparator_holds(c.operator, candidate, _core(c.version)) for c in version_range.comparators
    )


def range_is_self_contradictory(version_range: VersionRangeIR) -> bool:
    """Coarse check: does this range's lower bound exceed its upper bound?

    See this module's docstring for the precision this check does not cover.
    """
    lower_bounds = [
        _core(c.version) for c in version_range.comparators if c.operator in (">=", ">", "=")
    ]
    upper_bounds = [
        _core(c.version) for c in version_range.comparators if c.operator in ("<=", "<", "=")
    ]
    if not lower_bounds or not upper_bounds:
        return False
    return max(lower_bounds) > min(upper_bounds)
