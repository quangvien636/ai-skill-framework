import json
from dataclasses import replace
from urllib.error import URLError

import pytest

import _bootstrap

from asf_runtime.binding import resolve_skill_runtime_binding
from asf_runtime.catalog import build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_runtime.planner import plan_workflow
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry
from ollama_execution.executor import OllamaStepExecutor, assemble_prompt


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


def _research_parts():
    catalog = _catalog()
    context = ExecutionContext.create(
        "executor-test",
        "workflow:research-content-review",
        "1.0.0",
        {
            "topic": "AI",
            "objective": "Prepare a brief.",
            "content-type": "short-video-script",
            "brief": "Explain AI.",
            "audience": "Workers.",
            "platform": "youtube",
        },
    )
    step = plan_workflow(context, catalog).steps[0]
    skill = catalog.exact(step.skill_id, step.skill_version).ir
    binding, diagnostics = resolve_skill_runtime_binding(skill, catalog)
    assert binding is not None and not diagnostics
    return step, skill, binding


class MissingServerClient:
    def list_models(self, endpoint, timeout_seconds):
        raise URLError("connection refused")

    def generate(self, endpoint, model, prompt, timeout_seconds):
        raise AssertionError("generate must not run")


class MissingModelClient:
    def list_models(self, endpoint, timeout_seconds):
        return ("another-model:latest",)

    def generate(self, endpoint, model, prompt, timeout_seconds):
        raise AssertionError("generate must not run")


class SuccessfulClient:
    def list_models(self, endpoint, timeout_seconds):
        return ("local-test:latest",)

    def generate(self, endpoint, model, prompt, timeout_seconds):
        return json.dumps(
            {
                "research-brief": {},
                "quality-report": {},
            }
        )


def test_missing_ollama_is_a_structured_step_failure():
    step, skill, binding = _research_parts()
    result = OllamaStepExecutor(
        model="local-test", client=MissingServerClient()
    ).execute(step, skill, binding, {"topic": "AI"})
    assert result.status == "failed"
    assert result.diagnostics[0].code == "ASF-EXEC-OLLAMA-001"
    assert "localhost:11434" in result.error_message


def test_missing_model_is_a_structured_step_failure():
    step, skill, binding = _research_parts()
    result = OllamaStepExecutor(
        model="local-test", client=MissingModelClient()
    ).execute(step, skill, binding, {"topic": "AI"})
    assert result.status == "failed"
    assert result.diagnostics[0].code == "ASF-EXEC-OLLAMA-002"


def test_non_ollama_runtime_requires_explicit_local_model_override():
    step, skill, binding = _research_parts()
    result = OllamaStepExecutor(client=SuccessfulClient()).execute(
        step, skill, binding, {"topic": "AI"}
    )
    assert result.status == "failed"
    assert result.diagnostics[0].code == "ASF-EXEC-OLLAMA-003"


def test_ollama_runtime_binding_supplies_model_without_override():
    step, skill, binding = _research_parts()
    local_model = replace(
        binding.model,
        provider="ollama",
        model="local-test",
        endpoint="http://localhost:11434",
    )
    local_binding = replace(binding, model=local_model)
    result = OllamaStepExecutor(client=SuccessfulClient()).execute(
        step, skill, local_binding, {"topic": "AI"}
    )
    assert result.status == "succeeded"


def test_external_endpoint_is_rejected_before_any_request():
    with pytest.raises(ValueError, match="loopback"):
        OllamaStepExecutor(
            model="local-test", endpoint="https://example.com"
        )


def test_prompt_assembly_is_deterministic_and_declares_output_contract():
    step, skill, _binding = _research_parts()
    first = assemble_prompt(step, skill, {"objective": "B", "topic": "A"})
    second = assemble_prompt(step, skill, {"topic": "A", "objective": "B"})
    assert first == second
    assert '"research-brief"' in first
    assert "Do not claim browsing" in first
