"""
Transaction endpoints for CRUD operations.

Provides endpoints for:
- List transactions (with filtering and pagination)
- Create new transaction
- Get transaction by ID
- Update transaction
- Delete transaction
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.services import transaction_service

router = APIRouter()


@router.get("/", response_model=List[Transaction])
async def get_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    type: Optional[str] = Query(None, description="Filter by transaction type (income or expense)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of transactions for current user.

    Supports:
    - Pagination (skip/limit)
    - Filtering by type (income/expense)
    - Filtering by category
    - Results ordered by date (newest first)

    Args:
        skip: Number of records to skip (default 0)
        limit: Maximum records to return (default 20, max 100)
        type: Optional filter by transaction type
        category: Optional filter by category
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of transactions matching criteria
    """
    transactions = transaction_service.get_transactions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        type=type,
        category=category
    )
    return transactions


@router.post("/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new transaction for current user.

    Args:
        transaction_data: Transaction data (amount, description, type, category, date)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created transaction

    Raises:
        HTTPException: 400 if category is invalid
    """
    try:
        transaction = transaction_service.create_transaction(
            db=db,
            transaction_create=transaction_data,
            user_id=current_user.id
        )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific transaction by ID.

    Verifies the transaction belongs to the current user.

    Args:
        transaction_id: ID of transaction to retrieve
        current_user: Current authenticated user
        db: Database session

    Returns:
        Transaction details

    Raises:
        HTTPException: 404 if transaction not found or doesn't belong to user
    """
    transaction = transaction_service.get_transaction_by_id(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return transaction


@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing transaction.

    Only updates fields that are provided.
    Verifies the transaction belongs to the current user.

    Args:
        transaction_id: ID of transaction to update
        transaction_data: Fields to update
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated transaction

    Raises:
        HTTPException: 404 if transaction not found or doesn't belong to user
        HTTPException: 400 if category is invalid
    """
    try:
        transaction = transaction_service.update_transaction(
            db=db,
            transaction_id=transaction_id,
            transaction_update=transaction_data,
            user_id=current_user.id
        )

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a transaction.

    Verifies the transaction belongs to the current user.

    Args:
        transaction_id: ID of transaction to delete
        current_user: Current authenticated user
        db: Database session

    Returns:
        No content (204) on success

    Raises:
        HTTPException: 404 if transaction not found or doesn't belong to user
    """
    success = transaction_service.delete_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return None
