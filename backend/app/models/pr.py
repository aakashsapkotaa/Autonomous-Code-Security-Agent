"""
PR Agent request / response models
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class CreatePRRequest(BaseModel):
    scan_id: str = Field(..., description="UUID of the completed scan")
    repo_url: str = Field(..., description="Full GitHub HTTPS URL of the repository")
    base_branch: str = Field("main", description="Branch to open the PR against")
    github_token: Optional[str] = Field(
        None,
        description="Per-request GitHub PAT. Falls back to server GITHUB_TOKEN env var.",
    )


class CreatePRResponse(BaseModel):
    pr_url: str
    pr_number: int
    branch: str
    base_branch: str
    files_changed: list[str]
    fixes_applied: int
    total_vulnerabilities: int
