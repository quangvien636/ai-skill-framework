"""Declarative export descriptors for publishing targets (describe, never
publish).

See docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md and ADR-0013.
"""

from .descriptors import (
    SUPPORTED_TARGETS,
    DescriptorError,
    ExportDescriptor,
    compile_export_descriptor,
    export_descriptor_from_runtime,
    facebook_export,
    markdown_export,
    tiktok_export,
    wordpress_export,
    youtube_export,
)

__all__ = [
    "SUPPORTED_TARGETS",
    "DescriptorError",
    "ExportDescriptor",
    "compile_export_descriptor",
    "export_descriptor_from_runtime",
    "facebook_export",
    "markdown_export",
    "tiktok_export",
    "wordpress_export",
    "youtube_export",
]
