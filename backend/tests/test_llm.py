"""Tests for LLMService (mocked Anthropic API)."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from schemas.circuit_spec import CircuitSpec
from services.llm import LLMService, SYSTEM_PROMPT


def _mock_anthropic_response(text: str) -> MagicMock:
    """Build a mock Anthropic messages.create() response."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


class TestLLMService:
    def test_missing_api_key_raises(self, tmp_storage):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            from config import get_settings
            get_settings.cache_clear()
            svc = LLMService()
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                svc.get_spec("test")

    def test_get_spec_valid_json(self, tmp_storage):
        spec_dict = {
            "components": [{"ref": "R1", "value": "10k"}],
            "nets": [{"name": "VCC", "connections": [{"ref": "R1", "pin": "1"}]}],
        }
        mock_resp = _mock_anthropic_response(json.dumps(spec_dict))
        svc = LLMService()
        with patch.object(svc, "_get_client") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_resp
            result = svc.get_spec("Simple resistor circuit")
        assert isinstance(result, CircuitSpec)
        assert len(result.components) == 1
        assert result.components[0].ref == "R1"
        assert len(result.nets) == 1

    def test_get_spec_strips_markdown_fences(self, tmp_storage):
        spec_dict = {"components": [{"ref": "C1", "value": "100nF"}], "nets": []}
        raw = f"```json\n{json.dumps(spec_dict)}\n```"
        mock_resp = _mock_anthropic_response(raw)
        svc = LLMService()
        with patch.object(svc, "_get_client") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_resp
            result = svc.get_spec("Capacitor")
        assert result.components[0].ref == "C1"

    def test_get_spec_invalid_json_raises(self, tmp_storage):
        mock_resp = _mock_anthropic_response("this is not json")
        svc = LLMService()
        with patch.object(svc, "_get_client") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_resp
            with pytest.raises(json.JSONDecodeError):
                svc.get_spec("bad response")

    def test_get_spec_empty_response_raises(self, tmp_storage):
        response = MagicMock()
        response.content = []
        svc = LLMService()
        with patch.object(svc, "_get_client") as mock_client:
            mock_client.return_value.messages.create.return_value = response
            with pytest.raises(Exception):
                svc.get_spec("empty")

    def test_system_prompt_contains_schema(self):
        assert "components" in SYSTEM_PROMPT
        assert "nets" in SYSTEM_PROMPT
        assert "ref" in SYSTEM_PROMPT
        assert "footprint" in SYSTEM_PROMPT
