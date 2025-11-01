"""
AI Chat API endpoints.
Handles chat messages, analysis requests, and quick questions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.core.deps import get_current_user
from app.services.gemini_service import get_gemini_service, GeminiService
from app.schemas.ai_chat import (
    ChatMessage,
    ChatResponse,
    QuickQuestionsResponse,
    BudgetAnalysisRequest,
    HealthCheckResponse
)
from app.utils.prompt_templates import (
    SYSTEM_PROMPT,
    create_user_context_prompt,
    create_budget_analysis_prompt,
    QUICK_QUESTIONS
)

router = APIRouter()


@router.get("/quick-questions", response_model=QuickQuestionsResponse)
async def get_quick_questions():
    """
    Get list of suggested questions users can ask.

    Returns:
        List of predefined quick questions
    """
    return QuickQuestionsResponse(questions=QUICK_QUESTIONS)


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini_service)
):
    """
    Send a chat message and get AI response.

    Args:
        message: Chat message with user question
        current_user: Current authenticated user
        db: Database session
        gemini: Gemini service instance

    Returns:
        AI-generated response with timestamp

    Raises:
        500: AI generation failed
    """
    try:
        # Fetch recent transactions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= thirty_days_ago
        ).order_by(Transaction.transaction_date.desc()).all()

        # Prepare transaction data
        transaction_data = [
            {
                "date": t.transaction_date.strftime("%Y-%m-%d"),
                "description": t.description,
                "amount": float(t.amount),
                "type": t.type,
                "category": t.category
            }
            for t in transactions
        ]

        # Create contextualized prompt
        if message.include_context and transaction_data:
            # Calculate monthly income from transactions (last 30 days)
            monthly_income = sum(
                float(t.amount) for t in transactions
                if t.type == 'income'
            )

            user_data = {
                "name": current_user.full_name or current_user.email.split('@')[0],
                "income": monthly_income
            }
            prompt = create_user_context_prompt(
                user_data=user_data,
                transactions=transaction_data,
                question=message.question
            )
        else:
            prompt = message.question

        # Generate AI response
        response_text = await gemini.generate_response(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPT
        )

        return ChatResponse(
            response=response_text,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )


@router.post("/analyze-budget", response_model=ChatResponse)
async def analyze_budget(
    request: BudgetAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini_service)
):
    """
    Get comprehensive budget analysis.

    Args:
        request: Analysis request with period
        current_user: Current authenticated user
        db: Database session
        gemini: Gemini service

    Returns:
        Detailed budget analysis and recommendations
    """
    try:
        # Fetch transactions for period
        start_date = datetime.now() - timedelta(days=request.period_days)

        # Get income transactions
        income_transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.type == 'income'
        ).all()

        # Get expense transactions
        expense_transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.type == 'expense'
        ).all()

        # Calculate totals
        total_income = sum(float(t.amount) for t in income_transactions)
        total_spending = sum(float(t.amount) for t in expense_transactions)

        # Category breakdown
        category_spending = {}
        for t in expense_transactions:
            cat = t.category or 'Other'
            category_spending[cat] = category_spending.get(cat, 0) + float(t.amount)

        # Create analysis prompt
        prompt = create_budget_analysis_prompt(
            income=total_income,
            total_spending=total_spending,
            category_breakdown=category_spending
        )

        # Generate analysis
        response_text = await gemini.generate_response(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPT
        )

        return ChatResponse(
            response=response_text,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(gemini: GeminiService = Depends(get_gemini_service)):
    """
    Check AI service health.

    Returns:
        Service status
    """
    is_healthy = gemini.test_connection()
    return HealthCheckResponse(
        status="healthy" if is_healthy else "unhealthy",
        service="gemini-api",
        timestamp=datetime.now()
    )
