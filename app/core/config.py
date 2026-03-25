from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Code Migration AI"
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # MongoDB Configuration
    MONGODB_URL: str = ""
    MONGODB_DB: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
