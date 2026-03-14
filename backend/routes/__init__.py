from fastapi import APIRouter

from routes.generate import router as generate_router
from routes.projects import router as projects_router

api_router = APIRouter()
api_router.include_router(generate_router, tags=["generate"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
