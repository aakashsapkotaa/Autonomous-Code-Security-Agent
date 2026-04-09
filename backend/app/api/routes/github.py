"""
GitHub OAuth and Webhook Integration
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
import httpx
import hmac
import hashlib
from app.core.config import settings
from app.core.db import SupabaseDB
from app.core.auth import get_current_user

router = APIRouter()

class GitHubRepo(BaseModel):
    repo_url: str
    branch: str = "main"

@router.get("/auth/login")
async def github_login():
    """Redirect to GitHub OAuth"""
    if not settings.GITHUB_TOKEN:
        raise HTTPException(status_code=501, detail="GitHub integration not configured")
    
    github_oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_TOKEN}"
        f"&scope=repo,read:user"
    )
    return {"url": github_oauth_url}

@router.get("/auth/callback")
async def github_callback(code: str, db: SupabaseDB = Depends()):
    """Handle GitHub OAuth callback"""
    if not settings.GITHUB_TOKEN:
        raise HTTPException(status_code=501, detail="GitHub integration not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            resp = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_TOKEN,
                    "client_secret": settings.GITHUB_WEBHOOK_SECRET,
                    "code": code
                },
                headers={"Accept": "application/json"}
            )
            token_data = resp.json()
            
            if "access_token" not in token_data:
                raise HTTPException(status_code=400, detail="Failed to get access token")
            
            access_token = token_data["access_token"]
            
            # Get user info from GitHub
            user_resp = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            github_user = user_resp.json()
            
            return {
                "access_token": access_token,
                "github_user": github_user
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth failed: {str(e)}")

@router.post("/webhook")
async def github_webhook(request: Request, db: SupabaseDB = Depends()):
    """Handle GitHub webhook events"""
    
    # Verify webhook signature
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature or not settings.GITHUB_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    body = await request.body()
    expected_signature = "sha256=" + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Process webhook event
    event_type = request.headers.get("X-GitHub-Event")
    payload = await request.json()
    
    if event_type == "push":
        # Trigger scan on push
        repo_url = payload["repository"]["clone_url"]
        branch = payload["ref"].split("/")[-1]
        
        # Find repository in database
        repos = db.get_repositories(filters={"repo_url": repo_url})
        if repos:
            repo_id = repos[0]["id"]
            # Create new scan
            scan = db.create_scan(repo_id)
            
            # TODO: Implement background scanning
            # For now, just create the scan record
            
            return {"status": "scan_triggered", "scan_id": scan["id"]}
    
    return {"status": "event_received", "event_type": event_type}

@router.post("/repos/import")
async def import_github_repos(
    github_token: str,
    user = Depends(get_current_user),
    db: SupabaseDB = Depends()
):
    """Import user's GitHub repositories"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.github.com/user/repos",
                headers={"Authorization": f"Bearer {github_token}"},
                params={"per_page": 100, "sort": "updated"}
            )
            repos = resp.json()
            
            imported = []
            for repo in repos:
                # Add to database
                repo_data = {
                    "user_id": user.id,
                    "repo_name": repo["full_name"],
                    "repo_url": repo["clone_url"],
                    "branch": repo["default_branch"]
                }
                
                # Check if already exists
                existing = db.get_repositories(filters={"repo_url": repo["clone_url"]})
                if not existing:
                    new_repo = db.create_repository(repo_data)
                    imported.append(new_repo)
            
            return {"status": "success", "imported_count": len(imported), "repos": imported}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
