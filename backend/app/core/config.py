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
    https://ayeoqnvldhrazjpvbrey.supabase.co: str
    SUPABASE_KEY: str
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTY2MzI0MCwiZXhwIjoyMDkxMjM5MjQwfQ.w3RZhHch0qRfsQtEx4mgMuJVeRT69CvPLNeDIWXXPYw: str
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "secureshift-reports"
    AWS_REGION: str = "us-east-1"
    
    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    
    # MCP Agents
    MCP_ORCHESTRATOR_URL: str = "http://localhost:8001"
    MCP_FIXER_URL: str = "http://localhost:8002"
    MCP_REPORTER_URL: str = "http://localhost:8003"
    
    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-coder:6.7b"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
