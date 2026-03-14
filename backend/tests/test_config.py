"""Tests for config.py."""

import os
from unittest.mock import patch

from config import Settings, get_settings


class TestSettings:
    def test_defaults(self):
        s = Settings()
        assert s.anthropic_model == "claude-3-5-sonnet-20241022"
        assert s.sandbox_timeout_seconds == 120
        assert s.storage_path == "storage"

    def test_from_env(self):
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "sk-test-123",
            "STORAGE_PATH": "/tmp/my_storage",
            "SANDBOX_TIMEOUT_SECONDS": "60",
        }):
            s = Settings()
            assert s.anthropic_api_key == "sk-test-123"
            assert s.storage_path == "/tmp/my_storage"
            assert s.sandbox_timeout_seconds == 60

    def test_storage_dir_resolves(self):
        s = Settings(storage_path="storage")
        d = s.storage_dir()
        assert d.is_absolute()
        assert str(d).endswith("storage")


class TestGetSettings:
    def test_returns_settings(self):
        s = get_settings()
        assert isinstance(s, Settings)

    def test_cached(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
