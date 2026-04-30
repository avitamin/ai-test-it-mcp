from __future__ import annotations

import io
import json
import unittest

from mcp_server.mcp_protocol import McpServer, StdioTransport, ToolDefinition
from mcp_server.errors import ValidationError
from mcp_server.server import build_tools


class ProtocolTests(unittest.TestCase):
    def test_initialize_and_list_tools(self) -> None:
        tool = ToolDefinition(
            name="echo",
            description="Echo tool",
            input_schema={"type": "object", "properties": {}},
            handler=lambda arguments: {"ok": True, "arguments": arguments},
        )
        server = McpServer("name", "1.0.0", [tool])

        initialize = server.handle(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-06-18"},
            }
        )
        self.assertEqual(initialize["result"]["serverInfo"]["name"], "name")
        self.assertEqual(initialize["result"]["protocolVersion"], "2025-06-18")
        self.assertTrue(initialize["result"]["capabilities"]["tools"]["listChanged"])

        listing = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        self.assertEqual(listing["result"]["tools"][0]["name"], "echo")

    def test_tool_call_success_and_error(self) -> None:
        ok_tool = ToolDefinition(
            name="echo",
            description="Echo tool",
            input_schema={"type": "object", "properties": {}},
            handler=lambda arguments: {"echoed": arguments},
        )
        bad_tool = ToolDefinition(
            name="bad",
            description="Bad tool",
            input_schema={"type": "object", "properties": {}},
            handler=lambda _: (_ for _ in ()).throw(ValidationError("broken")),
        )
        server = McpServer("name", "1.0.0", [ok_tool, bad_tool])

        success = server.handle(
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "echo", "arguments": {"x": 1}}}
        )
        self.assertFalse(success["result"]["isError"])
        self.assertEqual(success["result"]["structuredContent"]["echoed"]["x"], 1)

        failure = server.handle(
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "bad", "arguments": {}}}
        )
        self.assertEqual(failure["error"]["data"]["code"], "ValidationError")

    def test_stdio_transport_roundtrip(self) -> None:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
        body = json.dumps(payload).encode("utf-8")
        raw = body + b"\n"
        input_stream = io.BytesIO(raw)
        output_stream = io.BytesIO()
        transport = StdioTransport(input_stream=input_stream, output_stream=output_stream)

        message = transport.read_message()
        self.assertEqual(message["method"], "ping")

        transport.write_message(payload)
        written = output_stream.getvalue()
        self.assertEqual(written, body + b"\n")

    def test_stdio_transport_accepts_content_length_messages(self) -> None:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
        body = json.dumps(payload).encode("utf-8")
        raw = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body
        transport = StdioTransport(input_stream=io.BytesIO(raw), output_stream=io.BytesIO())

        message = transport.read_message()
        self.assertEqual(message["method"], "ping")

    def test_build_tools_includes_advanced_step_tools(self) -> None:
        class Service:
            def __getattr__(self, name):
                return lambda arguments: {"ok": True}

        tools = build_tools(Service())
        by_name = {tool.name: tool for tool in tools}
        self.assertIn("get_test_case_steps", by_name)
        self.assertIn("search_shared_steps", by_name)
        self.assertIn("create_shared_step", by_name)
        self.assertIn("replace_test_case_steps_with_shared_step", by_name)
        self.assertIn("extract_shared_step_from_test_case_steps", by_name)
        self.assertIn("parameterize_test_case", by_name)
        self.assertEqual(
            by_name["replace_test_case_steps_with_shared_step"].input_schema["required"],
            ["testCaseId", "sharedStepId"],
        )
