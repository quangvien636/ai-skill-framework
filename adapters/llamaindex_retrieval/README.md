# LlamaIndex Retrieval Adapter

This adapter has two explicit halves:

- `retrieval_config.py` compiles validated Knowledge IR or a resolved
  `RuntimeBinding` into deterministic LlamaIndex `Document` objects and an ASF
  `RetrievalConfig`. It performs no execution.
- `retriever.py` builds a real in-memory LlamaIndex `VectorStoreIndex` and
  executes local retrieval with `similarity_top_k` from that config.

The execute half uses an explicit scikit-learn `HashingVectorizer` embedding
behind LlamaIndex's `BaseEmbedding` interface. It is stateless, deterministic,
credential-free, makes no network request, downloads no model, and never
constructs an LLM or response synthesizer. Its ranking is lexical; returned
scores must not be described as neural semantic judgments.

```python
from llamaindex_retrieval import KnowledgeRetriever, retrieval_config_from_binding

config = retrieval_config_from_binding(binding)
if config is not None:
    result = KnowledgeRetriever().query(config, "audience tone guidance")
```

See proposed ADR-0017 for the Build-vs-Reuse decision, validation, tradeoffs,
and rollback plan.

