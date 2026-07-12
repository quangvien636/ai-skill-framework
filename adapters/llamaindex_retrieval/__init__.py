"""ASF Knowledge IR compilation and local LlamaIndex query execution.

See docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md and ADR-0013.
"""

from .retrieval_config import (
    RetrievalConfig,
    compile_retrieval_config,
    knowledge_ir_to_document,
    retrieval_config_from_runtime,
)
from .retriever import (
    KnowledgeRetriever,
    LocalHashingEmbedding,
    RetrievalMatch,
    RetrievalResult,
)

__all__ = [
    "RetrievalConfig",
    "compile_retrieval_config",
    "knowledge_ir_to_document",
    "retrieval_config_from_runtime",
    "KnowledgeRetriever",
    "LocalHashingEmbedding",
    "RetrievalMatch",
    "RetrievalResult",
]
