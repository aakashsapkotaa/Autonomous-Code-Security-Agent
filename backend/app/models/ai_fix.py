"""
AI Fix models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AIFixCreate(BaseModel):
    vulnerability_id: str
    suggested_fix: str
    fixed_code: str
    ai_model: str = "deepseek-coder:6.7b"
    confidence: Optional[float] = None

class AIFix(BaseModel):
    id: str
    vulnerability_id: str
    suggested_fix: str
    fixed_code: str
    ai_model: str
    created_at: datetime

    class Config:
        from_attributes = True
