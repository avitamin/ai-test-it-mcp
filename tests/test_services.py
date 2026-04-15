from __future__ import annotations

import unittest

from ai_test_it_mcp.errors import ValidationError
from ai_test_it_mcp.services import TestItService


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
