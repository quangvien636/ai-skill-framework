import unittest

import _bootstrap  # noqa: F401

from asf_validator.diagnostics import (
    PARSE_METADATA_ID_NAME_MISMATCH,
    PARSE_UNSUPPORTED_SCHEMA_VERSION,
)
from asf_validator.metadata_ir import extract_metadata_ir

BASE_DOC = {
    "schema_version": "1.0.0",
    "id": "skill:summarize-document",
    "name": "summarize-document",
    "display_name": "Summarize Document",
    "description": "Produces a bounded summary.",
    "version": "1.0.0",
    "status": "draft",
    "owners": ["framework-maintainers"],
    "tags": ["summarization"],
}


class ExtractMetadataIrTests(unittest.TestCase):
    def test_valid_metadata(self):
        metadata, diagnostics = extract_metadata_ir(BASE_DOC, "test", id_prefix="skill")
        self.assertEqual(diagnostics, [])
        self.assertEqual(metadata.id, "skill:summarize-document")
        self.assertEqual(metadata.name, "summarize-document")
        self.assertEqual(metadata.schema_version.major, 1)
        self.assertEqual(metadata.owners, ("framework-maintainers",))
        self.assertEqual(metadata.tags, ("summarization",))

    def test_defaults_missing_tags_to_empty_tuple(self):
        doc = {k: v for k, v in BASE_DOC.items() if k != "tags"}
        metadata, diagnostics = extract_metadata_ir(doc, "test", id_prefix="skill")
        self.assertEqual(diagnostics, [])
        self.assertEqual(metadata.tags, ())

    def test_unsupported_schema_version_major(self):
        doc = {**BASE_DOC, "schema_version": "2.0.0"}
        metadata, diagnostics = extract_metadata_ir(doc, "test", id_prefix="skill")
        self.assertIsNone(metadata)
        self.assertTrue(any(d.code == PARSE_UNSUPPORTED_SCHEMA_VERSION for d in diagnostics))

    def test_id_name_mismatch(self):
        doc = {**BASE_DOC, "name": "different-name"}
        metadata, diagnostics = extract_metadata_ir(doc, "test", id_prefix="skill")
        self.assertIsNone(metadata)
        self.assertTrue(any(d.code == PARSE_METADATA_ID_NAME_MISMATCH for d in diagnostics))

    def test_id_prefix_mismatch_is_also_a_mismatch(self):
        doc = {**BASE_DOC, "id": "workflow:summarize-document"}
        metadata, diagnostics = extract_metadata_ir(doc, "test", id_prefix="skill")
        self.assertIsNone(metadata)
        self.assertTrue(any(d.code == PARSE_METADATA_ID_NAME_MISMATCH for d in diagnostics))


if __name__ == "__main__":
    unittest.main()
