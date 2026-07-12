# Publisher Adapters

`descriptors.py` compiles immutable cross-platform export plans and rejects
credential/session metadata. It performs no side effect.

`publisher.py` implements `PublisherAdapter.publish` for local Markdown only.
The caller supplies an output root; the adapter creates a UTF-8 Markdown file
with safe YAML front matter, a title-derived filename, root-containment checks,
and exclusive-create behavior by default. Overwrite requires an explicit
constructor option.

YouTube, TikTok, Facebook, and WordPress descriptors fail before filesystem or
network mutation. No platform SDK, account, upload, token, or API key exists in
this package.

```python
from pathlib import Path
from publisher_adapters import PublisherAdapter, markdown_export

descriptor = markdown_export("Local report", "Body", {"status": "draft"})
result = PublisherAdapter(Path("exports")).publish(descriptor)
```

See proposed ADR-0019 for the Build-vs-Reuse decision and rollback plan.

