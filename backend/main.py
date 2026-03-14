"""GenAI-Genesis backend: FastAPI app, CORS, routes, file serving."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from config import get_settings
from routes import api_router
from services.storage import StorageService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure storage directory and DB exist on startup."""
    settings = get_settings()
    settings.storage_dir().mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="GenAI-Genesis API",
    description="Generate KiCad schematic and PCB from natural language",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/files/{project_id}/{filename:path}")
async def serve_file(project_id: str, filename: str):
    """Serve generated schematic or board file for KiCanvas."""
    storage = StorageService()
    project_dir = storage.project_dir(project_id)
    if not project_dir.exists():
        return JSONResponse(content={"detail": "Project not found"}, status_code=404)
    # Restrict to known filenames
    if filename not in ("schematic.kicad_sch", "board.kicad_pcb"):
        return JSONResponse(content={"detail": "Not found"}, status_code=404)
    path = project_dir / filename
    if not path.is_file():
        return JSONResponse(content={"detail": "File not found"}, status_code=404)
    media_type = "text/plain; charset=utf-8"
    return FileResponse(path=path, filename=filename, media_type=media_type)


@app.get("/health")
async def health():
    return {"status": "ok"}
