"""Translates validated ASF ToolIR/ConnectorIR into MCP protocol constructs.

This module implements the ToolBinding seam from
docs/architecture/EXECUTION_ADAPTER_ARCHITECTURE.md. It holds no tool
execution behavior of its own: TOOL_CONNECTOR_ARCHITECTURE.md defines Tool
contracts as declarative-only, so the actual operation is always a
caller-supplied handler. This module only maps contract shape (inputs,
outputs, connector metadata) onto the MCP wire types and dispatches calls to
whatever handler was bound.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Mapping, Optional

import mcp.types as types

from asf_validator.connector_ir import ConnectorIR
from asf_validator.runtime_ir import RuntimeIR
from asf_validator.skill_ir import FieldIR
from asf_validator.tool_ir import ToolIR

ToolHandler = Callable[[dict[str, Any]], Awaitable[Any]]

_FIELD_TYPE_TO_JSON_SCHEMA_TYPE = {
    "string": "string",
    "number": "number",
    "integer": "integer",
    "boolean": "boolean",
    "array": "array",
    "object": "object",
}


def _field_to_json_schema(field: FieldIR) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": _FIELD_TYPE_TO_JSON_SCHEMA_TYPE[field.type],
        "description": field.description,
    }
    schema.update(field.constraints)
    if field.default is not None:
        schema["default"] = field.default
    return schema


def _fields_to_object_schema(fields: dict[str, FieldIR]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {name: _field_to_json_schema(field) for name, field in fields.items()},
        "required": sorted(name for name, field in fields.items() if field.required),
    }


def tool_ir_to_mcp_tool(tool: ToolIR) -> types.Tool:
    """Translate a validated ToolIR into the MCP wire-level Tool type.

    Uses ``tool.metadata.name`` (the bare kebab name) as the MCP tool name:
    MCP tool names are transport-facing identifiers, distinct from ASF's
    ``tool:``-prefixed contract IDs.
    """
    return types.Tool(
        name=tool.metadata.name,
        description=tool.responsibility,
        inputSchema=_fields_to_object_schema(tool.inputs),
        outputSchema=_fields_to_object_schema(tool.outputs) if tool.outputs else None,
    )


@dataclass(frozen=True)
class ConnectorBinding:
    """Non-executing carrier of Connector contract data for a bound Tool.

    Establishing a live connection or auth flow is a deployment concern
    outside this adapter's scope (TOOL_CONNECTOR_ARCHITECTURE.md Non-Goals);
    this only exposes what the Connector contract already declares so a
    deployer can wire it into MCP's own auth primitives.
    """

    id: str
    authentication: str
    configuration: dict[str, FieldIR]

    @classmethod
    def from_ir(cls, connector: ConnectorIR) -> "ConnectorBinding":
        return cls(
            id=connector.metadata.id,
            authentication=connector.authentication,
            configuration=connector.configuration,
        )


class MCPToolRegistry:
    """ToolBinding Protocol implementation backed by the MCP Python SDK.

    Binds ToolIR contracts to caller-supplied handlers, then serves the
    shape an ``mcp.server.lowlevel.Server``'s ``list_tools``/``call_tool``
    handlers need without ASF ever defining tool behavior itself.
    """

    def __init__(self) -> None:
        self._tools: dict[str, types.Tool] = {}
        self._handlers: dict[str, ToolHandler] = {}
        self._connectors: dict[str, ConnectorBinding] = {}

    def bind(
        self,
        tool: ToolIR,
        handler: ToolHandler,
        connector: ConnectorIR | None = None,
    ) -> None:
        mcp_tool = tool_ir_to_mcp_tool(tool)
        self._tools[mcp_tool.name] = mcp_tool
        self._handlers[mcp_tool.name] = handler
        if connector is not None:
            self._connectors[mcp_tool.name] = ConnectorBinding.from_ir(connector)

    def list_tools(self) -> list[types.Tool]:
        return list(self._tools.values())

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name not in self._handlers:
            raise KeyError(f"no handler bound for MCP tool '{name}'")
        return await self._handlers[name](arguments)

    def connector_for(self, name: str) -> ConnectorBinding | None:
        return self._connectors.get(name)


def bind_runtime_tools(
    registry: MCPToolRegistry,
    runtime: RuntimeIR,
    tools_by_id: Mapping[str, ToolIR],
    handlers_by_id: Mapping[str, ToolHandler],
    connectors_by_id: Optional[Mapping[str, ConnectorIR]] = None,
) -> tuple[str, ...]:
    """Bind every Tool a resolved Runtime Contract references to `registry`.
    Binding only -- no invocation.

    `tools_by_id`/`handlers_by_id` must already contain the Runtime
    Planning-resolved ToolIR/handler for each `runtime.tools.refs` id --
    this function does not resolve repository references itself (that is
    the Dependency Graph/planner's job). Returns an empty tuple when
    `runtime.tools.enabled` is false, matching ADR-0014's `enabled` pattern.
    """
    if not runtime.tools.enabled:
        return ()
    connectors = connectors_by_id or {}
    bound: list[str] = []
    for ref in runtime.tools.refs:
        tool = tools_by_id[ref.id]
        handler = handlers_by_id[ref.id]
        connector = None
        if tool.dependencies.connectors:
            connector = connectors.get(tool.dependencies.connectors[0].id)
        registry.bind(tool, handler, connector=connector)
        bound.append(tool.metadata.name)
    return tuple(bound)
