"""POST /generate: natural language prompt -> project with schematic and PCB URLs."""

from fastapi import APIRouter, Request, HTTPException

from schemas.api import GenerateRequest, GenerateResponse
from services.orchestrator import OrchestratorError, generate

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def post_generate(body: GenerateRequest, request: Request) -> GenerateResponse:
    """Run the pipeline: prompt -> LLM spec -> validate -> sandbox -> storage; return project."""
    try:
        result = await generate(prompt=body.prompt, run_erc=body.run_erc)
        # Optionally prepend base URL for file links
        base = str(request.base_url).rstrip("/")
        if base:
            result.schematic_url = f"{base}{result.schematic_url}"
            result.pcb_url = f"{base}{result.pcb_url}"
        return result
    except OrchestratorError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
