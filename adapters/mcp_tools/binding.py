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
from typing import Any, Awaitable, Callable

import mcp.types as types

from asf_validator.connector_ir import ConnectorIR
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
