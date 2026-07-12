# Content Creation Contract Tests

The production manifest is registered directly in:

- `tests/fixtures/contracts/cases.json` for schema conformance;
- `tests/fixtures/ir/cases.json` for Skill IR construction;
- `tests/fixtures/graph/cases.json` with its five Knowledge dependencies and
  Workflow for dependency/version resolution.

Local model execution is provided by the bounded Ollama adapter through the
Skill's resolved active `runtime:offline` binding. These contract fixtures
remain deterministic and do not call Ollama; live readiness is tested
separately.
The manifest therefore expresses runtime input bounds and embedded
Evaluation/Reflection behavior, while current automated tests prove the
artifact contracts and graph.
