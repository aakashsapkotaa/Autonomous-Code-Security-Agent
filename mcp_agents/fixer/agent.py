"""
MCP Fixer Agent - Generates AI-powered security fixes using DeepSeek Coder
Port: 8002
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import json
import os
from datetime import datetime
from supabase_client import supabase

app = FastAPI(title="Fixer Agent", version="1.0.0")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-coder:6.7b")

class VulnerabilityInput(BaseModel):
    id: str = None  # Vulnerability ID for storing fix
    vulnerability_type: str
    severity: str
    file_path: str
    line_number: int = None
    description: str
    tool: str = None

class FixResponse(BaseModel):
    suggested_fix: str
    confidence: float
    explanation: str

class FixerAgent:
    async def generate_fix(self, vulnerability: dict) -> dict:
        """Generate AI-powered fix suggestion using DeepSeek Coder via Ollama"""
        
        prompt = f"""You are a security expert. Analyze this vulnerability and provide a secure code fix.

Vulnerability Details:
- Type: {vulnerability['vulnerability_type']}
- Severity: {vulnerability['severity']}
- File: {vulnerability['file_path']}
- Line: {vulnerability.get('line_number', 'N/A')}
- Description: {vulnerability['description']}
- Detected by: {vulnerability.get('tool', 'N/A')}

Provide a JSON response with:
1. suggested_fix: The corrected code or fix instructions
2. confidence: Your confidence score (0.0 to 1.0)
3. explanation: Brief explanation of the fix

Response format:
{{"suggested_fix": "...", "confidence": 0.85, "explanation": "..."}}"""
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{OLLAMA_HOST}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse the response
                try:
                    fix_data = json.loads(result["response"])
                    fix_result = {
                        "suggested_fix": fix_data.get("suggested_fix", "No fix generated"),
                        "confidence": float(fix_data.get("confidence", 0.5)),
                        "explanation": fix_data.get("explanation", "")
                    }
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    fix_result = {
                        "suggested_fix": result["response"],
                        "confidence": 0.5,
                        "explanation": "Raw AI response (JSON parsing failed)"
                    }
                
                # Store the fix in ai_fixes table if vulnerability ID is provided
                if vulnerability.get("id"):
                    fix_record = {
                        "vulnerability_id": vulnerability["id"],
                        "suggested_fix": fix_result["suggested_fix"],
                        "fixed_code": None,  # Can be filled later when user applies fix
                        "ai_model": OLLAMA_MODEL,
                        "confidence_score": fix_result["confidence"],
                        "created_at": datetime.utcnow().isoformat()
                    }
                    
                    try:
                        supabase.table("ai_fixes").insert(fix_record).execute()
                        print(f"✅ Stored AI fix for vulnerability {vulnerability['id']}")
                    except Exception as e:
                        print(f"⚠️ Failed to store AI fix: {str(e)}")
                
                return fix_result
        
        except Exception as e:
            return {
                "suggested_fix": f"Error generating fix: {str(e)}",
                "confidence": 0.0,
                "explanation": "Fix generation failed"
            }

fixer = FixerAgent()

@app.post("/generate-fix", response_model=FixResponse)
async def generate_fix_endpoint(vulnerability: VulnerabilityInput):
    """Generate AI fix for a vulnerability"""
    try:
        fix_data = await fixer.generate_fix(vulnerability.dict())
        return FixResponse(**fix_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "fixer", "model": OLLAMA_MODEL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)