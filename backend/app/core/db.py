"""
Database connection and operations using Supabase
"""
from supabase import create_client, Client
from app.core.config import settings
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    """Supabase database client"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.https://ayeoqnvldhrazjpvbrey.supabase.co,
            settings.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF5ZW9xbnZsZGhyYXpqcHZicmV5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTY2MzI0MCwiZXhwIjoyMDkxMjM5MjQwfQ.w3RZhHch0qRfsQtEx4mgMuJVeRT69CvPLNeDIWXXPYw
        )
    
    async def create_repository(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new repository"""
        try:
            response = self.client.table("repositories").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            return None
    
    async def get_repository(self, repo_id: str) -> Optional[Dict]:
        """Get repository by ID"""
        try:
            response = self.client.table("repositories").select("*").eq("id", repo_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            return None
    
    async def list_repositories(self, user_id: Optional[str] = None) -> List[Dict]:
        """List repositories, optionally filtered by user"""
        try:
            query = self.client.table("repositories").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            response = query.order("created_at", desc=True).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return []
    
    async def create_scan(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new scan"""
        try:
            response = self.client.table("scans").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating scan: {e}")
            return None
    
    async def get_scan(self, scan_id: str) -> Optional[Dict]:
        """Get scan by ID"""
        try:
            response = self.client.table("scans").select("*").eq("id", scan_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting scan: {e}")
            return None
    
    async def update_scan(self, scan_id: str, data: Dict[str, Any]) -> bool:
        """Update scan status"""
        try:
            self.client.table("scans").update(data).eq("id", scan_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating scan: {e}")
            return False
    
    async def create_vulnerability(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a vulnerability"""
        try:
            response = self.client.table("vulnerabilities").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating vulnerability: {e}")
            return None
    
    async def get_vulnerabilities(self, scan_id: str) -> List[Dict]:
        """Get vulnerabilities for a scan"""
        try:
            response = self.client.table("vulnerabilities").select("*").eq("scan_id", scan_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting vulnerabilities: {e}")
            return []
    
    async def create_ai_fix(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create an AI fix"""
        try:
            response = self.client.table("ai_fixes").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating AI fix: {e}")
            return None
    
    async def get_ai_fixes(self, vulnerability_id: str) -> List[Dict]:
        """Get AI fixes for a vulnerability"""
        try:
            response = self.client.table("ai_fixes").select("*").eq("vulnerability_id", vulnerability_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting AI fixes: {e}")
            return []
    
    async def create_scan_log(self, scan_id: str, message: str, level: str = "info") -> bool:
        """Create a scan log entry"""
        try:
            self.client.table("scan_logs").insert({
                "scan_id": scan_id,
                "log_message": message,
                "log_level": level
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error creating scan log: {e}")
            return False

# Global database instance
db = Database()
