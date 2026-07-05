"""Runtime Contract IR: schemas/runtime.schema.json's object model.

Binds a Skill to a model, retriever, tools, and publisher plus operational
policy. Declarative only -- see ADR-0014 and
docs/architecture/RUNTIME_CONTRACT_ARCHITECTURE.md. This module builds and
normalizes the contract; it resolves nothing against other artifacts (that
is the Dependency Graph, ASF-GRAPH-*) and enforces no cross-field business
rule (that is Semantic Validation, ASF-SEMANTIC-*).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .diagnostics import Diagnostic, has_errors
from .metadata_ir import MetadataIR, extract_metadata_ir
from .reference_ir import (
    KnowledgeReferenceIR,
    ReferenceIR,
    build_knowledge_reference_ir,
    build_reference_ir,
)

_DEFAULT_SIMILARITY_TOP_K = 5


@dataclass(frozen=True)
class ModelBindingIR:
    enabled: bool
    provider: Optional[str]
    model: Optional[str]
    parameters: dict[str, Any]
    endpoint: Optional[str]


@dataclass(frozen=True)
class RetrieverBindingIR:
    enabled: bool
    knowledge: tuple[KnowledgeReferenceIR, ...]
    similarity_top_k: int


@dataclass(frozen=True)
class ToolsBindingIR:
    enabled: bool
    refs: tuple[ReferenceIR, ...]


@dataclass(frozen=True)
class PublisherBindingIR:
    enabled: bool
    target: Optional[str]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class TimeoutPolicyIR:
    timeout_seconds: int
    on_timeout: str


@dataclass(frozen=True)
class RetryPolicyIR:
    max_attempts: int
    backoff: str


@dataclass(frozen=True)
class SafetyProfileIR:
    content_filter: str
    blocked_terms: tuple[str, ...]


@dataclass(frozen=True)
class AuditProfileIR:
    log_level: str
    redact_fields: tuple[str, ...]


@dataclass(frozen=True)
class ConcurrencyProfileIR:
    max_parallel_steps: int
    max_parallel_tool_calls: int


@dataclass(frozen=True)
class FallbackProfileIR:
    enabled: bool
    fallback_runtime: Optional[ReferenceIR]
    max_fallback_depth: int


@dataclass(frozen=True)
class RuntimeIR:
    metadata: MetadataIR
    responsibility: str
    execution_profile: str
    model: ModelBindingIR
    retriever: RetrieverBindingIR
    tools: ToolsBindingIR
    publisher: PublisherBindingIR
    timeout_policy: TimeoutPolicyIR
    retry_policy: RetryPolicyIR
    safety_profile: SafetyProfileIR
    audit_profile: AuditProfileIR
    concurrency_profile: ConcurrencyProfileIR
    fallback_profile: FallbackProfileIR


def build_runtime_ir(doc: dict[str, Any], artifact: str) -> tuple[Optional[RuntimeIR], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []

    metadata, metadata_diagnostics = extract_metadata_ir(doc, artifact, id_prefix="runtime")
    diagnostics.extend(metadata_diagnostics)
    if metadata is None or has_errors(metadata_diagnostics):
        return None, diagnostics

    model_doc = doc["model"]
    model = ModelBindingIR(
        enabled=model_doc["enabled"],
        provider=model_doc.get("provider"),
        model=model_doc.get("model"),
        parameters=dict(model_doc.get("parameters", {})),
        endpoint=model_doc.get("endpoint"),
    )

    retriever_doc = doc["retriever"]
    retriever = RetrieverBindingIR(
        enabled=retriever_doc["enabled"],
        knowledge=tuple(
            build_knowledge_reference_ir(ref) for ref in retriever_doc.get("knowledge", [])
        ),
        similarity_top_k=retriever_doc.get("similarity_top_k", _DEFAULT_SIMILARITY_TOP_K),
    )

    tools_doc = doc["tools"]
    tools = ToolsBindingIR(
        enabled=tools_doc["enabled"],
        refs=tuple(build_reference_ir(ref) for ref in tools_doc.get("refs", [])),
    )

    publisher_doc = doc["publisher"]
    publisher = PublisherBindingIR(
        enabled=publisher_doc["enabled"],
        target=publisher_doc.get("target"),
        metadata=dict(publisher_doc.get("metadata", {})),
    )

    timeout_doc = doc["timeout_policy"]
    timeout_policy = TimeoutPolicyIR(
        timeout_seconds=timeout_doc["timeout_seconds"],
        on_timeout=timeout_doc["on_timeout"],
    )

    retry_doc = doc["retry_policy"]
    retry_policy = RetryPolicyIR(
        max_attempts=retry_doc["max_attempts"],
        backoff=retry_doc["backoff"],
    )

    safety_doc = doc["safety_profile"]
    safety_profile = SafetyProfileIR(
        content_filter=safety_doc["content_filter"],
        blocked_terms=tuple(safety_doc.get("blocked_terms", [])),
    )

    audit_doc = doc["audit_profile"]
    audit_profile = AuditProfileIR(
        log_level=audit_doc["log_level"],
        redact_fields=tuple(audit_doc.get("redact_fields", [])),
    )

    concurrency_doc = doc["concurrency_profile"]
    concurrency_profile = ConcurrencyProfileIR(
        max_parallel_steps=concurrency_doc["max_parallel_steps"],
        max_parallel_tool_calls=concurrency_doc["max_parallel_tool_calls"],
    )

    fallback_doc = doc["fallback_profile"]
    fallback_runtime_doc = fallback_doc.get("fallback_runtime")
    fallback_profile = FallbackProfileIR(
        enabled=fallback_doc["enabled"],
        fallback_runtime=(
            build_reference_ir(fallback_runtime_doc) if fallback_runtime_doc is not None else None
        ),
        max_fallback_depth=fallback_doc["max_fallback_depth"],
    )

    runtime = RuntimeIR(
        metadata=metadata,
        responsibility=doc["responsibility"],
        execution_profile=doc["execution_profile"],
        model=model,
        retriever=retriever,
        tools=tools,
        publisher=publisher,
        timeout_policy=timeout_policy,
        retry_policy=retry_policy,
        safety_profile=safety_profile,
        audit_profile=audit_profile,
        concurrency_profile=concurrency_profile,
        fallback_profile=fallback_profile,
    )
    return runtime, diagnostics
