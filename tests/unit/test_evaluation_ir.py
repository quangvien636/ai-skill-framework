import unittest

import _bootstrap  # noqa: F401

from asf_validator.evaluation_ir import build_evaluation_ir

DOC = {
    "metrics": [
        {
            "name": "accuracy",
            "description": "Claims match input.",
            "weight": 1.0,
            "rubric": {"0": "False.", "50": "Partial.", "100": "Supported."},
        }
    ],
    "scoring": {"scale": "0..100", "aggregate": "weighted-mean"},
    "acceptance": {"minimum_score": 80, "hard_gates": ["output-schema-valid"]},
    "on_failure": "fail",
}


class BuildEvaluationIrTests(unittest.TestCase):
    def test_builds_metrics_scoring_and_acceptance(self):
        evaluation = build_evaluation_ir(DOC)
        self.assertEqual(len(evaluation.metrics), 1)
        self.assertEqual(evaluation.metrics[0].name, "accuracy")
        self.assertEqual(evaluation.scoring.aggregate, "weighted-mean")
        self.assertEqual(evaluation.acceptance.minimum_score, 80)
        self.assertEqual(evaluation.acceptance.hard_gates, ("output-schema-valid",))
        self.assertEqual(evaluation.on_failure, "fail")

    def test_hard_gates_default_to_empty_tuple(self):
        doc = {**DOC, "acceptance": {"minimum_score": 80}}
        evaluation = build_evaluation_ir(doc)
        self.assertEqual(evaluation.acceptance.hard_gates, ())


if __name__ == "__main__":
    unittest.main()
