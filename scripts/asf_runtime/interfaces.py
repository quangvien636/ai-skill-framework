"""Tool-neutral Runtime pipeline interfaces.

No concrete Skill, model, tool, or connector executor is provided.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, Sequence

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
