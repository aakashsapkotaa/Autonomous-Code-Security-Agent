"""
Profile, Settings, and Notification models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Computed stats
    repo_count: int = 0
    scan_count: int = 0
    vuln_count: int = 0
    fixes_count: int = 0


class SettingsUpdate(BaseModel):
    theme: Optional[str] = None                    # dark | light | system
    notify_scan_complete: Optional[bool] = None
    notify_critical_vuln: Optional[bool] = None
    notify_pr_created: Optional[bool] = None
    github_token: Optional[str] = None
    nvd_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None


class SettingsResponse(BaseModel):
    theme: str = "dark"
    notify_scan_complete: bool = True
    notify_critical_vuln: bool = True
    notify_pr_created: bool = True
    github_token_set: bool = False     # never return the actual token
    nvd_api_key_set: bool = False
    openrouter_api_key_set: bool = False


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


class NotificationsListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int


class MarkReadRequest(BaseModel):
    notification_ids: Optional[list[str]] = None   # None = mark all
