from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Code Migration AI"
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # MongoDB Configuration
    MONGODB_URL: str = ""
    MONGODB_DB: str = ""

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True, 
        extra="ignore"
    )

settings = Settings()
