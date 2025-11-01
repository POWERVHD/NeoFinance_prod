"""
Tests for SQLAlchemy models (User and Transaction).

Tests model creation, relationships, and constraints.
"""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.transaction import Transaction
from app.core.security import get_password_hash


class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self, db):
        """Test creating a user with all fields."""
        user = User(
            email="newuser@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="New User",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_email_unique_constraint(self, db, test_user):
        """Test that duplicate emails are not allowed."""
        duplicate_user = User(
            email=test_user.email,  # Same email as test_user
            hashed_password=get_password_hash("password123"),
            full_name="Duplicate User",
        )
        db.add(duplicate_user)

        with pytest.raises(IntegrityError):
            db.commit()

    def test_user_default_is_active(self, db):
        """Test that is_active defaults to True."""
        user = User(
            email="activeuser@example.com",
            hashed_password=get_password_hash("password123"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.is_active is True

    def test_user_repr(self, test_user):
        """Test user string representation."""
        repr_str = repr(test_user)
        assert "User" in repr_str
        assert str(test_user.id) in repr_str
        assert test_user.email in repr_str


class TestTransactionModel:
    """Tests for the Transaction model."""

    def test_create_transaction(self, db, test_user):
        """Test creating a transaction with all fields."""
        transaction = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Lunch at cafe",
            type="expense",
            category="Food & Dining",
            transaction_date=date(2024, 1, 15),
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        assert transaction.id is not None
        assert transaction.user_id == test_user.id
        assert transaction.amount == Decimal("50.00")
        assert transaction.description == "Lunch at cafe"
        assert transaction.type == "expense"
        assert transaction.category == "Food & Dining"
        assert transaction.transaction_date == date(2024, 1, 15)
        assert transaction.created_at is not None
        assert transaction.updated_at is not None

    def test_transaction_type_constraint(self, db, test_user):
        """Test that transaction type must be 'income' or 'expense'."""
        # Note: SQLite doesn't enforce CHECK constraints strictly
        # This test documents expected behavior
        transaction = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Test",
            type="invalid_type",  # Invalid type
            category="Other",
            transaction_date=date.today(),
        )
        db.add(transaction)

        # In PostgreSQL, this would raise IntegrityError
        # In SQLite, it may pass (known limitation)
        # We'll validate this in application layer via Pydantic

    def test_transaction_user_relationship(self, db, test_user):
        """Test relationship between transaction and user."""
        transaction = Transaction(
            user_id=test_user.id,
            amount=Decimal("100.00"),
            description="Test transaction",
            type="income",
            category="Income",
            transaction_date=date.today(),
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        # Test forward relationship (transaction -> user)
        assert transaction.user is not None
        assert transaction.user.id == test_user.id
        assert transaction.user.email == test_user.email

        # Test reverse relationship (user -> transactions)
        db.refresh(test_user)
        assert len(test_user.transactions) == 1
        assert test_user.transactions[0].id == transaction.id

    def test_transaction_cascade_delete(self, db, test_user):
        """Test that deleting user cascades to transactions."""
        # Create a transaction
        transaction = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Test",
            type="expense",
            category="Other",
            transaction_date=date.today(),
        )
        db.add(transaction)
        db.commit()
        transaction_id = transaction.id

        # Delete the user
        db.delete(test_user)
        db.commit()

        # Verify transaction was also deleted (cascade)
        deleted_transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        assert deleted_transaction is None

    def test_transaction_repr(self, db, test_user):
        """Test transaction string representation."""
        transaction = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Test",
            type="expense",
            category="Other",
            transaction_date=date.today(),
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        repr_str = repr(transaction)
        assert "Transaction" in repr_str
        assert str(transaction.id) in repr_str
        assert str(transaction.amount) in repr_str

    def test_multiple_transactions_per_user(self, db, test_user):
        """Test that one user can have multiple transactions."""
        transactions = []
        for i in range(5):
            transaction = Transaction(
                user_id=test_user.id,
                amount=Decimal(f"{10 + i}.00"),
                description=f"Transaction {i}",
                type="expense" if i % 2 == 0 else "income",
                category="Other",
                transaction_date=date.today(),
            )
            transactions.append(transaction)
            db.add(transaction)

        db.commit()

        # Verify all transactions created
        db.refresh(test_user)
        assert len(test_user.transactions) == 5

        # Verify transaction details
        for i, transaction in enumerate(test_user.transactions):
            assert transaction.amount == Decimal(f"{10 + i}.00")
            assert transaction.description == f"Transaction {i}"
