"""Request/response models for API routes."""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Body for POST /generate."""

    prompt: str = Field(..., min_length=1, description="Natural language circuit description")
    run_erc: bool = Field(default=True, description="Whether to run ERC after generation")


class ERCResult(BaseModel):
    """ERC run result from sandbox."""

    passed: bool = Field(..., description="Whether ERC passed")
    messages: list[str] = Field(default_factory=list, description="ERC messages or errors")
    summary: str | None = Field(default=None, description="Short human-readable summary")


class GenerateResponse(BaseModel):
    """Response for POST /generate and GET /projects/{id} (project view)."""

    project_id: str = Field(..., description="Unique project ID")
    schematic_url: str = Field(..., description="URL to load schematic in KiCanvas")
    pcb_url: str = Field(..., description="URL to load PCB in KiCanvas")
    erc_result: ERCResult | None = Field(default=None, description="ERC result if run")
    status: str = Field(default="completed", description="pending | completed | failed")


class ProjectResponse(BaseModel):
    """Response for GET /projects/{project_id}."""

    project_id: str
    prompt: str | None = None
    schematic_url: str
    pcb_url: str
    erc_result: ERCResult | None = None
    status: str
    created_at: str | None = None
