"""Admin dashboard Pydantic models"""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class AdminOverview(BaseModel):
    total_users: int
    active_users: int
    suspended_users: int
    total_repositories: int
    total_scans: int
    running_scans: int
    failed_scans: int
    completed_scans: int
    total_vulnerabilities: int
    critical_vulnerabilities: int
    ai_fixes_generated: int
    pull_requests_created: int
    scans_today: int
    vulns_today: int


class AdminUser(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    status: str
    repo_count: int = 0
    scan_count: int = 0
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class AdminUserUpdate(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None
    name: Optional[str] = None


class AdminScan(BaseModel):
    id: str
    repo_id: str
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    owner_email: Optional[str] = None
    status: str
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    scan_started_at: Optional[datetime] = None
    scan_completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class AdminVulnerability(BaseModel):
    id: str
    scan_id: str
    repo_name: Optional[str] = None
    file_path: str
    vulnerability_type: str
    severity: str
    description: str
    line_number: Optional[int] = None
    tool: Optional[str] = None
    cvss_score: Optional[float] = None
    is_fixed: bool = False
    detected_at: Optional[datetime] = None


class AdminPR(BaseModel):
    scan_id: str
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    pr_url: Optional[str] = None
    owner_email: Optional[str] = None
    created_at: Optional[datetime] = None


class AuditLog(BaseModel):
    id: str
    actor_id: Optional[str] = None
    actor_email: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    metadata: dict = {}
    ip_address: Optional[str] = None
    created_at: datetime


class SystemSettings(BaseModel):
    github_token: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    nvd_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    max_concurrent_scans: Optional[int] = None


class SystemSettingsResponse(BaseModel):
    github_token_set: bool
    openrouter_api_key_set: bool
    nvd_api_key_set: bool
    openrouter_model: str
    max_concurrent_scans: int


class DailyCount(BaseModel):
    date: str
    count: int


class AnalyticsData(BaseModel):
    scans_per_day: list[DailyCount]
    vulns_per_day: list[DailyCount]
    severity_breakdown: dict[str, int]
    top_repos: list[dict]
    scan_status_breakdown: dict[str, int]
