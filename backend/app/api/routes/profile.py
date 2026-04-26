"""
Profile, Settings, and Notifications endpoints
"""
from fastapi import APIRouter, HTTPException, Header, Request
from typing import Optional
from datetime import datetime, timezone
import logging

from app.core.db import db
from app.models.profile import (
    ProfileUpdate, ProfileResponse,
    SettingsUpdate, SettingsResponse,
    NotificationResponse, NotificationsListResponse, MarkReadRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Auth helper ───────────────────────────────────────────────────────────────

def _get_user_id(x_user_id: Optional[str]) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required. Ensure you are logged in.")
    return x_user_id


def _ensure_user_row(user_id: str) -> dict:
    """
    Get the user row, creating a minimal one if it doesn't exist yet.
    Supabase Auth creates auth.users but our public.users trigger may not
    have fired (e.g. during development / first login).
    """
    user = db.get_user_by_id(user_id)
    if user:
        return user

    logger.info(f"[profile] Creating missing user row for {user_id}")
    # Pull email from Supabase Auth admin API via service role
    try:
        auth_res = db.client.auth.admin.get_user_by_id(user_id)
        email = auth_res.user.email if auth_res.user else f"{user_id}@unknown"
    except Exception:
        email = f"{user_id}@unknown"

    created = db.create_user({"id": user_id, "email": email, "name": email.split("@")[0]})
    return created or {"id": user_id, "email": email}


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("/profile", response_model=ProfileResponse)
def get_profile(request: Request, x_user_id: Optional[str] = Header(None)):
    logger.info(f"[profile] GET /profile  user={x_user_id}  origin={request.headers.get('origin')}")
    user_id = _get_user_id(x_user_id)
    user = _ensure_user_row(user_id)

    repos = db.list_repositories(user_id)
    repo_ids = [r["id"] for r in repos]

    scan_count = vuln_count = fixes_count = 0
    try:
        if repo_ids:
            scans_res = db.client.table("scans") \
                .select("id, total_vulnerabilities") \
                .in_("repo_id", repo_ids) \
                .execute()
            scans = scans_res.data or []
            scan_count = len(scans)
            vuln_count = sum(s.get("total_vulnerabilities") or 0 for s in scans)

            scan_ids = [s["id"] for s in scans]
            if scan_ids:
                # Get vulnerability IDs for these scans
                vuln_ids_res = db.client.table("vulnerabilities") \
                    .select("id") \
                    .in_("scan_id", scan_ids) \
                    .execute()
                vuln_ids = [v["id"] for v in (vuln_ids_res.data or [])]
                if vuln_ids:
                    fixes_res = db.client.table("ai_fixes") \
                        .select("id") \
                        .eq("is_applied", True) \
                        .in_("vulnerability_id", vuln_ids) \
                        .execute()
                    fixes_count = len(fixes_res.data or [])
    except Exception as e:
        logger.warning(f"[profile] Stats aggregation failed: {e}")

    return ProfileResponse(
        id=user["id"],
        email=user.get("email", ""),
        name=user.get("name"),
        avatar_url=user.get("avatar_url"),
        bio=user.get("bio"),
        created_at=user.get("created_at"),
        updated_at=user.get("updated_at"),
        repo_count=len(repos),
        scan_count=scan_count,
        vuln_count=vuln_count,
        fixes_count=fixes_count,
    )


@router.put("/profile", response_model=ProfileResponse)
def update_profile(request: Request, body: ProfileUpdate, x_user_id: Optional[str] = Header(None)):
    logger.info(f"[profile] PUT /profile  user={x_user_id}")
    user_id = _get_user_id(x_user_id)
    _ensure_user_row(user_id)

    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=422, detail="No fields to update")

    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        db.client.table("users").update(update_data).eq("id", user_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return get_profile(request, x_user_id)


# ── Settings ──────────────────────────────────────────────────────────────────

def _get_or_create_settings(user_id: str) -> dict:
    """Get settings row, creating defaults if missing. Ensures user row exists first."""
    _ensure_user_row(user_id)  # FK guard
    res = db.client.table("user_settings").select("*").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]
    row = db.client.table("user_settings").insert({"user_id": user_id}).execute()
    return row.data[0] if row.data else {}


@router.get("/settings", response_model=SettingsResponse)
def get_settings(request: Request, x_user_id: Optional[str] = Header(None)):
    logger.info(f"[profile] GET /settings  user={x_user_id}")
    user_id = _get_user_id(x_user_id)
    s = _get_or_create_settings(user_id)
    user = db.get_user_by_id(user_id) or {}

    return SettingsResponse(
        theme=s.get("theme", "dark"),
        notify_scan_complete=s.get("notify_scan_complete", True),
        notify_critical_vuln=s.get("notify_critical_vuln", True),
        notify_pr_created=s.get("notify_pr_created", True),
        github_token_set=bool(user.get("github_token")),
        nvd_api_key_set=bool(s.get("nvd_api_key")),
        openrouter_api_key_set=bool(s.get("openrouter_api_key")),
    )


@router.put("/settings", response_model=SettingsResponse)
def update_settings(request: Request, body: SettingsUpdate, x_user_id: Optional[str] = Header(None)):
    logger.info(f"[profile] PUT /settings  user={x_user_id}")
    user_id = _get_user_id(x_user_id)
    _get_or_create_settings(user_id)

    settings_fields = {
        "theme", "notify_scan_complete", "notify_critical_vuln",
        "notify_pr_created", "nvd_api_key", "openrouter_api_key",
    }
    settings_data = {
        k: v for k, v in body.model_dump().items()
        if k in settings_fields and v is not None
    }
    if settings_data:
        settings_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        db.client.table("user_settings").update(settings_data).eq("user_id", user_id).execute()

    if body.github_token is not None:
        db.client.table("users").update({"github_token": body.github_token}).eq("id", user_id).execute()

    return get_settings(request, x_user_id)


# ── Notifications ─────────────────────────────────────────────────────────────

@router.get("/notifications", response_model=NotificationsListResponse)
def get_notifications(request: Request, x_user_id: Optional[str] = Header(None), limit: int = 30):
    logger.info(f"[profile] GET /notifications  user={x_user_id}")
    user_id = _get_user_id(x_user_id)
    try:
        res = db.client.table("notifications") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        items = res.data or []
        unread = sum(1 for n in items if not n.get("is_read"))
        return NotificationsListResponse(
            notifications=[NotificationResponse(**n) for n in items],
            unread_count=unread,
        )
    except Exception as e:
        logger.error(f"[profile] notifications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/read")
def mark_notifications_read(
    request: Request, body: MarkReadRequest,
    x_user_id: Optional[str] = Header(None)
):
    user_id = _get_user_id(x_user_id)
    try:
        q = db.client.table("notifications").update({"is_read": True}).eq("user_id", user_id)
        if body.notification_ids:
            q = q.in_("id", body.notification_ids)
        q.execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
