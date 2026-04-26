"""
Admin Dashboard API — all routes require admin role.
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional
from datetime import datetime, timezone, timedelta
import logging

from app.core.db import db
from app.core.rbac import require_admin, require_super_admin, log_audit
from app.core.config import settings
from app.models.admin import (
    AdminOverview, AdminUser, AdminUserUpdate, AdminScan,
    AdminVulnerability, AdminPR, AuditLog, SystemSettings,
    SystemSettingsResponse, AnalyticsData, DailyCount,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Overview ──────────────────────────────────────────────────────────────────

@router.get("/overview", response_model=AdminOverview)
def admin_overview(admin_id: str = Depends(require_admin)):
    c = db.client
    today = datetime.now(timezone.utc).date().isoformat()

    users_res   = c.table("users").select("id, status").execute()
    users       = users_res.data or []
    repos_res   = c.table("repositories").select("id").execute()
    scans_res   = c.table("scans").select("id, status, created_at").execute()
    scans       = scans_res.data or []
    vulns_res   = c.table("vulnerabilities").select("id, severity").execute()
    vulns       = vulns_res.data or []
    fixes_res   = c.table("ai_fixes").select("id").execute()
    prs_res     = c.table("scans").select("id").not_.is_("pr_url", "null").execute()

    scans_today = sum(1 for s in scans if (s.get("created_at") or "").startswith(today))
    vulns_today = 0  # would need detected_at index for accuracy

    return AdminOverview(
        total_users=len(users),
        active_users=sum(1 for u in users if u.get("status") != "suspended"),
        suspended_users=sum(1 for u in users if u.get("status") == "suspended"),
        total_repositories=len(repos_res.data or []),
        total_scans=len(scans),
        running_scans=sum(1 for s in scans if s.get("status") == "running"),
        failed_scans=sum(1 for s in scans if s.get("status") == "failed"),
        completed_scans=sum(1 for s in scans if s.get("status") == "completed"),
        total_vulnerabilities=len(vulns),
        critical_vulnerabilities=sum(1 for v in vulns if v.get("severity") == "critical"),
        ai_fixes_generated=len(fixes_res.data or []),
        pull_requests_created=len(prs_res.data or []),
        scans_today=scans_today,
        vulns_today=vulns_today,
    )


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users")
def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    admin_id: str = Depends(require_admin),
):
    c = db.client
    q = c.table("users").select("*")
    if role:   q = q.eq("role", role)
    if status: q = q.eq("status", status)
    res = q.order("created_at", desc=True).execute()
    users = res.data or []

    if search:
        s = search.lower()
        users = [u for u in users if s in (u.get("email") or "").lower()
                 or s in (u.get("name") or "").lower()]

    total = len(users)
    start = (page - 1) * limit
    page_users = users[start: start + limit]

    # Attach repo/scan counts
    enriched = []
    for u in page_users:
        repos = c.table("repositories").select("id").eq("user_id", u["id"]).execute()
        scans_res = c.table("scans").select("id").in_(
            "repo_id", [r["id"] for r in (repos.data or [])]
        ).execute() if repos.data else type("R", (), {"data": []})()
        enriched.append({
            **u,
            "repo_count": len(repos.data or []),
            "scan_count": len(scans_res.data or []),
        })

    return {"users": enriched, "total": total, "page": page, "limit": limit}


@router.get("/users/{user_id}")
def get_user(user_id: str, admin_id: str = Depends(require_admin)):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}")
def update_user(
    request: Request,
    user_id: str,
    body: AdminUserUpdate,
    admin_id: str = Depends(require_admin),
):
    # Only super_admin can change roles
    if body.role:
        actor = db.get_user_by_id(admin_id) or {}
        if actor.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Only super_admin can change roles")

    update = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=422, detail="Nothing to update")

    db.client.table("users").update(update).eq("id", user_id).execute()
    log_audit(admin_id, "user.update", "user", user_id, update,
              request.client.host if request.client else None)
    return {"status": "ok"}


@router.delete("/users/{user_id}")
def delete_user(
    request: Request,
    user_id: str,
    admin_id: str = Depends(require_super_admin),
):
    db.client.table("users").delete().eq("id", user_id).execute()
    log_audit(admin_id, "user.delete", "user", user_id, {},
              request.client.host if request.client else None)
    return {"status": "ok"}


# ── Repositories ──────────────────────────────────────────────────────────────

@router.get("/repositories")
def list_all_repos(
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    admin_id: str = Depends(require_admin),
):
    c = db.client
    try:
        res = c.table("repositories").select("*, users!repositories_user_id_fkey(email, name)").order("created_at", desc=True).execute()
        repos = res.data or []
    except Exception:
        try:
            res = c.table("repositories").select("*").order("created_at", desc=True).execute()
            repos = res.data or []
        except Exception:
            repos = []

    if search:
        s = search.lower()
        repos = [r for r in repos if s in (r.get("repo_name") or "").lower()
                 or s in (r.get("repo_url") or "").lower()]

    total = len(repos)
    start = (page - 1) * limit
    return {"repositories": repos[start: start + limit], "total": total, "page": page, "limit": limit}


@router.delete("/repositories/{repo_id}")
def delete_repo(
    request: Request,
    repo_id: str,
    admin_id: str = Depends(require_admin),
):
    db.client.table("repositories").delete().eq("id", repo_id).execute()
    log_audit(admin_id, "repository.delete", "repository", repo_id, {},
              request.client.host if request.client else None)
    return {"status": "ok"}


# ── Scans ─────────────────────────────────────────────────────────────────────

@router.get("/scans")
def list_all_scans(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    admin_id: str = Depends(require_admin),
):
    c = db.client
    q = c.table("scans").select("*, repositories(repo_name, repo_url, users(email))")
    if status:
        q = q.eq("status", status)
    res = q.order("created_at", desc=True).execute()
    scans = res.data or []
    total = len(scans)
    start = (page - 1) * limit
    return {"scans": scans[start: start + limit], "total": total, "page": page, "limit": limit}


@router.get("/scans/{scan_id}/logs")
def get_scan_logs(scan_id: str, admin_id: str = Depends(require_admin)):
    res = db.client.table("scan_logs").select("*").eq("scan_id", scan_id).order("created_at").execute()
    return res.data or []


# ── Vulnerabilities ───────────────────────────────────────────────────────────

@router.get("/vulnerabilities")
def list_all_vulns(
    severity: Optional[str] = None,
    is_fixed: Optional[bool] = None,
    page: int = 1,
    limit: int = 20,
    admin_id: str = Depends(require_admin),
):
    c = db.client
    q = c.table("vulnerabilities").select(
        "*, scans(id, repositories(repo_name, repo_url))"
    )
    if severity: q = q.eq("severity", severity)
    if is_fixed is not None: q = q.eq("is_fixed", is_fixed)
    res = q.order("detected_at", desc=True).execute()
    vulns = res.data or []
    total = len(vulns)
    start = (page - 1) * limit
    return {"vulnerabilities": vulns[start: start + limit], "total": total, "page": page, "limit": limit}


# ── Pull Requests ─────────────────────────────────────────────────────────────

@router.get("/pull-requests")
def list_all_prs(
    page: int = 1,
    limit: int = 20,
    admin_id: str = Depends(require_admin),
):
    c = db.client
    try:
        res = c.table("scans").select(
            "id, pr_url, created_at, repositories(repo_name, repo_url)"
        ).not_.is_("pr_url", "null").order("created_at", desc=True).execute()
        prs = res.data or []
    except Exception:
        prs = []
    total = len(prs)
    start = (page - 1) * limit
    return {"pull_requests": prs[start: start + limit], "total": total, "page": page, "limit": limit}


# ── Analytics ─────────────────────────────────────────────────────────────────

@router.get("/analytics")
def get_analytics(days: int = 30, admin_id: str = Depends(require_admin)):
    c = db.client
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    try:
        scans_res = c.table("scans").select("id, status, created_at").gte("created_at", since).execute()
        scans = scans_res.data or []
    except Exception:
        scans = []

    try:
        vulns_res = c.table("vulnerabilities").select("id, severity, detected_at").gte("detected_at", since).execute()
        vulns = vulns_res.data or []
    except Exception:
        vulns = []

    # Scans per day
    scan_by_day: dict[str, int] = {}
    for s in scans:
        day = (s.get("created_at") or "")[:10]
        if day: scan_by_day[day] = scan_by_day.get(day, 0) + 1

    # Vulns per day
    vuln_by_day: dict[str, int] = {}
    for v in vulns:
        day = (v.get("detected_at") or "")[:10]
        if day: vuln_by_day[day] = vuln_by_day.get(day, 0) + 1

    # Severity breakdown
    sev_breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in vulns:
        sev = v.get("severity", "low")
        if sev in sev_breakdown:
            sev_breakdown[sev] += 1

    # Scan status breakdown
    status_breakdown: dict[str, int] = {}
    for s in scans:
        st = s.get("status", "unknown")
        status_breakdown[st] = status_breakdown.get(st, 0) + 1

    # Top repos by vuln count — use separate fresh queries with error guards
    try:
        repos_res = c.table("repositories").select("id, repo_name").execute()
        repo_map = {r["id"]: r.get("repo_name", "unknown") for r in (repos_res.data or [])}
    except Exception:
        repo_map = {}

    try:
        all_scans = c.table("scans").select("repo_id, total_vulnerabilities").execute().data or []
    except Exception:
        all_scans = []

    repo_vulns: dict[str, int] = {}
    for s in all_scans:
        rid = s.get("repo_id", "")
        if rid:
            repo_vulns[rid] = repo_vulns.get(rid, 0) + (s.get("total_vulnerabilities") or 0)

    top_repos = sorted(
        [{"repo_name": repo_map.get(k, k), "vuln_count": v} for k, v in repo_vulns.items()],
        key=lambda x: x["vuln_count"], reverse=True
    )[:10]

    return {
        "scans_per_day":         [{"date": k, "count": v} for k, v in sorted(scan_by_day.items())],
        "vulns_per_day":         [{"date": k, "count": v} for k, v in sorted(vuln_by_day.items())],
        "severity_breakdown":    sev_breakdown,
        "top_repos":             top_repos,
        "scan_status_breakdown": status_breakdown,
    }


# ── Audit Logs ────────────────────────────────────────────────────────────────

@router.get("/audit-logs")
def get_audit_logs(
    page: int = 1,
    limit: int = 50,
    admin_id: str = Depends(require_admin),
):
    res = db.client.table("audit_logs").select("*").order("created_at", desc=True).execute()
    logs = res.data or []
    total = len(logs)
    start = (page - 1) * limit
    return {"logs": logs[start: start + limit], "total": total, "page": page, "limit": limit}


# ── Admin Notifications ───────────────────────────────────────────────────────

@router.get("/notifications")
def get_admin_notifications(admin_id: str = Depends(require_admin)):
    try:
        res = db.client.table("admin_notifications").select("*").order("created_at", desc=True).limit(50).execute()
        items = res.data or []
    except Exception:
        items = []
    return {"notifications": items, "unread_count": sum(1 for n in items if not n.get("is_read"))}


@router.post("/notifications/read")
def mark_admin_notifications_read(admin_id: str = Depends(require_admin)):
    try:
        db.client.table("admin_notifications").update({"is_read": True}).eq("is_read", False).execute()
    except Exception:
        pass
    return {"status": "ok"}


# ── System Settings ───────────────────────────────────────────────────────────

@router.get("/system-settings", response_model=SystemSettingsResponse)
def get_system_settings(admin_id: str = Depends(require_super_admin)):
    return SystemSettingsResponse(
        github_token_set=bool(settings.GITHUB_TOKEN),
        openrouter_api_key_set=bool(settings.OPENROUTER_API_KEY),
        nvd_api_key_set=bool(settings.NVD_API_KEY),
        openrouter_model=settings.OPENROUTER_MODEL,
        max_concurrent_scans=5,
    )


@router.put("/system-settings")
def update_system_settings(
    request: Request,
    body: SystemSettings,
    admin_id: str = Depends(require_super_admin),
):
    # In production these would write to a config store / env manager
    log_audit(admin_id, "system.settings.update", "system", None,
              {k: "***" for k, v in body.model_dump().items() if v},
              request.client.host if request.client else None)
    return {"status": "ok", "message": "Settings noted. Restart backend to apply env changes."}


# ── Organizations ─────────────────────────────────────────────────────────────

@router.get("/organizations")
def list_orgs(admin_id: str = Depends(require_admin)):
    try:
        # Use explicit FK hint to avoid ambiguous relationship error
        res = db.client.table("organizations").select(
            "*, users!organizations_owner_id_fkey(email, name)"
        ).order("created_at", desc=True).execute()
        orgs = res.data or []
    except Exception:
        # Fallback: fetch without join if FK hint fails
        try:
            res = db.client.table("organizations").select("*").order("created_at", desc=True).execute()
            orgs = res.data or []
        except Exception:
            orgs = []
    return {"organizations": orgs}


# ── Reports (simple data export) ─────────────────────────────────────────────

@router.get("/reports/users")
def report_users(admin_id: str = Depends(require_admin)):
    res = db.client.table("users").select("id, email, name, role, status, created_at").execute()
    return res.data or []


@router.get("/reports/scans")
def report_scans(admin_id: str = Depends(require_admin)):
    res = db.client.table("scans").select(
        "id, status, total_vulnerabilities, critical_count, high_count, created_at, repositories(repo_name)"
    ).order("created_at", desc=True).execute()
    return res.data or []


@router.get("/reports/vulnerabilities")
def report_vulns(admin_id: str = Depends(require_admin)):
    res = db.client.table("vulnerabilities").select(
        "id, severity, vulnerability_type, file_path, is_fixed, detected_at"
    ).order("detected_at", desc=True).execute()
    return res.data or []
