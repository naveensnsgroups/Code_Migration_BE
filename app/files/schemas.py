from pydantic import BaseModel

class FileItem(BaseModel):
    name: str
    isDir: bool
    path: str

class FileContent(BaseModel):
    content: str
    path: str
    encoding: str = "utf-8"
