from __future__ import annotations

import unittest
from unittest.mock import patch

from mcp_server.config import Settings
from mcp_server.testit_client import TestItClient


class FakeResponse:
    headers = {"Content-Type": "application/json"}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def read(self) -> bytes:
        return b"{}"


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
