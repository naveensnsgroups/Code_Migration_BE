import os
from pathlib import Path
from fastapi import HTTPException
from typing import List
from app.schemas.files import FileItem, FileContent

# Current project root (e:\CODE_MIGRATION)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SOURCE_DIR = BASE_DIR / "source_code"

class FileSystemService:
    @staticmethod
    def list_source_files(path: str = "") -> List[FileItem]:
        """Lists files and directories in the source_code folder."""
        target_path = SOURCE_DIR / path
        
        if not SOURCE_DIR.exists():
            return []
        
        if not target_path.exists() or not str(target_path).startswith(str(SOURCE_DIR)):
            raise HTTPException(status_code=404, detail="Path not found")

        items = []
        try:
            for item in sorted(os.listdir(target_path)):
                full_path = target_path / item
                is_dir = full_path.is_dir()
                items.append(FileItem(
                    name=item,
                    isDir=is_dir,
                    path=str(full_path.relative_to(SOURCE_DIR)).replace("\\", "/")
                ))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
        return items

    @staticmethod
    def read_source_file(path: str) -> FileContent:
        """Reads the content of a specific file in the source_code folder."""
        target_path = SOURCE_DIR / path
        
        if not target_path.exists() or target_path.is_dir() or not str(target_path).startswith(str(SOURCE_DIR)):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            content = target_path.read_text(encoding="utf-8")
            return FileContent(content=content, path=path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

file_system_service = FileSystemService()
