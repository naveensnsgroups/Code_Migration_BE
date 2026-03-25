from fastapi import APIRouter
from app.health.router import router as health_router
from app.migrations.router import router as migrations_router
from app.files.router import router as files_router
from app.github.router import router as github_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(migrations_router, prefix="/migrations", tags=["migrations"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(github_router, prefix="/github", tags=["github"])
