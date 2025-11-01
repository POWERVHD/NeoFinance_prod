"""
Dashboard endpoint for summary statistics.

Provides endpoints for:
- Get dashboard summary (income, expenses, balance, recent transactions)
- Get transaction trends over time
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services import transaction_service

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary for current user.

    Returns:
    - total_income: Total income amount
    - total_expenses: Total expenses amount
    - balance: Net balance (income - expenses)
    - recent_transactions: Last 10 transactions
    - expenses_by_category: Breakdown of expenses by category

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dashboard summary data
    """
    summary = transaction_service.get_dashboard_summary(
        db=db,
        user_id=current_user.id
    )
    return summary


@router.get("/trends")                                                         # Done For Graphs
async def get_transaction_trends( 
    period: str = Query(default="monthly", regex="^(daily|weekly|monthly)$"),
    limit: int = Query(default=12, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction trends over time.

    Args:
        period: Time period to group by (daily, weekly, monthly)
        limit: Number of periods to return (default 12)
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of trend data with date, income, and expense for each period
    """
    trends = transaction_service.get_transaction_trends(
        db=db,
        user_id=current_user.id,
        period=period,
        limit=limit
    )
    return {"data": trends, "period": period}
