from __future__ import annotations

import unittest

from mcp_server.errors import ValidationError
from mcp_server.services import TestItService


class FakeClient:
    def __init__(self) -> None:
        self.calls = []

    def list_entities(self, entity, **kwargs):
        self.calls.append(("list", entity, kwargs))
        return {"items": [], "page": 1, "pageSize": 20, "total": 0, "nextPage": None}

    def list_test_suites(self, test_plan_id):
        self.calls.append(("list_test_suites", test_plan_id))
        return {"items": [], "page": 1, "pageSize": 1, "total": 0, "nextPage": None}

    def list_project_test_plans(self, project_id, include_deleted=None):
        self.calls.append(("list_test_plans", project_id, include_deleted))
        return {"items": [], "page": 1, "pageSize": 1, "total": 0, "nextPage": None}

    def list_project_test_runs(self, project_id, **kwargs):
        self.calls.append(("list_test_runs", project_id, kwargs))
        return {"items": [], "page": kwargs["pagination"].page, "pageSize": kwargs["pagination"].page_size, "total": 0, "nextPage": None}

    def search_test_results(self, **kwargs):
        self.calls.append(("list_test_results", kwargs))
        return {"items": [], "page": kwargs["pagination"].page, "pageSize": kwargs["pagination"].page_size, "total": 0, "nextPage": None}

    def get_entity(self, entity, entity_id):
        self.calls.append(("get", entity, entity_id))
        return {"entity": {"id": entity_id}}

    def create_entity(self, entity, data):
        self.calls.append(("create", entity, data))
        return {"entity": data, "entityId": "new-id"}

    def update_entity(self, entity, entity_id, data):
        self.calls.append(("update", entity, entity_id, data))
        return {"entity": data}

    def delete_entity(self, entity, entity_id):
        self.calls.append(("delete", entity, entity_id))
        return {"success": True, "entityId": entity_id}

    def search_work_items(self, **kwargs):
        self.calls.append(("search_work_items", kwargs))
        return {"items": [], "page": kwargs["pagination"].page, "pageSize": kwargs["pagination"].page_size, "total": 0, "nextPage": None}

    def get_work_item(self, work_item_id):
        self.calls.append(("get_work_item", work_item_id))
        return {
            "entity": {
                "id": work_item_id,
                "name": "Case",
                "steps": [
                    {"id": "s1", "action": "Open login page"},
                    {"id": "s2", "action": "Enter user"},
                    {"id": "s3", "action": "Submit"},
                ],
                "parameters": [{"name": "existing", "value": "ok"}],
            }
        }

    def update_work_item(self, work_item_id, data):
        self.calls.append(("update_work_item", work_item_id, data))
        return {"entity": data}

    def create_shared_step(self, data):
        self.calls.append(("create_shared_step", data))
        return {"entity": {"id": "shared-1", **data}, "entityId": "shared-1"}

    def get_shared_step_references(self, shared_step_id):
        self.calls.append(("get_shared_step_references", shared_step_id))
        return {"items": []}

    def complete_test_run(self, run_id):
        self.calls.append(("complete", run_id))
        return {"success": True}

    def link_entities(self, parent_kind, parent_id, test_case_ids):
        self.calls.append(("link", parent_kind, parent_id, test_case_ids))
        return {"success": True}

    def unlink_entities(self, parent_kind, parent_id, test_case_ids):
        self.calls.append(("unlink", parent_kind, parent_id, test_case_ids))
        return {"success": True}


class ServiceTests(unittest.TestCase):
    def test_search_test_cases_requires_project(self) -> None:
        service = TestItService(FakeClient())
        with self.assertRaises(ValidationError):
            service.search_test_cases({})

    def test_list_test_suites_requires_test_plan(self) -> None:
        service = TestItService(FakeClient())
        with self.assertRaises(ValidationError):
            service.list_test_suites({})

    def test_list_test_runs_passes_filters(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        result = service.list_test_runs({"projectId": "p1", "page": 2, "pageSize": 5, "SearchValue": "smoke"})
        self.assertEqual(result["page"], 2)
        call = client.calls[0]
        self.assertEqual(call[0], "list_test_runs")
        self.assertEqual(call[1], "p1")
        self.assertTrue(call[2]["not_started"])
        self.assertEqual(call[2]["filters"]["SearchValue"], "smoke")

    def test_list_test_results_builds_search_body(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        service.list_test_results({"projectId": "p1", "testRunId": "r1", "testCaseId": "w1"})
        call = client.calls[0]
        self.assertEqual(call[0], "list_test_results")
        self.assertEqual(call[1]["body"]["projectIds"], ["p1"])
        self.assertEqual(call[1]["body"]["testRunIds"], ["r1"])
        self.assertEqual(call[1]["body"]["workItemIds"], ["w1"])

    def test_link_requires_supported_parent_type(self) -> None:
        service = TestItService(FakeClient())
        with self.assertRaises(ValidationError):
            service.link_test_cases_to_suite_or_plan(
                {"parentType": "project", "parentId": "1", "testCaseIds": ["a"]}
            )

    def test_search_shared_steps_builds_work_item_search(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        service.search_shared_steps({"projectId": "p1", "search": "login", "pageSize": 5})
        call = client.calls[0]
        self.assertEqual(call[0], "search_work_items")
        self.assertEqual(call[1]["body"]["projectIds"], ["p1"])
        self.assertEqual(call[1]["body"]["entityTypes"], ["SharedSteps"])
        self.assertEqual(call[1]["body"]["search"], "login")
        self.assertEqual(call[1]["pagination"].page_size, 5)

    def test_replace_test_case_steps_with_shared_step_uses_one_based_indexes(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        result = service.replace_test_case_steps_with_shared_step(
            {
                "testCaseId": "tc1",
                "sharedStepId": "shared-1",
                "stepIndexes": [2, 3],
                "parameterValues": {"user": "admin"},
            }
        )
        self.assertEqual(result["replacedStepIndexes"], [2, 3])
        update_call = client.calls[-1]
        self.assertEqual(update_call[0], "update_work_item")
        self.assertEqual(update_call[2]["steps"][1]["sharedStepId"], "shared-1")
        self.assertEqual(update_call[2]["steps"][1]["parameters"]["user"], "admin")
        self.assertEqual(len(update_call[2]["steps"]), 2)

    def test_replace_test_case_steps_requires_exactly_one_selector(self) -> None:
        service = TestItService(FakeClient())
        with self.assertRaises(ValidationError):
            service.replace_test_case_steps_with_shared_step(
                {"testCaseId": "tc1", "sharedStepId": "shared-1", "stepIndexes": [1], "stepIds": ["s1"]}
            )

    def test_extract_shared_step_creates_and_replaces_steps(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        result = service.extract_shared_step_from_test_case_steps(
            {"testCaseId": "tc1", "projectId": "p1", "name": "Login", "stepIds": ["s1", "s2"]}
        )
        self.assertEqual(result["sharedStepId"], "shared-1")
        create_call = client.calls[1]
        self.assertEqual(create_call[0], "create_shared_step")
        self.assertEqual([step["id"] for step in create_call[1]["steps"]], ["s1", "s2"])
        update_call = client.calls[2]
        self.assertEqual(update_call[2]["steps"][0]["sharedStepId"], "shared-1")
        self.assertEqual(update_call[2]["steps"][1]["id"], "s3")

    def test_parameterize_test_case_rejects_conflicting_parameter(self) -> None:
        service = TestItService(FakeClient())
        with self.assertRaises(ValidationError):
            service.parameterize_test_case(
                {"testCaseId": "tc1", "parameters": [{"name": "existing", "value": "changed"}]}
            )

    def test_parameterize_test_case_merges_and_replaces_step_text(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        result = service.parameterize_test_case(
            {
                "testCaseId": "tc1",
                "parameters": [{"name": "user", "value": "admin"}],
                "replacements": [{"value": "user", "parameterName": "user"}],
            }
        )
        self.assertEqual(result["changedParameters"], ["user"])
        update_call = client.calls[-1]
        self.assertEqual(update_call[2]["parameters"][-1]["name"], "user")
        self.assertEqual(update_call[2]["steps"][1]["action"], "Enter {{user}}")
