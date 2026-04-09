"""
AI Chatbot endpoint for help bot
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from app.core.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are SecureShift AI Bot, a helpful assistant for the SecureShift security scanning platform.

SecureShift helps developers:
- Scan GitHub repositories for security vulnerabilities
- Get AI-powered fix suggestions for vulnerabilities
- Monitor security across multiple repositories
- Use tools like Bandit (Python security), Safety (dependency vulnerabilities), and TruffleHog (secrets detection)

Key features:
- Sign up/Sign in with email and password
- Add GitHub repositories by URL
- Automatic security scanning on repository addition
- View vulnerabilities with severity levels (low, medium, high, critical)
- AI-generated code fixes for detected issues

Answer user questions concisely and helpfully. Keep responses under 3 sentences when possible."""

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the AI chatbot and get a response
    """
    # List of free models to try in order of preference
    models_to_try = [
        settings.OPENROUTER_MODEL,  # Primary model from config
        "google/gemini-flash-1.5",
        "meta-llama/llama-3.1-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ]
    
    for model in models_to_try:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": request.message}
                        ],
                        "max_tokens": 200,
                        "temperature": 0.7,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data["choices"][0]["message"]["content"]
                    return ChatResponse(response=ai_response)
                
                # If this model failed, try the next one
                print(f"Model {model} failed with status {response.status_code}: {response.text}")
                continue
                
        except Exception as e:
            print(f"Error with model {model}: {str(e)}")
            continue
    
    # If all models failed, return fallback
    return ChatResponse(
        response="I'm having trouble connecting to my AI service right now. Here's what I can tell you: SecureShift scans GitHub repositories for security vulnerabilities using Bandit, Safety, and TruffleHog. You can add repositories from the dashboard, and we'll automatically scan them and provide AI-powered fix suggestions."
    )
