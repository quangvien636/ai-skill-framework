import io
import json
from contextlib import redirect_stdout

import _bootstrap

from asf_cli import main


def test_cli_compile_returns_compiled_graph_without_execution():
    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = main(
            (
                "--format",
                "json",
                "--start",
                str(_bootstrap.REPO_ROOT),
                "compile",
                "--workflow",
                "workflow:content-brief-to-package",
                "--execution-id",
                "cli-compile",
                "--inputs",
                '{"content-type":"article-outline","brief":"Explain ASF.",'
                '"audience":"Developers","platform":"generic"}',
            )
        )

    report = json.loads(output.getvalue())
    assert exit_code == 0
    assert report["compiled"]["graph"]["nodes"][1]["id"] == "create-content"
    assert report["compiled"]["bindings"][0]["runtime_id"] == "runtime:content"
