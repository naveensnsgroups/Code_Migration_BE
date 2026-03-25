from fastapi import APIRouter
from app.api.endpoints import health, migrations, files

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(migrations.router, prefix="/migrations", tags=["migrations"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
