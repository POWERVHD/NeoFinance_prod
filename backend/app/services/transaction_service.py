"""
Transaction service for transaction management and dashboard calculations.

This module provides business logic for:
- Transaction CRUD operations
- Transaction filtering and pagination
- Dashboard summary calculations
- Expense aggregations by category
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.core.constants import CATEGORIES


def get_transactions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    type: str | None = None,
    category: str | None = None,
) -> list[Transaction]:
    """
    Get transactions for a user with optional filtering and pagination.

    Args:
        db: Database session
        user_id: User ID to filter transactions
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        type: Optional filter by transaction type (income/expense)
        category: Optional filter by category

    Returns:
        List of Transaction objects
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    # Apply filters
    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(Transaction.category == category)

    # Order by date descending (most recent first)
    query = query.order_by(Transaction.transaction_date.desc())

    # Apply pagination
    transactions = query.offset(skip).limit(limit).all()

    return transactions


def get_transaction_count(
    db: Session,
    user_id: int,
    type: str | None = None,
    category: str | None = None,
) -> int:
    """
    Count total transactions matching filters.

    Args:
        db: Database session
        user_id: User ID to filter transactions
        type: Optional filter by transaction type
        category: Optional filter by category

    Returns:
        Total count of transactions
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    # Apply filters
    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(Transaction.category == category)

    return query.count()


def get_transaction_by_id(
    db: Session,
    transaction_id: int,
    user_id: int
) -> Transaction | None:
    """
    Get a single transaction by ID, verifying ownership.

    Args:
        db: Database session
        transaction_id: Transaction ID
        user_id: User ID (for ownership verification)

    Returns:
        Transaction object if found and owned by user, None otherwise
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id  # Verify ownership
    ).first()

    return transaction


def create_transaction(
    db: Session,
    transaction_create: TransactionCreate,
    user_id: int
) -> Transaction:
    """
    Create a new transaction.

    Args:
        db: Database session
        transaction_create: Transaction creation data
        user_id: User ID (owner of transaction)

    Returns:
        Created Transaction object

    Raises:
        HTTPException: 400 if category is invalid
    """
    # Validate category
    if transaction_create.category not in CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(CATEGORIES)}"
        )

    # Create transaction instance
    db_transaction = Transaction(
        user_id=user_id,
        amount=transaction_create.amount,
        description=transaction_create.description,
        type=transaction_create.type,
        category=transaction_create.category,
        transaction_date=transaction_create.transaction_date,
    )

    # Add to database
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction_update: TransactionUpdate,
    user_id: int
) -> Transaction | None:
    """
    Update an existing transaction.

    Args:
        db: Database session
        transaction_id: Transaction ID to update
        transaction_update: Transaction update data (only provided fields updated)
        user_id: User ID (for ownership verification)

    Returns:
        Updated Transaction object, or None if not found/not owned

    Raises:
        HTTPException: 400 if category is invalid
    """
    # Get transaction and verify ownership
    transaction = get_transaction_by_id(db, transaction_id, user_id)
    if not transaction:
        return None

    # Get update data (only fields that were provided)
    update_data = transaction_update.model_dump(exclude_unset=True)

    # Validate category if being updated
    if "category" in update_data and update_data["category"] not in CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(CATEGORIES)}"
        )

    # Update fields
    for field, value in update_data.items():
        setattr(transaction, field, value)

    # Commit changes
    db.commit()
    db.refresh(transaction)

    return transaction


def delete_transaction(
    db: Session,
    transaction_id: int,
    user_id: int
) -> bool:
    """
    Delete a transaction.

    Args:
        db: Database session
        transaction_id: Transaction ID to delete
        user_id: User ID (for ownership verification)

    Returns:
        True if deleted successfully, False if not found/not owned
    """
    # Get transaction and verify ownership
    transaction = get_transaction_by_id(db, transaction_id, user_id)
    if not transaction:
        return False

    # Delete transaction
    db.delete(transaction)
    db.commit()

    return True


def get_dashboard_summary(db: Session, user_id: int) -> dict:
    """
    Calculate dashboard summary with income, expense, balance, and category breakdowns.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with:
        - total_income: Total income amount
        - total_expense: Total expenses amount
        - balance: Net balance (income - expenses)
        - recent_transactions: List of 10 most recent transactions
        - expenses_by_category: Dict mapping category names to amounts
    """
    # Calculate total income
    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == "income"
    ).scalar() or Decimal("0.00")

    # Calculate total expenses
    total_expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).scalar() or Decimal("0.00")

    # Calculate balance
    balance = total_income - total_expenses

    # Get recent 10 transactions
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(
        Transaction.transaction_date.desc(),
        Transaction.created_at.desc()
    ).limit(10).all()

    # Get expenses grouped by category
    category_expenses = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(
        Transaction.category
    ).all()

    # Convert to dict (category -> amount)
    expenses_by_category = {
        category: total
        for category, total in category_expenses
    }

    return {
        "total_income": total_income,
        "total_expense": total_expenses,  # Frontend expects singular response
        "balance": balance,
        "recent_transactions": recent_transactions,
        "expenses_by_category": expenses_by_category,
    }


def get_transaction_trends(  # This is done for Graph Potrayal
    db: Session,
    user_id: int,
    period: str = "monthly",
    limit: int = 12
) -> list[dict]:
    """
    Get transaction trends over time grouped by period.

    Args:
        db: Database session
        user_id: User ID
        period: Period to group by ("daily", "weekly", "monthly")
        limit: Number of periods to return (default 12 for monthly)

    Returns:
        List of dictionaries with date, income, and expense for each period
    """
    # Calculate the start date based on period and limit
    now = datetime.now()
    if period == "monthly":
        # Get last N months
        months_data = []
        for i in range(limit - 1, -1, -1):
            # Calculate the month
            target_date = now - timedelta(days=i * 30)
            month = target_date.month
            year = target_date.year

            # Get income for this month
            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == year
            ).scalar() or Decimal("0.00")

            # Get expenses for this month
            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == year
            ).scalar() or Decimal("0.00")

            # Format the date label
            date_label = target_date.strftime("%b %Y")

            months_data.append({
                "date": date_label,
                "income": float(income),
                "expense": float(expense)
            })

        return months_data

    elif period == "weekly":
        # Get last N weeks
        weeks_data = []
        for i in range(limit - 1, -1, -1):
            start_date = now - timedelta(weeks=i+1)
            end_date = now - timedelta(weeks=i)

            # Get income for this week
            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                Transaction.transaction_date >= start_date.date(),
                Transaction.transaction_date < end_date.date()
            ).scalar() or Decimal("0.00")

            # Get expenses for this week
            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.transaction_date >= start_date.date(),
                Transaction.transaction_date < end_date.date()
            ).scalar() or Decimal("0.00")

            date_label = f"Week {start_date.strftime('%m/%d')}"

            weeks_data.append({
                "date": date_label,
                "income": float(income),
                "expense": float(expense)
            })

        return weeks_data

    else:  # daily
        # Get last N days
        days_data = []
        for i in range(limit - 1, -1, -1):
            target_date = now - timedelta(days=i)

            # Get income for this day
            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                Transaction.transaction_date == target_date.date()
            ).scalar() or Decimal("0.00")

            # Get expenses for this day
            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.transaction_date == target_date.date()
            ).scalar() or Decimal("0.00")

            date_label = target_date.strftime("%b %d")

            days_data.append({
                "date": date_label,
                "income": float(income),
                "expense": float(expense)
            })

        return days_data
