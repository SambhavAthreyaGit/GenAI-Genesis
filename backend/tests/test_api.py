"""Tests for API routes (using FastAPI TestClient)."""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from schemas.api import ERCResult, GenerateResponse


@pytest.fixture()
def client(tmp_storage):
    """TestClient for the FastAPI app with patched settings."""
    from main import app
    return TestClient(app)


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestGenerateEndpoint:
    def test_generate_success(self, client, tmp_storage):
        mock_response = GenerateResponse(
            project_id="test-id",
            schematic_url="/files/test-id/schematic.kicad_sch",
            pcb_url="/files/test-id/board.kicad_pcb",
            erc_result=ERCResult(passed=True, messages=[], summary="OK"),
            status="completed",
        )
        with patch("routes.generate.generate", new_callable=AsyncMock, return_value=mock_response):
            resp = client.post("/generate", json={"prompt": "Simple LED circuit"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["project_id"] == "test-id"
        assert data["status"] == "completed"
        assert "schematic" in data["schematic_url"]
        assert "board" in data["pcb_url"]

    def test_generate_empty_prompt(self, client):
        resp = client.post("/generate", json={"prompt": ""})
        assert resp.status_code == 422  # Validation error

    def test_generate_missing_prompt(self, client):
        resp = client.post("/generate", json={})
        assert resp.status_code == 422

    def test_generate_orchestrator_error(self, client, tmp_storage):
        from services.orchestrator import OrchestratorError
        with patch(
            "routes.generate.generate",
            new_callable=AsyncMock,
            side_effect=OrchestratorError("LLM failed", 502),
        ):
            resp = client.post("/generate", json={"prompt": "test"})
        assert resp.status_code == 502
        assert "LLM failed" in resp.json()["detail"]


class TestProjectsEndpoint:
    def test_get_project_not_found(self, client, tmp_storage):
        resp = client.get("/projects/nonexistent")
        assert resp.status_code == 404

    def test_get_project_found(self, client, tmp_storage):
        from services.storage import StorageService
        storage = StorageService()
        storage.create_project("proj-api-1", "my prompt")
        erc = ERCResult(passed=True, messages=[], summary="OK")
        storage.save_files("proj-api-1", b"sch", b"pcb", erc_result=erc)
        resp = client.get("/projects/proj-api-1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["project_id"] == "proj-api-1"
        assert data["status"] == "completed"

    def test_download_not_found(self, client, tmp_storage):
        resp = client.get("/projects/nonexistent/download")
        assert resp.status_code == 404

    def test_download_found(self, client, tmp_storage):
        from services.storage import StorageService
        storage = StorageService()
        storage.create_project("proj-dl", "test")
        storage.save_files("proj-dl", b"schematic file data", b"pcb data")
        resp = client.get("/projects/proj-dl/download")
        assert resp.status_code == 200
        assert resp.content == b"schematic file data"


class TestFileServing:
    def test_serve_schematic(self, client, tmp_storage):
        from services.storage import StorageService
        storage = StorageService()
        storage.create_project("proj-fs", "test")
        storage.save_files("proj-fs", b"(kicad_sch test)", b"(kicad_pcb test)")
        resp = client.get("/files/proj-fs/schematic.kicad_sch")
        assert resp.status_code == 200
        assert resp.content == b"(kicad_sch test)"

    def test_serve_pcb(self, client, tmp_storage):
        from services.storage import StorageService
        storage = StorageService()
        storage.create_project("proj-fs2", "test")
        storage.save_files("proj-fs2", b"sch", b"(kicad_pcb board)")
        resp = client.get("/files/proj-fs2/board.kicad_pcb")
        assert resp.status_code == 200
        assert resp.content == b"(kicad_pcb board)"

    def test_serve_unknown_file(self, client, tmp_storage):
        from services.storage import StorageService
        storage = StorageService()
        storage.create_project("proj-fs3", "test")
        resp = client.get("/files/proj-fs3/evil.sh")
        assert resp.status_code == 404

    def test_serve_nonexistent_project(self, client, tmp_storage):
        resp = client.get("/files/nope/schematic.kicad_sch")
        assert resp.status_code == 404
