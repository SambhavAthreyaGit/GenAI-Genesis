"""GET /projects/{project_id} and GET /projects/{project_id}/download."""

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse

from services.orchestrator import get_project
from services.storage import StorageService

router = APIRouter()


@router.get("/{project_id}")
async def get_project_by_id(project_id: str, request: Request):
    """Return project metadata, schematic URL, PCB URL, ERC result."""
    base = str(request.base_url).rstrip("/")
    data = get_project(project_id, base_url=base)
    if data is None:
        return JSONResponse(content={"detail": "Project not found"}, status_code=404)
    return data


@router.get("/{project_id}/download")
async def download_project(project_id: str):
    """Return schematic and PCB as a zip (or redirect to file URLs)."""
    storage = StorageService()
    proj = storage.get_project(project_id)
    if not proj:
        return JSONResponse(content={"detail": "Project not found"}, status_code=404)
    schematic_path = storage.get_schematic_path(project_id)
    pcb_path = storage.get_pcb_path(project_id)
    if not schematic_path or not schematic_path.exists():
        return JSONResponse(
            content={"detail": "Project files not ready or missing"},
            status_code=404,
        )
    # For MVP: return first file (schematic) as single download; frontend can offer both links
    # Optional: use zipfile to create an in-memory zip and return StreamingResponse
    return FileResponse(
        path=schematic_path,
        filename=f"{project_id}_schematic.kicad_sch",
        media_type="application/octet-stream",
    )
