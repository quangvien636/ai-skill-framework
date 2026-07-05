import json
from pathlib import Path

import _bootstrap

from asf_runtime.catalog import build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry
from langgraph_runtime.vertical_slice import compile_vertical_slice


SNAPSHOTS = Path(__file__).parent / "snapshots"


def _production_catalog():
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


def _snapshot(name, report):
    actual = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected = (SNAPSHOTS / name).read_text(encoding="utf-8")
    assert actual == expected


def test_content_creation_compiles_end_to_end_without_execution():
    context = ExecutionContext.create(
        "golden-content-creation",
        "workflow:content-brief-to-package",
        "1.0.0",
        {
            "content-type": "social-media-post",
            "brief": "Explain a planning ritual.",
            "audience": "Independent designers.",
            "platform": "linkedin",
        },
    )

    compiled = compile_vertical_slice(context, _production_catalog())

    assert compiled.binding_ir[0].runtime_id == "runtime:content"
    assert compiled.graph.get_graph().nodes
    _snapshot("content-creation.json", compiled.as_dict())
