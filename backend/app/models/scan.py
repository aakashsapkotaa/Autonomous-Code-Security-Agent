"""
Scan models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ScanRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL")
    user_id: str = Field(..., description="User ID")
    branch: Optional[str] = Field(default="main", description="Branch to scan")

class ScanResponse(BaseModel):
    scan_id: str
    status: ScanStatus
    message: str
    repo_id: Optional[str] = None

class ScanDetail(BaseModel):
    id: str
    repo_id: str
    status: ScanStatus
    total_vulnerabilities: int = 0
    scan_started_at: Optional[datetime] = None
    scan_completed_at: Optional[datetime] = None
    created_at: datetime
