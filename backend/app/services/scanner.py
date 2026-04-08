"""
Security scanner service - Integrates all security tools
"""
import subprocess
import json
import tempfile
import os
import shutil
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SecurityScanner:
    """Integrates Bandit, TruffleHog, Safety, and NVD API"""
    
    def __init__(self):
        self.temp_dir = None
    
    async def clone_repository(self, repo_url: str, branch: str = "main") -> Optional[str]:
        """Clone a GitHub repository"""
        try:
            self.temp_dir = tempfile.mkdtemp()
            cmd = ["git", "clone", "--depth", "1", "--branch", branch, repo_url, self.temp_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Successfully cloned {repo_url}")
                return self.temp_dir
            else:
                logger.error(f"Failed to clone repository: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return None
    
    async def run_bandit(self, repo_path: str) -> List[Dict]:
        """Run Bandit Python security scanner"""
        try:
            cmd = [
                "bandit",
                "-r", repo_path,
                "-f", "json",
                "-o", "/tmp/bandit-report.json"
            ]
            subprocess.run(cmd, capture_output=True, timeout=300)
            
            # Read results
            if os.path.exists("/tmp/bandit-report.json"):
                with open("/tmp/bandit-report.json", "r") as f:
                    data = json.load(f)
                    return self._parse_bandit_results(data)
            return []
        except Exception as e:
            logger.error(f"Error running Bandit: {e}")
            return []
    
    def _parse_bandit_results(self, data: Dict) -> List[Dict]:
        """Parse Bandit JSON output"""
        vulnerabilities = []
        for result in data.get("results", []):
            vulnerabilities.append({
                "file_path": result.get("filename", ""),
                "vulnerability_type": result.get("test_id", ""),
                "severity": result.get("issue_severity", "low").lower(),
                "description": result.get("issue_text", ""),
                "line_number": result.get("line_number"),
                "code_snippet": result.get("code", ""),
                "tool": "bandit"
            })
        return vulnerabilities
    
    async def run_trufflehog(self, repo_path: str) -> List[Dict]:
        """Run TruffleHog secret scanner"""
        try:
            cmd = [
                "trufflehog",
                "filesystem",
                repo_path,
                "--json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return self._parse_trufflehog_results(result.stdout)
            return []
        except Exception as e:
            logger.error(f"Error running TruffleHog: {e}")
            return []
    
    def _parse_trufflehog_results(self, output: str) -> List[Dict]:
        """Parse TruffleHog output"""
        vulnerabilities = []
        for line in output.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    vulnerabilities.append({
                        "file_path": data.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file", ""),
                        "vulnerability_type": "secret_exposure",
                        "severity": "high",
                        "description": f"Secret found: {data.get('DetectorName', 'Unknown')}",
                        "line_number": data.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line", 0),
                        "code_snippet": data.get("Raw", ""),
                        "tool": "trufflehog"
                    })
                except json.JSONDecodeError:
                    continue
        return vulnerabilities
    
    async def run_safety(self, repo_path: str) -> List[Dict]:
        """Run Safety dependency checker"""
        try:
            # Look for requirements.txt
            req_file = os.path.join(repo_path, "requirements.txt")
            if not os.path.exists(req_file):
                return []
            
            cmd = ["safety", "check", "--file", req_file, "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.stdout:
                return self._parse_safety_results(result.stdout)
            return []
        except Exception as e:
            logger.error(f"Error running Safety: {e}")
            return []
    
    def _parse_safety_results(self, output: str) -> List[Dict]:
        """Parse Safety JSON output"""
        vulnerabilities = []
        try:
            data = json.loads(output)
            for vuln in data:
                vulnerabilities.append({
                    "file_path": "requirements.txt",
                    "vulnerability_type": "dependency_vulnerability",
                    "severity": "medium",
                    "description": f"{vuln.get('package', 'Unknown')}: {vuln.get('advisory', '')}",
                    "line_number": None,
                    "code_snippet": vuln.get('package', ''),
                    "tool": "safety"
                })
        except json.JSONDecodeError:
            pass
        return vulnerabilities
    
    async def scan_repository(self, repo_url: str, branch: str = "main") -> List[Dict]:
        """
        Run all security scans on a repository
        
        Returns list of vulnerabilities from all tools
        """
        all_vulnerabilities = []
        
        try:
            # Clone repository
            repo_path = await self.clone_repository(repo_url, branch)
            if not repo_path:
                return []
            
            # Run all scanners
            logger.info("Running Bandit...")
            bandit_results = await self.run_bandit(repo_path)
            all_vulnerabilities.extend(bandit_results)
            
            logger.info("Running TruffleHog...")
            trufflehog_results = await self.run_trufflehog(repo_path)
            all_vulnerabilities.extend(trufflehog_results)
            
            logger.info("Running Safety...")
            safety_results = await self.run_safety(repo_path)
            all_vulnerabilities.extend(safety_results)
            
            logger.info(f"Total vulnerabilities found: {len(all_vulnerabilities)}")
            
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        
        return all_vulnerabilities

scanner = SecurityScanner()
