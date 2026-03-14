# GenAI-Genesis

Web app: natural language circuit description → KiCad schematic and placed PCB (view in KiCanvas, run ERC, optional download).

## Backend

- **API:** FastAPI (`POST /generate`, `GET /projects/{id}`, `GET /files/{project_id}/{filename}`).
- **Run:** From repo root or from `backend/`:
  ```bash
  cd backend
  python -m venv .venv && .venv/bin/pip install -r requirements.txt
  ANTHROPIC_API_KEY=your_key .venv/bin/uvicorn main:app --reload
  ```
- **Env:** `ANTHROPIC_API_KEY` (required for generation), `STORAGE_PATH` (default `storage`), `SANDBOX_IMAGE` (default `genai-genesis-sandbox:latest`). Build the sandbox image from `sandbox/` with `docker build -t genai-genesis-sandbox:latest .`.
