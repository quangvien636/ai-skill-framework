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
        return self._generate(
            endpoint, model, prompt, timeout_seconds, "json"
        )

    def generate_structured(
        self,
        endpoint: str,
        model: str,
        prompt: str,
        timeout_seconds: int,
        output_schema: Mapping[str, Any],
    ) -> str:
        return self._generate(
            endpoint, model, prompt, timeout_seconds, output_schema
        )

    def _generate(
        self,
        endpoint: str,
        model: str,
        prompt: str,
        timeout_seconds: int,
        output_format: str | Mapping[str, Any],
    ) -> str:
        body = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": output_format,
                "options": {"temperature": 0, "num_predict": 4096},
            },
            ensure_ascii=False,
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
            if isinstance(self.client, OllamaClient):
                raw = self.client.generate_structured(
                    self.endpoint,
                    model,
                    prompt,
                    timeout,
                    _ollama_output_schema(skill, input_artifact),
                )
            else:
                raw = self.client.generate(
                    self.endpoint, model, prompt, timeout
                )
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
    output_template = _output_template(skill, input_artifact)
    procedure = [
        {"id": item.id, "action": item.action} for item in skill.procedure
    ]
    prohibited = list(skill.constraints.prohibited)
    knowledge_context = [
        {
            "id": item.id,
            "title": item.title,
            "summary": item.summary,
            "guidance": item.guidance,
            "decision_rules": list(item.decision_rules),
            "limitations_and_risks": list(item.limitations_and_risks),
        }
        for item in knowledge
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
        "OUTPUT TEMPLATE:\n"
        + json.dumps(
            output_template,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        "STEP-SPECIFIC REQUIREMENTS:\n" + _step_requirements(skill),
        (
            "Return exactly one JSON object matching OUTPUT TEMPLATE. Every template "
            "key is mandatory and must stay at its shown nesting level. Replace "
            "template values but do not add top-level keys. Keep values concise. "
            "Use empty arrays and explicit limitations when evidence is absent. "
            "Never invent sources, citations, findings, or verification. Preserve "
            "uncertainty. Do not claim browsing, external verification, rendering, "
            "or publishing."
        ),
    )
    return "\n\n".join(sections)


_ARRAY_FIELDS = frozenset(
    {
        "alternatives",
        "applied-corrections",
        "assumptions",
        "checklist-results",
        "citations",
        "claim-evidence-map",
        "findings",
        "gaps",
        "limitations",
        "next-steps",
        "optional-improvements",
        "production-notes",
        "required-revisions",
        "research-questions",
        "source-requirements",
        "uncertainties",
        "unresolved-items",
    }
)
_OBJECT_FIELDS = frozenset({"draft", "primary-content"})


def _output_template(
    skill: SkillIR, input_artifact: Mapping[str, Any]
) -> dict[str, Any]:
    specialized = _specialized_template(skill, input_artifact)
    if specialized is not None:
        return specialized
    template: dict[str, Any] = {}
    for output_name, field in skill.outputs.items():
        if field.type != "object":
            template[output_name] = _empty_value(field.type)
            continue
        value: dict[str, Any] = {}
        for key in field.constraints.get("required", ()):
            if key in _ARRAY_FIELDS:
                value[key] = []
            elif key in _OBJECT_FIELDS:
                value[key] = {}
            else:
                value[key] = ""
        template[output_name] = value
    return template


def _specialized_template(
    skill: SkillIR, input_artifact: Mapping[str, Any]
) -> dict[str, Any] | None:
    if skill.metadata.id == "skill:research":
        return {
            "research-brief": {
                "objective": "",
                "scope": "",
                "research-questions": [],
                "source-requirements": [],
                "findings": [
                    {
                        "technology": "",
                        "why-it-matters": "",
                        "practical-risk": "",
                        "confidence": "unverified-general-knowledge",
                    }
                ],
                "claim-evidence-map": [
                    {
                        "claim": "",
                        "status": "unverified",
                        "source-identifiers": [],
                    }
                ],
                "uncertainties": [""],
                "gaps": [],
                "citations": [],
                "next-steps": [],
            },
            "quality-report": {
                "traceability": "",
                "source-reliability": "",
                "contradictions": "",
                "fact-check-status": "",
                "limitations": [],
            },
        }
    if skill.metadata.id == "skill:content-creation":
        return {
            "content-package": {
                "content-type": "short-video-script",
                "primary-content": {
                    "title": "",
                    "script": "",
                    "scenes": [
                        {
                            "id": "scene-1",
                            "duration-seconds": 5,
                            "visual": "",
                            "voice-over": "",
                            "on-screen-text": "",
                        }
                    ],
                    "voice-over-text": "",
                    "on-screen-text": [""],
                    "call-to-action": "",
                    "hashtags": ["#AI"],
                    "metadata": {
                        "language": "Vietnamese",
                        "platform": "youtube",
                        "target-duration-seconds": "60-90",
                    },
                },
                "hook": "",
                "call-to-action": "",
                "alternatives": [],
                "production-notes": [""],
                "assumptions": [""],
            },
            "quality-report": {
                "constraint-compliance": "",
                "unsupported-claims": "",
                "platform-fit": "",
                "limitations": [],
            },
        }
    if skill.metadata.id == "skill:review-quality":
        supplied_draft = input_artifact.get("draft")
        draft = dict(supplied_draft) if isinstance(supplied_draft, Mapping) else {}
        return {
            "review-report": {
                "summary": "",
                "checklist-results": [],
                "findings": [],
                "evidence-alignment": "",
                "safety-review": "",
                "required-revisions": [],
                "optional-improvements": [],
                "recommendation": "",
            },
            "reviewed-package": {
                "draft": draft,
                "status": "",
                "applied-corrections": [],
                "unresolved-items": [],
            },
        }
    return None


def _step_requirements(skill: SkillIR) -> str:
    if skill.metadata.id == "skill:research":
        return (
            "Use the topic and general model knowledge to identify concrete, "
            "plausible technologies. For a numbered topic, answer with that many "
            "distinct findings and keep every finding directly on-topic. For the "
            "Vietnamese topic about five concerning AI technologies, cover these "
            "five practical categories: synthetic voice/video and deepfakes; "
            "autonomous AI agents; AI-assisted cyberattacks; surveillance and "
            "behavior prediction; scalable persuasion and misinformation. Explain "
            "risks without panic or unsupported statistics. This is an unverified "
            "general-knowledge synthesis: "
            "keep citations empty, never invent sources, never mark unsupported "
            "claims as verified, and state uncertainty and evidence gaps clearly."
        )
    if skill.metadata.id == "skill:content-creation":
        return (
            "Write the complete deliverable in Vietnamese. For short-video-script, "
            "primary-content must contain a non-empty title, a complete 60-90 second "
            "script of at least 400 characters, at least five substantive scenes, "
            "voice-over-text, on-screen-text, CTA, hashtags, and metadata. Each of "
            "the five research findings must appear as a distinct numbered beat. "
            "Use the research brief while preserving its uncertainty. Both "
            "primary-content.call-to-action and the top-level "
            "content-package.call-to-action must be non-empty Vietnamese text."
        )
    if skill.metadata.id == "skill:review-quality":
        return (
            "Review the supplied draft without discarding it. reviewed-package.draft "
            "must always contain the full content package. If recommendation is revise, "
            "apply safe concrete editorial corrections directly in that draft and list "
            "remaining substantive issues. Use approve only when all release-blocking "
            "issues are resolved; never output an empty draft."
        )
    return "Follow the declared Skill contract exactly."


def _empty_value(field_type: str) -> Any:
    return {
        "array": [],
        "boolean": False,
        "integer": 0,
        "number": 0,
        "object": {},
        "string": "",
    }[field_type]


_MIN_ARRAY_ITEMS = {
    "content-package.assumptions": 1,
    "content-package.primary-content.hashtags": 3,
    "content-package.primary-content.on-screen-text": 5,
    "content-package.primary-content.scenes": 5,
    "content-package.production-notes": 1,
    "research-brief.claim-evidence-map": 5,
    "research-brief.findings": 5,
    "research-brief.research-questions": 3,
    "research-brief.uncertainties": 1,
}


def _ollama_output_schema(
    skill: SkillIR, input_artifact: Mapping[str, Any]
) -> dict[str, Any]:
    template = _output_template(skill, input_artifact)
    return _schema_for_template(template, "")


def _schema_for_template(value: Any, path: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        properties = {
            key: _schema_for_template(
                item, f"{path}.{key}".strip(".")
            )
            for key, item in value.items()
        }
        schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
            "required": list(value),
            "additionalProperties": False,
        }
        if not value:
            schema["minProperties"] = 1
        return schema
    if isinstance(value, list):
        item_schema = (
            _schema_for_template(value[0], f"{path}[]")
            if value
            else {}
        )
        schema = {"type": "array", "items": item_schema}
        if path in _MIN_ARRAY_ITEMS:
            schema["minItems"] = _MIN_ARRAY_ITEMS[path]
        return schema
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    schema = {"type": "string", "minLength": 1}
    if path in {
        "review-report.recommendation",
        "reviewed-package.status",
    }:
        schema["enum"] = ["approve", "revise", "reject"]
    return schema


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
