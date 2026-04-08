"""
Celery Worker for Background Tasks
Handles asynchronous security scanning
"""
from celery import Celery
from app.core.config import settings
import httpx
import asyncio

celery_app = Celery(
    "secureshift",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
)

@celery_app.task(bind=True, name="scan_repository")
def scan_repository(self, scan_id: str, repo_url: str):
    """
    Background task to trigger orchestrator agent for security scanning
    """
    try:
        # Call orchestrator agent synchronously
        async def call_orchestrator():
            async with httpx.AsyncClient(timeout=3600.0) as client:
                response = await client.post(
                    f"{settings.MCP_ORCHESTRATOR_URL}/run-scan",
                    json={"scan_id": scan_id, "repo_url": repo_url}
                )
                response.raise_for_status()
                return response.json()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(call_orchestrator())
        loop.close()
        
        return {
            "status": "success",
            "scan_id": scan_id,
            "result": result
        }
    
    except Exception as e:
        # Update scan status to failed
        from app.core.db import SupabaseDB
        db = SupabaseDB()
        db.update_scan(scan_id, {"status": "failed"})
        
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(name="cleanup_old_scans")
def cleanup_old_scans():
    """Periodic task to cleanup old scan data"""
    from app.core.db import SupabaseDB
    from datetime import datetime, timedelta
    
    db = SupabaseDB()
    cutoff_date = (datetime.utcnow() - timedelta(days=90)).isoformat()
    
    # Delete scans older than 90 days
    db.supabase.table("scans").delete().lt("created_at", cutoff_date).execute()
    
    return {"status": "cleanup_completed", "cutoff_date": cutoff_date}

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    'cleanup-old-scans': {
        'task': 'cleanup_old_scans',
        'schedule': 86400.0,  # Run daily
    },
}