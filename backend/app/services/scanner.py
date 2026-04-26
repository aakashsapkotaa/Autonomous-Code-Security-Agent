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
        """Clone a GitHub repository (shallow, single-branch for speed)."""
        try:
            self.temp_dir = tempfile.mkdtemp()
            logger.info(f"Cloning {repo_url}")

            # --single-branch + --depth 1 = fastest possible clone
            cmd = [
                "git", "clone",
                "--depth", "1",
                "--single-branch",
                "--branch", branch,
                "--no-tags",
                repo_url, self.temp_dir,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return self.temp_dir

            # Retry without explicit branch (uses default branch)
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = tempfile.mkdtemp()
            cmd = ["git", "clone", "--depth", "1", "--single-branch", "--no-tags",
                   repo_url, self.temp_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return self.temp_dir

            logger.error(f"Clone failed: {result.stderr}")
            return None
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return None
    
    async def run_bandit(self, repo_path: str) -> List[Dict]:
        """Run Bandit Python security scanner."""
        try:
            # Write to a temp file in the same temp dir (avoids /tmp on Windows)
            report_path = os.path.join(repo_path, "_bandit_report.json")
            cmd = [
                "bandit", "-r", repo_path,
                "-f", "json",
                "-o", report_path,
                "--quiet",
                "--skip", "B101",   # skip assert warnings — too noisy
            ]
            subprocess.run(cmd, capture_output=True, timeout=120)

            if os.path.exists(report_path):
                with open(report_path, "r") as f:
                    data = json.load(f)
                os.remove(report_path)
                return self._parse_bandit_results(data)
            return []
        except Exception as e:
            logger.error(f"Bandit error: {e}")
            return []
    
    def _parse_bandit_results(self, data: Dict) -> List[Dict]:
        """Parse Bandit JSON output"""
        vulnerabilities = []
        for result in data.get("results", []):
            vulnerabilities.append({
                "file_path":          result.get("filename", ""),
                "vulnerability_type": result.get("test_id", ""),
                "severity":           result.get("issue_severity", "low").lower(),
                "description":        result.get("issue_text", ""),
                "line_number":        result.get("line_number"),
                "code_snippet":       result.get("code", ""),   # ← was missing
                "tool":               "bandit",
            })
        return vulnerabilities
    
    async def run_trufflehog(self, repo_path: str) -> List[Dict]:
        """Run TruffleHog secret scanner"""
        try:
            # Check if trufflehog is available
            check_cmd = ["trufflehog", "--version"]
            check_result = subprocess.run(check_cmd, capture_output=True, timeout=5)
            
            if check_result.returncode != 0:
                logger.warning("TruffleHog not installed, skipping secret scanning")
                return []
            
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
        except FileNotFoundError:
            logger.warning("TruffleHog not found in PATH, skipping secret scanning")
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
        """Run Safety dependency checker."""
        try:
            req_file = os.path.join(repo_path, "requirements.txt")
            if not os.path.exists(req_file):
                return []
            cmd = ["safety", "check", "--file", req_file, "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.stdout:
                return self._parse_safety_results(result.stdout)
            return []
        except Exception as e:
            logger.error(f"Safety error: {e}")
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
        """Run all security scans on a repository."""
        all_vulnerabilities = []
        self.temp_dir = None   # reset so caller can read it after scan

        try:
            repo_path = await self.clone_repository(repo_url, branch)
            if not repo_path:
                logger.error("Failed to clone repository")
                return []

            logger.info(f"Repository cloned to: {repo_path}")
            
            # Run all scanners
            logger.info("Running Bandit...")
            try:
                bandit_results = await self.run_bandit(repo_path)
                all_vulnerabilities.extend(bandit_results)
                logger.info(f"Bandit found {len(bandit_results)} issues")
            except Exception as e:
                logger.error(f"Bandit scan failed: {e}")
            
            logger.info("Running TruffleHog...")
            try:
                trufflehog_results = await self.run_trufflehog(repo_path)
                all_vulnerabilities.extend(trufflehog_results)
                logger.info(f"TruffleHog found {len(trufflehog_results)} secrets")
            except Exception as e:
                logger.error(f"TruffleHog scan failed: {e}")
            
            logger.info("Running Safety...")
            try:
                safety_results = await self.run_safety(repo_path)
                all_vulnerabilities.extend(safety_results)
                logger.info(f"Safety found {len(safety_results)} vulnerable dependencies")
            except Exception as e:
                logger.error(f"Safety scan failed: {e}")
            
            logger.info(f"Total vulnerabilities found: {len(all_vulnerabilities)}")
            
        except Exception as e:
            logger.error(f"Error during scan: {e}", exc_info=True)
        finally:
            # Cleanup - use more aggressive cleanup for Windows
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    # On Windows, we need to handle read-only files
                    def handle_remove_readonly(func, path, exc):
                        import stat
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    
                    shutil.rmtree(self.temp_dir, onerror=handle_remove_readonly)
                    logger.info(f"Cleaned up temp directory: {self.temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory: {e}")
        
        return all_vulnerabilities

scanner = SecurityScanner()
