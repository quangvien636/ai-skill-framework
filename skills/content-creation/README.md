# Content Creation

`skill:content-creation` creates one reusable, platform-aware content package
from a supplied brief. Version 1 supports:

- short video scripts;
- social media posts;
- long-form article outlines;
- captions and hashtags;
- title and thumbnail ideas.

The Skill generates drafts only. It does not research facts, create media,
publish, schedule, or call external tools.

## Output contract

`content-package` contains the selected type, primary content, hook, call to
action, alternatives, production notes, and explicit assumptions.
`quality-report` records constraint compliance, unsupported-claim review,
platform fit, and limitations.

## Examples and validation

See [`examples/`](examples/) for minimal, representative, boundary, and refusal
cases. Contract expectations are documented in [`tests/`](tests/).

From the repository root:

```bash
python scripts/validate_contracts.py
python scripts/build_ir.py
python scripts/build_graph.py
python -m unittest discover
```

Use the end-to-end
[`content-brief-to-package`](../../workflows/content-brief-to-package/README.md)
Workflow when invoking this Skill as a framework process.
