"""Export descriptors and credential-free local Markdown publishing.

See docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md and ADR-0013.
"""

from .descriptors import (
    SUPPORTED_TARGETS,
    DescriptorError,
    ExportDescriptor,
    compile_export_descriptor,
    export_descriptor_from_binding,
    export_descriptor_from_runtime,
    facebook_export,
    markdown_export,
    tiktok_export,
    wordpress_export,
    youtube_export,
)
from .publisher import (
    PublishError,
    PublisherAdapter,
    PublishResult,
    UnsupportedPublishTargetError,
)

__all__ = [
    "SUPPORTED_TARGETS",
    "DescriptorError",
    "ExportDescriptor",
    "compile_export_descriptor",
    "export_descriptor_from_binding",
    "export_descriptor_from_runtime",
    "facebook_export",
    "markdown_export",
    "tiktok_export",
    "wordpress_export",
    "youtube_export",
    "PublishError",
    "PublisherAdapter",
    "PublishResult",
    "UnsupportedPublishTargetError",
]
