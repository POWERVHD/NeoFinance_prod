"""
Dashboard schemas for API responses.
"""

from decimal import Decimal
from typing import List, Dict
from pydantic import BaseModel, Field

from app.schemas.transaction import Transaction


class DashboardSummary(BaseModel):
    """Schema for dashboard summary response."""
    total_income: Decimal = Field(..., description="Total income amount")
    total_expense: Decimal = Field(..., description="Total expenses amount")
    balance: Decimal = Field(..., description="Net balance (income - expenses)")
    recent_transactions: List[Transaction] = Field(..., description="Last 10 transactions")
    expenses_by_category: Dict[str, Decimal] = Field(..., description="Expenses breakdown by category")

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str
        }
