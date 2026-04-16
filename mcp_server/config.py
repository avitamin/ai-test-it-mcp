from __future__ import annotations

import os
from dataclasses import dataclass

from .errors import ConfigurationError


def _read_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(
        f"Invalid boolean value for {name}: {raw!r}. Use true/false."
    )


def _read_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(
            f"Invalid integer value for {name}: {raw!r}."
        ) from exc


@dataclass(frozen=True)
class Settings:
    base_url: str
    token: str
    timeout_seconds: int = 30
    verify_ssl: bool = True
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        base_url = os.getenv("TESTIT_BASE_URL", "").strip()
        token = os.getenv("TESTIT_TOKEN", "").strip()
        if not base_url:
            raise ConfigurationError("TESTIT_BASE_URL is required.")
        if not token:
            raise ConfigurationError("TESTIT_TOKEN is required.")

        return cls(
            base_url=base_url.rstrip("/"),
            token=token,
            timeout_seconds=_read_int("TESTIT_TIMEOUT_SECONDS", 30),
            verify_ssl=_read_bool("TESTIT_VERIFY_SSL", True),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO",
        )
