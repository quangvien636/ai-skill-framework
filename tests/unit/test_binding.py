import unittest
from dataclasses import replace
from types import MappingProxyType

import _bootstrap

from asf_runtime.binding import (
    build_runtime_binding,
    resolve_skill_runtime_binding,
    to_binding_ir,
    validate_binding_batch,
)
from asf_runtime.catalog import ArtifactCatalog, CatalogArtifact, build_artifact_catalog
from asf_validator.pipeline import build_ir
from asf_validator.runtime_ir import ModelBindingIR, PublisherBindingIR
from asf_validator.schema_registry import build_schema_registry

RUNTIME_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph" / "valid-runtime"


def _runtime_catalog():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    results = [
        build_ir("skill", RUNTIME_FIXTURES / "skill.yaml", registry),
        build_ir("runtime", RUNTIME_FIXTURES / "runtime.yaml", registry),
        build_ir("runtime", RUNTIME_FIXTURES / "runtime-fallback.yaml", registry),
        build_ir("tool", RUNTIME_FIXTURES / "tool.yaml", registry),
        build_ir("knowledge", RUNTIME_FIXTURES / "knowledge.md", registry),
    ]
    assert all(result.ok for result in results), [
        (result.artifact, result.diagnostics) for result in results if not result.ok
    ]
    return build_artifact_catalog(results)


def _replace_catalog_artifact(catalog, artifact_id, new_ir):
    old = next(a for a in catalog.artifacts if a.id == artifact_id)
    replacement = CatalogArtifact(
        kind=old.kind, id=old.id, version=old.version, status=old.status, path=old.path, ir=new_ir
    )
    artifacts = tuple(replacement if a is old else a for a in catalog.artifacts)
    grouped: dict[str, list] = {}
    for artifact in artifacts:
        grouped.setdefault(artifact.id, []).append(artifact)
    return ArtifactCatalog(artifacts, MappingProxyType({k: tuple(v) for k, v in grouped.items()}))


class RuntimeBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = _runtime_catalog()
        cls.skill = cls.catalog.exact("skill:use-runtime", "1.0.0").ir
        cls.primary = cls.catalog.exact("runtime:primary", "1.0.0").ir

    def test_build_runtime_binding_resolves_full_chain(self):
        binding, diagnostics = build_runtime_binding(
            self.skill.metadata.id, self.skill.metadata.version.raw, self.primary, self.catalog
        )
        self.assertEqual(diagnostics, [])
        self.assertEqual(binding.chain, ("runtime:primary", "runtime:fallback-target"))
        self.assertEqual(binding.model.provider, "anthropic")
        self.assertEqual(binding.model_source_runtime_id, "runtime:primary")
        self.assertEqual(
            [doc.id for doc in binding.retriever_knowledge],
            ["kb:technical:writing:summarization:brevity"],
        )
        self.assertEqual([tool.metadata.id for tool in binding.resolved_tools], ["tool:read-file"])
        self.assertIsNone(binding.publisher)
        self.assertEqual(binding.timeout_seconds, 30)

    def test_resolve_skill_runtime_binding_end_to_end(self):
        binding, diagnostics = resolve_skill_runtime_binding(self.skill, self.catalog)
        self.assertEqual(diagnostics, [])
        self.assertIsNotNone(binding)
        self.assertEqual(binding.runtime_id, "runtime:primary")

    def test_skill_without_runtime_dependency_returns_none(self):
        no_runtime_skill = replace(
            self.skill, dependencies=replace(self.skill.dependencies, runtime=())
        )
        binding, diagnostics = resolve_skill_runtime_binding(no_runtime_skill, self.catalog)
        self.assertIsNone(binding)
        self.assertEqual(diagnostics, [])

    def test_missing_runtime_binding_is_reported(self):
        catalog = ArtifactCatalog(
            tuple(a for a in self.catalog.artifacts if a.id != "runtime:primary"),
            MappingProxyType(
                {
                    a.id: tuple(x for x in self.catalog.artifacts if x.id == a.id and x.id != "runtime:primary")
                    for a in self.catalog.artifacts
                    if a.id != "runtime:primary"
                }
            ),
        )
        binding, diagnostics = resolve_skill_runtime_binding(self.skill, catalog)
        self.assertIsNone(binding)
        self.assertEqual({d.code for d in diagnostics}, {"ASF-BINDING-001"})

    def test_invalid_inheritance_flags_non_active_source(self):
        disabled_model = ModelBindingIR(
            enabled=False, provider=None, model=None, parameters={}, endpoint=None
        )
        primary_without_model = replace(self.primary, model=disabled_model)
        deprecated_fallback = replace(
            self.catalog.exact("runtime:fallback-target", "1.0.0").ir,
            metadata=replace(
                self.catalog.exact("runtime:fallback-target", "1.0.0").ir.metadata,
                status="deprecated",
            ),
        )
        catalog = _replace_catalog_artifact(self.catalog, "runtime:primary", primary_without_model)
        catalog = _replace_catalog_artifact(catalog, "runtime:fallback-target", deprecated_fallback)

        binding, diagnostics = build_runtime_binding(
            self.skill.metadata.id, self.skill.metadata.version.raw, primary_without_model, catalog
        )
        self.assertEqual(binding.model.provider, "ollama")
        self.assertIn("ASF-BINDING-004", {d.code for d in diagnostics})

    def test_incompatible_descriptors_flagged_when_retriever_enabled_without_model(self):
        disabled_model = ModelBindingIR(
            enabled=False, provider=None, model=None, parameters={}, endpoint=None
        )
        no_model_no_fallback = replace(
            self.primary,
            model=disabled_model,
            fallback_profile=replace(self.primary.fallback_profile, enabled=False, fallback_runtime=None),
        )
        catalog = _replace_catalog_artifact(self.catalog, "runtime:primary", no_model_no_fallback)
        binding, diagnostics = build_runtime_binding(
            self.skill.metadata.id, self.skill.metadata.version.raw, no_model_no_fallback, catalog
        )
        self.assertIsNone(binding.model)
        self.assertIsNotNone(binding.retriever)
        self.assertIn("ASF-BINDING-006", {d.code for d in diagnostics})

    def test_differing_models_across_the_chain_is_not_flagged(self):
        # The whole point of a fallback chain is that it may use a
        # different (often local/cheaper) model than the primary -- this
        # must never be flagged as a conflict.
        binding, diagnostics = build_runtime_binding(
            self.skill.metadata.id, self.skill.metadata.version.raw, self.primary, self.catalog
        )
        self.assertNotIn("ASF-BINDING-007", {d.code for d in diagnostics})
        self.assertEqual(binding.model.provider, "anthropic")

    def test_conflicting_override_detected_for_differing_publisher_targets(self):
        primary_with_publisher = replace(
            self.primary,
            publisher=PublisherBindingIR(enabled=True, target="wordpress", metadata={}),
        )
        conflicting_fallback = replace(
            self.catalog.exact("runtime:fallback-target", "1.0.0").ir,
            publisher=PublisherBindingIR(enabled=True, target="youtube", metadata={}),
        )
        catalog = _replace_catalog_artifact(self.catalog, "runtime:primary", primary_with_publisher)
        catalog = _replace_catalog_artifact(catalog, "runtime:fallback-target", conflicting_fallback)

        binding, diagnostics = build_runtime_binding(
            self.skill.metadata.id,
            self.skill.metadata.version.raw,
            primary_with_publisher,
            catalog,
        )
        self.assertIn("ASF-BINDING-007", {d.code for d in diagnostics})
        # Override precedence still applies: primary's own publisher wins.
        self.assertEqual(binding.publisher.target, "wordpress")

    def test_binding_ir_round_trips_and_is_serializable(self):
        binding, diagnostics = build_runtime_binding(
            self.skill.metadata.id, self.skill.metadata.version.raw, self.primary, self.catalog
        )
        binding_ir = to_binding_ir(binding, diagnostics)
        self.assertEqual(binding_ir.id, "binding:skill:use-runtime@runtime:primary")
        payload = binding_ir.as_dict()
        self.assertEqual(payload["model"]["provider"], "anthropic")
        self.assertEqual(payload["retriever"]["knowledge_ids"], ["kb:technical:writing:summarization:brevity"])
        self.assertEqual(payload["tools"]["tool_ids"], ["tool:read-file"])

    def test_validate_binding_batch_detects_inconsistent_duplicate(self):
        binding, diagnostics = build_runtime_binding(
            self.skill.metadata.id, self.skill.metadata.version.raw, self.primary, self.catalog
        )
        first = to_binding_ir(binding, diagnostics)
        second = replace(first, timeout_seconds=first.timeout_seconds + 1)
        batch_diagnostics = validate_binding_batch([first, second])
        self.assertEqual({d.code for d in batch_diagnostics}, {"ASF-BINDING-005"})

    def test_validate_binding_batch_allows_identical_duplicates(self):
        binding, diagnostics = build_runtime_binding(
            self.skill.metadata.id, self.skill.metadata.version.raw, self.primary, self.catalog
        )
        first = to_binding_ir(binding, diagnostics)
        second = to_binding_ir(binding, diagnostics)
        self.assertEqual(validate_binding_batch([first, second]), [])


if __name__ == "__main__":
    unittest.main()
