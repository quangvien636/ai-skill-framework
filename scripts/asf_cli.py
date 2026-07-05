"""ASF compile-only command line interface."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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
from asf_validator.workflow_ir import WorkflowIR
from asf_validator.workspace_discovery import discover_workspace_root


@dataclass(frozen=True)
class Workspace:
    root: Path
    index: ProjectIndex
    results: tuple[AdapterResult, ...]
    catalog: ArtifactCatalog


CONTENT_WORKFLOW_ALIAS = "content-workflow"
CONTENT_WORKFLOW_ID = "workflow:research-content-review"
CONTENT_WORKFLOW_INPUTS = {
    "topic": "5 AI technologies to watch over the next two years",
    "objective": "Prepare a practical short-video research brief.",
    "content-type": "short-video-script",
    "brief": "Explain five potentially concerning AI technologies without exaggeration.",
    "audience": "Working adults, small shop owners, and content creators.",
    "platform": "youtube",
}

_MOJIBAKE_MARKERS = ("Ã", "Â", "Ä", "á»", "â€", "Æ")


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
    workflow_id = _workflow_id(args)
    if args.inputs is None:
        inputs = (
            dict(CONTENT_WORKFLOW_INPUTS)
            if getattr(args, "target", None) == CONTENT_WORKFLOW_ALIAS
            else {}
        )
    else:
        try:
            inputs = json.loads(args.inputs)
        except json.JSONDecodeError as error:
            raise ValueError(f"--inputs is not valid JSON: {error.msg}") from error
    if not isinstance(inputs, dict):
        raise ValueError("--inputs must decode to a JSON object")
    return ExecutionContext.create(
        args.execution_id, workflow_id, args.version, inputs
    )


def _workflow_id(args: argparse.Namespace) -> str:
    workflow = getattr(args, "workflow", None)
    target = getattr(args, "target", None)
    if workflow and target:
        raise ValueError("Use either a compile target or --workflow, not both.")
    if workflow:
        return workflow
    if target == CONTENT_WORKFLOW_ALIAS:
        return CONTENT_WORKFLOW_ID
    if target:
        raise ValueError(
            f"Unknown compile target '{target}'; supported alias: {CONTENT_WORKFLOW_ALIAS}."
        )
    raise ValueError("--workflow is required when no compile target is supplied.")


def _snapshot_report(workspace: Workspace) -> dict[str, Any]:
    directory = (
        workspace.root / "workflows" / "research-content-review" / "snapshots"
    )
    names = (
        "composite-workflow.json",
        "composite-binding.json",
        "composite-execution-plan.json",
        "compiled-state-graph.json",
        "reviewed-content-package.json",
    )
    snapshots = {
        name.removesuffix(".json"): json.loads(
            (directory / name).read_text(encoding="utf-8")
        )
        for name in names
    }
    return {
        "command": "snapshot",
        "status": "ok",
        "workflow_id": CONTENT_WORKFLOW_ID,
        "snapshots": snapshots,
    }


def _inspect_report(args: argparse.Namespace, workspace: Workspace) -> dict[str, Any]:
    artifact_id = (
        CONTENT_WORKFLOW_ID
        if args.artifact == CONTENT_WORKFLOW_ALIAS
        else args.artifact
    )
    artifact = workspace.catalog.exact(artifact_id, args.version)
    if not isinstance(artifact.ir, WorkflowIR):
        raise ValueError(
            f"inspect currently supports Workflow artifacts; '{artifact_id}' is not one."
        )
    workflow = artifact.ir
    return {
        "command": "inspect",
        "status": "ok",
        "artifact": {
            "id": workflow.metadata.id,
            "version": workflow.metadata.version.raw,
            "status": workflow.metadata.status,
            "entrypoint": workflow.entrypoint,
            "inputs": list(workflow.inputs),
            "steps": [
                {
                    "id": step.id,
                    "skill_id": step.skill.id,
                    "version": step.skill.version.raw,
                    "depends_on": list(step.depends_on),
                    "input_mapping": dict(step.input_mapping),
                }
                for step in workflow.steps
            ],
            "outputs": {
                name: output.source for name, output in workflow.outputs.items()
            },
        },
    }


def _explain_report(args: argparse.Namespace, workspace: Workspace) -> dict[str, Any]:
    inspected = _inspect_report(args, workspace)["artifact"]
    transfers = []
    for step in inspected["steps"]:
        for target, source in step["input_mapping"].items():
            if source.startswith("steps."):
                transfers.append(
                    {
                        "source": source,
                        "target": f"steps.{step['id']}.inputs.{target}",
                    }
                )
    return {
        "command": "explain",
        "status": "ok",
        "workflow_id": inspected["id"],
        "chain": [step["id"] for step in inspected["steps"]],
        "artifact_transfers": transfers,
        "final_artifact": "reviewed-content-package",
        "boundary": (
            "ASF compiles through Reviewed Content Package. Skill execution, "
            "rendering, media generation, export, and publishing are external."
        ),
    }


def _run_content_report(
    args: argparse.Namespace, workspace: Workspace
) -> dict[str, Any]:
    if args.target != CONTENT_WORKFLOW_ALIAS:
        raise ValueError(
            f"run supports only the '{CONTENT_WORKFLOW_ALIAS}' target."
        )
    if args.mode == "dry-run" and args.model:
        raise ValueError("--model is valid only with --mode live-local.")
    if args.mode == "live-local" and not args.model:
        raise ValueError("--mode live-local requires --model.")
    if args.timeout is not None and args.timeout <= 0:
        raise ValueError("--timeout must be greater than zero.")

    topic = _normalize_cli_unicode(args.topic)
    inputs = dict(CONTENT_WORKFLOW_INPUTS)
    inputs["topic"] = topic
    execution_id = args.execution_id or _execution_id(
        topic, args.mode, args.model
    )
    context = ExecutionContext.create(
        execution_id,
        CONTENT_WORKFLOW_ID,
        "1.0.0",
        inputs,
    )

    adapters = workspace.root / "adapters"
    if str(adapters) not in sys.path:
        sys.path.insert(0, str(adapters))
    from langgraph_runtime.vertical_slice import compile_vertical_slice
    from ollama_execution import OllamaStepExecutor, run_content_workflow

    compiled = compile_vertical_slice(context, workspace.catalog).as_dict()
    executor = (
        OllamaStepExecutor(
            model=args.model,
            endpoint=args.endpoint,
            timeout_seconds=args.timeout,
        )
        if args.mode == "live-local"
        else None
    )
    report_root = (
        args.reports_dir
        if args.reports_dir.is_absolute()
        else workspace.root / args.reports_dir
    )
    execution = run_content_workflow(
        context,
        workspace.catalog,
        mode=args.mode,
        executor=executor,
        compiled=compiled,
        report_root=report_root,
    )
    return {
        "command": "run",
        "status": (
            "ok"
            if execution.status in ("compiled", "succeeded")
            else "error"
        ),
        "execution": execution.as_dict(),
    }


def _execution_id(topic: str, mode: str, model: str | None) -> str:
    material = json.dumps(
        {"topic": topic, "mode": mode, "model": model},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()[:12]
    return f"content-workflow-{digest}"


def _normalize_cli_unicode(value: str) -> str:
    """Repair the narrow UTF-8-as-Windows-code-page argv failure mode.

    CPython normally receives Windows arguments through the wide-character
    command line. Some terminal/launcher chains encode UTF-8 first and decode
    those bytes as Windows-1252, producing strings such as ``cÃ´ng``. Only
    strings carrying known mojibake markers are considered, and a repair is
    accepted only when it strictly reduces those markers.
    """
    original_score = _mojibake_score(value)
    if original_score == 0:
        return value
    for encoding in ("cp1252", "latin-1"):
        try:
            candidate = value.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if _mojibake_score(candidate) < original_score:
            return candidate
    return value


def _mojibake_score(value: str) -> int:
    return sum(value.count(marker) for marker in _MOJIBAKE_MARKERS)


def _configure_utf8_stdio() -> None:
    if os.name != "nt":
        return
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


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
    if args.command == "snapshot":
        return _snapshot_report(workspace)
    if args.command == "inspect":
        return _inspect_report(args, workspace)
    if args.command == "explain":
        return _explain_report(args, workspace)
    if args.command == "run":
        return _run_content_report(args, workspace)

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
    for name in ("bindings", "plan"):
        command = subparsers.add_parser(name)
        command.add_argument("--workflow", required=True)
        command.add_argument("--version", default="1.0.0")
        command.add_argument("--inputs")
        command.add_argument("--execution-id", default="asf-dry-run")
    compile_command = subparsers.add_parser("compile")
    compile_command.add_argument("target", nargs="?")
    compile_command.add_argument("--workflow")
    compile_command.add_argument("--version", default="1.0.0")
    compile_command.add_argument("--inputs")
    compile_command.add_argument("--execution-id", default="asf-dry-run")
    snapshot_command = subparsers.add_parser("snapshot")
    snapshot_command.add_argument("target", nargs="?", default=CONTENT_WORKFLOW_ALIAS)
    for name in ("inspect", "explain"):
        command = subparsers.add_parser(name)
        command.add_argument("artifact", nargs="?", default=CONTENT_WORKFLOW_ALIAS)
        command.add_argument("--version", default="1.0.0")
    run_command = subparsers.add_parser("run")
    run_command.add_argument("target")
    run_command.add_argument("--topic", required=True)
    run_command.add_argument(
        "--mode", choices=("dry-run", "live-local"), default="dry-run"
    )
    run_command.add_argument("--model")
    run_command.add_argument(
        "--endpoint", default="http://localhost:11434"
    )
    run_command.add_argument("--timeout", type=int)
    run_command.add_argument("--execution-id")
    run_command.add_argument("--reports-dir", type=Path, default=Path("runs"))
    return parser


def _render(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(
            json.dumps(
                report, ensure_ascii=False, indent=2, sort_keys=True
            )
        )
        return
    print(f"ASF {report['command']}: {report['status'].upper()}")
    for diagnostic in report.get("diagnostics", ()):
        print(
            f"  {diagnostic['severity'].upper()} {diagnostic['code']} "
            f"{diagnostic['artifact']} [{diagnostic['location']}]"
        )
        print(f"    {diagnostic['message']}")
        if diagnostic.get("suggestion"):
            print(f"    Suggestion: {diagnostic['suggestion']}")
    if "summary" in report:
        print(
            "  "
            + ", ".join(f"{key}={value}" for key, value in report["summary"].items())
        )
    elif report["command"] == "doctor":
        for key, value in report["checks"].items():
            print(f"  {key}: {value}")
    elif report["command"] == "build-ir" and "artifacts" in report:
        valid = sum(item["ok"] for item in report["artifacts"])
        print(f"  built={valid}/{len(report['artifacts'])}")
    elif report["command"] == "graph" and "nodes" in report:
        print(f"  nodes={len(report['nodes'])}, edges={len(report['edges'])}")
    elif report["command"] == "bindings" and "bindings" in report:
        for binding in report["bindings"]:
            print(
                f"  {binding['skill_id']} -> {binding['runtime_id']} "
                f"({binding['model']['provider']}/{binding['model']['model']})"
            )
    elif report["command"] == "plan" and "plan" in report:
        plan = report["plan"]
        print(
            f"  {plan['workflow_id']}@{plan['workflow_version']}: "
            f"{len(plan['steps'])} step(s), {len(plan['batches'])} batch(es)"
        )
        for step in plan["steps"]:
            print(f"  - {step['id']} -> {step['skill_id']}@{step['skill_version']}")
    elif report["command"] == "compile" and "compiled" in report:
        compiled = report["compiled"]
        print(
            f"  {compiled['workflow']['id']}@{compiled['workflow']['version']}: "
            f"{len(compiled['graph']['nodes'])} nodes, "
            f"{len(compiled['graph']['edges'])} edges (not executed)"
        )
    elif report["command"] == "snapshot":
        print(
            f"  {report['workflow_id']}: "
            f"{len(report['snapshots'])} golden snapshots"
        )
    elif report["command"] == "inspect":
        artifact = report["artifact"]
        print(
            f"  {artifact['id']}@{artifact['version']}: "
            f"{len(artifact['steps'])} steps, {len(artifact['outputs'])} outputs"
        )
    elif report["command"] == "explain":
        print("  " + " -> ".join(report["chain"]))
        print(f"  final artifact: {report['final_artifact']}")
        print(f"  boundary: {report['boundary']}")
    elif report["command"] == "run" and "execution" in report:
        execution = report["execution"]
        print(
            f"  {execution['workflow_id']}@{execution['workflow_version']}: "
            f"{execution['status']} ({execution['mode']})"
        )
        for step in execution["steps"]:
            print(
                f"  - {step['step_id']}: {step['status']} "
                f"({step['duration_ms']} ms)"
            )
        print(f"  reports: {execution['report_directory']}")
    elif report["status"] == "ok":
        print(
            json.dumps(
                report, ensure_ascii=False, indent=2, sort_keys=True
            )
        )


def main(argv: Sequence[str] | None = None) -> int:
    _configure_utf8_stdio()
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        workspace = load_workspace(args.start)
        report = _run_command(args, workspace)
        exit_code = 1 if report["status"] == "error" else 0
    except (LookupError, PlanningError, RuntimeError, ValueError) as error:
        if isinstance(error, ValueError):
            exit_code = 2
        elif isinstance(error, (LookupError, PlanningError)):
            exit_code = 4
        else:
            exit_code = 1
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
    report["report_version"] = "1.0"
    _render(report, args.format)
    return exit_code
