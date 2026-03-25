import os
import subprocess
import shutil
from pathlib import Path
from fastapi import HTTPException

# Current project root (e:\CODE_MIGRATION)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SOURCE_DIR = BASE_DIR / "source_code"

class GitHubService:
    @staticmethod
    def clone_repository(repo_url: str, access_token: str) -> bool:
        """Clones a repository into the source_code folder using OAuth token."""
        source_path = SOURCE_DIR.resolve()

        # Clear existing source_code directory
        if os.path.exists(source_path):
            shutil.rmtree(source_path)
        os.makedirs(source_path, exist_ok=True)

        # Authenticated URL: https://<token>@github.com/user/repo.git
        authenticated_url = repo_url.replace("https://", f"https://{access_token}@")

        try:
            result = subprocess.run(
                ["git", "clone", authenticated_url, str(source_path)],
                capture_output=True,
                text=True,
                timeout=180,
            )

            if result.returncode != 0:
                raise HTTPException(status_code=400, detail=f"Clone failed: {result.stderr}")

            return True
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))

github_service = GitHubService()
