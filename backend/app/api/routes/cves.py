"""
CVE Lookup endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.core.db import SupabaseDB, get_database
from app.models.cve import CVESummary, CVEFinding
from app.services.cve_lookup import cve_agent

router = APIRouter()


# ── GET /api/cves/{scan_id} ───────────────────────────────────────────────────

@router.get("/{scan_id}", response_model=CVESummary, summary="Get CVE findings for a scan")
async def get_cve_findings(scan_id: str, db: SupabaseDB = Depends(get_database)):
    """
    Return all CVE findings stored for a completed scan.
    If no findings exist yet, returns an empty summary (does NOT trigger a new lookup).
    Use POST /api/cves/{scan_id}/run to trigger a fresh lookup.
    """
    scan = db.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found")

    try:
        resp = db.client.table("cve_findings") \
            .select("*") \
            .eq("scan_id", scan_id) \
            .order("cvss_score", desc=True) \
            .execute()

        findings = [CVEFinding(**row) for row in (resp.data or [])]
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
        for f in findings:
            counts[f.severity if f.severity in counts else "unknown"] += 1

        return CVESummary(
            scan_id=scan_id,
            total=len(findings),
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            unknown=counts["unknown"],
            packages_affected=len({f.package_name for f in findings}),
            findings=findings,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching CVE findings: {e}")


# ── POST /api/cves/{scan_id}/run ──────────────────────────────────────────────

class RunCVERequest(BaseModel):
    repo_path: Optional[str] = None
    manifest_contents: Optional[dict[str, str]] = None


@router.post("/{scan_id}/run", response_model=CVESummary, summary="Run CVE lookup for a scan")
async def run_cve_lookup(
    scan_id: str,
    body: RunCVERequest,
    db: SupabaseDB = Depends(get_database),
):
    """
    Trigger a CVE lookup for the given scan.

    Supply either:
    - `repo_path`          — absolute path to a locally cloned repo, OR
    - `manifest_contents`  — dict of `{filename: raw_content}` for each manifest
                             (useful when the repo is not cloned locally).

    The agent will:
    1. Parse all dependency manifests it finds.
    2. Query OSV.dev (batch) + NVD (per CVE-ID) concurrently.
    3. Persist results to `cve_findings` table.
    4. Return the full CVESummary.
    """
    scan = db.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found")

    if not body.repo_path and not body.manifest_contents:
        raise HTTPException(
            status_code=422,
            detail="Provide either 'repo_path' or 'manifest_contents'.",
        )

    try:
        summary = await cve_agent.run(
            scan_id=scan_id,
            repo_path=body.repo_path,
            manifest_contents=body.manifest_contents,
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CVE lookup failed: {e}")


# ── GET /api/cves/{scan_id}/package/{package_name} ────────────────────────────

@router.get(
    "/{scan_id}/package/{package_name}",
    response_model=list[CVEFinding],
    summary="Get CVEs for a specific package in a scan",
)
async def get_cves_for_package(
    scan_id: str,
    package_name: str,
    db: SupabaseDB = Depends(get_database),
):
    try:
        resp = db.client.table("cve_findings") \
            .select("*") \
            .eq("scan_id", scan_id) \
            .eq("package_name", package_name.lower()) \
            .order("cvss_score", desc=True) \
            .execute()
        return [CVEFinding(**row) for row in (resp.data or [])]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
