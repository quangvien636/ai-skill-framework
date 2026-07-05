"""Tool-neutral Runtime pipeline interfaces.

No concrete Skill, model, tool, or connector executor is provided.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, Sequence

from asf_validator.pipeline import AdapterResult
from asf_validator.project_discovery import ProjectIndex

from .catalog import ArtifactCatalog
from .models import ExecutionContext, ExecutionPlan


class ArtifactLoader(Protocol):
    def load(self, index: ProjectIndex) -> Sequence[AdapterResult]: ...


class CatalogBuilder(Protocol):
    def build(self, results: Sequence[AdapterResult]) -> ArtifactCatalog: ...


class WorkflowPlanner(Protocol):
    def plan(
        self, context: ExecutionContext, catalog: ArtifactCatalog
    ) -> ExecutionPlan: ...


class PlanStore(Protocol):
    def save(self, plan: ExecutionPlan, workspace_root: Path) -> None: ...


class PlanCompiler(Protocol):
    """Compiles an ExecutionPlan into a backend-native executable graph.

    Per ADR-0013 / docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md, this
    seam is implemented by an adapter package (e.g. adapters/langgraph_runtime/)
    that owns the concrete graph/executor type. This Protocol stays free of
    any execution-backend import, so the return type is intentionally opaque
    (``Any``) here -- the adapter's own public function is fully typed.
    """

    def compile(self, plan: ExecutionPlan, step_executor: Any | None = None) -> Any: ...
