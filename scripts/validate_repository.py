#!/usr/bin/env python3
"""Validate every canonical repository artifact through all implemented layers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from asf_validator.dependency_graph import build_dependency_graph  # noqa: E402
from asf_validator.pipeline import build_ir  # noqa: E402
from asf_validator.project_discovery import discover_project  # noqa: E402
from asf_validator.repository_validator import validate_repository  # noqa: E402
from asf_validator.schema_registry import build_schema_registry  # noqa: E402
from asf_validator.semantic_validator import validate_semantics  # noqa: E402
from asf_validator.version_graph import build_version_graph  # noqa: E402
from asf_validator.workspace_discovery import discover_workspace_root  # noqa: E402


def run(start: Path) -> int:
    root = discover_workspace_root(start)
    index = discover_project(root)
    registry = build_schema_registry(root / "schemas")
    loadable = [
        artifact
        for artifact in index.artifacts
        if artifact.kind in ("skill", "workflow", "knowledge")
    ]
    results = [
        build_ir(artifact.kind, artifact.path, registry) for artifact in loadable
    ]

    diagnostics = [diagnostic for result in results for diagnostic in result.diagnostics]
    dependency_graph, dependency_diagnostics = build_dependency_graph(results)
    _version_graph, version_diagnostics = build_version_graph(dependency_graph)
    diagnostics.extend(dependency_diagnostics)
    diagnostics.extend(version_diagnostics)
    diagnostics.extend(validate_semantics(results))
    diagnostics.extend(validate_repository(index, results))

    errors = [diagnostic for diagnostic in diagnostics if diagnostic.is_error()]
    for diagnostic in diagnostics:
        print(
            f"{diagnostic.severity.value.upper()} {diagnostic.code} "
            f"{diagnostic.artifact} [{diagnostic.location}]: {diagnostic.message}"
        )
    print(
        f"RESULT: discovered {len(index.artifacts)} locations; "
        f"loaded {sum(result.ok for result in results)}/{len(results)} artifacts; "
        f"{len(errors)} errors, {len(diagnostics) - len(errors)} warnings."
    )
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover and validate the AI Skill Framework repository."
    )
    parser.add_argument(
        "start",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Path within the workspace (defaults to current directory).",
    )
    return run(parser.parse_args().start)


if __name__ == "__main__":
    raise SystemExit(main())
