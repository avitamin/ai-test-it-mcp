from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable

from .errors import TestItMcpError, UpstreamError, ValidationError


ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler
    risk: str = "read"
    destructive: bool = False
    high_impact: bool = False
    supports_preview: bool = False
    target_fields: tuple[str, ...] = ()

    def descriptor(self) -> dict[str, Any]:
        descriptor = {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "annotations": {
                "readOnlyHint": self.risk == "read",
                "destructiveHint": self.destructive,
            },
            "metadata": {
                "risk": self.risk,
                "destructive": self.destructive,
                "highImpact": self.high_impact,
                "supportsPreview": self.supports_preview,
            },
        }
        return descriptor


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _validate_schema(value: Any, schema: dict[str, Any], path: str) -> None:
    expected_type = schema.get("type")
    if expected_type is not None:
        allowed = expected_type if isinstance(expected_type, list) else [expected_type]
        if _json_type(value) not in allowed:
            raise ValidationError(
                f"{path} must be {', '.join(allowed)}",
                {"field": path, "expected": allowed, "actual": _json_type(value)},
            )

    enum = schema.get("enum")
    if enum is not None and value not in enum:
        raise ValidationError(f"{path} must be one of: {', '.join(map(str, enum))}", {"field": path, "allowed": enum})

    if schema.get("type") == "object":
        if not isinstance(value, dict):
            return
        properties = schema.get("properties", {})
        for required_field in schema.get("required", []):
            required_value = value.get(required_field)
            if required_value in (None, ""):
                raise ValidationError(f"{required_field} is required", {"field": required_field})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise ValidationError("Unknown argument fields are not allowed.", {"fields": unknown})
        for key, item in value.items():
            child_schema = properties.get(key)
            if child_schema is not None:
                _validate_schema(item, child_schema, key if path == "arguments" else f"{path}.{key}")

    if schema.get("type") == "array":
        if not isinstance(value, list):
            return
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            raise ValidationError(f"{path} must contain at least {min_items} item(s).", {"field": path})
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                _validate_schema(item, item_schema, f"{path}[{index}]")


def _validate_arguments(arguments: Any, schema: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise ValidationError("Tool arguments must be an object.", {"field": "arguments"})
    _validate_schema(arguments, schema, "arguments")
    return arguments


def _canonical_arguments(arguments: dict[str, Any]) -> str:
    return json.dumps(arguments, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class StdioTransport:
    def __init__(self, input_stream=None, output_stream=None):
        self.input_stream = input_stream or sys.stdin.buffer
        self.output_stream = output_stream or sys.stdout.buffer

    def read_message(self) -> dict[str, Any] | None:
        first_line = self.input_stream.readline()
        if not first_line:
            return None

        stripped = first_line.strip()
        if not stripped:
            return self.read_message()

        # Current MCP stdio uses newline-delimited JSON messages.
        if stripped.startswith((b"{", b"[")):
            return json.loads(stripped.decode("utf-8"))

        # Accept Content-Length framing for compatibility with older clients.
        headers: dict[str, str] = {}
        current_line = first_line
        while True:
            if current_line in (b"\r\n", b"\n"):
                break
            name, _, value = current_line.decode("utf-8").partition(":")
            headers[name.strip().lower()] = value.strip()
            current_line = self.input_stream.readline()
            if not current_line:
                return None

        length = int(headers["content-length"])
        body = self.input_stream.read(length)
        if not body:
            return None
        return json.loads(body.decode("utf-8"))

    def write_message(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.output_stream.write(body)
        self.output_stream.write(b"\n")
        self.output_stream.flush()


class McpServer:
    PREVIEW_TTL_SECONDS = 600

    def __init__(self, name: str, version: str, tools: list[ToolDefinition]):
        self._name = name
        self._version = version
        expanded_tools = list(tools)
        for tool in tools:
            if tool.supports_preview:
                expanded_tools.extend(self._preview_tools(tool))
        self._tools = {tool.name: tool for tool in expanded_tools}
        self._initialized = False

    def _preview_tools(self, tool: ToolDefinition) -> list[ToolDefinition]:
        apply_schema = dict(tool.input_schema)
        apply_schema["properties"] = dict(apply_schema.get("properties", {})) | {
            "operationId": {"type": "string"},
        }
        apply_schema["required"] = list(apply_schema.get("required", [])) + ["operationId"]
        return [
            ToolDefinition(
                name=f"preview_{tool.name}",
                description=f"Preview the planned {tool.name} operation without changing Test IT.",
                input_schema=tool.input_schema,
                handler=lambda arguments, original=tool: self._preview_tool(original, arguments),
                risk="read",
                supports_preview=False,
                target_fields=tool.target_fields,
            ),
            ToolDefinition(
                name=f"apply_{tool.name}",
                description=f"Apply a previously previewed {tool.name} operation.",
                input_schema=apply_schema,
                handler=lambda arguments, original=tool: self._apply_previewed_tool(original, arguments),
                risk=tool.risk,
                destructive=tool.destructive,
                high_impact=tool.high_impact,
                supports_preview=False,
                target_fields=tool.target_fields,
            ),
        ]

    def _operation_id(self, tool: ToolDefinition, arguments: dict[str, Any], expires_at: int) -> str:
        payload = f"{tool.name}\n{expires_at}\n{_canonical_arguments(arguments)}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
        return f"preview-v1:{expires_at}:{digest}"

    def _preview_tool(self, tool: ToolDefinition, arguments: dict[str, Any]) -> dict[str, Any]:
        expires_at = int(time.time()) + self.PREVIEW_TTL_SECONDS
        target = {
            field: arguments[field]
            for field in tool.target_fields
            if field in arguments
        }
        changed_fields = sorted(set(arguments) - set(tool.target_fields))
        return {
            "operation": tool.name,
            "operationId": self._operation_id(tool, arguments, expires_at),
            "expiresAt": expires_at,
            "target": target,
            "changedFields": changed_fields,
            "risk": {
                "level": tool.risk,
                "destructive": tool.destructive,
                "highImpact": tool.high_impact,
            },
            "upstream": {
                "willCallUpstream": False,
                "applyTool": f"apply_{tool.name}",
            },
        }

    def _apply_previewed_tool(self, tool: ToolDefinition, arguments: dict[str, Any]) -> dict[str, Any]:
        operation_id = arguments.get("operationId")
        if not isinstance(operation_id, str):
            raise ValidationError("operationId is required", {"field": "operationId"})
        call_arguments = {key: value for key, value in arguments.items() if key != "operationId"}
        try:
            prefix, expires_at_text, _digest = operation_id.split(":", 2)
            expires_at = int(expires_at_text)
        except ValueError as exc:
            raise ValidationError("operationId is invalid", {"field": "operationId"}) from exc
        if prefix != "preview-v1":
            raise ValidationError("operationId is invalid", {"field": "operationId"})
        if int(time.time()) > expires_at:
            raise ValidationError("operationId has expired", {"field": "operationId"})
        if operation_id != self._operation_id(tool, call_arguments, expires_at):
            raise ValidationError("operationId does not match the supplied arguments.", {"field": "operationId"})
        return tool.handler(call_arguments)

    def handle(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        if method == "notifications/initialized":
            self._initialized = True
            return None

        request_id = request.get("id")
        params = request.get("params", {})

        try:
            if method == "initialize":
                params_protocol = params.get("protocolVersion")
                result = {
                    # Echo the negotiated protocol version back to the client.
                    "protocolVersion": params_protocol or "2025-06-18",
                    "serverInfo": {
                        "name": self._name,
                        "version": self._version,
                        "title": self._name,
                    },
                    "capabilities": {"tools": {"listChanged": True}},
                }
            elif method == "tools/list":
                result = {"tools": [tool.descriptor() for tool in self._tools.values()]}
            elif method == "tools/call":
                result = self._call_tool(params)
            else:
                raise UpstreamError(
                    f"Unsupported MCP method: {method}",
                    {"method": method},
                )
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except TestItMcpError as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(exc), "data": exc.to_payload()},
            }

    def _call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments", {})
        if arguments is None:
            arguments = {}
        tool = self._tools.get(name)
        if tool is None:
            raise UpstreamError(f"Unknown tool: {name}", {"tool": name})
        arguments = _validate_arguments(arguments, tool.input_schema)
        result = tool.handler(arguments)
        if tool.risk != "read":
            result = {
                "operation": tool.name,
                "target": {
                    field: arguments[field]
                    for field in tool.target_fields
                    if field in arguments
                },
                "changedFields": sorted(set(arguments) - set(tool.target_fields) - {"operationId"}),
                "risk": {
                    "level": tool.risk,
                    "destructive": tool.destructive,
                    "highImpact": tool.high_impact,
                },
                "success": True,
                "result": result,
            }
        return {
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=True)}],
            "structuredContent": result,
            "isError": False,
        }
