"""
AI Fix models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AIFixCreate(BaseModel):
    vulnerability_id: str
    suggested_fix: str
    fixed_code: Optional[str] = None
    ai_model: str = "deepseek-coder"
    confidence_score: Optional[float] = 0.5

class AIFix(BaseModel):
    id: str
    vulnerability_id: str
    suggested_fix: str
    fixed_code: Optional[str] = None
    ai_model: str
    confidence_score: float = 0.5
    is_applied: bool = False
    applied_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
