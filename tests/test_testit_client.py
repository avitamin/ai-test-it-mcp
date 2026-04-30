from __future__ import annotations

import unittest
from unittest.mock import patch

from mcp_server.config import Settings
from mcp_server.testit_client import TestItClient


class FakeResponse:
    headers = {"Content-Type": "application/json"}

    def __init__(self, body: bytes = b"{}") -> None:
        self._body = body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class TestItClientTests(unittest.TestCase):
    def test_request_uses_private_token_authorization_by_default(self) -> None:
        settings = Settings(base_url="https://demo.testit.software", token="secret")
        client = TestItClient(settings)

        with patch("urllib.request.urlopen", return_value=FakeResponse()) as urlopen:
            client._request("GET", "/api/v2/projects", operation="list", entity="projects")

        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "PrivateToken secret")

    def test_request_uses_bearer_authorization(self) -> None:
        settings = Settings(
            base_url="https://demo.testit.software",
            token="secret",
            auth_type="bearer",
        )
        client = TestItClient(settings)

        with patch("urllib.request.urlopen", return_value=FakeResponse()) as urlopen:
            client._request("GET", "/api/v2/projects", operation="list", entity="projects")

        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")

    def test_search_work_items_posts_project_scoped_body_and_pagination(self) -> None:
        settings = Settings(base_url="https://demo.testit.software", token="secret")
        client = TestItClient(settings)

        with patch("urllib.request.urlopen", return_value=FakeResponse(b'{"items": [], "total": 0}')) as urlopen:
            result = client.search_work_items(project_id="p1", body={"filter": {"types": ["TestCases"]}})

        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.full_url, "https://demo.testit.software/api/v2/projects/p1/workItems/search?Skip=0&Take=20")
        self.assertEqual(request.data, b'{"filter": {"types": ["TestCases"]}}')
        self.assertEqual(result["items"], [])

    def test_search_parameters_posts_body_and_pagination(self) -> None:
        settings = Settings(base_url="https://demo.testit.software", token="secret")
        client = TestItClient(settings)

        with patch("urllib.request.urlopen", return_value=FakeResponse(b'{"items": [], "total": 0}')) as urlopen:
            result = client.search_parameters(body={"name": "user", "isDeleted": False, "projectIds": ["p1"]})

        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.full_url, "https://demo.testit.software/api/v2/parameters/search?Skip=0&Take=20")
        self.assertEqual(request.data, b'{"name": "user", "isDeleted": false, "projectIds": ["p1"]}')
        self.assertEqual(result["items"], [])

    def test_create_shared_step_posts_work_item(self) -> None:
        settings = Settings(base_url="https://demo.testit.software", token="secret")
        client = TestItClient(settings)

        with patch("urllib.request.urlopen", return_value=FakeResponse(b'{"id": "shared-1"}')) as urlopen:
            result = client.create_shared_step({"projectId": "p1", "name": "Login"})

        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.full_url, "https://demo.testit.software/api/v2/workItems")
        self.assertEqual(result["entityId"], "shared-1")

    def test_update_work_item_uses_work_item_route(self) -> None:
        settings = Settings(base_url="https://demo.testit.software", token="secret")
        client = TestItClient(settings)

        with patch("urllib.request.urlopen", return_value=FakeResponse(b'{"id": "tc1"}')) as urlopen:
            client.update_work_item("tc1", {"name": "Case"})

        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "PUT")
        self.assertEqual(request.full_url, "https://demo.testit.software/api/v2/workItems")
        self.assertEqual(request.data, b'{"name": "Case", "id": "tc1"}')
