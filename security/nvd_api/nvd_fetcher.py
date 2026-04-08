"""
NVD API client for fetching CVE information
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime

class NVDFetcher:
    """
    Fetches CVE data from the National Vulnerability Database
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["apiKey"] = api_key
    
    async def search_cve(self, cve_id: str) -> Optional[Dict]:
        """
        Search for a specific CVE by ID
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}",
                    params={"cveId": cve_id},
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("vulnerabilities", [{}])[0]
            except Exception as e:
                print(f"Error fetching CVE {cve_id}: {e}")
                return None
    
    async def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        Search CVEs by keyword
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}",
                    params={
                        "keywordSearch": keyword,
                        "resultsPerPage": limit
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("vulnerabilities", [])
            except Exception as e:
                print(f"Error searching CVEs: {e}")
                return []

if __name__ == "__main__":
    import asyncio
    
    async def test():
        fetcher = NVDFetcher()
        cve = await fetcher.search_cve("CVE-2021-44228")  # Log4Shell
        print(f"Found CVE: {cve}")
    
    asyncio.run(test())
