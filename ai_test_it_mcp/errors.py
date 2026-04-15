from __future__ import annotations

from dataclasses import dataclass


class TestItMcpError(Exception):
    code = "UpstreamError"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}

    def to_payload(self) -> dict:
        payload = {"code": self.code, "message": str(self)}
        if self.details:
            payload["details"] = self.details
        return payload


class ConfigurationError(TestItMcpError):
    code = "ConfigurationError"


class AuthenticationError(TestItMcpError):
    code = "AuthenticationError"


class AuthorizationError(TestItMcpError):
    code = "AuthorizationError"


class NotFoundError(TestItMcpError):
    code = "NotFoundError"


class ValidationError(TestItMcpError):
    code = "ValidationError"


class RateLimitError(TestItMcpError):
    code = "RateLimitError"


class UpstreamError(TestItMcpError):
    code = "UpstreamError"


@dataclass(frozen=True)
class ErrorContext:
    operation: str
    entity: str
    status: int | None = None

    def details(self) -> dict:
        payload = {"operation": self.operation, "entity": self.entity}
        if self.status is not None:
            payload["status"] = self.status
        return payload


def map_http_error(status: int, operation: str, entity: str, reason: str) -> TestItMcpError:
    context = ErrorContext(operation=operation, entity=entity, status=status)
    message = f"{operation} failed for {entity}: {reason}"
    if status == 401:
        return AuthenticationError(message, context.details())
    if status == 403:
        return AuthorizationError(message, context.details())
    if status == 404:
        return NotFoundError(message, context.details())
    if status == 429:
        return RateLimitError(message, context.details())
    if 400 <= status < 500:
        return ValidationError(message, context.details())
    return UpstreamError(message, context.details())
