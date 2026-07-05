"""Local Ollama StepExecutor; no cloud provider and no API key."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from asf_runtime.binding import RuntimeBinding, to_binding_ir
from asf_runtime.models import PlanStep
from asf_validator.knowledge_ir import KnowledgeIR
from asf_validator.skill_ir import SkillIR

from .models import ExecutionDiagnostic, StepExecutionResult

DEFAULT_OLLAMA_ENDPOINT = "http://localhost:11434"


class OllamaClientProtocol(Protocol):
    def list_models(self, endpoint: str, timeout_seconds: int) -> tuple[str, ...]: ...

    def generate(
        self,
        endpoint: str,
        model: str,
        prompt: str,
        timeout_seconds: int,
    ) -> str: ...


class OllamaClient:
    """Small standard-library client for Ollama's local HTTP API."""

    def _json(
        self,
        request: Request,
        timeout_seconds: int,
    ) -> Mapping[str, Any]:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("Ollama returned a non-object JSON response.")
        return payload

    def list_models(self, endpoint: str, timeout_seconds: int) -> tuple[str, ...]:
        request = Request(f"{endpoint.rstrip('/')}/api/tags", method="GET")
        payload = self._json(request, timeout_seconds)
        models = payload.get("models", [])
        if not isinstance(models, list):
            raise ValueError("Ollama /api/tags response has invalid 'models'.")
        return tuple(
            str(item.get("name") or item.get("model"))
            for item in models
            if isinstance(item, Mapping) and (item.get("name") or item.get("model"))
        )

    def generate(
        self,
        endpoint: str,
        model: str,
        prompt: str,
        timeout_seconds: int,
    ) -> str:
        body = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
            }
        ).encode("utf-8")
        request = Request(
            f"{endpoint.rstrip('/')}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        payload = self._json(request, timeout_seconds)
        response = payload.get("response")
        if not isinstance(response, str) or not response.strip():
            raise ValueError("Ollama response is missing generated text.")
        return response


class OllamaStepExecutor:
    """Executes one already-planned Skill through local Ollama."""

    def __init__(
        self,
        model: str | None = None,
        endpoint: str = DEFAULT_OLLAMA_ENDPOINT,
        timeout_seconds: int | None = None,
        client: OllamaClientProtocol | None = None,
    ):
        _validate_local_endpoint(endpoint)
        self.model_override = model
        self.endpoint = endpoint.rstrip("/")
        self.timeout_override = timeout_seconds
        self.client = client or OllamaClient()

    def execute(
        self,
        step: PlanStep,
        skill: SkillIR,
        binding: RuntimeBinding,
        input_artifact: Mapping[str, Any],
        knowledge: tuple[KnowledgeIR, ...] = (),
    ) -> StepExecutionResult:
        started = time.perf_counter()
        binding_ir = to_binding_ir(binding, ()).as_dict()
        timeout = self.timeout_override or binding.timeout_seconds
        diagnostics: list[ExecutionDiagnostic] = []

        try:
            model = self._model(binding)
            available = self.client.list_models(self.endpoint, timeout)
            if not _model_is_available(model, available):
                message = (
                    f"Ollama model '{model}' is not installed. "
                    f"Available models: {list(available)}."
                )
                diagnostics.append(
                    ExecutionDiagnostic(
                        "ASF-EXEC-OLLAMA-002",
                        "error",
                        message,
                        step.id,
                    )
                )
                return _failed(
                    step, binding_ir, input_artifact, diagnostics, message, started
                )

            prompt = assemble_prompt(step, skill, input_artifact, knowledge)
            raw = self.client.generate(self.endpoint, model, prompt, timeout)
            output = _parse_generated_object(raw)
            return StepExecutionResult(
                step_id=step.id,
                skill_id=step.skill_id,
                runtime_binding=binding_ir,
                input_artifact=input_artifact,
                output_artifact=output,
                diagnostics=(),
                status="succeeded",
                error_message=None,
                duration_ms=_elapsed_ms(started),
            )
        except HTTPError as error:
            message = f"Ollama returned HTTP {error.code}: {error.reason}"
            diagnostics.append(
                ExecutionDiagnostic(
                    "ASF-EXEC-OLLAMA-004", "error", message, step.id
                )
            )
        except (ConnectionError, TimeoutError, URLError) as error:
            message = (
                f"Local Ollama is unavailable at '{self.endpoint}': "
                f"{getattr(error, 'reason', error)}"
            )
            diagnostics.append(
                ExecutionDiagnostic(
                    "ASF-EXEC-OLLAMA-001", "error", message, step.id
                )
            )
        except ValueError as error:
            code = (
                "ASF-EXEC-OLLAMA-003"
                if "not bound to Ollama" in str(error)
                else "ASF-EXEC-OLLAMA-005"
            )
            message = f"Ollama returned malformed structured output: {error}"
            if code == "ASF-EXEC-OLLAMA-003":
                message = str(error)
            diagnostics.append(
                ExecutionDiagnostic(
                    code, "error", message, step.id
                )
            )
        return _failed(step, binding_ir, input_artifact, diagnostics, message, started)

    def _model(self, binding: RuntimeBinding) -> str:
        if self.model_override:
            return self.model_override
        if binding.model is not None and binding.model.provider == "ollama":
            return binding.model.model
        raise ValueError(
            f"Skill '{binding.skill_id}' is not bound to Ollama; "
            "live-local requires an explicit --model override."
        )


def assemble_prompt(
    step: PlanStep,
    skill: SkillIR,
    input_artifact: Mapping[str, Any],
    knowledge: tuple[KnowledgeIR, ...] = (),
) -> str:
    """Build a stable JSON-only prompt from validated Skill IR."""
    output_contract = {
        name: {
            "type": field.type,
            "required_keys": list(field.constraints.get("required", ())),
            "additional_properties": field.additional_properties,
        }
        for name, field in skill.outputs.items()
    }
    procedure = [
        {"id": item.id, "action": item.action} for item in skill.procedure
    ]
    prohibited = list(skill.constraints.prohibited)
    knowledge_context = [
        item.as_normalized_dict() for item in knowledge
    ]
    sections = (
        f"STEP: {step.id}",
        f"SKILL: {skill.metadata.id}@{skill.metadata.version.raw}",
        f"RESPONSIBILITY: {skill.responsibility}",
        "PROCEDURE:\n"
        + json.dumps(procedure, ensure_ascii=False, sort_keys=True),
        "PROHIBITED:\n"
        + json.dumps(prohibited, ensure_ascii=False, sort_keys=True),
        "RESOLVED KNOWLEDGE:\n"
        + json.dumps(
            knowledge_context,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        "INPUT:\n"
        + json.dumps(
            input_artifact, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ),
        "OUTPUT CONTRACT:\n"
        + json.dumps(
            output_contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ),
        (
            "Return exactly one JSON object containing only the declared top-level "
            "outputs. Preserve uncertainty. Do not claim browsing, external "
            "verification, rendering, or publishing."
        ),
    )
    return "\n\n".join(sections)


def _validate_local_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        raise ValueError(
            "Ollama endpoint must be a local HTTP loopback address "
            "(localhost, 127.0.0.1, or ::1)."
        )


def _model_is_available(requested: str, available: tuple[str, ...]) -> bool:
    return any(
        item == requested
        or item == f"{requested}:latest"
        or requested == f"{item}:latest"
        for item in available
    )


def _parse_generated_object(raw: str) -> Mapping[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    payload = json.loads(text)
    if not isinstance(payload, Mapping):
        raise ValueError("generated JSON must be an object")
    return dict(payload)


def _failed(
    step: PlanStep,
    binding_ir: Mapping[str, Any],
    input_artifact: Mapping[str, Any],
    diagnostics: list[ExecutionDiagnostic],
    message: str,
    started: float,
) -> StepExecutionResult:
    return StepExecutionResult(
        step_id=step.id,
        skill_id=step.skill_id,
        runtime_binding=binding_ir,
        input_artifact=input_artifact,
        output_artifact=None,
        diagnostics=tuple(diagnostics),
        status="failed",
        error_message=message,
        duration_ms=_elapsed_ms(started),
    )


def _elapsed_ms(started: float) -> int:
    return max(0, round((time.perf_counter() - started) * 1000))
