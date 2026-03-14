"""Tests for the orchestrator pipeline (mocked services)."""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from schemas.api import ERCResult, GenerateResponse
from schemas.circuit_spec import CircuitSpec, Component, Net, NetSegment
from services.orchestrator import generate, get_project, OrchestratorError, run_generate
from services.spec_validator import SpecValidationError


def _sample_spec():
    return CircuitSpec(
        components=[Component(ref="R1", value="10k")],
        nets=[],
    )


def _sample_erc():
    return ERCResult(passed=True, messages=[], summary="ERC passed.")


class TestOrchestrator:
    @pytest.mark.asyncio
    async def test_full_pipeline_success(self, tmp_storage):
        spec = _sample_spec()
        erc = _sample_erc()
        with patch("services.orchestrator.LLMService") as MockLLM, \
             patch("services.orchestrator.SpecValidator") as MockValidator, \
             patch("services.orchestrator.SandboxRunner") as MockRunner:
            MockLLM.return_value.get_spec.return_value = spec
            MockValidator.return_value.validate.return_value = spec
            MockRunner.return_value.run = AsyncMock(
                return_value=(b"sch_content", b"pcb_content", erc)
            )
            result = await generate("test prompt")

        assert isinstance(result, GenerateResponse)
        assert result.status == "completed"
        assert result.project_id
        assert "/schematic.kicad_sch" in result.schematic_url
        assert "/board.kicad_pcb" in result.pcb_url
        assert result.erc_result is not None
        assert result.erc_result.passed is True

    @pytest.mark.asyncio
    async def test_llm_value_error_raises_400(self, tmp_storage):
        with patch("services.orchestrator.LLMService") as MockLLM:
            MockLLM.return_value.get_spec.side_effect = ValueError("API key missing")
            with pytest.raises(OrchestratorError) as exc_info:
                await generate("test")
            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_llm_generic_error_raises_502(self, tmp_storage):
        with patch("services.orchestrator.LLMService") as MockLLM:
            MockLLM.return_value.get_spec.side_effect = RuntimeError("API down")
            with pytest.raises(OrchestratorError) as exc_info:
                await generate("test")
            assert exc_info.value.status_code == 502
            assert "LLM failed" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_validation_error_raises_400(self, tmp_storage):
        spec = _sample_spec()
        with patch("services.orchestrator.LLMService") as MockLLM, \
             patch("services.orchestrator.SpecValidator") as MockValidator:
            MockLLM.return_value.get_spec.return_value = spec
            MockValidator.return_value.validate.side_effect = SpecValidationError("bad spec")
            with pytest.raises(OrchestratorError) as exc_info:
                await generate("test")
            assert exc_info.value.status_code == 400
            assert "Invalid spec" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_sandbox_runtime_error_raises_502(self, tmp_storage):
        spec = _sample_spec()
        with patch("services.orchestrator.LLMService") as MockLLM, \
             patch("services.orchestrator.SpecValidator") as MockValidator, \
             patch("services.orchestrator.SandboxRunner") as MockRunner:
            MockLLM.return_value.get_spec.return_value = spec
            MockValidator.return_value.validate.return_value = spec
            MockRunner.return_value.run = AsyncMock(
                side_effect=RuntimeError("Docker not found")
            )
            with pytest.raises(OrchestratorError) as exc_info:
                await generate("test")
            assert exc_info.value.status_code == 502
            assert "Sandbox failed" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_project_marked_failed_on_error(self, tmp_storage):
        """When LLM fails, the project should be marked as failed in storage."""
        from services.storage import StorageService
        with patch("services.orchestrator.LLMService") as MockLLM:
            MockLLM.return_value.get_spec.side_effect = RuntimeError("boom")
            with pytest.raises(OrchestratorError):
                await generate("test")
        # All projects in storage should be failed
        storage = StorageService()
        import sqlite3
        conn = sqlite3.connect(storage._db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM projects").fetchall()
        assert len(rows) == 1
        assert dict(rows[0])["status"] == "failed"
        conn.close()


class TestGetProject:
    def test_existing_project(self, tmp_storage):
        from services.storage import StorageService
        storage = StorageService()
        storage.create_project("test-proj", "my prompt")
        erc = ERCResult(passed=True, messages=[], summary="OK")
        storage.save_files("test-proj", b"sch", b"pcb", erc_result=erc)
        result = get_project("test-proj", base_url="http://localhost:8000")
        assert result is not None
        assert result["project_id"] == "test-proj"
        assert result["status"] == "completed"

    def test_nonexistent_project(self, tmp_storage):
        result = get_project("does-not-exist")
        assert result is None
