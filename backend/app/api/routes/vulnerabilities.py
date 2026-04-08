"""
Vulnerability management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.core.db import SupabaseDB
from app.models.vulnerability import Vulnerability, VulnerabilityWithFix, AIFix

router = APIRouter()

@router.get("/{vulnerability_id}", response_model=VulnerabilityWithFix)
async def get_vulnerability_with_fix(vulnerability_id: str, db: SupabaseDB = Depends()):
    """
    Get vulnerability details with associated AI fix
    """
    try:
        # Get vulnerability
        vuln_data = db.supabase.table("vulnerabilities").select("*").eq("id", vulnerability_id).execute()
        
        if not vuln_data.data:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
        
        vulnerability = vuln_data.data[0]
        
        # Get associated AI fix (if any)
        fix_data = db.supabase.table("ai_fixes").select("*").eq("vulnerability_id", vulnerability_id).execute()
        
        ai_fix = None
        if fix_data.data:
            ai_fix = AIFix(**fix_data.data[0])
        
        return VulnerabilityWithFix(
            **vulnerability,
            ai_fix=ai_fix
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vulnerability: {str(e)}")

@router.get("/scan/{scan_id}", response_model=List[VulnerabilityWithFix])
async def get_vulnerabilities_by_scan(scan_id: str, db: SupabaseDB = Depends()):
    """
    Get all vulnerabilities for a scan with their AI fixes
    """
    try:
        # Get all vulnerabilities for the scan
        vuln_data = db.supabase.table("vulnerabilities").select("*").eq("scan_id", scan_id).execute()
        
        if not vuln_data.data:
            return []
        
        vulnerabilities_with_fixes = []
        
        for vuln in vuln_data.data:
            # Get AI fix for this vulnerability
            fix_data = db.supabase.table("ai_fixes").select("*").eq("vulnerability_id", vuln["id"]).execute()
            
            ai_fix = None
            if fix_data.data:
                ai_fix = AIFix(**fix_data.data[0])
            
            vulnerabilities_with_fixes.append(
                VulnerabilityWithFix(
                    **vuln,
                    ai_fix=ai_fix
                )
            )
        
        return vulnerabilities_with_fixes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vulnerabilities: {str(e)}")

@router.get("/{vulnerability_id}/fixes", response_model=List[AIFix])
async def get_ai_fixes(vulnerability_id: str, db: SupabaseDB = Depends()):
    """
    Get all AI-generated fixes for a vulnerability
    """
    try:
        fix_data = db.supabase.table("ai_fixes").select("*").eq("vulnerability_id", vulnerability_id).execute()
        
        if not fix_data.data:
            return []
        
        return [AIFix(**fix) for fix in fix_data.data]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching AI fixes: {str(e)}")

@router.post("/{vulnerability_id}/apply-fix")
async def apply_fix(vulnerability_id: str, fix_id: str, db: SupabaseDB = Depends()):
    """
    Mark an AI fix as applied and store the fixed code
    """
    try:
        # Update the ai_fix record with applied status
        # This could be extended to actually apply the fix to the repository
        result = db.supabase.table("ai_fixes").update({
            "applied": True,
            "applied_at": "now()"
        }).eq("id", fix_id).eq("vulnerability_id", vulnerability_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Fix not found")
        
        return {"status": "success", "message": "Fix marked as applied"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying fix: {str(e)}")
