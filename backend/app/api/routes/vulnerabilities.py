"""
Vulnerability management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from app.core.db import SupabaseDB, get_database
from app.models.vulnerability import VulnerabilityWithFix, AIFix

router = APIRouter()


def validate_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


@router.get("/scan/{scan_id}", response_model=List[VulnerabilityWithFix])
async def get_vulnerabilities_by_scan(scan_id: str, db: SupabaseDB = Depends(get_database)):
    """Get all vulnerabilities for a scan with their AI fixes"""
    try:
        vuln_data = db.client.table("vulnerabilities").select("*").eq("scan_id", scan_id).execute()
        if not vuln_data.data:
            return []
        result = []
        for vuln in vuln_data.data:
            fix_data = db.client.table("ai_fixes").select("*").eq("vulnerability_id", vuln["id"]).execute()
            ai_fix = AIFix(**fix_data.data[0]) if fix_data.data else None
            result.append(VulnerabilityWithFix(**vuln, ai_fix=ai_fix))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vulnerabilities: {str(e)}")


@router.get("/{vulnerability_id}/fixes", response_model=List[AIFix])
async def get_ai_fixes(vulnerability_id: str, db: SupabaseDB = Depends(get_database)):
    """Get all AI-generated fixes for a vulnerability"""
    try:
        fix_data = db.client.table("ai_fixes").select("*").eq("vulnerability_id", vulnerability_id).execute()
        return [AIFix(**fix) for fix in fix_data.data] if fix_data.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching AI fixes: {str(e)}")


@router.get("/{vulnerability_id}", response_model=VulnerabilityWithFix)
async def get_vulnerability_with_fix(vulnerability_id: str, db: SupabaseDB = Depends(get_database)):
    """Get vulnerability details with associated AI fix"""
    if not validate_uuid(vulnerability_id):
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    try:
        vuln_data = db.client.table("vulnerabilities").select("*").eq("id", vulnerability_id).execute()
        if not vuln_data.data:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
        vulnerability = vuln_data.data[0]
        fix_data = db.client.table("ai_fixes").select("*").eq("vulnerability_id", vulnerability_id).execute()
        ai_fix = AIFix(**fix_data.data[0]) if fix_data.data else None
        return VulnerabilityWithFix(**vulnerability, ai_fix=ai_fix)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vulnerability: {str(e)}")


@router.post("/{vulnerability_id}/apply-fix")
async def apply_fix(vulnerability_id: str, fix_id: str, db: SupabaseDB = Depends(get_database)):
    """Mark an AI fix as applied"""
    try:
        result = db.client.table("ai_fixes").update({
            "is_applied": True,
            "applied_at": "now()"
        }).eq("id", fix_id).eq("vulnerability_id", vulnerability_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Fix not found")
        return {"status": "success", "message": "Fix marked as applied"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying fix: {str(e)}")
