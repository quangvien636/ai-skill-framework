import json
import unittest

import _bootstrap

from asf_validator.pipeline import build_ir
from asf_validator.schema_registry import build_schema_registry


class PipelineFixtureConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
        manifest = json.loads((_bootstrap.FIXTURES_ROOT / "cases.json").read_text(encoding="utf-8"))
        cls.cases = manifest["cases"]

    def test_every_declared_case_matches_its_expectation(self):
        failures = []
        for case in self.cases:
            fixture = _bootstrap.REPO_ROOT / case["fixture"]
            result = build_ir(case["kind"], fixture, self.schema_registry)
            actual = "valid" if result.ok else "invalid"
            if actual != case["expected"]:
                failures.append(f"{case['name']}: expected {case['expected']}, got {actual}")
                continue
            expected_code = case.get("expected_code")
            if expected_code and not any(d.code == expected_code for d in result.diagnostics):
                failures.append(
                    f"{case['name']}: expected diagnostic {expected_code}, "
                    f"got {sorted({d.code for d in result.diagnostics})}"
                )
        self.assertEqual(failures, [])

    def test_unsupported_kind_raises_value_error(self):
        with self.assertRaises(ValueError):
            build_ir("unsupported-kind", _bootstrap.FIXTURES_ROOT / "skill" / "valid.yaml", self.schema_registry)

    def test_valid_skill_ir_is_reusable_across_calls_no_global_state(self):
        fixture = _bootstrap.FIXTURES_ROOT / "skill" / "valid.yaml"
        first = build_ir("skill", fixture, self.schema_registry)
        second = build_ir("skill", fixture, self.schema_registry)
        self.assertTrue(first.ok)
        self.assertTrue(second.ok)
        self.assertIsNot(first.ir, second.ir)  # independent objects, no shared mutable state


if __name__ == "__main__":
    unittest.main()
