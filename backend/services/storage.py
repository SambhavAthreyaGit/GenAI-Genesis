"""Persist generated files and project metadata; expose stable URLs."""

import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

from config import get_settings
from schemas.api import ERCResult


class StorageService:
    """File storage (MVP: local) + SQLite metadata."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._root = self.settings.storage_dir()
        self._root.mkdir(parents=True, exist_ok=True)
        self._db_path = self._root / "projects.db"
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    prompt TEXT,
                    status TEXT NOT NULL,
                    schematic_path TEXT,
                    pcb_path TEXT,
                    erc_passed INTEGER,
                    erc_summary TEXT,
                    erc_messages TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def project_dir(self, project_id: str) -> Path:
        return self._root / project_id

    def create_project(self, project_id: str, prompt: str) -> None:
        """Create project record (status pending) and directory."""
        dir_path = self.project_dir(project_id)
        dir_path.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO projects (project_id, prompt, status, created_at)
                VALUES (?, ?, 'pending', ?)
                """,
                (project_id, prompt, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

    def save_files(
        self,
        project_id: str,
        schematic_content: bytes,
        pcb_content: bytes,
        erc_result: ERCResult | None = None,
    ) -> None:
        """Write schematic and PCB files under project dir; update metadata."""
        d = self.project_dir(project_id)
        d.mkdir(parents=True, exist_ok=True)
        (d / "schematic.kicad_sch").write_bytes(schematic_content)
        (d / "board.kicad_pcb").write_bytes(pcb_content)
        if erc_result is not None:
            (d / "erc_result.json").write_text(
                erc_result.model_dump_json(indent=2),
                encoding="utf-8",
            )
        erc_passed = 1 if (erc_result and erc_result.passed) else 0
        erc_summary = erc_result.summary if erc_result else None
        erc_messages = json.dumps(erc_result.messages) if erc_result else None
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE projects
                SET status = 'completed',
                    schematic_path = ?,
                    pcb_path = ?,
                    erc_passed = ?,
                    erc_summary = ?,
                    erc_messages = ?
                WHERE project_id = ?
                """,
                (
                    str(d / "schematic.kicad_sch"),
                    str(d / "board.kicad_pcb"),
                    erc_passed,
                    erc_summary,
                    erc_messages,
                    project_id,
                ),
            )
            conn.commit()

    def mark_failed(self, project_id: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE projects SET status = 'failed' WHERE project_id = ?",
                (project_id,),
            )
            conn.commit()

    def get_project(self, project_id: str) -> dict | None:
        """Return project row as dict or None."""
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def get_schematic_path(self, project_id: str) -> Path | None:
        proj = self.get_project(project_id)
        if not proj or not proj.get("schematic_path"):
            return None
        return Path(proj["schematic_path"])

    def get_pcb_path(self, project_id: str) -> Path | None:
        proj = self.get_project(project_id)
        if not proj or not proj.get("pcb_path"):
            return None
        return Path(proj["pcb_path"])

    def get_erc_result(self, project_id: str) -> ERCResult | None:
        p = self.project_dir(project_id) / "erc_result.json"
        if not p.exists():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        return ERCResult.model_validate(data)

    def build_file_url(self, project_id: str, filename: str) -> str:
        """Build URL for file serving (e.g. /files/{project_id}/schematic.kicad_sch)."""
        return f"/files/{project_id}/{filename}"

    def get_project_response(self, project_id: str, base_url: str = "") -> dict | None:
        """Build API response dict for a project (for GET /projects/{id})."""
        proj = self.get_project(project_id)
        if not proj:
            return None
        prefix = base_url.rstrip("/") if base_url else ""
        schematic_url = proj.get("schematic_path") and (
            f"{prefix}/files/{project_id}/schematic.kicad_sch"
        )
        pcb_url = proj.get("pcb_path") and (
            f"{prefix}/files/{project_id}/board.kicad_pcb"
        )
        erc = self.get_erc_result(project_id)
        return {
            "project_id": project_id,
            "prompt": proj.get("prompt"),
            "schematic_url": schematic_url or "",
            "pcb_url": pcb_url or "",
            "erc_result": erc.model_dump() if erc else None,
            "status": proj["status"],
            "created_at": proj.get("created_at"),
        }


def generate_project_id() -> str:
    return str(uuid.uuid4())
