"""Dependency Resolver: walks a Runtime Contract's fallback chain and
resolves inheritance/override for its four capability sections.

Per ADR-0015: never executes, produces data only. Reuses the same
``ArtifactCatalog.resolve()`` the planner already uses (deterministic --
exactly one active artifact per id/version-range). A disabled capability
section is treated as "look at my fallback chain"; an enabled section is
final and is never overridden by anything farther down the chain.
"""

from __future__ import annotations

from typing import Optional

from asf_validator.diagnostics import (
    BINDING_CYCLIC_FALLBACK,
    BINDING_UNRESOLVED_CHAIN,
    Diagnostic,
    Severity,
)
from asf_validator.knowledge_ir import KnowledgeIR
from asf_validator.runtime_ir import (
    ModelBindingIR,
    PublisherBindingIR,
    RetrieverBindingIR,
    RuntimeIR,
    ToolsBindingIR,
)
from asf_validator.tool_ir import ToolIR

from .catalog import ArtifactCatalog


def resolve_fallback_chain(
    primary: RuntimeIR, catalog: ArtifactCatalog
) -> tuple[tuple[RuntimeIR, ...], list[Diagnostic]]:
    """Walk ``primary.fallback_profile.fallback_runtime`` up to
    ``primary.fallback_profile.max_fallback_depth`` hops.

    Returns the chain starting with ``primary`` itself (so callers can
    always inherit-search the whole chain, primary included), plus any
    diagnostics: a cycle detected mid-walk, or a required fallback
    reference that did not resolve. The walk stops (without raising) at
    the first problem -- this module reports, it does not hard-fail;
    ``asf_runtime.planner`` remains the hard-failure boundary.
    """
    diagnostics: list[Diagnostic] = []
    chain: list[RuntimeIR] = [primary]
    visited: set[str] = {primary.metadata.id}
    current = primary
    depth = 0
    while (
        current.fallback_profile.enabled
        and current.fallback_profile.fallback_runtime is not None
        and depth < primary.fallback_profile.max_fallback_depth
    ):
        ref = current.fallback_profile.fallback_runtime
        if ref.id in visited:
            diagnostics.append(
                Diagnostic(
                    code=BINDING_CYCLIC_FALLBACK,
                    severity=Severity.ERROR,
                    artifact=primary.metadata.id,
                    location="fallback_profile.fallback_runtime",
                    message=(
                        f"Fallback chain from '{primary.metadata.id}' revisits '{ref.id}': "
                        f"{' -> '.join(r.metadata.id for r in chain)} -> {ref.id}."
                    ),
                    suggestion="Break the cycle so each Runtime's fallback chain terminates.",
                )
            )
            break
        try:
            artifact = catalog.resolve(ref.id, ref.version)
        except LookupError as error:
            if ref.required:
                diagnostics.append(
                    Diagnostic(
                        code=BINDING_UNRESOLVED_CHAIN,
                        severity=Severity.ERROR,
                        artifact=primary.metadata.id,
                        location="fallback_profile.fallback_runtime",
                        message=f"Required fallback Runtime '{ref.id}' did not resolve: {error}",
                        suggestion="Fix the fallback reference or its version range.",
                    )
                )
            break
        if not isinstance(artifact.ir, RuntimeIR):
            diagnostics.append(
                Diagnostic(
                    code=BINDING_UNRESOLVED_CHAIN,
                    severity=Severity.ERROR,
                    artifact=primary.metadata.id,
                    location="fallback_profile.fallback_runtime",
                    message=f"'{ref.id}' does not resolve to a Runtime Contract.",
                )
            )
            break
        chain.append(artifact.ir)
        visited.add(artifact.ir.metadata.id)
        current = artifact.ir
        depth += 1
    return tuple(chain), diagnostics


def inherit_model(
    chain: tuple[RuntimeIR, ...]
) -> tuple[Optional[ModelBindingIR], Optional[str]]:
    """First chain member (primary first) with ``model.enabled`` wins --
    override precedence is "closer beats farther," so primary always wins
    if it enables the capability itself."""
    for runtime in chain:
        if runtime.model.enabled:
            return runtime.model, runtime.metadata.id
    return None, None


def inherit_retriever(
    chain: tuple[RuntimeIR, ...]
) -> tuple[Optional[RetrieverBindingIR], Optional[str]]:
    for runtime in chain:
        if runtime.retriever.enabled:
            return runtime.retriever, runtime.metadata.id
    return None, None


def inherit_tools(
    chain: tuple[RuntimeIR, ...]
) -> tuple[Optional[ToolsBindingIR], Optional[str]]:
    for runtime in chain:
        if runtime.tools.enabled:
            return runtime.tools, runtime.metadata.id
    return None, None


def inherit_publisher(
    chain: tuple[RuntimeIR, ...]
) -> tuple[Optional[PublisherBindingIR], Optional[str]]:
    for runtime in chain:
        if runtime.publisher.enabled:
            return runtime.publisher, runtime.metadata.id
    return None, None


def resolve_retriever_knowledge(
    retriever: Optional[RetrieverBindingIR], catalog: ArtifactCatalog
) -> tuple[tuple[KnowledgeIR, ...], list[Diagnostic]]:
    """Resolve the effective retriever's Knowledge references to their IR."""
    if retriever is None:
        return (), []
    diagnostics: list[Diagnostic] = []
    resolved: list[KnowledgeIR] = []
    for ref in retriever.knowledge:
        try:
            artifact = catalog.resolve(ref.id, ref.version)
        except LookupError as error:
            if ref.required:
                diagnostics.append(
                    Diagnostic(
                        code=BINDING_UNRESOLVED_CHAIN,
                        severity=Severity.ERROR,
                        artifact=ref.id,
                        location="retriever.knowledge",
                        message=f"Required Knowledge '{ref.id}' did not resolve: {error}",
                    )
                )
            continue
        if isinstance(artifact.ir, KnowledgeIR):
            resolved.append(artifact.ir)
    return tuple(resolved), diagnostics


def resolve_tools(
    tools: Optional[ToolsBindingIR], catalog: ArtifactCatalog
) -> tuple[tuple[ToolIR, ...], list[Diagnostic]]:
    """Resolve the effective tools' Tool references to their IR."""
    if tools is None:
        return (), []
    diagnostics: list[Diagnostic] = []
    resolved: list[ToolIR] = []
    for ref in tools.refs:
        try:
            artifact = catalog.resolve(ref.id, ref.version)
        except LookupError as error:
            if ref.required:
                diagnostics.append(
                    Diagnostic(
                        code=BINDING_UNRESOLVED_CHAIN,
                        severity=Severity.ERROR,
                        artifact=ref.id,
                        location="tools.refs",
                        message=f"Required Tool '{ref.id}' did not resolve: {error}",
                    )
                )
            continue
        if isinstance(artifact.ir, ToolIR):
            resolved.append(artifact.ir)
    return tuple(resolved), diagnostics
