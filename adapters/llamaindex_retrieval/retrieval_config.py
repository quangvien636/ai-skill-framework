"""Compiles validated ASF Knowledge IR into LlamaIndex retrieval configuration.

Per Priority 2: configuration only. This module never builds an index,
generates an embedding, or talks to a vector store -- it constructs
``llama_index.core.schema.Document`` objects (plain data containers; no
index/embedding/vector-store class is imported or instantiated) and an
ASF-owned ``RetrievalConfig`` describing which documents a future retriever
should be scoped to. Deploying an actual query engine (choosing an
embedding model, a vector store, calling ``VectorStoreIndex.from_documents``)
is deliberately out of scope here and is left to whoever wires this config
into a live LlamaIndex retriever, mirroring how adapters/mcp_tools binds a
caller-supplied handler instead of inventing tool behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from llama_index.core.schema import Document

from asf_runtime.binding import RuntimeBinding
from asf_validator.knowledge_ir import KnowledgeIR
from asf_validator.runtime_ir import RuntimeIR

_DEFAULT_SIMILARITY_TOP_K = 5


def _document_text(knowledge: KnowledgeIR) -> str:
    """Deterministic plain-text serialization of the sections a retriever
    would want to search over. Field order is fixed so the same KnowledgeIR
    always compiles to the same Document text.
    """
    lines = [
        f"# {knowledge.title}",
        "",
        knowledge.summary,
        "",
        "## Guidance",
        knowledge.guidance,
    ]
    if knowledge.decision_rules:
        lines.append("")
        lines.append("## Decision Rules")
        lines.extend(f"{i}. {rule}" for i, rule in enumerate(knowledge.decision_rules, start=1))
    if knowledge.examples_good:
        lines.append("")
        lines.append("## Good Example")
        lines.append(knowledge.examples_good)
    if knowledge.examples_counterexample:
        lines.append("")
        lines.append("## Counterexample")
        lines.append(knowledge.examples_counterexample)
    return "\n".join(lines)


def knowledge_ir_to_document(knowledge: KnowledgeIR) -> Document:
    """Translate one validated KnowledgeIR into a LlamaIndex ``Document``.

    Constructing a ``Document`` performs no I/O, embedding, or indexing --
    it is a plain pydantic data container, exactly as ``mcp.types.Tool`` is
    for the ``mcp_tools`` adapter.
    """
    return Document(
        doc_id=knowledge.id,
        text=_document_text(knowledge),
        metadata={
            "id": knowledge.id,
            "category": knowledge.category,
            "domain": knowledge.domain,
            "topic": knowledge.topic,
            "version": knowledge.version,
            "status": knowledge.status,
            "related_knowledge": list(knowledge.related_knowledge),
        },
    )


@dataclass(frozen=True)
class RetrievalConfig:
    """Non-executing retrieval configuration: which Knowledge documents a
    future retriever should be scoped to, and how many results to return.
    Building an actual index/query engine from this config is a deployment
    concern outside this adapter's scope.
    """

    knowledge_ids: tuple[str, ...]
    documents: tuple[Document, ...]
    similarity_top_k: int


def compile_retrieval_config(
    knowledge_docs: Sequence[KnowledgeIR],
    similarity_top_k: int = _DEFAULT_SIMILARITY_TOP_K,
) -> RetrievalConfig:
    """Compile validated Knowledge IR into a ``RetrievalConfig``.

    Deterministic by construction: documents are produced in
    ``knowledge_docs`` order, and ``knowledge_ir_to_document`` has no
    non-deterministic step (no embedding, no I/O).
    """
    if similarity_top_k < 1:
        raise ValueError("similarity_top_k must be at least 1")
    documents = tuple(knowledge_ir_to_document(knowledge) for knowledge in knowledge_docs)
    return RetrievalConfig(
        knowledge_ids=tuple(knowledge.id for knowledge in knowledge_docs),
        documents=documents,
        similarity_top_k=similarity_top_k,
    )


def retrieval_config_from_runtime(
    runtime: RuntimeIR, knowledge_docs: Sequence[KnowledgeIR]
) -> Optional[RetrievalConfig]:
    """Bind a resolved Runtime Contract's ``retriever`` section to a
    ``RetrievalConfig``. Binding only -- no indexing, embedding, or query.

    `knowledge_docs` must already be the Runtime Planning-resolved Knowledge
    IR for `runtime.retriever.knowledge` (this module does not resolve
    repository references itself -- that is the Dependency Graph/planner's
    job). Returns ``None`` when ``runtime.retriever.enabled`` is false,
    matching ADR-0014's `enabled` pattern.
    """
    if not runtime.retriever.enabled:
        return None
    return compile_retrieval_config(
        knowledge_docs, similarity_top_k=runtime.retriever.similarity_top_k
    )


def retrieval_config_from_binding(binding: RuntimeBinding) -> Optional[RetrievalConfig]:
    """Bind a resolved ``RuntimeBinding``'s effective ``retriever``
    capability to a ``RetrievalConfig`` (ADR-0015 Phase 4). Binding only --
    no indexing, embedding, or query.

    Unlike ``retrieval_config_from_runtime``, no separate ``knowledge_docs``
    argument is needed: ``binding.retriever_knowledge`` already carries the
    Dependency Resolver's resolved Knowledge IR for the effective (possibly
    inherited) retriever. Returns ``None`` when nothing in the binding's
    fallback chain enables retrieval (``binding.retriever is None``).
    """
    if binding.retriever is None:
        return None
    return compile_retrieval_config(
        binding.retriever_knowledge, similarity_top_k=binding.retriever.similarity_top_k
    )
