from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class TransactionBase(BaseModel):
    """
    Base transaction schema with common attributes.
    """
    amount: Decimal = Field(..., gt=0, description="Transaction amount (must be positive)")
    description: str = Field(..., min_length=1, max_length=500)
    type: Literal["income", "expense"] = Field(..., description="Transaction type: income or expense")
    category: str = Field(..., min_length=1, max_length=50)
    transaction_date: date


class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction.
    """
    pass


class TransactionUpdate(BaseModel):
    """
    Schema for updating a transaction (all fields optional).
    """
    amount: Decimal | None = Field(None, gt=0)
    description: str | None = Field(None, min_length=1, max_length=500)
    type: Literal["income", "expense"] | None = None
    category: str | None = Field(None, min_length=1, max_length=50)
    transaction_date: date | None = None


class Transaction(TransactionBase):
    """
    Schema for transaction response.
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionList(BaseModel):
    """
    Schema for paginated transaction list response.
    """
    transactions: list[Transaction]
    total: int
    skip: int
    limit: int
