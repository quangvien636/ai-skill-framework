import json
import os
import tempfile
from pathlib import Path

import pytest

import _bootstrap

from asf_runtime.catalog import build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry
from ollama_execution import OllamaStepExecutor, run_content_workflow


def _catalog():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    index = discover_project(
        _bootstrap.REPO_ROOT,
        kinds=("skill", "workflow", "knowledge", "runtime"),
    )
    results = [
        build_ir(item.kind, item.path, registry) for item in index.artifacts
    ]
    assert all(result.ok for result in results)
    return build_artifact_catalog(results)


def _context(execution_id="runner-test"):
    return ExecutionContext.create(
        execution_id,
        "workflow:research-content-review",
        "1.0.0",
        {
            "topic": "AI",
            "objective": "Prepare a brief.",
            "content-type": "short-video-script",
            "brief": "Explain AI without exaggeration.",
            "audience": "Workers.",
            "platform": "youtube",
        },
    )


def _research():
    return {
        "research-brief": {
            "objective": "Prepare a brief.",
            "scope": "Supplied evidence only.",
            "research-questions": [],
            "source-requirements": [],
            "findings": [],
            "claim-evidence-map": [],
            "uncertainties": [],
            "gaps": ["No evidence supplied."],
            "citations": [],
            "next-steps": ["Supply evidence."],
        },
        "quality-report": {
            "traceability": "No findings.",
            "source-reliability": "Not assessed.",
            "contradictions": "Not assessed.",
            "fact-check-status": "Not checked.",
            "limitations": ["No evidence."],
        },
    }


def _content():
    return {
        "content-package": {
            "content-type": "short-video-script",
            "primary-content": {"title": "AI"},
            "hook": "AI deserves attention.",
            "call-to-action": "Review the evidence.",
            "alternatives": [],
            "production-notes": [],
            "assumptions": ["Fixture."],
        },
        "quality-report": {
            "constraint-compliance": "Pass.",
            "unsupported-claims": "None.",
            "platform-fit": "Pass.",
            "limitations": [],
        },
    }


def _review():
    return {
        "review-report": {
            "summary": "Fixture review.",
            "checklist-results": [],
            "findings": [],
            "evidence-alignment": "No claims.",
            "safety-review": "Pass.",
            "required-revisions": [],
            "optional-improvements": [],
            "recommendation": "approve",
        },
        "reviewed-package": {
            "draft": _content()["content-package"],
            "status": "approve",
            "applied-corrections": [],
            "unresolved-items": [],
        },
    }


class SequenceClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = 0

    def list_models(self, endpoint, timeout_seconds):
        return ("local-test:latest",)

    def generate(self, endpoint, model, prompt, timeout_seconds):
        self.calls += 1
        return json.dumps(self.outputs.pop(0))


def test_dry_run_compiles_and_persists_without_ollama():
    with tempfile.TemporaryDirectory(
        dir=_bootstrap.REPO_ROOT / "runs"
    ) as temporary:
        report_root = Path(temporary)
        report = run_content_workflow(
            _context("dry-run-test"),
            _catalog(),
            mode="dry-run",
            compiled={"graph": {"nodes": []}},
            report_root=report_root,
        )
        assert report.status == "compiled"
        assert [step.status for step in report.steps] == [
            "compiled",
            "compiled",
            "compiled",
        ]
        assert report.final_artifact is None
        directory = report_root / "dry-run-test"
        assert (directory / "execution-report.json").is_file()
        assert (directory / "report.txt").is_file()
        assert len(list(directory.glob("*.json"))) == 4


def test_live_local_produces_final_reviewed_content_package():
    with tempfile.TemporaryDirectory(
        dir=_bootstrap.REPO_ROOT / "runs"
    ) as temporary:
        client = SequenceClient((_research(), _content(), _review()))
        report = run_content_workflow(
            _context("live-fixture"),
            _catalog(),
            mode="live-local",
            executor=OllamaStepExecutor(model="local-test", client=client),
            compiled={"graph": {"nodes": []}},
            report_root=Path(temporary),
        )
        assert report.status == "succeeded"
        assert client.calls == 3
        assert (
            report.final_artifact["reviewed-content-package"]["status"]
            == "approve"
        )
        assert [step.status for step in report.steps] == [
            "succeeded",
            "succeeded",
            "succeeded",
        ]


def test_missing_research_brief_fails_at_artifact_boundary():
    invalid_research = _research()
    del invalid_research["research-brief"]
    client = SequenceClient((invalid_research,))
    report = run_content_workflow(
        _context("boundary-test"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(model="local-test", client=client),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[0].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-002"
    assert len(report.steps) == 1


def test_malformed_content_package_fails_before_review():
    invalid_content = _content()
    invalid_content["content-package"] = []
    client = SequenceClient((_research(), invalid_content))
    report = run_content_workflow(
        _context("content-boundary"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(model="local-test", client=client),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-003"
    assert len(report.steps) == 2


@pytest.mark.skipif(
    os.getenv("ASF_TEST_OLLAMA") != "1",
    reason="live Ollama requires explicit ASF_TEST_OLLAMA=1 opt-in",
)
def test_live_local_ollama_opt_in():
    model = os.environ["ASF_OLLAMA_MODEL"]
    report = run_content_workflow(
        _context("live-ollama-opt-in"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(model=model),
        compiled={},
    )
    assert report.status in ("succeeded", "failed")
