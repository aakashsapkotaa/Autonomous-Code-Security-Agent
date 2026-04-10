"""
Scan management endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.services.scanner import scanner
from app.core.db import db
from datetime import datetime
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ScanTriggerRequest(BaseModel):
    scan_id: str
    repo_url: str
    repo_id: str

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str

# MCP Orchestrator URL
ORCHESTRATOR_URL = os.getenv("MCP_ORCHESTRATOR_URL", "http://localhost:8001")

async def run_scan_background(scan_id: str, repo_url: str):
    """
    Background task to run security scan
    """
    try:
        logger.info(f"Starting scan {scan_id} for {repo_url}")
        
        # Update scan status to running
        db.update_scan(scan_id, {"status": "running"})
        
        # Run security scanner
        vulnerabilities = await scanner.scan_repository(repo_url)
        
        logger.info(f"Found {len(vulnerabilities)} vulnerabilities")
        
        # Store vulnerabilities in database
        for vuln in vulnerabilities:
            vuln_data = {
                "scan_id": scan_id,
                "file_path": vuln.get("file_path", ""),
                "vulnerability_type": vuln.get("vulnerability_type", ""),
                "severity": vuln.get("severity", "low"),
                "description": vuln.get("description", ""),
                "line_number": vuln.get("line_number"),
                "tool": vuln.get("tool", "unknown"),
            }
            
            # Create vulnerability record
            vuln_record = db.create_vulnerability(vuln_data)
            
            if vuln_record:
                logger.info(f"Created vulnerability: {vuln_record['id']}")
                
                # Try to generate AI fix using OpenRouter
                try:
                    from mcp_agents.fixer.openrouter_client import OpenRouterClient
                    fixer = OpenRouterClient()
                    
                    fix_result = await fixer.generate_fix(
                        vuln.get("vulnerability_type", ""),
                        vuln.get("severity", "low"),
                        vuln.get("file_path", ""),
                        vuln.get("description", ""),
                        vuln.get("code_snippet")
                    )
                    
                    # Store AI fix
                    fix_data = {
                        "vulnerability_id": vuln_record['id'],
                        "suggested_fix": fix_result.get("suggested_fix", ""),
                        "ai_model": "openrouter",
                        "confidence_score": fix_result.get("confidence", 0.5),
                    }
                    db.create_ai_fix(fix_data)
                    logger.info(f"Created AI fix for vulnerability {vuln_record['id']}")
                    
                except Exception as fix_error:
                    logger.error(f"Error generating AI fix: {fix_error}")
        
        # Update scan status to completed
        db.update_scan(scan_id, {
            "status": "completed",
            "total_vulnerabilities": len(vulnerabilities),
            "scan_completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Scan {scan_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error running scan {scan_id}: {e}")
        # Update scan status to failed
        db.update_scan(scan_id, {
            "status": "failed",
            "scan_completed_at": datetime.utcnow().isoformat()
        })

@router.post("/trigger", response_model=ScanResponse)
async def trigger_scan(request: ScanTriggerRequest, background_tasks: BackgroundTasks):
    """
    Trigger a security scan for a repository
    
    This endpoint:
    1. Validates the scan exists
    2. Starts the scan in the background
    3. Runs security tools (Bandit, TruffleHog, Safety)
    4. Stores vulnerabilities
    5. Generates AI fixes
    """
    try:
        logger.info(f"Received scan trigger request: scan_id={request.scan_id}, repo_url={request.repo_url}")
        
        # Verify scan exists
        scan = db.get_scan(request.scan_id)
        if not scan:
            logger.error(f"Scan not found: {request.scan_id}")
            raise HTTPException(status_code=404, detail="Scan not found")
        
        logger.info(f"Scan found, starting background task")
        
        # Add background task to run the scan
        background_tasks.add_task(run_scan_background, request.scan_id, request.repo_url)
        
        logger.info(f"Background task added successfully")
        
        return ScanResponse(
            scan_id=request.scan_id,
            status="running",
            message="Scan started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering scan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scan_id}")
async def get_scan_status(scan_id: str):
    """
    Get scan status and results
    """
    try:
        scan = db.get_scan(scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Get vulnerabilities for this scan
        vulnerabilities = db.get_vulnerabilities(scan_id)
        
        # Get AI fixes for each vulnerability
        for vuln in vulnerabilities:
            fixes = db.get_ai_fixes(vuln['id'])
            vuln['ai_fixes'] = fixes
        
        return {
            "scan": scan,
            "vulnerabilities": vulnerabilities
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
