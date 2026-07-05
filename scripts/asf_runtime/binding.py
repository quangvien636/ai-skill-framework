"""Runtime Binding: the resolved, single source of a Skill's runtime
dependencies (ADR-0015).

``RuntimeBinding`` (Phase 2) is the rich, in-memory result adapters and the
planner consume -- the fully resolved model/retriever/tools/publisher after
walking the fallback chain (``dependency_resolver``) and applying
inheritance/override. ``BindingIR`` (Phase 3) is a flattened, serializable,
diagnostic-carrying summary derived from a ``RuntimeBinding``, matching this
repository's established ``(ir_or_none, diagnostics)`` adapter shape.

Never executes. Binding only combines and reports on already-resolved,
already-validated IR.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence

from asf_validator.diagnostics import (
    BINDING_CONFLICTING_OVERRIDE,
    BINDING_INCOMPATIBLE_DESCRIPTORS,
    BINDING_INVALID_INHERITANCE,
    BINDING_MISSING_RUNTIME,
    BINDING_DUPLICATE_ID,
    Diagnostic,
    Severity,
)
from asf_validator.knowledge_ir import KnowledgeIR
from asf_validator.runtime_ir import (
    AuditProfileIR,
    ModelBindingIR,
    PublisherBindingIR,
    RetrieverBindingIR,
    RetryPolicyIR,
    RuntimeIR,
    SafetyProfileIR,
    ToolsBindingIR,
)
from asf_validator.skill_ir import SkillIR
from asf_validator.tool_ir import ToolIR

from .catalog import ArtifactCatalog
from .dependency_resolver import (
    inherit_model,
    inherit_publisher,
    inherit_retriever,
    inherit_tools,
    resolve_fallback_chain,
    resolve_retriever_knowledge,
    resolve_tools,
)


@dataclass(frozen=True)
class RuntimeBinding:
    """The fully resolved binding an adapter or the planner consumes.

    Every ``*_source_runtime_id`` names which runtime in the fallback chain
    actually supplied that capability -- the primary's own id if the
    primary enabled it directly (override), a fallback's id if inherited,
    or ``None`` if nothing in the chain enables that capability at all.
    """

    skill_id: str
    skill_version: str
    runtime_id: str
    runtime_version: str
    chain: tuple[str, ...]
    model: Optional[ModelBindingIR]
    model_source_runtime_id: Optional[str]
    retriever: Optional[RetrieverBindingIR]
    retriever_source_runtime_id: Optional[str]
    retriever_knowledge: tuple[KnowledgeIR, ...]
    tools: Optional[ToolsBindingIR]
    tools_source_runtime_id: Optional[str]
    resolved_tools: tuple[ToolIR, ...]
    publisher: Optional[PublisherBindingIR]
    publisher_source_runtime_id: Optional[str]
    timeout_seconds: int
    retry_policy: RetryPolicyIR
    safety_profile: SafetyProfileIR
    audit_profile: AuditProfileIR


def build_runtime_binding(
    skill_id: str,
    skill_version: str,
    runtime: RuntimeIR,
    catalog: ArtifactCatalog,
) -> tuple[RuntimeBinding, list[Diagnostic]]:
    """Build the effective binding for one already-resolved primary Runtime
    Contract: walk its fallback chain, resolve inheritance/override for
    each capability, resolve cross-artifact references, and run Binding
    validation over the result.
    """
    diagnostics: list[Diagnostic] = []
    chain, chain_diagnostics = resolve_fallback_chain(runtime, catalog)
    diagnostics.extend(chain_diagnostics)

    model, model_source = inherit_model(chain)
    retriever, retriever_source = inherit_retriever(chain)
    tools, tools_source = inherit_tools(chain)
    publisher, publisher_source = inherit_publisher(chain)

    retriever_knowledge, knowledge_diagnostics = resolve_retriever_knowledge(retriever, catalog)
    diagnostics.extend(knowledge_diagnostics)
    resolved_tools, tools_diagnostics = resolve_tools(tools, catalog)
    diagnostics.extend(tools_diagnostics)

    binding = RuntimeBinding(
        skill_id=skill_id,
        skill_version=skill_version,
        runtime_id=runtime.metadata.id,
        runtime_version=runtime.metadata.version.raw,
        chain=tuple(member.metadata.id for member in chain),
        model=model,
        model_source_runtime_id=model_source,
        retriever=retriever,
        retriever_source_runtime_id=retriever_source,
        retriever_knowledge=retriever_knowledge,
        tools=tools,
        tools_source_runtime_id=tools_source,
        resolved_tools=resolved_tools,
        publisher=publisher,
        publisher_source_runtime_id=publisher_source,
        timeout_seconds=runtime.timeout_policy.timeout_seconds,
        retry_policy=runtime.retry_policy,
        safety_profile=runtime.safety_profile,
        audit_profile=runtime.audit_profile,
    )
    diagnostics.extend(_validate_binding(binding, chain))
    return binding, diagnostics


def resolve_skill_runtime_binding(
    skill: SkillIR, catalog: ArtifactCatalog
) -> tuple[Optional[RuntimeBinding], list[Diagnostic]]:
    """Resolve a Skill's ``dependencies.runtime`` to one ``RuntimeBinding``:
    the first declared reference that resolves to an active Runtime
    Contract wins. Returns ``(None, [])`` when the Skill declares no
    runtime dependency at all -- that is not an error. Emits
    ``ASF-BINDING-001`` when a runtime dependency is declared but none of
    its references resolve.
    """
    if not skill.dependencies.runtime:
        return None, []
    for reference in skill.dependencies.runtime:
        try:
            artifact = catalog.resolve(reference.id, reference.version)
        except LookupError:
            continue
        if not isinstance(artifact.ir, RuntimeIR):
            continue
        return build_runtime_binding(
            skill.metadata.id, skill.metadata.version.raw, artifact.ir, catalog
        )
    diagnostics = [
        Diagnostic(
            code=BINDING_MISSING_RUNTIME,
            severity=Severity.ERROR,
            artifact=skill.metadata.id,
            location="dependencies.runtime",
            message=(
                f"Skill '{skill.metadata.id}' declares a runtime dependency, "
                "but none of its references resolved to an active Runtime Contract."
            ),
            suggestion="Fix the reference id/version range, or add the missing Runtime Contract.",
        )
    ]
    return None, diagnostics


def _validate_binding(
    binding: RuntimeBinding, chain: tuple[RuntimeIR, ...]
) -> list[Diagnostic]:
    """ASF-BINDING-004, -006, -007: consistency checks over one resolved
    binding and its chain. ASF-BINDING-001/002/003 are raised earlier
    (missing binding, cyclic/unresolved chain); ASF-BINDING-005 requires a
    batch of bindings (``validate_binding_batch``)."""
    diagnostics: list[Diagnostic] = []
    by_id = {member.metadata.id: member for member in chain}

    for source_id, capability in (
        (binding.model_source_runtime_id, "model"),
        (binding.retriever_source_runtime_id, "retriever"),
        (binding.tools_source_runtime_id, "tools"),
        (binding.publisher_source_runtime_id, "publisher"),
    ):
        if source_id is None or source_id == binding.runtime_id:
            continue  # not inherited -- the primary's own override
        source_runtime = by_id.get(source_id)
        if source_runtime is not None and source_runtime.metadata.status != "active":
            diagnostics.append(
                Diagnostic(
                    code=BINDING_INVALID_INHERITANCE,
                    severity=Severity.ERROR,
                    artifact=binding.runtime_id,
                    location=capability,
                    message=(
                        f"'{capability}' is inherited from '{source_id}', which is "
                        f"status '{source_runtime.metadata.status}', not 'active'."
                    ),
                    suggestion="Only inherit from an active Runtime Contract.",
                )
            )

    if binding.retriever is not None and binding.model is None:
        diagnostics.append(
            Diagnostic(
                code=BINDING_INCOMPATIBLE_DESCRIPTORS,
                severity=Severity.ERROR,
                artifact=binding.runtime_id,
                location="retriever",
                message=(
                    "retriever is enabled (directly or inherited) but no model is "
                    "enabled anywhere in the resolved fallback chain."
                ),
                suggestion="Enable a model somewhere in the chain, or disable the retriever.",
            )
        )

    diagnostics.extend(_check_conflicting_overrides(chain))
    return diagnostics


def _check_conflicting_overrides(chain: tuple[RuntimeIR, ...]) -> list[Diagnostic]:
    """Only ``publisher`` is checked here, deliberately: a fallback chain
    enabling a *different model* than its primary (typically a cheaper or
    local provider) is the whole point of a fallback -- flagging that would
    contradict the pattern Phase 8's "hybrid" -> "offline" example
    demonstrates. A fallback silently redirecting published output to a
    *different platform*, however, is a much more surprising outcome worth
    flagging as likely unintentional.
    """
    diagnostics: list[Diagnostic] = []

    enabled_publishers = [
        (member.metadata.id, member.publisher.target)
        for member in chain
        if member.publisher.enabled
    ]
    if len({target for _, target in enabled_publishers}) > 1:
        diagnostics.append(
            Diagnostic(
                code=BINDING_CONFLICTING_OVERRIDE,
                severity=Severity.ERROR,
                artifact=chain[0].metadata.id,
                location="publisher",
                message=(
                    "Multiple Runtimes in the fallback chain enable publisher with "
                    f"different targets: {', '.join(id for id, _ in enabled_publishers)}."
                ),
                suggestion="Confirm this is intentional, or align the publish targets.",
            )
        )

    return diagnostics


@dataclass(frozen=True)
class BindingIR:
    """Flattened, serializable, diagnostic-carrying record derived from a
    ``RuntimeBinding`` -- canonical references only, no embedded IR
    objects, matching ``KnowledgeIR.as_normalized_dict()``'s precedent."""

    id: str
    skill_id: str
    skill_version: str
    runtime_id: str
    runtime_version: str
    chain: tuple[str, ...]
    model_provider: Optional[str]
    model_name: Optional[str]
    model_source_runtime_id: Optional[str]
    retriever_knowledge_ids: tuple[str, ...]
    retriever_source_runtime_id: Optional[str]
    tool_ids: tuple[str, ...]
    tools_source_runtime_id: Optional[str]
    publisher_target: Optional[str]
    publisher_source_runtime_id: Optional[str]
    timeout_seconds: int
    retry_max_attempts: int
    retry_backoff: str
    safety_content_filter: str
    audit_log_level: str
    diagnostics: tuple[Diagnostic, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "skill_id": self.skill_id,
            "skill_version": self.skill_version,
            "runtime_id": self.runtime_id,
            "runtime_version": self.runtime_version,
            "chain": list(self.chain),
            "model": {
                "provider": self.model_provider,
                "model": self.model_name,
                "source_runtime_id": self.model_source_runtime_id,
            },
            "retriever": {
                "knowledge_ids": list(self.retriever_knowledge_ids),
                "source_runtime_id": self.retriever_source_runtime_id,
            },
            "tools": {
                "tool_ids": list(self.tool_ids),
                "source_runtime_id": self.tools_source_runtime_id,
            },
            "publisher": {
                "target": self.publisher_target,
                "source_runtime_id": self.publisher_source_runtime_id,
            },
            "timeout_seconds": self.timeout_seconds,
            "retry": {"max_attempts": self.retry_max_attempts, "backoff": self.retry_backoff},
            "safety_content_filter": self.safety_content_filter,
            "audit_log_level": self.audit_log_level,
            "diagnostic_codes": [d.code for d in self.diagnostics],
        }


def to_binding_ir(binding: RuntimeBinding, diagnostics: Sequence[Diagnostic]) -> BindingIR:
    """Derive a serializable ``BindingIR`` from a resolved ``RuntimeBinding``."""
    return BindingIR(
        id=f"binding:{binding.skill_id}@{binding.runtime_id}",
        skill_id=binding.skill_id,
        skill_version=binding.skill_version,
        runtime_id=binding.runtime_id,
        runtime_version=binding.runtime_version,
        chain=binding.chain,
        model_provider=binding.model.provider if binding.model else None,
        model_name=binding.model.model if binding.model else None,
        model_source_runtime_id=binding.model_source_runtime_id,
        retriever_knowledge_ids=tuple(doc.id for doc in binding.retriever_knowledge),
        retriever_source_runtime_id=binding.retriever_source_runtime_id,
        tool_ids=tuple(tool.metadata.id for tool in binding.resolved_tools),
        tools_source_runtime_id=binding.tools_source_runtime_id,
        publisher_target=binding.publisher.target if binding.publisher else None,
        publisher_source_runtime_id=binding.publisher_source_runtime_id,
        timeout_seconds=binding.timeout_seconds,
        retry_max_attempts=binding.retry_policy.max_attempts,
        retry_backoff=binding.retry_policy.backoff,
        safety_content_filter=binding.safety_profile.content_filter,
        audit_log_level=binding.audit_profile.log_level,
        diagnostics=tuple(diagnostics),
    )


def validate_binding_batch(bindings: Sequence[BindingIR]) -> list[Diagnostic]:
    """ASF-BINDING-005: within one batch, the same canonical binding id must
    always resolve to the same content -- a determinism/consistency
    invariant, not a "one binding per id" restriction (the same Skill and
    Runtime pair legitimately produces one shared binding id across
    multiple Workflow steps)."""
    diagnostics: list[Diagnostic] = []
    seen: dict[str, BindingIR] = {}
    for binding in bindings:
        previous = seen.get(binding.id)
        if previous is None:
            seen[binding.id] = binding
            continue
        if previous.as_dict() != binding.as_dict():
            diagnostics.append(
                Diagnostic(
                    code=BINDING_DUPLICATE_ID,
                    severity=Severity.ERROR,
                    artifact=binding.id,
                    location="id",
                    message=f"Binding id '{binding.id}' resolved to different content in two places.",
                    suggestion="Investigate non-deterministic resolution -- the same skill/runtime pair must bind identically.",
                )
            )
    return diagnostics
