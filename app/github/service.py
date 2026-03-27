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

    @staticmethod
    def cleanup_on_logout() -> bool:
        """Deletes the source_code directory on logout, handling read-only git objects."""
        source_path = SOURCE_DIR.resolve()
        
        def remove_readonly(func, path, excinfo):
            """Error handler for shutil.rmtree to handle read-only files (common in .git)."""
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if os.path.exists(source_path):
            try:
                shutil.rmtree(source_path, onerror=remove_readonly)
                print(f"DEBUG: Source code cleanup successful at {source_path}")
                return True
            except Exception as e:
                print(f"ERROR: Failed to cleanup source code: {e}")
                return False
        return True

github_service = GitHubService()
