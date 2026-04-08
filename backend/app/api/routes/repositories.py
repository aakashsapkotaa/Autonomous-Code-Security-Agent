"""
Repository management endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.repository import Repository, RepositoryCreate
from app.core.db import db
from typing import List, Optional, Dict

router = APIRouter()

@router.get("/")
async def list_repositories(user_id: Optional[str] = None) -> List[Dict]:
    """
    List all repositories for a user
    """
    repositories = await db.list_repositories(user_id)
    return repositories

@router.post("/")
async def create_repository(repo_data: RepositoryCreate) -> Dict:
    """
    Add a new repository
    """
    repo = await db.create_repository(repo_data.dict())
    
    if not repo:
        raise HTTPException(status_code=400, detail="Failed to create repository")
    
    return repo

@router.get("/{repo_id}")
async def get_repository(repo_id: str) -> Dict:
    """
    Get repository by ID
    """
    repo = await db.get_repository(repo_id)
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return repo
