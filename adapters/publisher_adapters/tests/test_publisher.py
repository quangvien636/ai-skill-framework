import tempfile
import unittest
from pathlib import Path

import _bootstrap

from publisher_adapters import (
    PublishError,
    PublisherAdapter,
    UnsupportedPublishTargetError,
    markdown_export,
    wordpress_export,
)


class PublisherAdapterTests(unittest.TestCase):
    def test_markdown_publish_creates_real_utf8_file(self):
        with tempfile.TemporaryDirectory() as directory:
            descriptor = markdown_export(
                "Tiếng Việt & Local AI",
                "Nội dung cục bộ.",
                front_matter={"status": "draft", "tags": ["local", "ai"]},
            )
            result = PublisherAdapter(Path(directory)).publish(descriptor)
            path = Path(result.path)

            self.assertTrue(path.is_file())
            self.assertEqual(path.name, "tiếng-việt-local-ai.md")
            content = path.read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "---\nstatus: draft\ntags:\n- local\n- ai\n---\n\n"
                "# Tiếng Việt & Local AI\n\nNội dung cục bộ.\n",
            )
            self.assertEqual(result.bytes_written, len(content.encode("utf-8")))

    def test_existing_file_fails_closed_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter = PublisherAdapter(Path(directory))
            descriptor = markdown_export("Same Title", "first")
            adapter.publish(descriptor)
            with self.assertRaisesRegex(PublishError, "already exists"):
                adapter.publish(markdown_export("Same Title", "second"))
            self.assertIn(
                "first",
                (Path(directory) / "same-title.md").read_text(encoding="utf-8"),
            )

    def test_explicit_overwrite_replaces_local_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            PublisherAdapter(root).publish(markdown_export("Title", "first"))
            PublisherAdapter(root, overwrite=True).publish(
                markdown_export("Title", "second")
            )
            self.assertIn("second", (root / "title.md").read_text(encoding="utf-8"))

    def test_platform_target_fails_before_creating_output_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "not-created"
            with self.assertRaises(UnsupportedPublishTargetError):
                PublisherAdapter(root).publish(wordpress_export("Title", "Body"))
            self.assertFalse(root.exists())

    def test_path_like_title_is_slugged_inside_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = PublisherAdapter(root).publish(
                markdown_export("../../Outside", "safe")
            )
            self.assertEqual(Path(result.path).parent, root.resolve())
            self.assertEqual(Path(result.path).name, "outside.md")

    def test_punctuation_only_title_is_rejected_before_root_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "not-created"
            with self.assertRaisesRegex(PublishError, "usable filename"):
                PublisherAdapter(root).publish(markdown_export("!!!", "Body"))
            self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()

