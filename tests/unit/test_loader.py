import tempfile
import unittest
from pathlib import Path

import _bootstrap

from asf_validator.loader import load_json, load_yaml


class LoaderLineColumnTests(unittest.TestCase):
    """Sprint 16's Deferred/Documented Gap, narrowed scope: real line/column
    source-position tracking for the one layer that can report it exactly
    -- YAML/JSON parse errors, which PyYAML/json already carry a precise
    mark for. Schema/semantic-level diagnostics (a missing required field,
    a wrong enum value, etc.) still report a field/section path rather than
    a source line -- see PROJECT_TRACKER.md's Next Actions for why that
    remains open (it needs a position-preserving YAML loader plus mapping
    a jsonschema error path back to a line, a materially larger change)."""

    def test_malformed_yaml_reports_real_line_and_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.yaml"
            path.write_text("a: [1, 2\nb: 3\n", encoding="utf-8")
            result = load_yaml(path)

            self.assertFalse(result.ok)
            self.assertEqual(len(result.diagnostics), 1)
            diagnostic = result.diagnostics[0]
            self.assertEqual(diagnostic.code, "ASF-PARSE-001")
            self.assertRegex(diagnostic.location, r"^line \d+, column \d+$")

    def test_malformed_json_reports_real_line_and_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text('{\n  "a": [1, 2\n  "b": 3\n}\n', encoding="utf-8")
            result = load_json(path)

            self.assertFalse(result.ok)
            self.assertEqual(len(result.diagnostics), 1)
            diagnostic = result.diagnostics[0]
            self.assertEqual(diagnostic.code, "ASF-PARSE-001")
            self.assertRegex(diagnostic.location, r"^line \d+, column \d+$")

    def test_valid_yaml_and_json_are_unaffected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            yaml_path = root / "ok.yaml"
            yaml_path.write_text("a: 1\nb: 2\n", encoding="utf-8")
            json_path = root / "ok.json"
            json_path.write_text('{"a": 1, "b": 2}\n', encoding="utf-8")

            yaml_result = load_yaml(yaml_path)
            json_result = load_json(json_path)

            self.assertTrue(yaml_result.ok)
            self.assertEqual(yaml_result.document, {"a": 1, "b": 2})
            self.assertTrue(json_result.ok)
            self.assertEqual(json_result.document, {"a": 1, "b": 2})


if __name__ == "__main__":
    unittest.main()
