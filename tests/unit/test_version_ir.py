import unittest

import _bootstrap  # noqa: F401

from asf_validator.version_ir import parse_version, parse_version_range


class ParseVersionTests(unittest.TestCase):
    def test_valid_semver(self):
        version, error = parse_version("1.2.3")
        self.assertIsNone(error)
        self.assertEqual((version.major, version.minor, version.patch), (1, 2, 3))
        self.assertIsNone(version.prerelease)
        self.assertIsNone(version.build)

    def test_prerelease_and_build(self):
        version, error = parse_version("1.0.0-alpha.1+build.5")
        self.assertIsNone(error)
        self.assertEqual(version.prerelease, "alpha.1")
        self.assertEqual(version.build, "build.5")

    def test_rejects_incomplete_version(self):
        version, error = parse_version("1.2")
        self.assertIsNone(version)
        self.assertIsNotNone(error)

    def test_rejects_floating_label(self):
        version, error = parse_version("latest")
        self.assertIsNone(version)
        self.assertIsNotNone(error)


class ParseVersionRangeTests(unittest.TestCase):
    def test_exact_pin(self):
        version_range, error = parse_version_range("1.4.2")
        self.assertIsNone(error)
        self.assertEqual(len(version_range.comparators), 1)
        self.assertEqual(version_range.comparators[0].operator, "=")

    def test_comparator_range(self):
        version_range, error = parse_version_range(">=1.2.0 <2.0.0")
        self.assertIsNone(error)
        operators = [c.operator for c in version_range.comparators]
        self.assertEqual(operators, [">=", "<"])
        self.assertEqual(version_range.comparators[0].version.major, 1)
        self.assertEqual(version_range.comparators[1].version.major, 2)

    def test_rejects_floating_label(self):
        version_range, error = parse_version_range("latest")
        self.assertIsNone(version_range)
        self.assertIsNotNone(error)


if __name__ == "__main__":
    unittest.main()
