"""Tests for StorageService."""

import json

import pytest

from schemas.api import ERCResult
from services.storage import StorageService, generate_project_id


class TestGenerateProjectId:
    def test_returns_uuid_string(self):
        pid = generate_project_id()
        assert isinstance(pid, str)
        assert len(pid) == 36  # UUID format

    def test_unique(self):
        ids = {generate_project_id() for _ in range(100)}
        assert len(ids) == 100


class TestStorageService:
    def test_create_project(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-1", "test prompt")
        proj = storage.get_project("proj-1")
        assert proj is not None
        assert proj["project_id"] == "proj-1"
        assert proj["prompt"] == "test prompt"
        assert proj["status"] == "pending"
        assert proj["created_at"] is not None

    def test_create_project_creates_dir(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-2", "test")
        assert storage.project_dir("proj-2").is_dir()

    def test_get_nonexistent_project(self, tmp_storage):
        storage = StorageService()
        assert storage.get_project("nope") is None

    def test_save_files(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-3", "test")
        erc = ERCResult(passed=True, messages=[], summary="ERC passed.")
        storage.save_files("proj-3", b"schematic data", b"pcb data", erc_result=erc)

        proj = storage.get_project("proj-3")
        assert proj["status"] == "completed"
        assert proj["erc_passed"] == 1
        assert proj["erc_summary"] == "ERC passed."

        d = storage.project_dir("proj-3")
        assert (d / "schematic.kicad_sch").read_bytes() == b"schematic data"
        assert (d / "board.kicad_pcb").read_bytes() == b"pcb data"
        assert (d / "erc_result.json").exists()

    def test_save_files_without_erc(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-4", "test")
        storage.save_files("proj-4", b"sch", b"pcb", erc_result=None)
        proj = storage.get_project("proj-4")
        assert proj["status"] == "completed"
        assert proj["erc_passed"] == 0

    def test_mark_failed(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-5", "test")
        storage.mark_failed("proj-5")
        proj = storage.get_project("proj-5")
        assert proj["status"] == "failed"

    def test_get_schematic_path(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-6", "test")
        assert storage.get_schematic_path("proj-6") is None
        storage.save_files("proj-6", b"sch", b"pcb")
        path = storage.get_schematic_path("proj-6")
        assert path is not None
        assert path.name == "schematic.kicad_sch"

    def test_get_pcb_path(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-7", "test")
        storage.save_files("proj-7", b"sch", b"pcb")
        path = storage.get_pcb_path("proj-7")
        assert path is not None
        assert path.name == "board.kicad_pcb"

    def test_get_erc_result(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-8", "test")
        erc = ERCResult(passed=False, messages=["err1"], summary="Failed")
        storage.save_files("proj-8", b"sch", b"pcb", erc_result=erc)
        result = storage.get_erc_result("proj-8")
        assert result is not None
        assert result.passed is False
        assert result.messages == ["err1"]

    def test_get_erc_result_missing(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-9", "test")
        storage.save_files("proj-9", b"sch", b"pcb")
        assert storage.get_erc_result("proj-9") is None

    def test_build_file_url(self, tmp_storage):
        storage = StorageService()
        url = storage.build_file_url("proj-10", "schematic.kicad_sch")
        assert url == "/files/proj-10/schematic.kicad_sch"

    def test_get_project_response(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-11", "hello")
        erc = ERCResult(passed=True, messages=[], summary="OK")
        storage.save_files("proj-11", b"sch", b"pcb", erc_result=erc)
        resp = storage.get_project_response("proj-11", base_url="http://localhost:8000")
        assert resp["project_id"] == "proj-11"
        assert resp["prompt"] == "hello"
        assert resp["status"] == "completed"
        assert "schematic.kicad_sch" in resp["schematic_url"]
        assert "board.kicad_pcb" in resp["pcb_url"]
        assert resp["erc_result"]["passed"] is True

    def test_get_project_response_not_found(self, tmp_storage):
        storage = StorageService()
        assert storage.get_project_response("nope") is None

    def test_get_project_response_pending(self, tmp_storage):
        storage = StorageService()
        storage.create_project("proj-12", "pending test")
        resp = storage.get_project_response("proj-12")
        assert resp["status"] == "pending"
        assert resp["schematic_url"] == ""
        assert resp["pcb_url"] == ""
