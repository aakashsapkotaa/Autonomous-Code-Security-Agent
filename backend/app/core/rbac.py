"""
Role-Based Access Control helpers for admin endpoints.
"""
from fastapi import HTTPException, Header
from typing import Optional
from app.core.db import db
import logging

logger = logging.getLogger(__name__)

ADMIN_ROLES = {"admin", "super_admin", "enterprise_manager"}
SUPER_ROLES = {"super_admin"}


def require_admin(x_user_id: Optional[str] = Header(None)) -> str:
    """Dependency: user must be admin, super_admin, or enterprise_manager."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin access required")
    if user.get("status") == "suspended":
        raise HTTPException(status_code=403, detail="Account suspended")
    return x_user_id


def require_super_admin(x_user_id: Optional[str] = Header(None)) -> str:
    """Dependency: user must be super_admin."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.get_user_by_id(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.get("role") not in SUPER_ROLES:
        raise HTTPException(status_code=403, detail="Super admin access required")
    return x_user_id


def log_audit(
    actor_id: str,
    action: str,
    target_type: str = None,
    target_id: str = None,
    metadata: dict = None,
    ip_address: str = None,
):
    """Write an audit log entry."""
    try:
        actor = db.get_user_by_id(actor_id) or {}
        db.client.table("audit_logs").insert({
            "actor_id":    actor_id,
            "actor_email": actor.get("email", ""),
            "action":      action,
            "target_type": target_type,
            "target_id":   str(target_id) if target_id else None,
            "metadata":    metadata or {},
            "ip_address":  ip_address,
        }).execute()
    except Exception as e:
        logger.warning(f"[audit] Failed to write log: {e}")
