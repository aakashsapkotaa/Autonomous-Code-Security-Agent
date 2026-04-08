"""
DeepSeek Coder Client via Ollama
Handles AI-powered code fix generation
"""
import httpx
import json
from typing import Dict, Optional
import os

class DeepSeekClient:
    def __init__(self, host: str = None, model: str = None):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "deepseek-coder:6.7b")
        self.timeout = 120.0
    
    async def generate(
        self,
        prompt: str,
        format: str = "json",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Generate response from DeepSeek Coder model
        
        Args:
            prompt: The input prompt
            format: Response format ('json' or 'text')
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dict with 'response' and 'metadata'
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                if format == "json":
                    payload["format"] = "json"
                
                response = await client.post(
                    f"{self.host}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                return {
                    "response": result.get("response", ""),
                    "metadata": {
                        "model": result.get("model", self.model),
                        "total_duration": result.get("total_duration", 0),
                        "load_duration": result.get("load_duration", 0),
                        "prompt_eval_count": result.get("prompt_eval_count", 0),
                        "eval_count": result.get("eval_count", 0)
                    }
                }
        
        except httpx.TimeoutException:
            raise Exception(f"Request to Ollama timed out after {self.timeout}s")
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error from Ollama: {str(e)}")
        except Exception as e:
            raise Exception(f"DeepSeek client error: {str(e)}")
    
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
            result = await self.generate(prompt, format="json")
            fix_data = json.loads(result["response"])
            
            return {
                "suggested_fix": fix_data.get("suggested_fix", "No fix generated"),
                "confidence": float(fix_data.get("confidence", 0.5)),
                "explanation": fix_data.get("explanation", "")
            }
        
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "suggested_fix": result["response"],
                "confidence": 0.5,
                "explanation": "Raw AI response (JSON parsing failed)"
            }
        except Exception as e:
            return {
                "suggested_fix": f"Error: {str(e)}",
                "confidence": 0.0,
                "explanation": "Fix generation failed"
            }
    
    async def check_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.host}/api/tags")
                return response.status_code == 200
        except:
            return False
