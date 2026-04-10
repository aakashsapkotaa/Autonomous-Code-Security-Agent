"""
OpenRouter AI Client - Alternative to Ollama for AI-powered fixes
Handles AI-powered code fix generation using OpenRouter API
"""
import httpx
import json
from typing import Dict, Optional
import os

class OpenRouterClient:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model = model or os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = 120.0
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Generate response from OpenRouter AI model
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dict with 'response' and 'metadata'
        """
        if not self.api_key or self.api_key == "your-openrouter-key":
            return {
                "response": "AI service not configured. Please set OPENROUTER_API_KEY in backend/.env",
                "metadata": {"error": "no_api_key"}
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                return {
                    "response": result["choices"][0]["message"]["content"],
                    "metadata": {
                        "model": result.get("model", self.model),
                        "usage": result.get("usage", {}),
                        "id": result.get("id", "")
                    }
                }
        
        except httpx.TimeoutException:
            raise Exception(f"Request to OpenRouter timed out after {self.timeout}s")
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error from OpenRouter: {str(e)}")
        except Exception as e:
            raise Exception(f"OpenRouter client error: {str(e)}")
    
    async def generate_fix(
        self,
        vulnerability_type: str,
        severity: str,
        file_path: str,
        description: str,
        code_snippet: Optional[str] = None
    ) -> Dict:
        """
        Generate security fix for a vulnerability
        
        Returns:
            Dict with 'suggested_fix', 'confidence', and 'explanation'
        """
        prompt = f"""You are a security expert. Analyze this vulnerability and provide a secure code fix.

Vulnerability Details:
- Type: {vulnerability_type}
- Severity: {severity}
- File: {file_path}
- Description: {description}
"""
        
        if code_snippet:
            prompt += f"\nVulnerable Code:\n```\n{code_snippet}\n```\n"
        
        prompt += """
Provide a JSON response with:
1. suggested_fix: The corrected code or detailed fix instructions
2. confidence: Your confidence score (0.0 to 1.0)
3. explanation: Brief explanation of why this fix works

Response format:
{"suggested_fix": "...", "confidence": 0.85, "explanation": "..."}"""
        
        try:
            result = await self.generate(prompt)
            
            # Try to parse JSON from the response
            import re
            json_match = re.search(r'\{.*\}', result["response"], re.DOTALL)
            if json_match:
                fix_data = json.loads(json_match.group())
                return {
                    "suggested_fix": fix_data.get("suggested_fix", "No fix generated"),
                    "confidence": float(fix_data.get("confidence", 0.5)),
                    "explanation": fix_data.get("explanation", "")
                }
            else:
                # Fallback if JSON parsing fails
                return {
                    "suggested_fix": result["response"],
                    "confidence": 0.5,
                    "explanation": "AI response (JSON parsing failed)"
                }
        
        except Exception as e:
            return {
                "suggested_fix": f"Error: {str(e)}",
                "confidence": 0.0,
                "explanation": "Fix generation failed"
            }
    
    async def check_health(self) -> bool:
        """Check if OpenRouter service is available"""
        try:
            if not self.api_key or self.api_key == "your-openrouter-key":
                return False
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.get(f"{self.base_url}/models", headers=headers)
                return response.status_code == 200
        except:
            return False
