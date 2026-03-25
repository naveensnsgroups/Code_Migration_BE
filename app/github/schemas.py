from pydantic import BaseModel
from typing import Optional, List

class RepoInfo(BaseModel):
    id: int
    name: str
    full_name: str
    html_url: str
    description: Optional[str]
    language: Optional[str]
    stargazers_count: int

class CloneSelectedRequest(BaseModel):
    repo_url: str
    access_token: str

class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    scope: str
