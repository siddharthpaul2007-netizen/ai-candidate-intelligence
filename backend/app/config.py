import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Candidate Intelligence Platform"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./evaluation.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()

