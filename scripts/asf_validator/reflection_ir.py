"""Reflection IR: schemas/reflection.schema.json's object model.

Reflection is an embedded object, like Evaluation -- see evaluation_ir.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReflectionIR:
    enabled: bool
    max_attempts: int
    minimum_improvement: float
    on_exhausted: str
    reflectable_hard_gates: tuple[str, ...]


def build_reflection_ir(doc: dict[str, Any]) -> ReflectionIR:
    return ReflectionIR(
        enabled=doc["enabled"],
        max_attempts=doc["max_attempts"],
        minimum_improvement=doc["minimum_improvement"],
        on_exhausted=doc["on_exhausted"],
        reflectable_hard_gates=tuple(doc.get("reflectable_hard_gates", [])),
    )
