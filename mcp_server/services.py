from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import UpstreamError, ValidationError
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


def _required_list(arguments: dict[str, Any], field: str) -> list[Any]:
    value = _required(arguments, field)
    if not isinstance(value, list) or not value:
        raise ValidationError(f"{field} must be a non-empty array", {"field": field})
    return value


def _work_item_entity(result: dict[str, Any]) -> dict[str, Any]:
    entity = result.get("entity")
    if not isinstance(entity, dict):
        raise UpstreamError("Unexpected work item response format from Test IT.", {"payloadType": type(entity).__name__})
    return entity


def _steps_key(work_item: dict[str, Any]) -> str:
    for key in ("steps", "testSteps", "workItemSteps"):
        if isinstance(work_item.get(key), list):
            return key
    return "steps"


def _parameters_key(work_item: dict[str, Any]) -> str:
    for key in ("parameters", "testParameters"):
        if isinstance(work_item.get(key), list):
            return key
    return "parameters"


def _step_id(step: Any) -> str | None:
    if not isinstance(step, dict):
        return None
    value = step.get("id") or step.get("globalId") or step.get("stepId")
    return str(value) if value not in (None, "") else None


def _step_payload(step: dict[str, Any], *, include_id: bool) -> dict[str, Any]:
    payload = {
        "action": step.get("action"),
        "expected": step.get("expected"),
        "testData": step.get("testData"),
        "comments": step.get("comments"),
        "workItemId": step.get("workItemId"),
    }
    if include_id:
        payload["id"] = _step_id(step)
    return payload


def _selected_step_positions(steps: list[Any], arguments: dict[str, Any]) -> list[int]:
    has_ids = arguments.get("stepIds") is not None
    has_indexes = arguments.get("stepIndexes") is not None
    if has_ids == has_indexes:
        raise ValidationError("Provide exactly one of stepIds or stepIndexes.", {"fields": ["stepIds", "stepIndexes"]})

    if has_ids:
        requested = {str(value) for value in _required_list(arguments, "stepIds")}
        positions = [index for index, step in enumerate(steps) if _step_id(step) in requested]
        found = {_step_id(steps[index]) for index in positions}
        missing = sorted(requested - {value for value in found if value is not None})
        if missing:
            raise ValidationError("Some stepIds were not found.", {"field": "stepIds", "missing": missing})
        return positions

    positions = []
    for raw_index in _required_list(arguments, "stepIndexes"):
        try:
            index = int(raw_index)
        except (TypeError, ValueError) as exc:
            raise ValidationError("stepIndexes must contain integers.", {"field": "stepIndexes"}) from exc
        if index < 1 or index > len(steps):
            raise ValidationError("stepIndexes are 1-based and must point to existing steps.", {"field": "stepIndexes"})
        positions.append(index - 1)
    if len(set(positions)) != len(positions):
        raise ValidationError("stepIndexes must not contain duplicates.", {"field": "stepIndexes"})
    return sorted(positions)


def _shared_step_reference(shared_step_id: str, source_step: Any) -> dict[str, Any]:
    if not isinstance(source_step, dict):
        raise ValidationError("Selected step must be an object.", {"field": "steps"})
    step_id = _step_id(source_step)
    if step_id is None:
        raise ValidationError("Selected step must include id for update.", {"field": "steps"})
    return {
        "id": step_id,
        "action": "",
        "expected": "",
        "testData": "",
        "comments": "",
        "workItemId": shared_step_id,
    }


def _replace_positions(steps: list[Any], positions: list[int], replacement: dict[str, Any]) -> list[Any]:
    selected = set(positions)
    first = positions[0]
    updated = []
    for index, step in enumerate(steps):
        if index == first:
            updated.append(replacement)
        if index not in selected:
            updated.append(step)
    return updated


def _update_work_item_payload(work_item: dict[str, Any], work_item_id: str) -> dict[str, Any]:
    payload = {
        "id": work_item_id,
        "sectionId": work_item.get("sectionId"),
        "description": work_item.get("description"),
        "state": work_item.get("state"),
        "priority": work_item.get("priority"),
        "sourceType": work_item.get("sourceType"),
        "steps": [_step_payload(step, include_id=True) for step in work_item.get("steps", [])],
        "preconditionSteps": [
            _step_payload(step, include_id=True)
            for step in work_item.get("preconditionSteps", [])
        ],
        "postconditionSteps": [
            _step_payload(step, include_id=True)
            for step in work_item.get("postconditionSteps", [])
        ],
        "duration": work_item.get("duration"),
        "attributes": work_item.get("attributes", {}),
        "tags": work_item.get("tags", []),
        "links": work_item.get("links", []),
        "name": work_item.get("name"),
        "attachments": work_item.get("attachments", []),
    }
    if work_item.get("iterations") is not None:
        payload["iterations"] = work_item["iterations"]
    if work_item.get("autoTests") is not None:
        payload["autoTests"] = work_item["autoTests"]
    return payload


def _create_work_item_payload(arguments: dict[str, Any], *, entity_type: str, duration: int) -> dict[str, Any]:
    payload = dict(arguments)
    payload["entityTypeName"] = payload.pop("entityType", payload.get("entityTypeName", entity_type))
    payload.pop("parameters", None)
    payload.setdefault("duration", duration)
    payload.setdefault("tags", [])
    payload.setdefault("links", [])
    payload.setdefault("attributes", {})
    payload.setdefault("preconditionSteps", [])
    payload.setdefault("postconditionSteps", [])
    return payload


def _work_item_search_body(project_id: str, entity_type: str, arguments: dict[str, Any]) -> dict[str, Any]:
    body: dict[str, Any] = {
        "filter": {
            "projectIds": [project_id],
            "types": [entity_type],
            "isDeleted": arguments.get("includeDeleted", False),
        }
    }
    search = arguments.get("search")
    if search not in (None, ""):
        body["filter"]["nameOrId"] = search
    return body


def _parameter_name(parameter: Any) -> str | None:
    if not isinstance(parameter, dict):
        return None
    value = parameter.get("name") or parameter.get("key")
    return str(value) if value not in (None, "") else None


def _replace_strings(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        updated = value
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        return updated
    if isinstance(value, list):
        return [_replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace_strings(item, replacements) for key, item in value.items()}
    return value


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
        project_id = _required(arguments, "projectId")
        return self._client.search_work_items(
            project_id=project_id,
            pagination=_pagination(arguments),
            filters=_optional_filters(
                arguments,
                ["OrderBy", "SearchField", "SearchValue"],
            ),
            body=_work_item_search_body(project_id, "TestCases", arguments),
        )

    def get_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.get_entity("test_case", _required(arguments, "testCaseId"))

    def create_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.create_entity(
            "test_case",
            _create_work_item_payload(arguments, entity_type="TestCases", duration=600000),
        )

    def update_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_case_id = _required(arguments, "testCaseId")
        payload = {key: value for key, value in arguments.items() if key != "testCaseId"}
        return self._client.update_work_item(test_case_id, payload)

    def delete_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._client.delete_entity("test_case", _required(arguments, "testCaseId"))

    def get_test_case_steps(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_case_id = _required(arguments, "testCaseId")
        work_item = _work_item_entity(self._client.get_work_item(test_case_id))
        steps_key = _steps_key(work_item)
        parameters_key = _parameters_key(work_item)
        steps = work_item.get(steps_key, [])
        parameters = work_item.get(parameters_key, [])
        return {
            "testCaseId": test_case_id,
            "steps": steps,
            "parameters": parameters,
            "stepsField": steps_key,
            "parametersField": parameters_key,
        }

    def search_shared_steps(self, arguments: dict[str, Any]) -> dict[str, Any]:
        project_id = _required(arguments, "projectId")
        return self._client.search_work_items(
            project_id=project_id,
            pagination=_pagination(arguments),
            filters=_optional_filters(arguments, ["OrderBy", "SearchField", "SearchValue"]),
            body=_work_item_search_body(project_id, "SharedSteps", arguments),
        )

    def create_shared_step(self, arguments: dict[str, Any]) -> dict[str, Any]:
        project_id = _required(arguments, "projectId")
        name = _required(arguments, "name")
        steps = _required_list(arguments, "steps")
        payload = _create_work_item_payload(arguments, entity_type="SharedSteps", duration=0)
        payload["projectId"] = project_id
        payload["name"] = name
        payload["steps"] = [_step_payload(step, include_id=False) for step in steps]
        return self._client.create_shared_step(payload)

    def replace_test_case_steps_with_shared_step(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_case_id = _required(arguments, "testCaseId")
        shared_step_id = _required(arguments, "sharedStepId")
        work_item = deepcopy(_work_item_entity(self._client.get_work_item(test_case_id)))
        steps_key = _steps_key(work_item)
        steps = work_item.get(steps_key, [])
        positions = _selected_step_positions(steps, arguments)
        replacement = _shared_step_reference(shared_step_id, steps[positions[0]])
        work_item[steps_key] = _replace_positions(steps, positions, replacement)
        result = self._client.update_work_item(
            test_case_id,
            _update_work_item_payload(work_item, test_case_id),
        )
        return {
            "testCaseId": test_case_id,
            "sharedStepId": shared_step_id,
            "replacedStepIndexes": [index + 1 for index in positions],
            "entity": result.get("entity"),
        }

    def extract_shared_step_from_test_case_steps(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_case_id = _required(arguments, "testCaseId")
        project_id = _required(arguments, "projectId")
        name = _required(arguments, "name")
        work_item = deepcopy(_work_item_entity(self._client.get_work_item(test_case_id)))
        steps_key = _steps_key(work_item)
        steps = work_item.get(steps_key, [])
        positions = _selected_step_positions(steps, arguments)
        selected_steps = [_step_payload(deepcopy(steps[index]), include_id=False) for index in positions]
        create_result = self._client.create_shared_step(
            _create_work_item_payload(
                {
                    key: value
                    for key, value in arguments.items()
                    if key
                    not in {
                        "testCaseId",
                        "stepIds",
                        "stepIndexes",
                        "parameterValues",
                        "parameters",
                    }
                } | {
                    "projectId": project_id,
                    "name": name,
                    "entityTypeName": arguments.get("entityTypeName", arguments.get("entityType", "SharedSteps")),
                    "steps": selected_steps,
                },
                entity_type="SharedSteps",
                duration=0,
            )
        )
        shared_step_id = create_result.get("entityId")
        if not shared_step_id and isinstance(create_result.get("entity"), dict):
            shared_step_id = create_result["entity"].get("id")
        if not shared_step_id:
            raise UpstreamError("Created shared step response does not include an ID.", {"operation": "create_shared_step"})
        work_item[steps_key] = _replace_positions(
            steps,
            positions,
            _shared_step_reference(str(shared_step_id), steps[positions[0]]),
        )
        update_result = self._client.update_work_item(
            test_case_id,
            _update_work_item_payload(work_item, test_case_id),
        )
        return {
            "testCaseId": test_case_id,
            "sharedStepId": shared_step_id,
            "replacedStepIndexes": [index + 1 for index in positions],
            "createdSharedStep": create_result.get("entity"),
            "entity": update_result.get("entity"),
        }

    def parameterize_test_case(self, arguments: dict[str, Any]) -> dict[str, Any]:
        test_case_id = _required(arguments, "testCaseId")
        new_parameters = _required_list(arguments, "parameters")
        allow_overwrite = bool(arguments.get("allowParameterOverwrite", False))
        work_item = deepcopy(_work_item_entity(self._client.get_work_item(test_case_id)))
        parameters_key = _parameters_key(work_item)
        existing_parameters = work_item.get(parameters_key, [])
        existing_by_name = {
            name: parameter
            for parameter in existing_parameters
            if (name := _parameter_name(parameter)) is not None
        }

        merged = list(existing_parameters)
        added_or_updated = []
        for parameter in new_parameters:
            name = _parameter_name(parameter)
            if name is None:
                raise ValidationError("Each parameter must include name.", {"field": "parameters"})
            if name in existing_by_name:
                if not allow_overwrite and existing_by_name[name] != parameter:
                    raise ValidationError(
                        "Parameter already exists with a different definition.",
                        {"field": "parameters", "parameter": name},
                    )
                merged = [parameter if _parameter_name(item) == name else item for item in merged]
            else:
                merged.append(parameter)
            added_or_updated.append(name)
        work_item[parameters_key] = merged

        replacement_pairs = {}
        for replacement in arguments.get("replacements", []):
            if not isinstance(replacement, dict):
                raise ValidationError("replacements must contain objects.", {"field": "replacements"})
            literal = replacement.get("value") or replacement.get("from")
            parameter_name = replacement.get("parameterName") or replacement.get("name")
            if literal in (None, "") or parameter_name in (None, ""):
                raise ValidationError(
                    "Each replacement must include value and parameterName.",
                    {"field": "replacements"},
                )
            replacement_pairs[str(literal)] = "{{" + str(parameter_name) + "}}"
        if replacement_pairs:
            steps_key = _steps_key(work_item)
            work_item[steps_key] = _replace_strings(work_item.get(steps_key, []), replacement_pairs)

        result = self._client.update_work_item(
            test_case_id,
            _update_work_item_payload(work_item, test_case_id),
        )
        return {
            "testCaseId": test_case_id,
            "parameters": merged,
            "changedParameters": added_or_updated,
            "entity": result.get("entity"),
        }

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
