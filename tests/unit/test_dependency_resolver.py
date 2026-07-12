import unittest
from dataclasses import replace

import _bootstrap

from asf_runtime.catalog import build_artifact_catalog
from asf_runtime.dependency_resolver import (
    inherit_model,
    inherit_publisher,
    inherit_retriever,
    inherit_tools,
    resolve_fallback_chain,
    resolve_retriever_knowledge,
    resolve_tools,
)
from asf_validator.pipeline import build_ir
from asf_validator.reference_ir import ReferenceIR
from asf_validator.runtime_ir import ModelBindingIR, RetrieverBindingIR, ToolsBindingIR
from asf_validator.schema_registry import build_schema_registry

RUNTIME_FIXTURES = _bootstrap.REPO_ROOT / "tests" / "fixtures" / "graph" / "valid-runtime"


def _runtime_catalog():
    registry = build_schema_registry(_bootstrap.SCHEMA_ROOT)
    results = [
        build_ir("runtime", RUNTIME_FIXTURES / "runtime.yaml", registry),
        build_ir("runtime", RUNTIME_FIXTURES / "runtime-fallback.yaml", registry),
        build_ir("tool", RUNTIME_FIXTURES / "tool.yaml", registry),
        build_ir("knowledge", RUNTIME_FIXTURES / "knowledge.md", registry),
    ]
    assert all(result.ok for result in results), [
        (result.artifact, result.diagnostics) for result in results if not result.ok
    ]
    return build_artifact_catalog(results)


class DependencyResolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = _runtime_catalog()
        cls.primary = cls.catalog.exact("runtime:primary", "1.0.0").ir
        cls.fallback_target = cls.catalog.exact("runtime:fallback-target", "1.0.0").ir

    def test_resolve_fallback_chain_includes_primary_first(self):
        chain, diagnostics = resolve_fallback_chain(self.primary, self.catalog)
        self.assertEqual(diagnostics, [])
        self.assertEqual(
            [runtime.metadata.id for runtime in chain],
            ["runtime:primary", "runtime:fallback-target"],
        )

    def test_fallback_chain_stops_at_terminal_runtime(self):
        chain, diagnostics = resolve_fallback_chain(self.fallback_target, self.catalog)
        self.assertEqual(diagnostics, [])
        self.assertEqual([runtime.metadata.id for runtime in chain], ["runtime:fallback-target"])

    def test_override_wins_when_primary_enables_capability_itself(self):
        chain, _ = resolve_fallback_chain(self.primary, self.catalog)
        model, source = inherit_model(chain)
        self.assertEqual(source, "runtime:primary")
        self.assertEqual(model.provider, "anthropic")

        retriever, retriever_source = inherit_retriever(chain)
        self.assertEqual(retriever_source, "runtime:primary")

        tools, tools_source = inherit_tools(chain)
        self.assertEqual(tools_source, "runtime:primary")

    def test_inheritance_falls_through_to_fallback_when_primary_disables(self):
        disabled_model = ModelBindingIR(
            enabled=False, provider=None, model=None, parameters={}, endpoint=None
        )
        primary_without_model = replace(self.primary, model=disabled_model)
        chain = (primary_without_model, self.fallback_target)

        model, source = inherit_model(chain)
        self.assertEqual(source, "runtime:fallback-target")
        self.assertEqual(model.provider, "ollama")
        self.assertEqual(model.model, "llama3")

    def test_inherit_publisher_returns_none_when_nobody_in_chain_enables_it(self):
        chain, _ = resolve_fallback_chain(self.primary, self.catalog)
        publisher, source = inherit_publisher(chain)
        self.assertIsNone(publisher)
        self.assertIsNone(source)

    def test_resolve_retriever_knowledge_and_tools(self):
        chain, _ = resolve_fallback_chain(self.primary, self.catalog)
        retriever, _ = inherit_retriever(chain)
        knowledge, knowledge_diagnostics = resolve_retriever_knowledge(retriever, self.catalog)
        self.assertEqual(knowledge_diagnostics, [])
        self.assertEqual(
            [doc.id for doc in knowledge],
            ["kb:technical:writing:summarization:brevity"],
        )

        tools_binding, _ = inherit_tools(chain)
        tools, tools_diagnostics = resolve_tools(tools_binding, self.catalog)
        self.assertEqual(tools_diagnostics, [])
        self.assertEqual([tool.metadata.id for tool in tools], ["tool:read-file"])

    def test_cyclic_fallback_is_detected(self):
        cyclic_primary = replace(
            self.primary,
            fallback_profile=replace(
                self.primary.fallback_profile,
                max_fallback_depth=3,
            ),
        )
        cyclic_fallback = replace(
            self.fallback_target,
            fallback_profile=replace(
                self.fallback_target.fallback_profile,
                enabled=True,
                fallback_runtime=self.primary.fallback_profile.fallback_runtime.__class__(
                    id="runtime:primary", version=self.primary.fallback_profile.fallback_runtime.version, required=True
                ),
            ),
        )
        # Directly exercise the walk with in-memory IR rather than a catalog
        # round-trip, since the cycle only needs to exist in the resolved
        # object graph the resolver walks.
        from asf_runtime.catalog import ArtifactCatalog, CatalogArtifact
        from types import MappingProxyType

        artifacts = (
            CatalogArtifact(
                kind="runtime",
                id=cyclic_primary.metadata.id,
                version=cyclic_primary.metadata.version,
                status=cyclic_primary.metadata.status,
                path="<test>",
                ir=cyclic_primary,
            ),
            CatalogArtifact(
                kind="runtime",
                id=cyclic_fallback.metadata.id,
                version=cyclic_fallback.metadata.version,
                status=cyclic_fallback.metadata.status,
                path="<test>",
                ir=cyclic_fallback,
            ),
        )
        cyclic_catalog = ArtifactCatalog(
            artifacts,
            MappingProxyType(
                {
                    cyclic_primary.metadata.id: (artifacts[0],),
                    cyclic_fallback.metadata.id: (artifacts[1],),
                }
            ),
        )
        chain, diagnostics = resolve_fallback_chain(cyclic_primary, cyclic_catalog)
        self.assertEqual({d.code for d in diagnostics}, {"ASF-BINDING-002"})
        self.assertEqual(
            [runtime.metadata.id for runtime in chain],
            ["runtime:primary", "runtime:fallback-target"],
        )

    def test_unresolved_required_fallback_runtime_is_reported(self):
        missing_ref = ReferenceIR(
            id="runtime:does-not-exist",
            version=self.primary.fallback_profile.fallback_runtime.version,
            required=True,
        )
        primary_with_missing_fallback = replace(
            self.primary,
            fallback_profile=replace(self.primary.fallback_profile, fallback_runtime=missing_ref),
        )
        chain, diagnostics = resolve_fallback_chain(primary_with_missing_fallback, self.catalog)
        self.assertEqual({d.code for d in diagnostics}, {"ASF-BINDING-003"})
        self.assertEqual([runtime.metadata.id for runtime in chain], ["runtime:primary"])

    def test_unresolved_required_retriever_knowledge_is_reported(self):
        chain, _ = resolve_fallback_chain(self.primary, self.catalog)
        retriever, _ = inherit_retriever(chain)
        missing_knowledge_ref = replace(retriever.knowledge[0], id="kb:does-not-exist")
        retriever_with_missing_ref = RetrieverBindingIR(
            enabled=True, knowledge=(missing_knowledge_ref,), similarity_top_k=retriever.similarity_top_k
        )

        knowledge, diagnostics = resolve_retriever_knowledge(retriever_with_missing_ref, self.catalog)
        self.assertEqual(knowledge, ())
        self.assertEqual({d.code for d in diagnostics}, {"ASF-BINDING-003"})

    def test_unresolved_required_tool_reference_is_reported(self):
        chain, _ = resolve_fallback_chain(self.primary, self.catalog)
        tools_binding, _ = inherit_tools(chain)
        missing_tool_ref = replace(tools_binding.refs[0], id="tool:does-not-exist")
        tools_with_missing_ref = ToolsBindingIR(enabled=True, refs=(missing_tool_ref,))

        tools, diagnostics = resolve_tools(tools_with_missing_ref, self.catalog)
        self.assertEqual(tools, ())
        self.assertEqual({d.code for d in diagnostics}, {"ASF-BINDING-003"})


if __name__ == "__main__":
    unittest.main()
