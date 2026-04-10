"""
Authentication middleware and utilities
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.db import SupabaseDB
from typing import Optional
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SupabaseDB = Depends()
):
    """
    Verify JWT token and return current user
    Ensures user exists in custom users table
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token = credentials.credentials
    
    try:
        # Verify token with Supabase
        user_response = db.supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        user = user_response.user
        
        # Ensure user exists in custom users table
        user_id = user.id
        user_email = user.email
        user_name = user.user_metadata.get('name', user_email) if user.user_metadata else user_email
        
        try:
            # Check if user exists in custom users table
            existing = await db.get_user_by_id(user_id)
            if not existing:
                # Create user record if it doesn't exist
                await db.create_user({
                    'id': user_id,
                    'email': user_email,
                    'name': user_name
                })
                logger.info(f"Created user record for {user_email}")
        except Exception as e:
            logger.warning(f"Could not ensure user exists in custom table: {e}")
        
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

async def get_optional_user(
    request: Request,
    db: SupabaseDB = Depends()
) -> Optional[dict]:
    """
    Get user if authenticated, otherwise return None
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        user_response = db.supabase.auth.get_user(token)
        return user_response.user if user_response else None
    except:
        return None

def verify_user_owns_resource(user_id: str, resource_user_id: str):
    """
    Verify that user owns the resource
    """
    if user_id != resource_user_id:
        raise HTTPException(status_code=403, detail="Access denied: You don't own this resource")