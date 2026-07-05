"""ASF compile-only command line interface."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from asf_runtime.binding import resolve_skill_runtime_binding, to_binding_ir
from asf_runtime.catalog import ArtifactCatalog, build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_runtime.planner import PlanningError, plan_workflow
from asf_validator.dependency_graph import build_dependency_graph
from asf_validator.diagnostics import Diagnostic
from asf_validator.pipeline import AdapterResult, build_ir
from asf_validator.project_discovery import ProjectIndex, discover_project
from asf_validator.repository_validator import validate_repository
from asf_validator.schema_registry import build_schema_registry
from asf_validator.semantic_validator import validate_semantics
from asf_validator.skill_ir import SkillIR
from asf_validator.version_graph import build_version_graph
from asf_validator.workspace_discovery import discover_workspace_root


@dataclass(frozen=True)
class Workspace:
    root: Path
    index: ProjectIndex
    results: tuple[AdapterResult, ...]
    catalog: ArtifactCatalog


def load_workspace(start: Path) -> Workspace:
    root = discover_workspace_root(start)
    index = discover_project(root)
    registry = build_schema_registry(root / "schemas")
    locations = (
        item
        for item in index.artifacts
        if item.kind
        in ("skill", "workflow", "knowledge", "tool", "connector", "runtime")
    )
    results = tuple(build_ir(item.kind, item.path, registry) for item in locations)
    return Workspace(root, index, results, build_artifact_catalog(results))


def validate_workspace(workspace: Workspace) -> list[Diagnostic]:
    diagnostics = [
        item for result in workspace.results for item in result.diagnostics
    ]
    graph, graph_diagnostics = build_dependency_graph(list(workspace.results))
    _versions, version_diagnostics = build_version_graph(graph)
    diagnostics.extend(graph_diagnostics)
    diagnostics.extend(version_diagnostics)
    diagnostics.extend(validate_semantics(list(workspace.results)))
    diagnostics.extend(
        validate_repository(workspace.index, list(workspace.results))
    )
    return diagnostics


def diagnostic_dict(item: Diagnostic) -> dict[str, Any]:
    return {
        "code": item.code,
        "severity": item.severity.value,
        "artifact": item.artifact,
        "location": item.location,
        "message": item.message,
        "rule_reference": item.rule_reference,
        "suggestion": item.suggestion,
    }


def _context(args: argparse.Namespace) -> ExecutionContext:
    try:
        inputs = json.loads(args.inputs)
    except json.JSONDecodeError as error:
        raise ValueError(f"--inputs is not valid JSON: {error.msg}") from error
    if not isinstance(inputs, dict):
        raise ValueError("--inputs must decode to a JSON object")
    return ExecutionContext.create(
        args.execution_id, args.workflow, args.version, inputs
    )


def _plan_dict(plan) -> dict[str, Any]:
    return {
        "execution_id": plan.execution_id,
        "workflow_id": plan.workflow_id,
        "workflow_version": plan.workflow_version,
        "batches": [list(batch) for batch in plan.batches],
        "steps": [
            {
                "id": step.id,
                "skill_id": step.skill_id,
                "skill_version": step.skill_version,
                "depends_on": list(step.depends_on),
                "knowledge": [item.target_id for item in step.knowledge],
                "runtime": [item.target_id for item in step.runtime],
            }
            for step in plan.steps
        ],
        "outputs": dict(plan.outputs),
    }


def _bindings(workspace: Workspace, plan) -> list[dict[str, Any]]:
    reports = []
    for step in plan.steps:
        artifact = workspace.catalog.exact(step.skill_id, step.skill_version)
        if not isinstance(artifact.ir, SkillIR):
            raise RuntimeError(f"'{step.skill_id}' is not Skill IR")
        binding, diagnostics = resolve_skill_runtime_binding(
            artifact.ir, workspace.catalog
        )
        if binding is None:
            detail = diagnostics[0].message if diagnostics else "no runtime declared"
            raise RuntimeError(f"step '{step.id}' has no binding: {detail}")
        reports.append(to_binding_ir(binding, diagnostics).as_dict())
    return reports


def _run_command(args: argparse.Namespace, workspace: Workspace) -> dict[str, Any]:
    if args.command == "validate":
        diagnostics = validate_workspace(workspace)
        errors = sum(item.is_error() for item in diagnostics)
        return {
            "command": "validate",
            "status": "error" if errors else "ok",
            "diagnostics": [diagnostic_dict(item) for item in diagnostics],
            "summary": {
                "discovered": len(workspace.index.artifacts),
                "loaded": sum(item.ok for item in workspace.results),
                "errors": errors,
                "warnings": len(diagnostics) - errors,
            },
        }
    if args.command == "build-ir":
        return {
            "command": "build-ir",
            "status": "ok",
            "artifacts": [
                {
                    "kind": item.kind,
                    "path": str(Path(item.artifact).relative_to(workspace.root)),
                    "ok": item.ok,
                    "diagnostics": [
                        diagnostic_dict(diagnostic)
                        for diagnostic in item.diagnostics
                    ],
                }
                for item in workspace.results
            ],
        }
    if args.command == "graph":
        graph, diagnostics = build_dependency_graph(list(workspace.results))
        return {
            "command": "graph",
            "status": "error" if any(item.is_error() for item in diagnostics) else "ok",
            "nodes": [
                {"id": node.id, "kind": node.kind, "status": node.status}
                for node in graph.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "kind": edge.kind,
                    "required": edge.required,
                }
                for edge in graph.edges
            ],
            "diagnostics": [diagnostic_dict(item) for item in diagnostics],
        }
    if args.command == "doctor":
        diagnostics = validate_workspace(workspace)
        return {
            "command": "doctor",
            "status": "error" if any(item.is_error() for item in diagnostics) else "ok",
            "checks": {
                "python": platform.python_version(),
                "workspace": str(workspace.root),
                "schemas": (workspace.root / "schemas").is_dir(),
                "langgraph": _langgraph_available(),
                "repository_valid": not any(item.is_error() for item in diagnostics),
            },
        }

    context = _context(args)
    plan = plan_workflow(context, workspace.catalog)
    if args.command == "plan":
        return {"command": "plan", "status": "ok", "plan": _plan_dict(plan)}
    if args.command == "bindings":
        return {
            "command": "bindings",
            "status": "ok",
            "bindings": _bindings(workspace, plan),
        }
    if args.command == "compile":
        adapters = workspace.root / "adapters"
        if str(adapters) not in sys.path:
            sys.path.insert(0, str(adapters))
        from langgraph_runtime.vertical_slice import compile_vertical_slice

        compiled = compile_vertical_slice(context, workspace.catalog)
        return {
            "command": "compile",
            "status": "ok",
            "compiled": compiled.as_dict(),
        }
    raise ValueError(f"unsupported command: {args.command}")


def _langgraph_available() -> bool:
    try:
        import langgraph  # noqa: F401
    except ImportError:
        return False
    return True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="asf", description="Validate and compile ASF artifacts without execution."
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--start", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "build-ir", "graph", "doctor"):
        subparsers.add_parser(name)
    for name in ("bindings", "plan", "compile"):
        command = subparsers.add_parser(name)
        command.add_argument("--workflow", required=True)
        command.add_argument("--version", default="1.0.0")
        command.add_argument("--inputs", default="{}")
        command.add_argument("--execution-id", default="asf-dry-run")
    return parser


def _render(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    print(f"ASF {report['command']}: {report['status'].upper()}")
    if "summary" in report:
        print(
            "  "
            + ", ".join(f"{key}={value}" for key, value in report["summary"].items())
        )
    elif report["command"] == "doctor":
        for key, value in report["checks"].items():
            print(f"  {key}: {value}")
    else:
        print(json.dumps(report, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        workspace = load_workspace(args.start)
        report = _run_command(args, workspace)
    except (LookupError, PlanningError, RuntimeError, ValueError) as error:
        report = {
            "command": args.command,
            "status": "error",
            "diagnostics": [
                {
                    "code": getattr(error, "code", "ASF-CLI-001"),
                    "severity": "error",
                    "artifact": getattr(args, "workflow", str(args.start)),
                    "location": "command",
                    "message": str(error),
                    "rule_reference": None,
                    "suggestion": "Check the command arguments and referenced artifacts.",
                }
            ],
        }
    _render(report, args.format)
    return 1 if report["status"] == "error" else 0
