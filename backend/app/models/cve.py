"""
CVE Lookup models
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CVEFinding(BaseModel):
    id: str
    scan_id: str
    package_name: str
    package_version: str
    ecosystem: str
    source_file: str
    cve_id: str
    cvss_score: Optional[float] = None
    severity: str
    description: Optional[str] = None
    fix_version: Optional[str] = None
    reference_url: Optional[str] = None
    source: str  # "osv" | "nvd"
    created_at: datetime

    class Config:
        from_attributes = True


class CVESummary(BaseModel):
    scan_id: str
    total: int
    critical: int
    high: int
    medium: int
    low: int
    unknown: int
    packages_affected: int
    findings: list[CVEFinding]


class PackageRef(BaseModel):
    """Internal: a parsed package name + version from a manifest file."""
    name: str
    version: str
    ecosystem: str   # "pypi" | "npm"
    source_file: str
