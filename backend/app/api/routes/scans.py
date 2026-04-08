"""
Scan management endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.scan import ScanRequest, ScanResponse
from app.services.scan_service import scan_service
from app.core.db import db
from typing import List, Dict

router = APIRouter()

@router.post("/", response_model=ScanResponse)
async def create_scan(scan_request: ScanRequest):
    """
    Start a new security scan for a repository
    
    - Validates GitHub URL
    - Creates scan record
    - Queues Celery task
    - Returns scan ID
    """
    result = await scan_service.create_scan(scan_request)
    
    if not result.scan_id:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@router.get("/{scan_id}")
async def get_scan(scan_id: str) -> Dict:
    """
    Get scan details and results
    """
    scan = await scan_service.get_scan_details(scan_id)
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan

@router.get("/{scan_id}/vulnerabilities")
async def get_scan_vulnerabilities(scan_id: str) -> List[Dict]:
    """
    Get vulnerabilities found in a scan
    """
    vulnerabilities = await db.get_vulnerabilities(scan_id)
    return vulnerabilities
