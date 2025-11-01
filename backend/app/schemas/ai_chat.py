"""
Pydantic schemas for AI Chat feature.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message request model."""
    question: str = Field(..., min_length=1, max_length=500, description="User's question")
    include_context: bool = Field(default=True, description="Include transaction context in prompt")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="AI-generated response")
    timestamp: datetime = Field(..., description="Response timestamp")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used (if available)")


class QuickQuestionsResponse(BaseModel):
    """Quick questions list response."""
    questions: List[str] = Field(..., description="List of suggested questions")


class BudgetAnalysisRequest(BaseModel):
    """Budget analysis request model."""
    period_days: int = Field(default=30, ge=1, le=365, description="Number of days to analyze")


class HealthCheckResponse(BaseModel):
    """AI service health check response."""
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Check timestamp")
