"""
Repository models
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime

class RepositoryCreate(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL")
    repo_name: str = Field(..., description="Repository name")
    user_id: str = Field(..., description="User ID")

class Repository(BaseModel):
    id: str
    user_id: str
    repo_url: str
    repo_name: str
    created_at: datetime

    class Config:
        from_attributes = True
