from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from .config import Settings
from .errors import ConfigurationError, UpstreamError, map_http_error
from .models import PaginationInput, paginated_from_upstream


def _append_query(path: str, query: dict[str, Any] | None) -> str:
    if not query:
        return path
    filtered = {
        key: value
        for key, value in query.items()
        if value is not None and value != ""
    }
    if not filtered:
        return path
    return f"{path}?{urllib.parse.urlencode(filtered, doseq=True)}"


@dataclass(frozen=True)
class EntityRoute:
    singular: str
    plural: str


class TestItClient:
    ROUTES = {
        "project": EntityRoute("project", "projects"),
        "test_suite": EntityRoute("testSuite", "testSuites"),
        "test_plan": EntityRoute("testPlan", "testPlans"),
        "test_case": EntityRoute("workItem", "workItems"),
        "test_run": EntityRoute("testRun", "testRuns"),
        "test_result": EntityRoute("testResult", "testResults"),
    }

    def __init__(self, settings: Settings):
        self._settings = settings
        self._ssl_context = None
        if not settings.verify_ssl:
            self._ssl_context = ssl._create_unverified_context()

    def _authorization_header(self) -> str:
        if self._settings.auth_type == "private_token":
            return f"PrivateToken {self._settings.token}"
        return f"Bearer {self._settings.token}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        operation: str,
        entity: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self._settings.base_url}{_append_query(path, query)}"
        payload = None
        headers = {
            "Accept": "application/json",
            "Authorization": self._authorization_header(),
        }
        if body is not None:
            payload = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url=url,
            data=payload,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=self._settings.timeout_seconds,
                context=self._ssl_context,
            ) as response:
                raw = response.read()
                if not raw:
                    return None
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return json.loads(raw.decode("utf-8"))
                return raw.decode("utf-8")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            reason = raw.strip() or exc.reason or f"HTTP {exc.code}"
            raise map_http_error(exc.code, operation, entity, reason) from exc
        except urllib.error.URLError as exc:
            raise UpstreamError(
                f"{operation} failed for {entity}: {exc.reason}",
                {"operation": operation, "entity": entity},
            ) from exc

    def _entity_route(self, entity: str) -> EntityRoute:
        try:
            return self.ROUTES[entity]
        except KeyError as exc:
            raise ConfigurationError(f"Unsupported entity route: {entity}") from exc

    def list_entities(
        self,
        entity: str,
        *,
        project_id: str | None = None,
        pagination: PaginationInput | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        route = self._entity_route(entity)
        resolved_pagination = pagination or PaginationInput()
        query: dict[str, Any] = resolved_pagination.to_query()
        if filters:
            query.update(filters)
        path = f"/api/v2/{route.plural}"
        if project_id:
            query["projectId"] = project_id
        payload = self._request(
            "GET",
            path,
            operation=f"list_{route.plural}",
            entity=route.plural,
            query=query,
        )
        items, total = self._extract_items(payload)
        return paginated_from_upstream(
            items,
            resolved_pagination.page,
            resolved_pagination.page_size,
            total,
        )

    def list_test_suites(self, test_plan_id: str) -> dict[str, Any]:
        payload = self._request(
            "GET",
            f"/api/v2/testPlans/{test_plan_id}/testSuites",
            operation="list_test_suites",
            entity="testSuites",
        )
        items, total = self._extract_items(payload)
        return paginated_from_upstream(items, 1, len(items) or 1, total)

    def list_project_test_plans(
        self,
        project_id: str,
        *,
        include_deleted: bool | None = None,
    ) -> dict[str, Any]:
        payload = self._request(
            "GET",
            f"/api/v2/projects/{project_id}/testPlans",
            operation="list_test_plans",
            entity="testPlans",
            query={"isDeleted": include_deleted},
        )
        items, total = self._extract_items(payload)
        return paginated_from_upstream(items, 1, len(items) or 1, total)

    def list_project_test_runs(
        self,
        project_id: str,
        *,
        not_started: bool,
        in_progress: bool,
        stopped: bool,
        completed: bool,
        test_plan_id: str | None = None,
        created_date_from: str | None = None,
        created_date_to: str | None = None,
        pagination: PaginationInput | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resolved_pagination = pagination or PaginationInput()
        query = {
            "notStarted": not_started,
            "inProgress": in_progress,
            "stopped": stopped,
            "completed": completed,
            "testPlanId": test_plan_id,
            "createdDateFrom": created_date_from,
            "createdDateTo": created_date_to,
            "Skip": (resolved_pagination.page - 1) * resolved_pagination.page_size,
            "Take": resolved_pagination.page_size,
        }
        if filters:
            query.update(filters)
        payload = self._request(
            "GET",
            f"/api/v2/projects/{project_id}/testRuns",
            operation="list_test_runs",
            entity="testRuns",
            query=query,
        )
        items, total = self._extract_items(payload)
        return paginated_from_upstream(
            items,
            resolved_pagination.page,
            resolved_pagination.page_size,
            total,
        )

    def search_test_results(
        self,
        *,
        pagination: PaginationInput | None = None,
        filters: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resolved_pagination = pagination or PaginationInput()
        query = {
            "Skip": (resolved_pagination.page - 1) * resolved_pagination.page_size,
            "Take": resolved_pagination.page_size,
        }
        if filters:
            query.update(filters)
        payload = self._request(
            "POST",
            "/api/v2/testResults/search",
            operation="list_test_results",
            entity="testResults",
            query=query,
            body=body or {},
        )
        items, total = self._extract_items(payload)
        return paginated_from_upstream(
            items,
            resolved_pagination.page,
            resolved_pagination.page_size,
            total,
        )

    def search_work_items(
        self,
        *,
        pagination: PaginationInput | None = None,
        filters: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resolved_pagination = pagination or PaginationInput()
        query = {
            "Skip": (resolved_pagination.page - 1) * resolved_pagination.page_size,
            "Take": resolved_pagination.page_size,
        }
        if filters:
            query.update(filters)
        payload = self._request(
            "POST",
            "/api/v2/workItems/search",
            operation="search_work_items",
            entity="workItems",
            query=query,
            body=body or {},
        )
        items, total = self._extract_items(payload)
        return paginated_from_upstream(
            items,
            resolved_pagination.page,
            resolved_pagination.page_size,
            total,
        )

    def get_entity(self, entity: str, entity_id: str) -> dict[str, Any]:
        route = self._entity_route(entity)
        payload = self._request(
            "GET",
            f"/api/v2/{route.plural}/{entity_id}",
            operation=f"get_{route.singular}",
            entity=route.singular,
        )
        return {"entity": payload}

    def get_work_item(self, work_item_id: str) -> dict[str, Any]:
        return self.get_entity("test_case", work_item_id)

    def create_entity(self, entity: str, data: dict[str, Any]) -> dict[str, Any]:
        route = self._entity_route(entity)
        payload = self._request(
            "POST",
            f"/api/v2/{route.plural}",
            operation=f"create_{route.singular}",
            entity=route.singular,
            body=data,
        )
        created_id = payload.get("id") if isinstance(payload, dict) else None
        return {"entity": payload, "entityId": created_id}

    def update_entity(self, entity: str, entity_id: str, data: dict[str, Any]) -> dict[str, Any]:
        route = self._entity_route(entity)
        payload = self._request(
            "PUT",
            f"/api/v2/{route.plural}/{entity_id}",
            operation=f"update_{route.singular}",
            entity=route.singular,
            body=data,
        )
        return {"entity": payload}

    def update_work_item(self, work_item_id: str, data: dict[str, Any]) -> dict[str, Any]:
        payload = dict(data)
        payload.setdefault("id", work_item_id)
        updated = self._request(
            "PUT",
            "/api/v2/workItems",
            operation="update_work_item",
            entity="workItem",
            body=payload,
        )
        return {"entity": updated}

    def create_shared_step(self, data: dict[str, Any]) -> dict[str, Any]:
        payload = self._request(
            "POST",
            "/api/v2/workItems",
            operation="create_shared_step",
            entity="workItem",
            body=data,
        )
        created_id = payload.get("id") if isinstance(payload, dict) else None
        return {"entity": payload, "entityId": created_id}

    def get_shared_step_references(self, shared_step_id: str) -> dict[str, Any]:
        payload = self._request(
            "GET",
            f"/api/v2/workItems/sharedSteps/{shared_step_id}/references",
            operation="get_shared_step_references",
            entity="workItems",
        )
        return {"items": payload if isinstance(payload, list) else payload}

    def delete_entity(self, entity: str, entity_id: str) -> dict[str, Any]:
        route = self._entity_route(entity)
        self._request(
            "DELETE",
            f"/api/v2/{route.plural}/{entity_id}",
            operation=f"delete_{route.singular}",
            entity=route.singular,
        )
        return {"success": True, "entityId": entity_id}

    def complete_test_run(self, run_id: str) -> dict[str, Any]:
        payload = self._request(
            "POST",
            f"/api/v2/testRuns/{run_id}/complete",
            operation="complete_test_run",
            entity="testRun",
        )
        return {"success": True, "entity": payload}

    def link_entities(
        self,
        parent_kind: str,
        parent_id: str,
        test_case_ids: list[str],
    ) -> dict[str, Any]:
        route = self._entity_route(parent_kind)
        payload = self._request(
            "POST",
            f"/api/v2/{route.plural}/{parent_id}/workItems",
            operation=f"link_test_cases_to_{route.singular}",
            entity=route.singular,
            body={"workItemIds": test_case_ids},
        )
        return {"success": True, "entity": payload}

    def unlink_entities(
        self,
        parent_kind: str,
        parent_id: str,
        test_case_ids: list[str],
    ) -> dict[str, Any]:
        route = self._entity_route(parent_kind)
        payload = self._request(
            "DELETE",
            f"/api/v2/{route.plural}/{parent_id}/workItems",
            operation=f"unlink_test_cases_from_{route.singular}",
            entity=route.singular,
            body={"workItemIds": test_case_ids},
        )
        return {"success": True, "entity": payload}

    @staticmethod
    def _extract_items(payload: Any) -> tuple[list[dict[str, Any]], int | None]:
        if isinstance(payload, list):
            return payload, len(payload)
        if isinstance(payload, dict):
            for items_key in ("items", "results", "data"):
                items = payload.get(items_key)
                if isinstance(items, list):
                    total = payload.get("total") or payload.get("totalCount")
                    return items, total
        raise UpstreamError("Unexpected list response format from Test IT.", {"payloadType": type(payload).__name__})
