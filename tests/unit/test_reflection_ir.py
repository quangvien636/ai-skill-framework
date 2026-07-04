import unittest

import _bootstrap  # noqa: F401

from asf_validator.reflection_ir import build_reflection_ir

DOC = {
    "enabled": True,
    "max_attempts": 2,
    "minimum_improvement": 5,
    "on_exhausted": "manual-review",
    "reflectable_hard_gates": ["output-schema-valid"],
}


class BuildReflectionIrTests(unittest.TestCase):
    def test_builds_reflection_ir(self):
        reflection = build_reflection_ir(DOC)
        self.assertTrue(reflection.enabled)
        self.assertEqual(reflection.max_attempts, 2)
        self.assertEqual(reflection.reflectable_hard_gates, ("output-schema-valid",))

    def test_reflectable_hard_gates_default_to_empty_tuple(self):
        doc = {k: v for k, v in DOC.items() if k != "reflectable_hard_gates"}
        reflection = build_reflection_ir(doc)
        self.assertEqual(reflection.reflectable_hard_gates, ())


if __name__ == "__main__":
    unittest.main()
