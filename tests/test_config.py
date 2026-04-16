from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from mcp_server.config import Settings
from mcp_server.errors import ConfigurationError


class SettingsTests(unittest.TestCase):
    def test_reads_required_values_and_defaults(self) -> None:
        env = {
            "TESTIT_BASE_URL": "https://demo.testit.software/",
            "TESTIT_TOKEN": "secret",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings.from_env()
        self.assertEqual(settings.base_url, "https://demo.testit.software")
        self.assertEqual(settings.token, "secret")
        self.assertEqual(settings.timeout_seconds, 30)
        self.assertTrue(settings.verify_ssl)
        self.assertEqual(settings.log_level, "INFO")

    def test_missing_required_values_raise(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_env()

    def test_invalid_bool_raises(self) -> None:
        env = {
            "TESTIT_BASE_URL": "https://demo.testit.software",
            "TESTIT_TOKEN": "secret",
            "TESTIT_VERIFY_SSL": "maybe",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_env()
