# Content Brief to Package

This active one-step Workflow invokes `skill:content-creation` with every
declared input and returns both generated content and its quality report. It is
the canonical end-to-end Content Creation v1 path.

Example input:

```yaml
content-type: "short-video-script"
brief: "Explain how a weekly planning ritual reduces context switching."
audience: "Busy independent designers who already use a task list."
platform: "tiktok"
tone: "practical, warm, and concise"
source-facts:
  - "The ritual takes 20 minutes every Friday."
call-to-action: "Save this and try the ritual on Friday."
constraints:
  - "Target 45 seconds."
```

Run the repository checks from the root:

```bash
python scripts/validate_contracts.py
python scripts/build_ir.py
python scripts/build_graph.py
python -m unittest discover
```
