"""
Scan service - Business logic for scanning operations
"""
from app.core.db import db
from app.models.scan import ScanRequest, ScanResponse, ScanStatus
from datetime import datetime
from typing import Optional, Dict
import logging
import re

logger = logging.getLogger(__name__)

class ScanService:
    """Service for managing security scans"""
    
    @staticmethod
    def validate_github_url(url: str) -> bool:
        """Validate GitHub repository URL"""
        pattern = r'^https?://github\.com/[\w-]+/[\w.-]+/?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def extract_repo_name(url: str) -> str:
        """Extract repository name from URL"""
        parts = url.rstrip('/').split('/')
        return parts[-1] if parts else "unknown"
    
    async def create_scan(self, request: ScanRequest) -> ScanResponse:
        """
        Create a new security scan
        
        Steps:
        1. Validate repository URL
        2. Create or get repository record
        3. Create scan record
        4. Queue Celery task
        5. Return scan ID
        """
        try:
            # Validate URL
            if not self.validate_github_url(request.repo_url):
                return ScanResponse(
                    scan_id="",
                    status=ScanStatus.FAILED,
                    message="Invalid GitHub repository URL"
                )
            
            # Extract repo name
            repo_name = self.extract_repo_name(request.repo_url)
            
            # Create or get repository
            repo_data = {
                "user_id": request.user_id,
                "repo_url": request.repo_url,
                "repo_name": repo_name
            }
            
            repo = await db.create_repository(repo_data)
            if not repo:
                return ScanResponse(
                    scan_id="",
                    status=ScanStatus.FAILED,
                    message="Failed to create repository record"
                )
            
            # Create scan record
            scan_data = {
                "repo_id": repo["id"],
                "status": ScanStatus.PENDING.value,
                "scan_started_at": datetime.utcnow().isoformat()
            }
            
            scan = await db.create_scan(scan_data)
            if not scan:
                return ScanResponse(
                    scan_id="",
                    status=ScanStatus.FAILED,
                    message="Failed to create scan record"
                )
            
            # Log scan creation
            await db.create_scan_log(
                scan["id"],
                f"Scan created for repository: {repo_name}",
                "info"
            )
            
            # TODO: Implement actual scanning logic
            # For now, just return pending status
            # In production, this would trigger a background job
            
            return ScanResponse(
                scan_id=scan["id"],
                status=ScanStatus.PENDING,
                message="Scan queued successfully",
                repo_id=repo["id"]
            )
            
        except Exception as e:
            logger.error(f"Error creating scan: {e}")
            return ScanResponse(
                scan_id="",
                status=ScanStatus.FAILED,
                message=f"Internal error: {str(e)}"
            )
    
    async def get_scan_details(self, scan_id: str) -> Optional[Dict]:
        """Get scan details with vulnerabilities"""
        scan = await db.get_scan(scan_id)
        if not scan:
            return None
        
        vulnerabilities = await db.get_vulnerabilities(scan_id)
        
        return {
            **scan,
            "vulnerabilities": vulnerabilities
        }
    
    async def update_scan_status(
        self,
        scan_id: str,
        status: ScanStatus,
        total_vulnerabilities: int = 0
    ) -> bool:
        """Update scan status"""
        data = {
            "status": status.value,
            "total_vulnerabilities": total_vulnerabilities
        }
        
        if status == ScanStatus.COMPLETED:
            data["scan_completed_at"] = datetime.utcnow().isoformat()
        
        return await db.update_scan(scan_id, data)

scan_service = ScanService()
