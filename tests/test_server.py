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

    def test_tool_call_validates_declared_schema(self) -> None:
        tool = ToolDefinition(
            name="strict",
            description="Strict tool",
            input_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
                "additionalProperties": False,
            },
            handler=lambda arguments: {"arguments": arguments},
        )
        server = McpServer("name", "1.0.0", [tool])

        failure = server.handle(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "strict", "arguments": {"name": "ok", "extra": True}},
            }
        )

        self.assertEqual(failure["error"]["data"]["code"], "ValidationError")
        self.assertEqual(failure["error"]["data"]["details"]["fields"], ["extra"])

    def test_preview_and_apply_tools_are_generated_for_high_impact_tools(self) -> None:
        calls = []

        tool = ToolDefinition(
            name="delete_thing",
            description="Delete thing",
            input_schema={
                "type": "object",
                "properties": {"thingId": {"type": "string"}},
                "required": ["thingId"],
                "additionalProperties": False,
            },
            handler=lambda arguments: calls.append(arguments) or {"deleted": arguments["thingId"]},
            risk="destructive",
            destructive=True,
            high_impact=True,
            supports_preview=True,
            target_fields=("thingId",),
        )
        server = McpServer("name", "1.0.0", [tool])

        listing = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        by_name = {item["name"]: item for item in listing["result"]["tools"]}
        self.assertTrue(by_name["delete_thing"]["metadata"]["supportsPreview"])
        self.assertTrue(by_name["delete_thing"]["annotations"]["destructiveHint"])
        self.assertIn("preview_delete_thing", by_name)
        self.assertIn("apply_delete_thing", by_name)

        preview = server.handle(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "preview_delete_thing", "arguments": {"thingId": "t1"}},
            }
        )
        self.assertEqual(calls, [])
        operation_id = preview["result"]["structuredContent"]["operationId"]

        apply_result = server.handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "apply_delete_thing",
                    "arguments": {"thingId": "t1", "operationId": operation_id},
                },
            }
        )
        self.assertEqual(calls, [{"thingId": "t1"}])
        self.assertTrue(apply_result["result"]["structuredContent"]["success"])

    def test_apply_rejects_operation_id_for_changed_arguments(self) -> None:
        tool = ToolDefinition(
            name="delete_thing",
            description="Delete thing",
            input_schema={
                "type": "object",
                "properties": {"thingId": {"type": "string"}},
                "required": ["thingId"],
                "additionalProperties": False,
            },
            handler=lambda arguments: {"deleted": arguments["thingId"]},
            risk="destructive",
            destructive=True,
            high_impact=True,
            supports_preview=True,
            target_fields=("thingId",),
        )
        server = McpServer("name", "1.0.0", [tool])
        preview = server.handle(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "preview_delete_thing", "arguments": {"thingId": "t1"}},
            }
        )

        failure = server.handle(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "apply_delete_thing",
                    "arguments": {"thingId": "t2", "operationId": preview["result"]["structuredContent"]["operationId"]},
                },
            }
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
        self.assertEqual(
            by_name["parameterize_test_case"].input_schema["required"],
            ["testCaseId", "projectId"],
        )
        self.assertNotIn(
            "allowParameterOverwrite",
            by_name["parameterize_test_case"].input_schema["properties"],
        )
