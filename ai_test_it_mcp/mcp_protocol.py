from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any, Callable

from .errors import TestItMcpError, UpstreamError


ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler

    def descriptor(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


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
    def __init__(self, name: str, version: str, tools: list[ToolDefinition]):
        self._name = name
        self._version = version
        self._tools = {tool.name: tool for tool in tools}
        self._initialized = False

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
        arguments = params.get("arguments") or {}
        tool = self._tools.get(name)
        if tool is None:
            raise UpstreamError(f"Unknown tool: {name}", {"tool": name})
        result = tool.handler(arguments)
        return {
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=True)}],
            "structuredContent": result,
            "isError": False,
        }
