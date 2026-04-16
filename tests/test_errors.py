from __future__ import annotations

import unittest

from mcp_server.errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    UpstreamError,
    ValidationError,
    map_http_error,
)


class ErrorMappingTests(unittest.TestCase):
    def test_http_status_mapping(self) -> None:
        self.assertIsInstance(map_http_error(401, "op", "entity", "bad"), AuthenticationError)
        self.assertIsInstance(map_http_error(404, "op", "entity", "bad"), NotFoundError)
        self.assertIsInstance(map_http_error(429, "op", "entity", "bad"), RateLimitError)
        self.assertIsInstance(map_http_error(422, "op", "entity", "bad"), ValidationError)
        self.assertIsInstance(map_http_error(500, "op", "entity", "bad"), UpstreamError)
