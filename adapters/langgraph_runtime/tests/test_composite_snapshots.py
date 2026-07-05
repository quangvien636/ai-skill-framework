import json
from pathlib import Path

import _bootstrap

from asf_runtime.catalog import build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry
from langgraph_runtime.vertical_slice import compile_vertical_slice


SNAPSHOTS = (
    _bootstrap.REPO_ROOT
    / "workflows"
    / "research-content-review"
    / "snapshots"
)


def _load(name):
    return json.loads((SNAPSHOTS / name).read_text(encoding="utf-8"))


def _catalog():
    registry = build_schema_registry(_bootstrap.REPO_ROOT / "schemas")
    index = discover_project(
        _bootstrap.REPO_ROOT,
        kinds=("skill", "workflow", "knowledge", "tool", "runtime"),
    )
    results = [
        build_ir(item.kind, item.path, registry) for item in index.artifacts
    ]
    assert all(result.ok for result in results)
    return build_artifact_catalog(results)


def _compiled():
    context = ExecutionContext.create(
        "golden-research-content-review",
        "workflow:research-content-review",
        "1.0.0",
        {
            "topic": "Five AI technologies to watch.",
            "objective": "Prepare a practical short-video brief.",
            "content-type": "short-video-script",
            "brief": "Explain five AI risks without exaggeration.",
            "audience": "Working adults and small businesses.",
            "platform": "youtube",
        },
    )
    return compile_vertical_slice(context, _catalog())


def test_composite_workflow_snapshot_matches_resolved_workflow():
    compiled = _compiled()
    steps = [
        {
            "id": step.id,
            "skill_id": step.skill_id,
            "depends_on": list(step.depends_on),
        }
        for step in compiled.plan.steps
    ]
    actual = {
        "id": compiled.plan.workflow_id,
        "version": compiled.plan.workflow_version,
        "entrypoint": "research-topic",
        "steps": steps,
        "artifact_flow": [
            {
                "source": "steps.research-topic.outputs.research-brief",
                "target": "steps.create-content.inputs.research-brief",
            },
            {
                "source": "steps.create-content.outputs.content-package",
                "target": "steps.review-content.inputs.draft",
            },
        ],
    }
    assert actual == _load("composite-workflow.json")


def test_composite_binding_snapshot_matches_runtime_resolution():
    compiled = _compiled()
    actual = {
        "bindings": [
            {
                "step_id": step.id,
                "skill_id": binding.skill_id,
                "runtime_id": binding.runtime_id,
                "runtime_version": binding.runtime_version,
            }
            for step, binding in zip(compiled.plan.steps, compiled.binding_ir)
        ]
    }
    assert actual == _load("composite-binding.json")


def test_composite_execution_plan_snapshot_is_deterministic():
    compiled = _compiled()
    actual = {
        "execution_id": compiled.plan.execution_id,
        "workflow_id": compiled.plan.workflow_id,
        "workflow_version": compiled.plan.workflow_version,
        "batches": [list(batch) for batch in compiled.plan.batches],
        "steps": [
            {
                "id": step.id,
                "skill_id": step.skill_id,
                "skill_version": step.skill_version,
                "depends_on": list(step.depends_on),
            }
            for step in compiled.plan.steps
        ],
        "outputs": dict(compiled.plan.outputs),
    }
    assert actual == _load("composite-execution-plan.json")


def test_compiled_state_graph_snapshot_is_deterministic():
    report = _compiled().as_dict()
    actual_nodes = []
    for node in report["graph"]["nodes"]:
        if "metadata" not in node:
            actual_nodes.append({"id": node["id"]})
            continue
        metadata = node["metadata"]
        actual_nodes.append(
            {
                "id": node["id"],
                "workflow_id": metadata["workflow_id"],
                "skill_id": metadata["skill_id"],
                "runtime_id": metadata["runtime_id"],
                "batch_index": metadata["batch_index"],
            }
        )
    actual = {
        "nodes": actual_nodes,
        "edges": report["graph"]["edges"],
    }
    assert actual == _load("compiled-state-graph.json")


def test_reviewed_content_package_snapshot_has_canonical_editorial_fields():
    package = _load("reviewed-content-package.json")
    primary = package["content-package"]["primary-content"]
    assert set(
        (
            "title",
            "hook",
            "script",
            "scenes",
            "voice-over-text",
            "on-screen-text",
            "image-prompts",
            "call-to-action",
            "hashtags",
            "metadata",
        )
    ).issubset(primary)
    assert "review-report" in package
    assert "content-quality-report" in package
    assert package["reviewed-content-package"]["status"] == "revise"
