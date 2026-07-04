"""Evaluation IR: schemas/evaluation.schema.json's object model.

Evaluation is an embedded object (no schema_version, no id) -- it is
validated in place inside a Skill manifest or as a standalone fixture. This
adapter assumes structural (JSON Schema) validation already passed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetricIR:
    name: str
    description: str
    weight: float
    rubric: dict[str, str]
    minimum_score: float | None = None


@dataclass(frozen=True)
class ScoringIR:
    scale: str
    aggregate: str


@dataclass(frozen=True)
class AcceptanceIR:
    minimum_score: float
    hard_gates: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationIR:
    metrics: tuple[MetricIR, ...]
    scoring: ScoringIR
    acceptance: AcceptanceIR
    on_failure: str


def build_evaluation_ir(doc: dict[str, Any]) -> EvaluationIR:
    metrics = tuple(
        MetricIR(
            name=m["name"],
            description=m["description"],
            weight=m["weight"],
            rubric=dict(m["rubric"]),
            minimum_score=m.get("minimum_score"),
        )
        for m in doc["metrics"]
    )
    scoring = ScoringIR(scale=doc["scoring"]["scale"], aggregate=doc["scoring"]["aggregate"])
    acceptance = AcceptanceIR(
        minimum_score=doc["acceptance"]["minimum_score"],
        hard_gates=tuple(doc["acceptance"].get("hard_gates", [])),
    )
    return EvaluationIR(metrics=metrics, scoring=scoring, acceptance=acceptance, on_failure=doc["on_failure"])
