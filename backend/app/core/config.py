"""
Configuration settings for FastAPI backend
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SecureShift"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://secureshift.vercel.app"
    ]
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # OpenRouter AI
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "nvidia/nemotron-3-super-120b-a12b:free"
    
    # GitHub OAuth
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    
    # MCP Agents (optional for local development)
    MCP_ORCHESTRATOR_URL: str = "http://localhost:5001"
    MCP_FIXER_URL: str = "http://localhost:5002"
    MCP_REPORTER_URL: str = "http://localhost:5003"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
