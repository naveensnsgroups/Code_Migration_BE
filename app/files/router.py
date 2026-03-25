from fastapi import APIRouter
from typing import List
from .schemas import FileItem, FileContent
from .service import file_system_service

router = APIRouter()

@router.get("/list", response_model=List[FileItem])
async def list_source_files(path: str = ""):
    """List project files."""
    return file_system_service.list_source_files(path)

@router.get("/read", response_model=FileContent)
async def read_source_file(path: str):
    """Read file content."""
    return file_system_service.read_source_file(path)
