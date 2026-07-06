"""Integration tests for the seam between ``runner.run_content_workflow``
and the topic-relevance subsystem (``evaluate_topic_relevance`` /
``TopicRelevanceResult``).

Each module already has focused unit tests (test_topic_relevance.py,
test_domain_classification.py, test_tokenization.py, test_semantic.py,
test_topic_relevance_config.py); this file verifies they compose correctly
through the real ``run_content_workflow`` execution path, not in isolation.
"""

from __future__ import annotations

import importlib
import json

import _bootstrap  # noqa: F401  (adds scripts/ and adapters/ to sys.path)

from asf_runtime.catalog import build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_validator.pipeline import build_ir
from asf_validator.project_discovery import discover_project
from asf_validator.schema_registry import build_schema_registry

import ollama_execution.runner as runner_module
from ollama_execution import OllamaStepExecutor
from ollama_execution.semantic import CosineSimilarity, SemanticRelevanceValidator
from ollama_execution.topic_relevance import TopicRelevanceResult, evaluate_topic_relevance


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


def _context(execution_id: str, topic: str) -> ExecutionContext:
    return ExecutionContext.create(
        execution_id,
        "workflow:research-content-review",
        "1.0.0",
        {
            "topic": topic,
            "objective": "Prepare a brief.",
            "content-type": "short-video-script",
            "brief": "Explain AI without exaggeration.",
            "audience": "Workers.",
            "platform": "youtube",
        },
    )


_AI_TOPIC = "5 scariest AI technologies in the next two years"


def _research():
    return {
        "research-brief": {
            "objective": "Identify the scariest AI technologies to watch.",
            "scope": "Supplied evidence only.",
            "research-questions": [],
            "source-requirements": [],
            "findings": [
                "Deepfake technologies can imitate real people's voices and faces.",
                "Autonomous AI agents can take multi-step actions without oversight.",
                "AI-assisted cyberattacks can personalize scams at scale.",
                "Surveillance AI technologies can predict and track human behavior.",
                "Persuasion AI technologies can scale convincing misinformation.",
            ],
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
            "primary-content": {
                "title": "5 Scariest AI Technologies You Should Know",
                "script": (
                    "Let's explore five scariest AI technologies raising real "
                    "concerns today, from deepfake video generation to "
                    "autonomous AI agents that can act without oversight. "
                )
                * 5,
                "scenes": [
                    {
                        "id": f"scene-{index}",
                        "visual": "A presenter speaks directly to camera.",
                        "voice-over": (
                            "AI is reshaping how attacks and surveillance can "
                            "scale."
                        ),
                        "on-screen-text": "Scary AI Tech",
                    }
                    for index in range(1, 6)
                ],
                "voice-over-text": (
                    "These AI technologies are reshaping cybersecurity, "
                    "surveillance, and misinformation risks; each deserves "
                    "careful scrutiny. "
                )
                * 4,
                "on-screen-text": [
                    "Deepfakes",
                    "AI agents",
                    "Cyberattacks",
                    "Surveillance",
                    "Misinformation",
                ],
                "call-to-action": "Which AI technology worries you the most?",
                "hashtags": ["#AI", "#TechNews", "#Cybersecurity"],
                "metadata": {"language": "English", "platform": "youtube"},
            },
            "hook": "Which scary AI technologies should you watch for?",
            "call-to-action": "Which AI technology worries you the most?",
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


def _offtopic_environment_content():
    content = _content()
    package = content["content-package"]
    primary = package["primary-content"]
    primary["title"] = "How AI Helps Protect the Environment"
    primary["script"] = (
        "Discover how AI technology helps protect the environment and "
        "fight climate change. AI analyzes greenhouse gas emissions, "
        "tracks air pollution, and recommends renewable energy solutions "
        "for a sustainable future. "
    ) * 4
    primary["voice-over-text"] = (
        "AI is helping humanity protect the environment by monitoring "
        "climate change and optimizing renewable energy across "
        "industries. "
    ) * 4
    package["hook"] = "Did you know AI can help protect the environment?"
    return content


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


# ---------------------------------------------------------------------------
# Priority 1 requirement: runner.py correctly consumes TopicRelevanceResult.passed
# ---------------------------------------------------------------------------


def test_runner_treats_passed_true_as_no_topic_diagnostic(monkeypatch):
    """A stubbed `evaluate_topic_relevance` returning passed=True must add
    zero diagnostics, regardless of what real lexical scoring would say."""
    monkeypatch.setattr(
        runner_module,
        "evaluate_topic_relevance",
        lambda *args, **kwargs: TopicRelevanceResult(passed=True, reason=None),
    )
    report = runner_module.run_content_workflow(
        _context("stub-passed-true", _AI_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), _content(), _review())),
        ),
        compiled={},
    )
    assert report.status == "succeeded"
    assert all(
        diagnostic.code != "ASF-EXEC-BOUNDARY-013"
        for diagnostic in report.diagnostics
    )


def test_runner_treats_passed_false_as_a_boundary_013_failure(monkeypatch):
    """A stubbed `evaluate_topic_relevance` returning passed=False must be
    surfaced as ASF-EXEC-BOUNDARY-013 with the stub's own reason text,
    regardless of the (perfectly on-topic) real content supplied."""
    monkeypatch.setattr(
        runner_module,
        "evaluate_topic_relevance",
        lambda *args, **kwargs: TopicRelevanceResult(
            passed=False, reason="stubbed rejection for integration test"
        ),
    )
    report = runner_module.run_content_workflow(
        _context("stub-passed-false", _AI_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), _content(), _review())),
        ),
        compiled={},
    )
    assert report.status == "failed"
    failing_step = report.steps[-1]
    assert failing_step.diagnostics[-1].code == "ASF-EXEC-BOUNDARY-013"
    assert "stubbed rejection for integration test" in failing_step.error_message


# ---------------------------------------------------------------------------
# Priority 1 requirement: legacy .relevant property still behaves identically
# ---------------------------------------------------------------------------


def test_legacy_relevant_alias_matches_passed_using_runners_own_config():
    """Exercise evaluate_topic_relevance with the exact config object runner.py
    loads at import time, for both an accepted and a rejected input, and
    confirm `.relevant` never diverges from `.passed`."""
    config = runner_module._TOPIC_RELEVANCE_CONFIG

    accepted = evaluate_topic_relevance(
        _AI_TOPIC,
        "The scariest AI technologies include deepfakes and autonomous agents.",
        config=config,
    )
    assert accepted.passed is True
    assert accepted.relevant is accepted.passed

    rejected = evaluate_topic_relevance(
        _AI_TOPIC,
        (
            "AI helps protect the environment and fight climate change by "
            "tracking greenhouse gas emissions and renewable energy."
        ),
        config=config,
    )
    assert rejected.passed is False
    assert rejected.relevant is rejected.passed


# ---------------------------------------------------------------------------
# Priority 1 requirement: evaluate_topic_relevance() integrates correctly
# with runner (success and rejection paths, with cross-checked diagnostics)
# ---------------------------------------------------------------------------


def test_runner_success_path_reflects_a_real_passing_topic_relevance_result():
    report = runner_module.run_content_workflow(
        _context("integration-success", _AI_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), _content(), _review())),
        ),
        compiled={},
    )
    assert report.status == "succeeded"
    assert report.final_artifact["reviewed-content-package"]["status"] == "approve"


def test_runner_rejection_path_message_matches_direct_evaluate_call():
    """The diagnostic message the runner reports for a drifted step must be
    derived from the same TopicRelevanceResult.reason a direct call to
    evaluate_topic_relevance would produce for equivalent input -- proving
    the two layers are not silently diverging."""
    offtopic_content = _offtopic_environment_content()
    report = runner_module.run_content_workflow(
        _context("integration-rejection", _AI_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), offtopic_content)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    failing_step = report.steps[-1]
    assert failing_step.diagnostics[-1].code == "ASF-EXEC-BOUNDARY-013"

    primary = offtopic_content["content-package"]["primary-content"]
    package = offtopic_content["content-package"]
    combined_text = " ".join(
        [
            package["hook"],
            package["call-to-action"],
            primary["title"],
            primary["script"],
            primary["voice-over-text"],
            primary["call-to-action"],
        ]
    )
    direct_result = evaluate_topic_relevance(
        _AI_TOPIC, combined_text, config=runner_module._TOPIC_RELEVANCE_CONFIG
    )
    assert direct_result.passed is False
    assert direct_result.reason in failing_step.error_message


# ---------------------------------------------------------------------------
# Priority 1 requirement: lexical rejection prevents semantic evaluation,
# and the disabled-semantic path never performs embedding work -- both
# verified through the real runner call path, not just the facade function.
# ---------------------------------------------------------------------------


def test_lexical_rejection_prevents_semantic_evaluation_through_runner(monkeypatch):
    """The research step is on-topic (lexically passes, so its own semantic
    pass legitimately runs); the content step drifts to the environment
    domain (lexically rejected). Only the content step's rejection is under
    test here: its offtopic text must never reach the embedding provider.
    """
    embed_calls: list[str] = []

    class RecordingEmbeddingProvider:
        def embed(self, text: str) -> tuple[float, ...]:
            embed_calls.append(text)
            return (1.0, 0.0)

    spy_semantic_validator = SemanticRelevanceValidator(
        embedding_provider=RecordingEmbeddingProvider(),
        similarity=CosineSimilarity(),
        threshold=0.5,
        enabled=True,
    )
    real_evaluate = runner_module.evaluate_topic_relevance

    def wrapped_evaluate(topic, text, config, **kwargs):
        return real_evaluate(
            topic, text, config=config, semantic_validator=spy_semantic_validator
        )

    monkeypatch.setattr(runner_module, "evaluate_topic_relevance", wrapped_evaluate)

    offtopic_content = _offtopic_environment_content()
    report = runner_module.run_content_workflow(
        _context("lexical-blocks-semantic", _AI_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), offtopic_content)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-013"
    # The research step passed lexically, so its own semantic pass ran (one
    # embed() call for the topic, one for the research text) -- that's
    # correct, expected behavior, not what this test guards against.
    assert len(embed_calls) == 2
    # What must never happen: the drifted content step's text reaching the
    # embedding provider at all.
    assert not any("protect the environment" in call for call in embed_calls)


def test_runner_never_wires_a_semantic_validator_in_production(monkeypatch):
    """Today runner.py never passes `semantic_validator` at all. Spy on the
    call to guarantee that stays true -- i.e. embedding work is structurally
    impossible in the default production path, not just "disabled" by a
    flag that a future change could flip unnoticed."""
    calls: list[dict] = []
    real_evaluate = runner_module.evaluate_topic_relevance

    def spying_evaluate(*args, **kwargs):
        calls.append(kwargs)
        return real_evaluate(*args, **kwargs)

    monkeypatch.setattr(runner_module, "evaluate_topic_relevance", spying_evaluate)

    report = runner_module.run_content_workflow(
        _context("no-semantic-by-default", _AI_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), _content(), _review())),
        ),
        compiled={},
    )
    assert report.status == "succeeded"
    assert len(calls) == 3  # research, content-creation, review-quality steps
    for call_kwargs in calls:
        assert call_kwargs.get("semantic_validator") is None


# ---------------------------------------------------------------------------
# Priority 1 requirement: config loading works correctly in real execution
# ---------------------------------------------------------------------------


def test_module_level_config_matches_a_fresh_load_with_no_override(monkeypatch):
    from ollama_execution.topic_relevance_config import load_topic_relevance_config

    monkeypatch.delenv("ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG", raising=False)
    assert runner_module._TOPIC_RELEVANCE_CONFIG == load_topic_relevance_config()


def test_env_var_config_override_changes_runner_behavior_after_reload(
    tmp_path, monkeypatch
):
    """Config is loaded once at module-import time (a documented, deliberate
    choice: config changes take effect on process restart, not mid-process).
    Simulate that restart with importlib.reload and confirm an override
    genuinely changes what the real execution path accepts or rejects.
    """
    override = tmp_path / "topic_relevance.json"
    override.write_text(
        json.dumps(
            {
                "domain_terms": {"custom-drift-test": ["deepfake"]},
                "min_domain_indicator_occurrences": 1,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG", str(override))
    try:
        importlib.reload(runner_module)
        assert runner_module._TOPIC_RELEVANCE_CONFIG.domain_terms.get(
            "custom-drift-test"
        ) == ("deepfake",)

        # The topic never mentions "deepfake", so the newly configured
        # domain now flags the (otherwise on-topic) content as drifted --
        # behavior the default config would never produce for this input.
        report = runner_module.run_content_workflow(
            _context("env-override-drift", _AI_TOPIC),
            _catalog(),
            mode="live-local",
            executor=OllamaStepExecutor(
                model="local-test",
                client=SequenceClient((_research(), _content())),
            ),
            compiled={},
        )
        assert report.status == "failed"
        failing_step = report.steps[-1]
        assert failing_step.diagnostics[-1].code == "ASF-EXEC-BOUNDARY-013"
        assert "custom-drift-test" in failing_step.error_message
    finally:
        monkeypatch.delenv("ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG", raising=False)
        importlib.reload(runner_module)


def test_reload_without_override_restores_default_behavior(monkeypatch):
    """Companion to the override test above: confirms module reload is a
    clean, reversible operation so test isolation holds for every test file
    that imports ollama_execution.runner after this one runs."""
    monkeypatch.delenv("ASF_OLLAMA_TOPIC_RELEVANCE_CONFIG", raising=False)
    importlib.reload(runner_module)
    report = runner_module.run_content_workflow(
        _context("post-reload-default", _AI_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), _content(), _review())),
        ),
        compiled={},
    )
    assert report.status == "succeeded"
