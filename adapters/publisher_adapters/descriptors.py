"""Declarative export descriptions for publishing targets. Priority 4 scope:
describe an export, never perform it.

This module builds immutable ``ExportDescriptor`` values naming a target
platform, title, body, and platform-specific declarative metadata. It makes
no network call, imports no platform SDK, performs no filesystem write (even
for the "markdown" target -- exporting the descriptor to a file is a
deployer's job, not this module's), and rejects any metadata key that looks
like a credential. Actually publishing (``PublisherAdapter.publish`` in
docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md) is unimplemented; when
built, each platform's official SDK/API is the reuse target -- e.g.
google-api-python-client for YouTube, a WordPress REST client -- never a
hand-rolled HTTP client, per ADR-0013.

This is ASF's own "Export planning" intellectual property (there is no
mature OSS project that declaratively plans cross-platform exports without
also performing them), not a wrapped reuse target -- consistent with the
Build vs Reuse rule that only functionality with no adequate OSS equivalent
gets built here.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Optional

SUPPORTED_TARGETS = ("youtube", "tiktok", "facebook", "wordpress", "markdown")

_CREDENTIAL_LIKE_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "key",
        "token",
        "secret",
        "authorization",
        "auth",
        "password",
        "credential",
        "credentials",
        "access_token",
        "bearer",
        "session_id",
        "cookie",
    }
)


class DescriptorError(ValueError):
    """Raised when a declarative export descriptor is invalid or would carry
    a credential."""


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_")


def _validate_metadata(metadata: Mapping[str, Any]) -> None:
    for key, value in metadata.items():
        if _normalize_key(key) in _CREDENTIAL_LIKE_KEYS:
            raise DescriptorError(
                f"metadata key '{key}' looks like a credential; publisher_adapters "
                "is declarative-only and must never carry secrets or session state "
                "(Priority 4: \"No authentication\")"
            )
        if isinstance(value, Mapping):
            _validate_metadata(value)


@dataclass(frozen=True)
class ExportDescriptor:
    """A non-executing description of one export: what would be published,
    where, and with what declarative metadata. Contains no credential and
    triggers no publish, upload, or file write when constructed.
    """

    target: str
    title: str
    body: str
    metadata: Mapping[str, Any]


def compile_export_descriptor(
    target: str,
    title: str,
    body: str,
    metadata: Optional[Mapping[str, Any]] = None,
) -> ExportDescriptor:
    """Compile a declarative ``ExportDescriptor``. Never calls a network,
    imports a platform SDK, or writes a file.
    """
    if target not in SUPPORTED_TARGETS:
        raise DescriptorError(
            f"unsupported target '{target}' (supported: {SUPPORTED_TARGETS})"
        )
    if not title:
        raise DescriptorError("title must not be empty")

    meta = dict(metadata or {})
    _validate_metadata(meta)

    return ExportDescriptor(
        target=target,
        title=title,
        body=body,
        metadata=MappingProxyType(meta),
    )


def youtube_export(
    title: str,
    description: str,
    tags: tuple[str, ...] = (),
    category: Optional[str] = None,
    privacy_status: str = "private",
    thumbnail_ref: Optional[str] = None,
) -> ExportDescriptor:
    return compile_export_descriptor(
        "youtube",
        title,
        description,
        {
            "tags": tuple(tags),
            "category": category,
            "privacy_status": privacy_status,
            "thumbnail_ref": thumbnail_ref,
        },
    )


def tiktok_export(
    title: str,
    caption: str,
    hashtags: tuple[str, ...] = (),
    video_ref: Optional[str] = None,
) -> ExportDescriptor:
    return compile_export_descriptor(
        "tiktok",
        title,
        caption,
        {"hashtags": tuple(hashtags), "video_ref": video_ref},
    )


def facebook_export(
    title: str,
    message: str,
    link: Optional[str] = None,
    media_ref: Optional[str] = None,
) -> ExportDescriptor:
    return compile_export_descriptor(
        "facebook",
        title,
        message,
        {"link": link, "media_ref": media_ref},
    )


def wordpress_export(
    title: str,
    content: str,
    categories: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    status: str = "draft",
) -> ExportDescriptor:
    return compile_export_descriptor(
        "wordpress",
        title,
        content,
        {"categories": tuple(categories), "tags": tuple(tags), "status": status},
    )


def markdown_export(
    title: str,
    content: str,
    front_matter: Optional[Mapping[str, Any]] = None,
) -> ExportDescriptor:
    return compile_export_descriptor(
        "markdown",
        title,
        content,
        {"front_matter": dict(front_matter or {})},
    )
