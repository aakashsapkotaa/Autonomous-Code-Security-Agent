"""
Ollama-based security scanning using LLM
"""
import httpx
from typing import Dict, List

class OllamaSecurityScanner:
    """
    Uses Ollama LLM to analyze code for security issues
    """
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.model = "deepseek-coder:6.7b"
    
    async def analyze_code(self, code: str, language: str = "python") -> Dict:
        """
        Analyze code for security vulnerabilities using LLM
        """
        prompt = f"""
Analyze the following {language} code for security vulnerabilities:

```{language}
{code}
```

Identify:
1. Security vulnerabilities
2. Severity (critical/high/medium/low)
3. Recommended fixes

Format as JSON.
"""
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error analyzing code: {e}")
                return {}

if __name__ == "__main__":
    import asyncio
    
    async def test():
        scanner = OllamaSecurityScanner()
        code = """
import os
password = "hardcoded_password"
os.system(f"echo {user_input}")
"""
        result = await scanner.analyze_code(code)
        print(result)
    
    asyncio.run(test())
