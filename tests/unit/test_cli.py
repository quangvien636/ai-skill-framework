import io
import json
import unittest
from contextlib import redirect_stdout

import _bootstrap

from asf_cli import main


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

    def test_invalid_inputs_are_structured_cli_diagnostic(self):
        exit_code, report = self.run_cli(
            "plan",
            "--workflow",
            "workflow:research-topic-to-brief",
            "--inputs",
            "[]",
        )
        self.assertEqual(exit_code, 1)
        self.assertEqual(report["diagnostics"][0]["code"], "ASF-CLI-001")

