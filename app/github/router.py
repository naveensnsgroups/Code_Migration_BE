from fastapi import APIRouter, HTTPException
import httpx
from typing import List
from app.core.config import settings
from .schemas import RepoInfo, CloneSelectedRequest
from .service import github_service

router = APIRouter()

@router.get("/login")
async def github_login():
    """Redirect to GitHub OAuth page."""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID not configured.")
    
    scope = "repo,user"
    url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&scope={scope}"
    return {"url": url}

@router.get("/callback")
async def github_callback(code: str):
    """Handle callback from GitHub and exchange code for access token."""
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub Credentials not configured.")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            params={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        data = response.json()
        
        if "access_token" not in data:
            raise HTTPException(status_code=400, detail=f"Failed to get access token: {data}")
        
        return data

@router.get("/repos", response_model=List[RepoInfo])
async def list_user_repos(access_token: str):
    """Fetch all repositories for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"sort": "updated", "per_page": 100}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch repos from GitHub.")
        
        return response.json()

@router.post("/clone-selected")
async def clone_selected_repo(request: CloneSelectedRequest):
    """Clone the selected repo using the access token."""
    github_service.clone_repository(request.repo_url, request.access_token)
    return {"status": "success", "message": "Repository cloned successfully."}
