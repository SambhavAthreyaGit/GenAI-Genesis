"""Orchestrate the generate pipeline: LLM -> validate -> sandbox -> storage."""

import asyncio
from typing import Any

from config import get_settings
from schemas.api import ERCResult, GenerateResponse
from schemas.circuit_spec import CircuitSpec
from services.llm import LLMService
from services.sandbox_runner import SandboxRunner
from services.spec_validator import SpecValidationError, SpecValidator
from services.storage import StorageService, generate_project_id


class OrchestratorError(Exception):
    """Raised when pipeline step fails."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def run_generate(
    prompt: str,
    run_erc: bool = True,
) -> GenerateResponse:
    """
    Run the full pipeline: create project -> LLM -> validate -> sandbox -> save.
    Returns GenerateResponse or raises OrchestratorError.
    """
    settings = get_settings()
    storage = StorageService()
    project_id = generate_project_id()
    storage.create_project(project_id, prompt)
    base_url = ""  # Routes will set this from request base_url if needed

    try:
        # 1. LLM: prompt -> spec
        llm = LLMService()
        raw_spec = llm.get_spec(prompt)
    except ValueError as e:
        storage.mark_failed(project_id)
        raise OrchestratorError(str(e), 400)
    except Exception as e:
        storage.mark_failed(project_id)
        raise OrchestratorError(f"LLM failed: {e}", 502)

    try:
        # 2. Validate / normalize
        validator = SpecValidator()
        validated_spec = validator.validate(raw_spec)
    except SpecValidationError as e:
        storage.mark_failed(project_id)
        raise OrchestratorError(f"Invalid spec: {e}", 400)

    try:
        # 3. Sandbox: spec -> schematic, board, ERC
        runner = SandboxRunner()
        schematic_content, pcb_content, erc_result = await runner.run(
            validated_spec,
            run_erc=run_erc,
        )
    except RuntimeError as e:
        storage.mark_failed(project_id)
        raise OrchestratorError(f"Sandbox failed: {e}", 502)
    except Exception as e:
        storage.mark_failed(project_id)
        raise OrchestratorError(f"Sandbox error: {e}", 502)

    # 4. Save files and update metadata
    storage.save_files(
        project_id,
        schematic_content,
        pcb_content,
        erc_result=erc_result,
    )

    # Build response URLs (relative; app will add base URL when needed)
    schematic_url = f"/files/{project_id}/schematic.kicad_sch"
    pcb_url = f"/files/{project_id}/board.kicad_pcb"

    return GenerateResponse(
        project_id=project_id,
        schematic_url=schematic_url,
        pcb_url=pcb_url,
        erc_result=erc_result,
        status="completed",
    )


# Singleton orchestrator entrypoint used by routes
async def generate(prompt: str, run_erc: bool = True) -> GenerateResponse:
    """Public entry: run pipeline and return response."""
    return await run_generate(prompt, run_erc=run_erc)


def get_project(project_id: str, base_url: str = "") -> dict | None:
    """Return project response dict for GET /projects/{id} or None if not found."""
    storage = StorageService()
    return storage.get_project_response(project_id, base_url=base_url)
