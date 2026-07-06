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


def _context(execution_id="runner-test", topic="AI"):
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


_CONCERNING_AI_TOPIC = "5 công nghệ AI đáng sợ nhất trong 2 năm tới"
_CONCERNING_AI_TOPIC_EN = "5 scariest AI technologies in the next two years"
_UNRELATED_TOPIC = "Best pasta recipes for a family dinner party"


def _research():
    return {
        "research-brief": {
            "objective": "Prepare a brief.",
            "scope": "Supplied evidence only.",
            "research-questions": [],
            "source-requirements": [],
            "findings": [
                "AI agents can automate multi-step digital work.",
                "Synthetic media can imitate voices and faces.",
                "AI-assisted cyber abuse can personalize attacks.",
                "Behavioral prediction can increase surveillance risk.",
                "Automated persuasion can scale misleading content.",
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
                "title": "5 công nghệ AI cần chú ý",
                "script": (
                    "Đây là kịch bản tiếng Việt hoàn chỉnh, trình bày năm "
                    "công nghệ AI cùng rủi ro thực tế và giới hạn bằng chứng. "
                ) * 5,
                "scenes": [
                    {
                        "id": f"scene-{index}",
                        "visual": "Người dẫn nhìn vào máy quay.",
                        "voice-over": "AI đang thay đổi cách chúng ta làm việc.",
                        "on-screen-text": "5 công nghệ AI",
                    }
                    for index in range(1, 6)
                ],
                "voice-over-text": (
                    "AI đang thay đổi cách chúng ta làm việc; mỗi công nghệ "
                    "cần được đánh giá bằng dữ liệu và trong đúng bối cảnh. "
                ) * 4,
                "on-screen-text": [
                    "Deepfake",
                    "AI agent",
                    "Tấn công mạng",
                    "Giám sát",
                    "Thông tin sai lệch",
                ],
                "call-to-action": "Bạn quan tâm công nghệ nào nhất?",
                "hashtags": ["#AI", "#CongNghe", "#AnToanSo"],
                "metadata": {
                    "language": "Vietnamese",
                    "platform": "youtube",
                },
            },
            "hook": "Năm công nghệ AI nào cần được chú ý?",
            "call-to-action": "Bạn quan tâm công nghệ nào nhất?",
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
    """A structurally valid package that drifted off the requested AI topic."""
    content = _content()
    package = content["content-package"]
    primary = package["primary-content"]
    primary["title"] = "Công nghệ AI giúp bảo vệ môi trường"
    primary["script"] = (
        "Cùng khám phá cách công nghệ AI có thể giúp bảo vệ môi trường và "
        "ứng phó với biến đổi khí hậu. AI phân tích khí thải nhà kính, theo "
        "dõi ô nhiễm không khí và đề xuất giải pháp năng lượng xanh cho "
        "tương lai bền vững. "
    ) * 4
    primary["voice-over-text"] = (
        "AI đang giúp con người bảo vệ môi trường bằng cách giám sát biến "
        "đổi khí hậu và tối ưu năng lượng xanh trong từng ngành công "
        "nghiệp. "
    ) * 4
    package["hook"] = "Bạn có biết AI giúp bảo vệ môi trường như thế nào?"
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


def _research_en():
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


def _content_en():
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
                "metadata": {
                    "language": "English",
                    "platform": "youtube",
                },
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


def _offtopic_environment_content_en():
    """An English package that structurally passes but drifted off-topic."""
    content = _content_en()
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


def _review_en():
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
            "draft": _content_en()["content-package"],
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
        content = report.final_artifact["content-package"]
        assert content["primary-content"]
        assert content["call-to-action"]
        assert report.final_artifact["reviewed-content-package"]["draft"]


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


def test_empty_primary_content_is_rejected():
    invalid_content = _content()
    invalid_content["content-package"]["primary-content"] = {}
    report = run_content_workflow(
        _context("empty-primary"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), invalid_content)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-007"


def test_empty_call_to_action_is_rejected():
    invalid_content = _content()
    invalid_content["content-package"]["call-to-action"] = ""
    report = run_content_workflow(
        _context("empty-cta"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), invalid_content)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-008"


def test_empty_reviewed_draft_is_rejected():
    invalid_review = _review()
    invalid_review["reviewed-package"]["draft"] = {}
    report = run_content_workflow(
        _context("empty-reviewed-draft"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), _content(), invalid_review)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-009"


def test_offtopic_environmental_drift_is_rejected():
    report = run_content_workflow(
        _context("offtopic-drift", topic=_CONCERNING_AI_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient(
                (_research(), _offtopic_environment_content())
            ),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-013"
    assert "off-topic" in report.steps[-1].error_message


def test_empty_hashtags_is_rejected():
    invalid_content = _content()
    invalid_content["content-package"]["primary-content"]["hashtags"] = []
    report = run_content_workflow(
        _context("empty-hashtags"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), invalid_content)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-011"
    assert "hashtags" in report.steps[-1].error_message


def test_too_short_script_and_voiceover_is_rejected():
    invalid_content = _content()
    invalid_content["content-package"]["primary-content"]["script"] = "Quá ngắn."
    invalid_content["content-package"]["primary-content"][
        "voice-over-text"
    ] = "Quá ngắn."
    report = run_content_workflow(
        _context("short-script"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), invalid_content)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-011"
    assert "script<400-chars" in report.steps[-1].error_message
    assert "voice-over-text<300-chars" in report.steps[-1].error_message


def test_draft_review_status_is_rejected():
    invalid_review = _review()
    invalid_review["reviewed-package"]["status"] = "Draft"
    report = run_content_workflow(
        _context("draft-status"),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research(), _content(), invalid_review)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-012"


def test_valid_ai_technology_output_is_accepted():
    report = run_content_workflow(
        _context("valid-ai-topic", topic=_CONCERNING_AI_TOPIC),
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


def test_english_valid_ai_technology_output_is_accepted():
    report = run_content_workflow(
        _context("valid-ai-topic-en", topic=_CONCERNING_AI_TOPIC_EN),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research_en(), _content_en(), _review_en())),
        ),
        compiled={},
    )
    assert report.status == "succeeded"
    assert report.final_artifact["reviewed-content-package"]["status"] == "approve"


def test_english_offtopic_environmental_drift_is_rejected():
    report = run_content_workflow(
        _context("offtopic-drift-en", topic=_CONCERNING_AI_TOPIC_EN),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient(
                (_research_en(), _offtopic_environment_content_en())
            ),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-013"
    assert "off-topic" in report.steps[-1].error_message


def test_completely_unrelated_topic_is_rejected():
    report = run_content_workflow(
        _context("unrelated-topic", topic=_UNRELATED_TOPIC),
        _catalog(),
        mode="live-local",
        executor=OllamaStepExecutor(
            model="local-test",
            client=SequenceClient((_research_en(),)),
        ),
        compiled={},
    )
    assert report.status == "failed"
    assert report.steps[-1].diagnostics[-1].code == "ASF-EXEC-BOUNDARY-013"


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
