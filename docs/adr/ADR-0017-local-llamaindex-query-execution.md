# ADR-0017: Local LlamaIndex Query Execution

- **Status:** Accepted
- **Date:** 2026-07-12
- **Decision owners:** Project maintainers

## Context

The `llamaindex_retrieval` adapter currently compiles validated Knowledge IR
into `RetrievalConfig` and deliberately stops before indexing or querying.
The next execute-half must build a real LlamaIndex index and retrieve relevant
Knowledge without using a cloud embedding API, credentials, a paid service, or
an ASF-built vector engine. `llama-index-core` is already the selected reuse
target under ADR-0013, but its default settings may resolve an external
embedding or LLM unless the adapter supplies an explicit local embedding and
uses retrieval rather than response synthesis.

## Options

### LlamaIndex plus a downloaded Hugging Face embedding model

Semantically strong, but the required integration package and model weights are
not installed or cached in the current environment. First use would depend on
external model download state and make offline validation non-reproducible.

### LlamaIndex `MockEmbedding`

Credential-free, but it is explicitly a test double. Shipping it as production
retrieval would be a stub disguised as execution and would not rank documents
from their content.

### LlamaIndex plus scikit-learn `HashingVectorizer`

`HashingVectorizer` is a mature, local, stateless feature extractor. A thin
LlamaIndex `BaseEmbedding` adapter can turn its normalized vectors into the
embedding shape `VectorStoreIndex` expects. LlamaIndex still owns the index,
similarity search, node scoring, and retrieval execution; ASF only translates
the selected local embedding interface and result shape.

## Decision

Reuse `llama-index-core`'s real `VectorStoreIndex` and retriever, with an
explicit local `BaseEmbedding` implementation backed by scikit-learn
`HashingVectorizer`. `KnowledgeRetriever.query` will:

1. validate a non-empty query;
2. build an in-memory `VectorStoreIndex` from `RetrievalConfig.documents`;
3. create a LlamaIndex retriever with `config.similarity_top_k`;
4. execute `retrieve(query)`;
5. return immutable ASF result records carrying document id, text, metadata,
   and similarity score.

No LlamaIndex response synthesizer or LLM is used. Empty document configs return
an empty result without constructing an index. The embedding uses a fixed
dimension and tokenization settings, performs no I/O, and has no credential or
network path.

## Build vs Reuse

LlamaIndex owns indexing and vector retrieval; scikit-learn owns token hashing,
normalization, and vector production. ASF builds only the narrow adapters from
`RetrievalConfig` to these APIs and from scored LlamaIndex nodes back to an ASF
result. No vector database, similarity engine, tokenizer, embedding service, or
query scheduler is reimplemented.

## Consequences

- Retrieval becomes real, deterministic, local, and testable without model
  downloads or cloud APIs.
- Hashing embeddings provide lexical rather than semantic similarity. A future
  locally cached semantic model may replace this implementation behind the same
  interface through a reviewed ADR; callers must not interpret scores as model-
  based semantic judgments.
- The adapter gains an explicit `scikit-learn` dependency and remains isolated
  from other adapter packages.
- An in-memory index is rebuilt per query in this first bounded implementation;
  persistence/caching is deferred until a measured consumer requires it.

## Validation Plan

- Unit-test relevant-document ranking, `similarity_top_k`, metadata/id
  preservation, empty configs, blank-query rejection, determinism, and absence
  of any LLM/network configuration.
- Run the complete adapter suite and the repository's mandatory contract, IR,
  graph, semantic, repository, and core unit validations.

## Rollback Plan

Remove the query module and exports, restore the adapter requirement file to
`llama-index-core` only, and return the architecture/tracker to compile-only
status. `RetrievalConfig` and all existing binding functions remain unchanged,
so rollback does not alter any stable contract or production artifact.

## Related Documents

- ADR-0013
- ADR-0014
- ADR-0015
- `docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md`
- `adapters/llamaindex_retrieval/retrieval_config.py`

