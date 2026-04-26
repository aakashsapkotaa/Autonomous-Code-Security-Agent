"""
Repository management endpoints
"""
from fastapi import APIRouter, HTTPException, Header
from app.models.repository import Repository, RepositoryCreate
from app.core.db import db
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
def list_repositories(x_user_id: Optional[str] = Header(None)) -> List[Dict]:
    """List all repositories for the authenticated user."""
    return db.list_repositories(x_user_id)


@router.post("/")
def create_repository(
    repo_data: RepositoryCreate,
    x_user_id: Optional[str] = Header(None),
) -> Dict:
    """Add a new repository."""
    # Use header user_id if not in body
    user_id = repo_data.user_id or x_user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Fast path: try insert directly — let DB FK catch missing user
    # Only do the user-existence check if the insert fails
    data = repo_data.dict()
    data["user_id"] = user_id

    repo = db.create_repository(data)
    if repo:
        return repo

    # Insert failed — check if user row is missing (auth trigger may not have fired)
    existing = db.get_user_by_id(user_id)
    if not existing:
        logger.warning(f"User {user_id} missing from users table, auto-creating stub")
        db.create_user({
            "id":    user_id,
            "email": f"user_{user_id[:8]}@placeholder.local",
            "name":  "User",
        })

    # Retry once
    repo = db.create_repository(data)
    if not repo:
        raise HTTPException(status_code=400, detail="Failed to create repository")
    return repo


@router.get("/{repo_id}")
def get_repository(repo_id: str) -> Dict:
    """Get repository by ID."""
    repo = db.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo


@router.delete("/{repo_id}")
def delete_repository(
    repo_id: str,
    x_user_id: Optional[str] = Header(None),
) -> Dict:
    """Delete a repository."""
    repo = db.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    if repo.get("user_id") != x_user_id:
        raise HTTPException(status_code=403, detail="Not your repository")
    try:
        db.client.table("repositories").delete().eq("id", repo_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok"}
