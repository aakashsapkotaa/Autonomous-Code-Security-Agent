"""
MCP Orchestrator Agent - Coordinates security scanning workflow
Port: 8001
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import httpx
from supabase_client import supabase

app = FastAPI(title="Orchestrator Agent", version="1.0.0")

class ScanRequest(BaseModel):
    scan_id: str
    repo_url: str

class Orchestrator:
    async def clone_repo(self, repo_url: str) -> str:
        """Clone repository to temporary directory"""
        temp_dir = tempfile.mkdtemp(prefix="secureshift_")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, temp_dir],
                check=True,
                capture_output=True,
                timeout=300
            )
            return temp_dir
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repo: {str(e)}")
    
    async def run_security_tools(self, repo_path: str, scan_id: str) -> list:
        """Run Bandit, TruffleHog, Safety and collect vulnerabilities"""
        vulnerabilities = []
        
        # Run Bandit (Python security)
        try:
            result = subprocess.run(
                ["bandit", "-r", repo_path, "-f", "json", "-o", "/tmp/bandit.json"],
                capture_output=True,
                timeout=300
            )
            if Path("/tmp/bandit.json").exists():
                import json
                with open("/tmp/bandit.json") as f:
                    bandit_data = json.load(f)
                    for issue in bandit_data.get("results", []):
                        vuln = {
                            "scan_id": scan_id,
                            "vulnerability_type": issue["test_id"],
                            "severity": issue["issue_severity"].lower(),
                            "file_path": issue["filename"],
                            "line_number": issue["line_number"],
                            "description": issue["issue_text"],
                            "tool": "bandit"
                        }
                        # Insert into Supabase
                        resp = supabase.table("vulnerabilities").insert(vuln).execute()
                        vuln["id"] = resp.data[0]["id"]
                        vulnerabilities.append(vuln)
        except Exception as e:
            print(f"Bandit scan error: {e}")
        
        # Run TruffleHog (secrets detection)
        try:
            result = subprocess.run(
                ["trufflehog", "filesystem", repo_path, "--json"],
                capture_output=True,
                timeout=300,
                text=True
            )
            for line in result.stdout.splitlines():
                if line.strip():
                    import json
                    secret = json.loads(line)
                    vuln = {
                        "scan_id": scan_id,
                        "vulnerability_type": "secret_exposure",
                        "severity": "high",
                        "file_path": secret.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file", "unknown"),
                        "description": f"Secret detected: {secret.get('DetectorName', 'unknown')}",
                        "tool": "trufflehog"
                    }
                    resp = supabase.table("vulnerabilities").insert(vuln).execute()
                    vuln["id"] = resp.data[0]["id"]
                    vulnerabilities.append(vuln)
        except Exception as e:
            print(f"TruffleHog scan error: {e}")
        
        return vulnerabilities
    
    async def run_scan(self, scan_id: str, repo_url: str):
        """Main orchestration logic"""
        try:
            # 1. Update scan status to 'running'
            supabase.table("scans").update({
                "status": "running",
                "scan_started_at": datetime.utcnow().isoformat()
            }).eq("id", scan_id).execute()
            
            # 2. Clone repo
            repo_path = await self.clone_repo(repo_url)
            
            # 3. Run security tools
            vulnerabilities = await self.run_security_tools(repo_path, scan_id)
            
            # 4. Request fixes from Fixer agent (Fixer will store them in ai_fixes table)
            async with httpx.AsyncClient(timeout=300.0) as client:
                for vuln in vulnerabilities:
                    try:
                        resp = await client.post(
                            "http://localhost:8002/generate-fix",
                            json=vuln  # Includes vuln["id"] for Fixer to store
                        )
                        if resp.status_code == 200:
                            fix_data = resp.json()
                            print(f"✅ Fix generated for vuln {vuln['id']}: confidence {fix_data['confidence']}")
                        else:
                            print(f"⚠️ Fix generation failed for vuln {vuln['id']}: {resp.status_code}")
                    except Exception as e:
                        print(f"❌ Fix generation error for vuln {vuln['id']}: {e}")
            
            # 5. Generate report
            async with httpx.AsyncClient(timeout=300.0) as client:
                try:
                    resp = await client.post(
                        "http://localhost:8003/generate-report",
                        json={"scan_id": scan_id, "vulnerabilities": vulnerabilities}
                    )
                    if resp.status_code == 200:
                        report_url = resp.json()["report_url"]
                        print(f"✅ Report generated: {report_url}")
                except Exception as e:
                    print(f"❌ Report generation error: {e}")
                    report_url = None
            
            # 6. Update scan status to 'completed'
            supabase.table("scans").update({
                "status": "completed",
                "total_vulnerabilities": len(vulnerabilities),
                "scan_completed_at": datetime.utcnow().isoformat()
            }).eq("id", scan_id).execute()
            
            # Cleanup
            shutil.rmtree(repo_path, ignore_errors=True)
            
        except Exception as e:
            # Update scan status to 'failed'
            supabase.table("scans").update({
                "status": "failed",
                "scan_completed_at": datetime.utcnow().isoformat()
            }).eq("id", scan_id).execute()
            raise

orchestrator = Orchestrator()

@app.post("/run-scan")
async def run_scan_endpoint(request: ScanRequest):
    """Trigger security scan orchestration"""
    try:
        await orchestrator.run_scan(request.scan_id, request.repo_url)
        return {"status": "success", "scan_id": request.scan_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "orchestrator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)