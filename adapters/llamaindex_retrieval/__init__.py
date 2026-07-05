"""RetrievalConfig compiler: ASF Knowledge IR <-> LlamaIndex Document config.

See docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md and ADR-0013.
"""

from .retrieval_config import (
    RetrievalConfig,
    compile_retrieval_config,
    knowledge_ir_to_document,
    retrieval_config_from_runtime,
)

__all__ = [
    "RetrievalConfig",
    "compile_retrieval_config",
    "knowledge_ir_to_document",
    "retrieval_config_from_runtime",
]
