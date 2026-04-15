from __future__ import annotations

import logging
import os
import sys
from typing import Any

from .config import Settings
from .mcp_protocol import McpServer, StdioTransport, ToolDefinition
from .services import TestItService
from .testit_client import TestItClient


def _debug_enabled() -> bool:
    return os.getenv("MCP_DEBUG_STARTUP", "").strip().lower() in {"1", "true", "yes", "on"}


def _debug(message: str) -> None:
    if not _debug_enabled():
        return
    sys.stderr.write(f"[ai-test-it-mcp] {message}\n")
    sys.stderr.flush()


def _schema(
    properties: dict[str, Any],
    required: list[str] | None = None,
    *,
    additional_properties: bool = False,
) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": additional_properties,
    }


def build_tools(service: TestItService) -> list[ToolDefinition]:
    return [
        ToolDefinition(
            "list_projects",
            "List Test IT projects with pagination.",
            _schema({"page": {"type": "integer"}, "pageSize": {"type": "integer"}}),
            service.list_projects,
        ),
        ToolDefinition(
            "get_project",
            "Get a single project by ID.",
            _schema({"projectId": {"type": "string"}}, ["projectId"]),
            service.get_project,
        ),
        ToolDefinition(
            "list_test_suites",
            "List test suites for a test plan.",
            _schema(
                {
                    "testPlanId": {"type": "string"},
                },
                ["testPlanId"],
            ),
            service.list_test_suites,
        ),
        ToolDefinition(
            "get_test_suite",
            "Get a single test suite by ID.",
            _schema({"testSuiteId": {"type": "string"}}, ["testSuiteId"], additional_properties=True),
            service.get_test_suite,
        ),
        ToolDefinition(
            "create_test_suite",
            "Create a test suite.",
            _schema({"projectId": {"type": "string"}, "name": {"type": "string"}}, ["projectId", "name"], additional_properties=True),
            service.create_test_suite,
        ),
        ToolDefinition(
            "update_test_suite",
            "Update a test suite.",
            _schema({"testSuiteId": {"type": "string"}}, ["testSuiteId"], additional_properties=True),
            service.update_test_suite,
        ),
        ToolDefinition(
            "list_test_plans",
            "List test plans for a project.",
            _schema(
                {
                    "projectId": {"type": "string"},
                    "includeDeleted": {"type": "boolean"},
                },
                ["projectId"],
            ),
            service.list_test_plans,
        ),
        ToolDefinition(
            "get_test_plan",
            "Get a single test plan by ID.",
            _schema({"testPlanId": {"type": "string"}}, ["testPlanId"]),
            service.get_test_plan,
        ),
        ToolDefinition(
            "create_test_plan",
            "Create a test plan.",
            _schema({"projectId": {"type": "string"}, "name": {"type": "string"}}, ["projectId", "name"], additional_properties=True),
            service.create_test_plan,
        ),
        ToolDefinition(
            "update_test_plan",
            "Update a test plan.",
            _schema({"testPlanId": {"type": "string"}}, ["testPlanId"], additional_properties=True),
            service.update_test_plan,
        ),
        ToolDefinition(
            "search_test_cases",
            "Search test cases within a project.",
            _schema(
                {
                    "projectId": {"type": "string"},
                    "page": {"type": "integer"},
                    "pageSize": {"type": "integer"},
                    "search": {"type": "string"},
                    "updatedFrom": {"type": "string"},
                    "updatedTo": {"type": "string"},
                    "includeDeleted": {"type": "boolean"},
                },
                ["projectId"],
            ),
            service.search_test_cases,
        ),
        ToolDefinition(
            "get_test_case",
            "Get a single test case by ID.",
            _schema({"testCaseId": {"type": "string"}}, ["testCaseId"]),
            service.get_test_case,
        ),
        ToolDefinition(
            "create_test_case",
            "Create a test case.",
            _schema({"projectId": {"type": "string"}, "name": {"type": "string"}}, ["projectId", "name"], additional_properties=True),
            service.create_test_case,
        ),
        ToolDefinition(
            "update_test_case",
            "Update a test case.",
            _schema({"testCaseId": {"type": "string"}}, ["testCaseId"], additional_properties=True),
            service.update_test_case,
        ),
        ToolDefinition(
            "delete_test_case",
            "Delete a test case.",
            _schema({"testCaseId": {"type": "string"}}, ["testCaseId"]),
            service.delete_test_case,
        ),
        ToolDefinition(
            "list_test_runs",
            "List test runs for a project.",
            _schema(
                {
                    "projectId": {"type": "string"},
                    "page": {"type": "integer"},
                    "pageSize": {"type": "integer"},
                    "testPlanId": {"type": "string"},
                    "notStarted": {"type": "boolean"},
                    "inProgress": {"type": "boolean"},
                    "stopped": {"type": "boolean"},
                    "completed": {"type": "boolean"},
                    "createdDateFrom": {"type": "string"},
                    "createdDateTo": {"type": "string"},
                    "OrderBy": {"type": "string"},
                    "SearchField": {"type": "string"},
                    "SearchValue": {"type": "string"},
                },
                ["projectId"],
            ),
            service.list_test_runs,
        ),
        ToolDefinition(
            "get_test_run",
            "Get a single test run by ID.",
            _schema({"testRunId": {"type": "string"}}, ["testRunId"]),
            service.get_test_run,
        ),
        ToolDefinition(
            "create_test_run",
            "Create a test run.",
            _schema({"projectId": {"type": "string"}, "name": {"type": "string"}}, ["projectId", "name"], additional_properties=True),
            service.create_test_run,
        ),
        ToolDefinition(
            "update_test_run",
            "Update a test run.",
            _schema({"testRunId": {"type": "string"}}, ["testRunId"], additional_properties=True),
            service.update_test_run,
        ),
        ToolDefinition(
            "complete_test_run",
            "Complete a test run.",
            _schema({"testRunId": {"type": "string"}}, ["testRunId"]),
            service.complete_test_run,
        ),
        ToolDefinition(
            "list_test_results",
            "List test results for a project.",
            _schema(
                {
                    "projectId": {"type": "string"},
                    "testRunId": {"type": "string"},
                    "testCaseId": {"type": "string"},
                    "page": {"type": "integer"},
                    "pageSize": {"type": "integer"},
                    "OrderBy": {"type": "string"},
                    "SearchField": {"type": "string"},
                    "SearchValue": {"type": "string"},
                },
                ["projectId"],
            ),
            service.list_test_results,
        ),
        ToolDefinition(
            "get_test_result",
            "Get a single test result by ID.",
            _schema({"testResultId": {"type": "string"}}, ["testResultId"]),
            service.get_test_result,
        ),
        ToolDefinition(
            "create_test_result",
            "Create a test result.",
            _schema({"projectId": {"type": "string"}}, ["projectId"], additional_properties=True),
            service.create_test_result,
        ),
        ToolDefinition(
            "update_test_result",
            "Update a test result.",
            _schema({"testResultId": {"type": "string"}}, ["testResultId"], additional_properties=True),
            service.update_test_result,
        ),
        ToolDefinition(
            "link_test_cases_to_suite_or_plan",
            "Link test cases to a test suite or test plan.",
            _schema(
                {
                    "parentType": {"type": "string", "enum": ["test_suite", "test_plan"]},
                    "parentId": {"type": "string"},
                    "testCaseIds": {"type": "array", "items": {"type": "string"}},
                },
                ["parentType", "parentId", "testCaseIds"],
            ),
            service.link_test_cases_to_suite_or_plan,
        ),
        ToolDefinition(
            "unlink_test_cases_from_suite_or_plan",
            "Unlink test cases from a test suite or test plan.",
            _schema(
                {
                    "parentType": {"type": "string", "enum": ["test_suite", "test_plan"]},
                    "parentId": {"type": "string"},
                    "testCaseIds": {"type": "array", "items": {"type": "string"}},
                },
                ["parentType", "parentId", "testCaseIds"],
            ),
            service.unlink_test_cases_from_suite_or_plan,
        ),
    ]


def create_server() -> McpServer:
    _debug("create_server: reading environment")
    settings = Settings.from_env()
    _debug(
        "create_server: environment loaded "
        f"base_url={settings.base_url!r} timeout={settings.timeout_seconds} verify_ssl={settings.verify_ssl}"
    )
    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
    _debug(f"create_server: logging configured level={settings.log_level}")
    service = TestItService(TestItClient(settings))
    _debug("create_server: service initialized")
    return McpServer("ai-test-it-mcp", "0.1.0", build_tools(service))


def run() -> None:
    _debug("run: starting MCP server")
    transport = StdioTransport()
    try:
        server = create_server()
    except Exception as exc:
        _debug(f"run: startup failed: {exc.__class__.__name__}: {exc}")
        raise

    _debug("run: startup complete, waiting for messages")
    while True:
        try:
            message = transport.read_message()
        except Exception as exc:
            _debug(f"run: failed to read message: {exc.__class__.__name__}: {exc}")
            raise
        if message is None:
            _debug("run: stdin closed, stopping")
            break
        _debug(f"run: received method={message.get('method')!r} id={message.get('id')!r}")
        try:
            response = server.handle(message)
        except Exception as exc:
            _debug(f"run: handler crashed: {exc.__class__.__name__}: {exc}")
            raise
        if response is not None:
            _debug(f"run: sending response for id={response.get('id')!r}")
            transport.write_message(response)
