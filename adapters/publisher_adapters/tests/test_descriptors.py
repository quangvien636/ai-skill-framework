import unittest

import _bootstrap  # noqa: F401  (adds adapters/ to sys.path)

from publisher_adapters.descriptors import (
    DescriptorError,
    compile_export_descriptor,
    facebook_export,
    markdown_export,
    tiktok_export,
    wordpress_export,
    youtube_export,
)


class ExportDescriptorTests(unittest.TestCase):
    def test_youtube_export_is_declarative_only(self):
        descriptor = youtube_export(
            "Title", "Description", tags=("ai", "skills"), category="Education"
        )
        self.assertEqual(descriptor.target, "youtube")
        self.assertEqual(descriptor.metadata["tags"], ("ai", "skills"))
        self.assertEqual(descriptor.metadata["privacy_status"], "private")

    def test_tiktok_export(self):
        descriptor = tiktok_export("Title", "Caption", hashtags=("fyp",))
        self.assertEqual(descriptor.target, "tiktok")
        self.assertEqual(descriptor.metadata["hashtags"], ("fyp",))

    def test_facebook_export(self):
        descriptor = facebook_export("Title", "Message", link="https://example.com")
        self.assertEqual(descriptor.target, "facebook")
        self.assertEqual(descriptor.metadata["link"], "https://example.com")

    def test_wordpress_export_defaults_to_draft_status(self):
        descriptor = wordpress_export("Title", "Content")
        self.assertEqual(descriptor.metadata["status"], "draft")

    def test_markdown_export_never_writes_a_file(self):
        descriptor = markdown_export("Title", "# Body", front_matter={"date": "2026-07-05"})
        self.assertEqual(descriptor.target, "markdown")
        self.assertEqual(descriptor.metadata["front_matter"]["date"], "2026-07-05")

    def test_unsupported_target_is_rejected(self):
        with self.assertRaises(DescriptorError):
            compile_export_descriptor("instagram", "Title", "Body")

    def test_empty_title_is_rejected(self):
        with self.assertRaises(DescriptorError):
            compile_export_descriptor("markdown", "", "Body")

    def test_credential_like_metadata_key_is_rejected(self):
        for key in ("api_key", "Access-Token", "cookie", "session_id"):
            with self.assertRaises(DescriptorError):
                compile_export_descriptor("wordpress", "Title", "Body", {key: "value"})

    def test_credential_like_key_nested_in_front_matter_is_rejected(self):
        with self.assertRaises(DescriptorError):
            markdown_export("Title", "Body", front_matter={"api_key": "sk-not-real"})

    def test_descriptor_metadata_is_immutable(self):
        descriptor = youtube_export("Title", "Description")
        with self.assertRaises(TypeError):
            descriptor.metadata["privacy_status"] = "public"


if __name__ == "__main__":
    unittest.main()
