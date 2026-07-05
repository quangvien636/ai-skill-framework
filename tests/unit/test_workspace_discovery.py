import tempfile
import unittest
from pathlib import Path

import _bootstrap

from asf_validator.workspace_discovery import (
    WorkspaceNotFoundError,
    discover_workspace_root,
)


class WorkspaceDiscoveryTests(unittest.TestCase):
    def test_discovers_nearest_root_from_nested_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "PROJECT_CONTEXT.md").touch()
            (root / "PROJECT_TRACKER.md").touch()
            nested = root / "a" / "b"
            nested.mkdir(parents=True)
            self.assertEqual(discover_workspace_root(nested), root.resolve())

    def test_requires_both_markers_and_does_not_use_git(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "PROJECT_CONTEXT.md").touch()
            (root / ".git").mkdir()
            with self.assertRaises(WorkspaceNotFoundError):
                discover_workspace_root(root)

    def test_search_is_bounded_and_error_names_start(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "PROJECT_CONTEXT.md").touch()
            (root / "PROJECT_TRACKER.md").touch()
            nested = root / "one" / "two"
            nested.mkdir(parents=True)
            with self.assertRaises(WorkspaceNotFoundError) as caught:
                discover_workspace_root(nested, max_parents=1)
            self.assertIn(str(nested.resolve()), str(caught.exception))

    def test_file_start_uses_parent_directory(self):
        self.assertEqual(
            discover_workspace_root(_bootstrap.REPO_ROOT / "README.md"),
            _bootstrap.REPO_ROOT.resolve(),
        )

    def test_negative_parent_bound_is_rejected(self):
        with self.assertRaises(ValueError):
            discover_workspace_root(_bootstrap.REPO_ROOT, max_parents=-1)


if __name__ == "__main__":
    unittest.main()
