from __future__ import annotations

import unittest

from mcp_server.errors import ValidationError
from mcp_server.services import TestItService


class FakeClient:
    def __init__(self) -> None:
        self.calls = []
        self.parameters = [
            {"id": "param-existing", "name": "existing", "value": "ok"},
            {"id": "param-user", "name": "user", "value": "admin"},
            {"id": "param-password", "name": "password", "value": "secret"},
        ]

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
                "sectionId": "section-1",
                "description": "",
                "state": "NotReady",
                "priority": "Medium",
                "sourceType": "Manual",
                "duration": 600000,
                "attributes": {},
                "tags": [],
                "links": [],
                "attachments": [],
                "steps": [
                    {"id": "s1", "action": "Open login page", "expected": "", "testData": "", "comments": "", "workItemId": None},
                    {"id": "s2", "action": "Enter user", "expected": "", "testData": "", "comments": "", "workItemId": None},
                    {"id": "s3", "action": "Submit", "expected": "", "testData": "", "comments": "", "workItemId": None},
                ],
                "preconditionSteps": [],
                "postconditionSteps": [],
                "iterations": [],
            }
        }

    def update_work_item(self, work_item_id, data):
        self.calls.append(("update_work_item", work_item_id, data))
        return {"entity": data}

    def search_parameters(self, **kwargs):
        self.calls.append(("search_parameters", kwargs))
        name = kwargs["body"].get("name")
        items = [parameter for parameter in self.parameters if parameter["name"] == name]
        return {"items": items, "page": kwargs["pagination"].page, "pageSize": kwargs["pagination"].page_size, "total": len(items), "nextPage": None}

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

    def test_search_test_cases_uses_project_scoped_work_item_search(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        service.search_test_cases({"projectId": "p1", "search": "login", "pageSize": 5})
        call = client.calls[0]
        self.assertEqual(call[0], "search_work_items")
        self.assertEqual(call[1]["project_id"], "p1")
        self.assertEqual(call[1]["body"]["filter"]["projectIds"], ["p1"])
        self.assertEqual(call[1]["body"]["filter"]["types"], ["TestCases"])
        self.assertEqual(call[1]["body"]["filter"]["nameOrId"], "login")

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
        self.assertEqual(call[1]["project_id"], "p1")
        self.assertEqual(call[1]["body"]["filter"]["projectIds"], ["p1"])
        self.assertEqual(call[1]["body"]["filter"]["types"], ["SharedSteps"])
        self.assertEqual(call[1]["body"]["filter"]["nameOrId"], "login")
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
        self.assertEqual(update_call[2]["steps"][1]["id"], "s2")
        self.assertEqual(update_call[2]["steps"][1]["workItemId"], "shared-1")
        self.assertNotIn("sharedStepId", update_call[2]["steps"][1])
        self.assertNotIn("type", update_call[2]["steps"][1])
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
            {
                "testCaseId": "tc1",
                "projectId": "p1",
                "sectionId": "section-1",
                "name": "Login",
                "state": "NotReady",
                "priority": "Medium",
                "stepIds": ["s1", "s2"],
            }
        )
        self.assertEqual(result["sharedStepId"], "shared-1")
        create_call = client.calls[1]
        self.assertEqual(create_call[0], "create_shared_step")
        self.assertEqual([step["action"] for step in create_call[1]["steps"]], ["Open login page", "Enter user"])
        self.assertNotIn("id", create_call[1]["steps"][0])
        self.assertEqual(create_call[1]["sectionId"], "section-1")
        self.assertEqual(create_call[1]["state"], "NotReady")
        self.assertEqual(create_call[1]["priority"], "Medium")
        self.assertEqual(create_call[1]["entityTypeName"], "SharedSteps")
        self.assertEqual(create_call[1]["duration"], 0)
        update_call = client.calls[2]
        self.assertEqual(update_call[2]["steps"][0]["workItemId"], "shared-1")
        self.assertEqual(update_call[2]["steps"][1]["id"], "s3")

    def test_parameterize_test_case_requires_parameters_or_iterations(self) -> None:
        service = TestItService(FakeClient())
        with self.assertRaises(ValidationError):
            service.parameterize_test_case({"testCaseId": "tc1", "projectId": "p1"})

    def test_parameterize_test_case_uses_existing_parameter_and_replaces_step_text(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        result = service.parameterize_test_case(
            {
                "testCaseId": "tc1",
                "projectId": "p1",
                "parameters": [{"name": "user", "value": "admin"}],
                "replacements": [{"value": "user", "parameterName": "user"}],
            }
        )
        self.assertEqual(result["changedParameters"], ["user"])
        self.assertEqual(result["iterations"], [{"parameters": [{"id": "param-user"}]}])
        search_call = client.calls[1]
        self.assertEqual(search_call[0], "search_parameters")
        self.assertEqual(search_call[1]["body"], {"name": "user", "isDeleted": False, "projectIds": ["p1"]})
        update_call = client.calls[-1]
        self.assertEqual(update_call[2]["steps"][1]["action"], "Enter {{user}}")
        self.assertEqual(update_call[2]["iterations"], [{"parameters": [{"id": "param-user"}]}])

    def test_parameterize_test_case_builds_multiple_iterations(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        result = service.parameterize_test_case(
            {
                "testCaseId": "tc1",
                "projectId": "p1",
                "iterations": [
                    {"parameters": [{"name": "user", "value": "admin"}]},
                    {"parameters": [{"name": "password", "value": "secret"}]},
                ],
            }
        )
        self.assertEqual(
            result["iterations"],
            [
                {"parameters": [{"id": "param-user"}]},
                {"parameters": [{"id": "param-password"}]},
            ],
        )

    def test_parameterize_test_case_rejects_missing_parameter_without_update(self) -> None:
        client = FakeClient()
        service = TestItService(client)
        with self.assertRaises(ValidationError) as ctx:
            service.parameterize_test_case(
                {
                    "testCaseId": "tc1",
                    "projectId": "p1",
                    "parameters": [{"name": "user", "value": "missing"}],
                    "replacements": [{"value": "user", "parameterName": "user"}],
                }
            )
        self.assertEqual(ctx.exception.details["missingParameters"], [{"name": "user", "value": "missing"}])
        self.assertNotIn("update_work_item", [call[0] for call in client.calls])
