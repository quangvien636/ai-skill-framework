import unittest

import _bootstrap
from asf_validator.diagnostics import Severity
from asf_validator.connector_ir import build_connector_ir


class BuildConnectorIrTests(unittest.TestCase):
    def test_build_connector_ir_valid(self):
        doc = {
            "schema_version": "1.0.0",
            "id": "connector:google-search",
            "name": "google-search",
            "display_name": "Google Search",
            "description": "Connects to Google Search API",
            "version": "1.0.0",
            "status": "draft",
            "owners": ["me"],
            "responsibility": "Provide search results",
            "authentication": "api_key",
            "configuration": {
                "api_endpoint": {
                    "type": "string",
                    "required": True,
                    "description": "The API endpoint URL"
                }
            }
        }

        connector, diagnostics = build_connector_ir(doc, "connectors/google-search/connector.yaml")
        self.assertIsNotNone(connector)
        self.assertEqual(len(diagnostics), 0)
        self.assertEqual(connector.metadata.id, "connector:google-search")
        self.assertEqual(connector.responsibility, "Provide search results")
        self.assertEqual(connector.authentication, "api_key")
        self.assertEqual(len(connector.configuration), 1)
        self.assertIn("api_endpoint", connector.configuration)

    def test_build_connector_ir_invalid_metadata(self):
        doc = {
            "schema_version": "1.0.0",
            "id": "tool:google-search",  # Invalid prefix for connector
            "name": "google-search",
            "display_name": "Google Search",
            "description": "Connects to Google Search API",
            "version": "1.0.0",
            "status": "draft",
            "owners": ["me"],
            "responsibility": "Provide search results",
            "authentication": "api_key",
            "configuration": {}
        }

        connector, diagnostics = build_connector_ir(doc, "connectors/google-search/connector.yaml")
        self.assertIsNone(connector)
        self.assertGreater(len(diagnostics), 0)
        self.assertEqual(diagnostics[0].severity, Severity.ERROR)


if __name__ == "__main__":
    unittest.main()
