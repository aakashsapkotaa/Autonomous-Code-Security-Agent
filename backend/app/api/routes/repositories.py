"""
Repository management endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.repository import Repository, RepositoryCreate
from app.core.db import db
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
def list_repositories(user_id: Optional[str] = None) -> List[Dict]:
    """
    List all repositories for a user
    """
    repositories = db.list_repositories(user_id)
    return repositories

@router.post("/")
def create_repository(repo_data: RepositoryCreate) -> Dict:
    """
    Add a new repository
    """
    # If user_id is provided, ensure the user exists
    if repo_data.user_id:
        existing_user = db.get_user_by_id(repo_data.user_id)
        if not existing_user:
            logger.warning(f"User {repo_data.user_id} does not exist, attempting to create...")
            # Try to create a user record if it doesn't exist
            # This could happen if Supabase Auth created a user but our trigger didn't fire
            user_created = db.create_user({
                'id': repo_data.user_id,
                'email': f'user_{repo_data.user_id}@example.com',
                'name': 'Unknown User'
            })
            if not user_created:
                raise HTTPException(
                    status_code=400, 
                    detail=f"User {repo_data.user_id} does not exist in the database. Please ensure you are authenticated."
                )
    
    repo = db.create_repository(repo_data.dict())
    
    if not repo:
        raise HTTPException(status_code=400, detail="Failed to create repository")
    
    return repo

@router.get("/{repo_id}")
def get_repository(repo_id: str) -> Dict:
    """
    Get repository by ID
    """
    repo = db.get_repository(repo_id)
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return repo
