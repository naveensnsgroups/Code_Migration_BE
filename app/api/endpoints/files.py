from fastapi import APIRouter
from typing import List
from app.schemas.files import FileItem, FileContent
from app.crud.file_ops.service import file_system_service

router = APIRouter()

@router.get("/list", response_model=List[FileItem])
async def list_source_files(path: str = ""):
    """Router only: Delegates to file_system_service."""
    return file_system_service.list_source_files(path)

@router.get("/read", response_model=FileContent)
async def read_source_file(path: str):
    """Router only: Delegates to file_system_service."""
    return file_system_service.read_source_file(path)
