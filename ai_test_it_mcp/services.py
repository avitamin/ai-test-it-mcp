from __future__ import annotations

from typing import Any

from .errors import ValidationError
from .models import PaginationInput
from .testit_client import TestItClient


def _pagination(arguments: dict[str, Any]) -> PaginationInput:
    page = int(arguments.get("page", 1))
    page_size = int(arguments.get("pageSize", 20))
    if page < 1:
        raise ValidationError("page must be >= 1", {"field": "page"})
    if page_size < 1 or page_size > 100:
        raise ValidationError("pageSize must be between 1 and 100", {"field": "pageSize"})
    return PaginationInput(page=page, page_size=page_size)


def _required(arguments: dict[str, Any], field: str) -> Any:
    value = arguments.get(field)
    if value in (None, ""):
        raise ValidationError(f"{field} is required", {"field": field})
    return value


def _optional_filters(arguments: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {
        key: arguments.get(key)
        for key in keys
        if arguments.get(key) is not None
    }


class TestItService:
    def __init__(self, client: TestItClient):
        self._client = client

    def list_projects(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.list_entities("project", pagination=_pagination(arguments))

    def get_project(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.get_entity("project", _required(arguments, "projectId"))

    def list_test_suites(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.list_test_suites(
            _required(arguments, "testPlanId"),
        )

    def get_test_suite(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.get_entity("test_suite", _required(arguments, "testSuiteId"))

    def create_test_suite(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.create_entity("test_suite", arguments)

    def update_test_suite(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_suite_id = _required(arguments, "testSuiteId")
        payload = {key: value for key, value in arguments.items() if key != "testSuiteId"}
        return self._client.update_entity("test_suite", test_suite_id, payload)

    def list_test_plans(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.list_project_test_plans(
            _required(arguments, "projectId"),
            include_deleted=arguments.get("includeDeleted"),
        )

    def get_test_plan(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.get_entity("test_plan", _required(arguments, "testPlanId"))

    def create_test_plan(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.create_entity("test_plan", arguments)

    def update_test_plan(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_plan_id = _required(arguments, "testPlanId")
        payload = {key: value for key, value in arguments.items() if key != "testPlanId"}
        return self._client.update_entity("test_plan", test_plan_id, payload)

    def search_test_cases(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.list_entities(
            "test_case",
            project_id=_required(arguments, "projectId"),
            pagination=_pagination(arguments),
            filters=_optional_filters(
                arguments,
                ["search", "updatedFrom", "updatedTo", "includeDeleted"],
            ),
        )

    def get_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.get_entity("test_case", _required(arguments, "testCaseId"))

    def create_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.create_entity("test_case", arguments)

    def update_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_case_id = _required(arguments, "testCaseId")
        payload = {key: value for key, value in arguments.items() if key != "testCaseId"}
        return self._client.update_entity("test_case", test_case_id, payload)

    def delete_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.delete_entity("test_case", _required(arguments, "testCaseId"))

    def list_test_runs(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.list_project_test_runs(
            _required(arguments, "projectId"),
            pagination=_pagination(arguments),
            not_started=bool(arguments.get("notStarted", True)),
            in_progress=bool(arguments.get("inProgress", True)),
            stopped=bool(arguments.get("stopped", True)),
            completed=bool(arguments.get("completed", True)),
            test_plan_id=arguments.get("testPlanId"),
            created_date_from=arguments.get("createdDateFrom"),
            created_date_to=arguments.get("createdDateTo"),
            filters=_optional_filters(arguments, ["OrderBy", "SearchField", "SearchValue"]),
        )

    def get_test_run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.get_entity("test_run", _required(arguments, "testRunId"))

    def create_test_run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.create_entity("test_run", arguments)

    def update_test_run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_run_id = _required(arguments, "testRunId")
        payload = {key: value for key, value in arguments.items() if key != "testRunId"}
        return self._client.update_entity("test_run", test_run_id, payload)

    def complete_test_run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.complete_test_run(_required(arguments, "testRunId"))

    def list_test_results(self, arguments: dict[str, Any]) -> dict[str, Any]:
        project_id = _required(arguments, "projectId")
        body = {"projectIds": [project_id]}
        if arguments.get("testRunId") is not None:
            body["testRunIds"] = [arguments["testRunId"]]
        if arguments.get("testCaseId") is not None:
            body["workItemIds"] = [arguments["testCaseId"]]
        return self._client.search_test_results(
            pagination=_pagination(arguments),
            filters=_optional_filters(arguments, ["OrderBy", "SearchField", "SearchValue"]),
            body=body,
        )

    def get_test_result(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.get_entity("test_result", _required(arguments, "testResultId"))

    def create_test_result(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.create_entity("test_result", arguments)

    def update_test_result(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_result_id = _required(arguments, "testResultId")
        payload = {key: value for key, value in arguments.items() if key != "testResultId"}
        return self._client.update_entity("test_result", test_result_id, payload)

    def link_test_cases_to_suite_or_plan(self, arguments: dict[str, Any]) -> dict[str, Any]:
        parent_type = _required(arguments, "parentType")
        if parent_type not in {"test_suite", "test_plan"}:
            raise ValidationError(
                "parentType must be one of: test_suite, test_plan",
                {"field": "parentType"},
            )
        return self._client.link_entities(
            parent_type,
            _required(arguments, "parentId"),
            list(_required(arguments, "testCaseIds")),
        )

    def unlink_test_cases_from_suite_or_plan(self, arguments: dict[str, Any]) -> dict[str, Any]:
        parent_type = _required(arguments, "parentType")
        if parent_type not in {"test_suite", "test_plan"}:
            raise ValidationError(
                "parentType must be one of: test_suite, test_plan",
                {"field": "parentType"},
            )
        return self._client.unlink_entities(
            parent_type,
            _required(arguments, "parentId"),
            list(_required(arguments, "testCaseIds")),
        )
