import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

import _bootstrap

from asf_cli import _bindings, _normalize_cli_unicode, main
from asf_runtime.catalog import ArtifactCatalog, CatalogArtifact, build_artifact_catalog
from asf_runtime.models import ExecutionContext
from asf_runtime.planner import plan_workflow
from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry


class CliTests(unittest.TestCase):
    def run_cli(self, *arguments):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                ("--format", "json", "--start", str(_bootstrap.REPO_ROOT))
                + arguments
            )
        return exit_code, json.loads(output.getvalue())

    def test_validate_returns_structured_clean_report(self):
        exit_code, report = self.run_cli("validate")
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["summary"]["errors"], 0)

    def test_all_read_only_repository_commands_succeed(self):
        for command in ("build-ir", "graph", "doctor"):
            with self.subTest(command=command):
                exit_code, report = self.run_cli(command)
                self.assertEqual(exit_code, 0)
                self.assertEqual(report["status"], "ok")

    def test_plan_and_bindings_reuse_runtime_pipeline(self):
        common = (
            "--workflow",
            "workflow:research-topic-to-brief",
            "--inputs",
            '{"topic":"Determinism","objective":"Prepare a brief."}',
        )
        exit_code, plan = self.run_cli("plan", *common)
        self.assertEqual(exit_code, 0)
        self.assertEqual(plan["plan"]["steps"][0]["runtime"][0], "runtime:research")
        exit_code, bindings = self.run_cli("bindings", *common)
        self.assertEqual(exit_code, 0)
        self.assertEqual(bindings["bindings"][0]["runtime_id"], "runtime:research")

    def test_bindings_reports_missing_binding_as_a_diagnostic_not_a_crash(self):
        """ASF-BINDING-001 (a step's Skill has no resolvable binding) must be
        collected into the report's diagnostics, matching validate/graph --
        not raised as a bare exception that skips every other step."""
        from dataclasses import replace

        fixtures = (
            _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph" / "valid-runtime"
        )
        registry = build_schema_registry(_bootstrap.REPO_ROOT / "schemas")
        results = [
            build_ir("workflow", fixtures / "workflow.yaml", registry),
            build_ir("skill", fixtures / "skill.yaml", registry),
            build_ir("runtime", fixtures / "runtime.yaml", registry),
            build_ir("runtime", fixtures / "runtime-fallback.yaml", registry),
            build_ir("tool", fixtures / "tool.yaml", registry),
            build_ir("knowledge", fixtures / "knowledge.md", registry),
        ]
        assert all(result.ok for result in results), [
            (result.artifact, result.diagnostics) for result in results if not result.ok
        ]
        catalog = build_artifact_catalog(results)
        context = ExecutionContext.create(
            execution_id="execution-missing-binding",
            workflow_id="workflow:use-runtime",
            workflow_version="1.0.0",
            inputs={},
        )
        plan = plan_workflow(context, catalog)

        # Planning itself already hard-fails on an unresolved *required*
        # runtime reference, so the only way _bindings() legitimately sees
        # binding=None for an already-planned step is a *non-required*
        # reference that still fails to resolve -- swap the skill's
        # dependency after planning to construct exactly that.
        original = next(a for a in catalog.artifacts if a.id == "skill:use-runtime")
        dangling_ref = replace(
            original.ir.dependencies.runtime[0], id="runtime:does-not-exist", required=False
        )
        broken_skill = replace(
            original.ir,
            dependencies=replace(original.ir.dependencies, runtime=(dangling_ref,)),
        )
        broken_artifact = CatalogArtifact(
            kind=original.kind, id=original.id, version=original.version,
            status=original.status, path=original.path, ir=broken_skill,
        )
        artifacts = tuple(
            broken_artifact if a is original else a for a in catalog.artifacts
        )
        grouped: dict[str, list] = {}
        for artifact in artifacts:
            grouped.setdefault(artifact.id, []).append(artifact)
        broken_catalog = ArtifactCatalog(
            artifacts, MappingProxyType({k: tuple(v) for k, v in grouped.items()})
        )

        workspace = SimpleNamespace(catalog=broken_catalog)
        bindings, diagnostics = _bindings(workspace, plan)

        self.assertEqual(bindings, [])
        self.assertEqual({d.code for d in diagnostics}, {"ASF-BINDING-001"})

    def test_invalid_inputs_are_structured_cli_diagnostic(self):
        exit_code, report = self.run_cli(
            "plan",
            "--workflow",
            "workflow:research-topic-to-brief",
            "--inputs",
            "[]",
        )
        self.assertEqual(exit_code, 2)
        self.assertEqual(report["diagnostics"][0]["code"], "ASF-CLI-001")

    def test_missing_workflow_uses_not_found_exit_code(self):
        exit_code, report = self.run_cli(
            "plan", "--workflow", "workflow:not-present"
        )
        self.assertEqual(exit_code, 4)
        self.assertEqual(report["status"], "error")

    def test_reports_have_a_stable_version(self):
        _exit_code, report = self.run_cli("doctor")
        self.assertEqual(report["report_version"], "1.0")

    def test_text_plan_is_concise_and_names_the_skill(self):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                (
                    "--start",
                    str(_bootstrap.REPO_ROOT),
                    "plan",
                    "--workflow",
                    "workflow:research-topic-to-brief",
                    "--inputs",
                    '{"topic":"Determinism","objective":"Prepare a brief."}',
                )
            )
        self.assertEqual(exit_code, 0)
        self.assertIn("1 step(s), 1 batch(es)", output.getvalue())
        self.assertIn("skill:research@1.0.0", output.getvalue())

    def test_text_error_renders_diagnostic_without_result_payload(self):
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                (
                    "--start",
                    str(_bootstrap.REPO_ROOT),
                    "plan",
                    "--workflow",
                    "workflow:research-topic-to-brief",
                    "--inputs",
                    "[]",
                )
            )
        self.assertEqual(exit_code, 2)
        self.assertIn("ASF-CLI-001", output.getvalue())
        self.assertIn("Suggestion:", output.getvalue())

    def test_composite_cli_surfaces_are_read_only_and_structured(self):
        exit_code, compiled = self.run_cli(
            "compile",
            "content-workflow",
            "--execution-id",
            "cli-composite",
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            [step["id"] for step in compiled["compiled"]["plan"]["steps"]],
            ["research-topic", "create-content", "review-content"],
        )

        exit_code, snapshots = self.run_cli("snapshot")
        self.assertEqual(exit_code, 0)
        self.assertEqual(len(snapshots["snapshots"]), 5)

        exit_code, inspected = self.run_cli("inspect")
        self.assertEqual(exit_code, 0)
        self.assertEqual(len(inspected["artifact"]["steps"]), 3)

        exit_code, explained = self.run_cli("explain")
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            explained["chain"],
            ["research-topic", "create-content", "review-content"],
        )
        self.assertEqual(len(explained["artifact_transfers"]), 2)

    def test_compile_rejects_alias_and_explicit_workflow_together(self):
        exit_code, report = self.run_cli(
            "compile",
            "content-workflow",
            "--workflow",
            "workflow:research-content-review",
        )
        self.assertEqual(exit_code, 2)
        self.assertEqual(report["diagnostics"][0]["code"], "ASF-CLI-001")

    def test_run_content_workflow_defaults_to_compile_only_dry_run(self):
        with tempfile.TemporaryDirectory() as directory:
            exit_code, report = self.run_cli(
                "run",
                "content-workflow",
                "--topic",
                "Local AI execution",
                "--mode",
                "dry-run",
                "--reports-dir",
                directory,
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["execution"]["status"], "compiled")
            self.assertTrue(
                report["execution"]["report_directory"].startswith(directory)
            )
            self.assertTrue(
                all(
                    step["status"] == "compiled"
                    for step in report["execution"]["steps"]
                )
            )

    def test_vietnamese_topic_survives_windows_mojibake_and_utf8_reports(self):
        expected = "5 công nghệ AI đáng sợ nhất trong 2 năm tới"
        mojibake = "5 cÃ´ng nghá»‡ AI Ä‘Ã¡ng sá»£ nháº¥t trong 2 nÄƒm tá»›i"
        self.assertEqual(_normalize_cli_unicode(expected), expected)
        self.assertEqual(_normalize_cli_unicode(mojibake), expected)

        with tempfile.TemporaryDirectory() as directory:
            exit_code, report = self.run_cli(
                "run",
                "content-workflow",
                "--topic",
                mojibake,
                "--mode",
                "dry-run",
                "--reports-dir",
                directory,
            )
            self.assertEqual(exit_code, 0)
            first_input = report["execution"]["steps"][0]["input_artifact"]
            self.assertEqual(first_input["topic"], expected)

            report_directory = Path(
                report["execution"]["report_directory"]
            )
            json_path = report_directory / "execution-report.json"
            json_bytes = json_path.read_bytes()
            self.assertIn(expected.encode("utf-8"), json_bytes)
            self.assertNotIn(mojibake.encode("utf-8"), json_bytes)
            persisted = json.loads(json_bytes.decode("utf-8"))
            self.assertEqual(
                persisted["steps"][0]["input_artifact"]["topic"], expected
            )

            human = (report_directory / "report.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn(f"Topic: {expected}", human)

    def test_run_cli_requires_explicit_model_for_live_local(self):
        exit_code, report = self.run_cli(
            "run",
            "content-workflow",
            "--topic",
            "Local AI execution",
            "--mode",
            "live-local",
        )
        self.assertEqual(exit_code, 2)
        self.assertIn(
            "requires --model", report["diagnostics"][0]["message"]
        )

    def test_run_cli_rejects_model_in_dry_run_and_unknown_target(self):
        exit_code, _report = self.run_cli(
            "run",
            "content-workflow",
            "--topic",
            "Local AI execution",
            "--model",
            "llama3",
        )
        self.assertEqual(exit_code, 2)

        exit_code, report = self.run_cli(
            "run",
            "arbitrary-workflow",
            "--topic",
            "Local AI execution",
        )
        self.assertEqual(exit_code, 2)
        self.assertIn("only", report["diagnostics"][0]["message"])
