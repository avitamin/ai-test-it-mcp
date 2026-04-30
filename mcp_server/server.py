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
    sys.stderr.write(f"[mcp-server] {message}\n")
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


_COMMON_ENTITY_FIELDS: dict[str, Any] = {
    "projectId": {"type": "string"},
    "name": {"type": "string"},
    "description": {"type": "string"},
}

_WORK_ITEM_FIELDS: dict[str, Any] = {
    "projectId": {"type": "string"},
    "sectionId": {"type": "string"},
    "name": {"type": "string"},
    "description": {"type": "string"},
    "state": {"type": "string"},
    "priority": {"type": "string"},
    "sourceType": {"type": "string"},
    "steps": {"type": "array", "items": {"type": "object"}, "minItems": 1},
    "preconditionSteps": {"type": "array", "items": {"type": "object"}},
    "postconditionSteps": {"type": "array", "items": {"type": "object"}},
    "duration": {"type": "integer"},
    "attributes": {"type": "object"},
    "tags": {"type": "array", "items": {"type": "object"}},
    "links": {"type": "array", "items": {"type": "object"}},
    "attachments": {"type": "array", "items": {"type": "object"}},
    "entityTypeName": {"type": "string"},
}

_TEST_CASE_UPDATE_FIELDS: dict[str, Any] = {
    "testCaseId": {"type": "string"},
    **{key: value for key, value in _WORK_ITEM_FIELDS.items() if key != "projectId"},
    "iterations": {"type": "array", "items": {"type": "object"}},
    "autoTests": {"type": "array", "items": {"type": "object"}},
}

_TEST_RUN_FIELDS: dict[str, Any] = {
    **_COMMON_ENTITY_FIELDS,
    "testPlanId": {"type": "string"},
}

_TEST_RESULT_FIELDS: dict[str, Any] = {
    "projectId": {"type": "string"},
    "testRunId": {"type": "string"},
    "testCaseId": {"type": "string"},
    "outcome": {"type": "string"},
    "comment": {"type": "string"},
    "duration": {"type": "integer"},
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
            _schema({"testSuiteId": {"type": "string"}}, ["testSuiteId"]),
            service.get_test_suite,
        ),
        ToolDefinition(
            "create_test_suite",
            "Create a test suite.",
            _schema(_COMMON_ENTITY_FIELDS, ["projectId", "name"]),
            service.create_test_suite,
            risk="write",
            target_fields=("projectId",),
        ),
        ToolDefinition(
            "update_test_suite",
            "Update a test suite.",
            _schema({"testSuiteId": {"type": "string"}, "name": {"type": "string"}, "description": {"type": "string"}}, ["testSuiteId"]),
            service.update_test_suite,
            risk="write",
            target_fields=("testSuiteId",),
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
            _schema(_COMMON_ENTITY_FIELDS, ["projectId", "name"]),
            service.create_test_plan,
            risk="write",
            target_fields=("projectId",),
        ),
        ToolDefinition(
            "update_test_plan",
            "Update a test plan.",
            _schema({"testPlanId": {"type": "string"}, "name": {"type": "string"}, "description": {"type": "string"}}, ["testPlanId"]),
            service.update_test_plan,
            risk="write",
            target_fields=("testPlanId",),
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
                    "OrderBy": {"type": "string"},
                    "SearchField": {"type": "string"},
                    "SearchValue": {"type": "string"},
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
            _schema(
                _WORK_ITEM_FIELDS,
                ["projectId", "sectionId", "name", "state", "priority", "steps"],
            ),
            service.create_test_case,
            risk="write",
            target_fields=("projectId", "sectionId"),
        ),
        ToolDefinition(
            "update_test_case",
            "Update a test case.",
            _schema(_TEST_CASE_UPDATE_FIELDS, ["testCaseId"]),
            service.update_test_case,
            risk="write",
            high_impact=True,
            supports_preview=True,
            target_fields=("testCaseId",),
        ),
        ToolDefinition(
            "delete_test_case",
            "Delete a test case.",
            _schema({"testCaseId": {"type": "string"}}, ["testCaseId"]),
            service.delete_test_case,
            risk="destructive",
            destructive=True,
            high_impact=True,
            supports_preview=True,
            target_fields=("testCaseId",),
        ),
        ToolDefinition(
            "get_test_case_steps",
            "Get normalized steps and parameters from a test case.",
            _schema({"testCaseId": {"type": "string"}}, ["testCaseId"]),
            service.get_test_case_steps,
        ),
        ToolDefinition(
            "search_shared_steps",
            "Search shared steps within a project.",
            _schema(
                {
                    "projectId": {"type": "string"},
                    "page": {"type": "integer"},
                    "pageSize": {"type": "integer"},
                    "search": {"type": "string"},
                    "OrderBy": {"type": "string"},
                    "SearchField": {"type": "string"},
                    "SearchValue": {"type": "string"},
                },
                ["projectId"],
            ),
            service.search_shared_steps,
        ),
        ToolDefinition(
            "create_shared_step",
            "Create a shared step work item.",
            _schema(
                _WORK_ITEM_FIELDS,
                ["projectId", "sectionId", "name", "state", "priority", "steps"],
            ),
            service.create_shared_step,
            risk="write",
            target_fields=("projectId", "sectionId"),
        ),
        ToolDefinition(
            "replace_test_case_steps_with_shared_step",
            "Replace selected test case steps with a shared step reference.",
            _schema(
                {
                    "testCaseId": {"type": "string"},
                    "sharedStepId": {"type": "string"},
                    "stepIds": {"type": "array", "items": {"type": "string"}},
                    "stepIndexes": {"type": "array", "items": {"type": "integer"}},
                    "parameterValues": {"type": "object"},
                },
                ["testCaseId", "sharedStepId"],
            ),
            service.replace_test_case_steps_with_shared_step,
            risk="write",
            high_impact=True,
            supports_preview=True,
            target_fields=("testCaseId", "sharedStepId"),
        ),
        ToolDefinition(
            "extract_shared_step_from_test_case_steps",
            "Create a shared step from selected test case steps and replace them in the source test case.",
            _schema(
                {
                    "testCaseId": {"type": "string"},
                    "projectId": {"type": "string"},
                    "sectionId": {"type": "string"},
                    "name": {"type": "string"},
                    "state": {"type": "string"},
                    "priority": {"type": "string"},
                    "stepIds": {"type": "array", "items": {"type": "string"}},
                    "stepIndexes": {"type": "array", "items": {"type": "integer"}},
                    "parameterValues": {"type": "object"},
                    "entityTypeName": {"type": "string"},
                },
                ["testCaseId", "projectId", "sectionId", "name", "state", "priority"],
            ),
            service.extract_shared_step_from_test_case_steps,
            risk="write",
            high_impact=True,
            supports_preview=True,
            target_fields=("testCaseId", "projectId", "sectionId"),
        ),
        ToolDefinition(
            "parameterize_test_case",
            "Assign existing Test IT parameters to test case iterations and optionally replace literal step text with parameter placeholders.",
            _schema(
                {
                    "testCaseId": {"type": "string"},
                    "projectId": {"type": "string"},
                    "parameters": {"type": "array", "items": {"type": "object"}},
                    "iterations": {"type": "array", "items": {"type": "object"}},
                    "replacements": {"type": "array", "items": {"type": "object"}},
                },
                ["testCaseId", "projectId"],
            ),
            service.parameterize_test_case,
            risk="write",
            high_impact=True,
            supports_preview=True,
            target_fields=("testCaseId", "projectId"),
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
            _schema(_TEST_RUN_FIELDS, ["projectId", "name"]),
            service.create_test_run,
            risk="write",
            target_fields=("projectId",),
        ),
        ToolDefinition(
            "update_test_run",
            "Update a test run.",
            _schema({"testRunId": {"type": "string"}, "name": {"type": "string"}, "description": {"type": "string"}, "testPlanId": {"type": "string"}}, ["testRunId"]),
            service.update_test_run,
            risk="write",
            target_fields=("testRunId",),
        ),
        ToolDefinition(
            "complete_test_run",
            "Complete a test run.",
            _schema({"testRunId": {"type": "string"}}, ["testRunId"]),
            service.complete_test_run,
            risk="destructive",
            destructive=True,
            high_impact=True,
            supports_preview=True,
            target_fields=("testRunId",),
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
            _schema(_TEST_RESULT_FIELDS, ["projectId"]),
            service.create_test_result,
            risk="write",
            target_fields=("projectId", "testRunId", "testCaseId"),
        ),
        ToolDefinition(
            "update_test_result",
            "Update a test result.",
            _schema({"testResultId": {"type": "string"}, **{key: value for key, value in _TEST_RESULT_FIELDS.items() if key != "projectId"}}, ["testResultId"]),
            service.update_test_result,
            risk="write",
            target_fields=("testResultId",),
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
            risk="write",
            target_fields=("parentType", "parentId"),
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
            risk="destructive",
            destructive=True,
            high_impact=True,
            supports_preview=True,
            target_fields=("parentType", "parentId"),
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
    return McpServer("mcp-server", "0.1.0", build_tools(service))


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
