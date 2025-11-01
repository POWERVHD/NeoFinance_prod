"""
Tests for transaction service functions.

Tests transaction CRUD operations, filtering, pagination, and dashboard calculations.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi import HTTPException

from app.services.transaction_service import (
    get_transactions,
    get_transaction_count,
    get_transaction_by_id,
    create_transaction,
    update_transaction,
    delete_transaction,
    get_dashboard_summary,
)
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.models.transaction import Transaction


#Helper function to create test transaction
def create_test_transaction(db, user_id, **kwargs):
    """Helper to create a transaction for testing."""
    defaults = {
        "amount": Decimal("50.00"),
        "description": "Test transaction",
        "type": "expense",
        "category": "Other",
        "transaction_date": date.today(),
    }
    defaults.update(kwargs)

    transaction = Transaction(user_id=user_id, **defaults)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


class TestGetTransactions:
    """Tests for get_transactions function."""

    def test_get_transactions_empty(self, db, test_user):
        """Test getting transactions when none exist."""
        transactions = get_transactions(db, test_user.id)

        assert transactions == []

    def test_get_transactions_basic(self, db, test_user):
        """Test getting transactions for a user."""
        # Create 3 transactions
        for i in range(3):
            create_test_transaction(
                db, test_user.id,
                description=f"Transaction {i}",
                amount=Decimal(f"{10 + i}.00")
            )

        transactions = get_transactions(db, test_user.id)

        assert len(transactions) == 3

    def test_get_transactions_pagination(self, db, test_user):
        """Test transaction pagination."""
        # Create 10 transactions
        for i in range(10):
            create_test_transaction(db, test_user.id, description=f"Trans {i}")

        # Get first 5
        page1 = get_transactions(db, test_user.id, skip=0, limit=5)
        assert len(page1) == 5

        # Get next 5
        page2 = get_transactions(db, test_user.id, skip=5, limit=5)
        assert len(page2) == 5

        # Ensure they're different
        page1_ids = {t.id for t in page1}
        page2_ids = {t.id for t in page2}
        assert page1_ids.isdisjoint(page2_ids)

    def test_get_transactions_filter_by_type(self, db, test_user):
        """Test filtering transactions by type."""
        # Create income and expense transactions
        create_test_transaction(db, test_user.id, type="income", description="Income 1")
        create_test_transaction(db, test_user.id, type="income", description="Income 2")
        create_test_transaction(db, test_user.id, type="expense", description="Expense 1")

        # Get only income
        income_transactions = get_transactions(db, test_user.id, type="income")
        assert len(income_transactions) == 2
        assert all(t.type == "income" for t in income_transactions)

        # Get only expense
        expense_transactions = get_transactions(db, test_user.id, type="expense")
        assert len(expense_transactions) == 1
        assert expense_transactions[0].type == "expense"

    def test_get_transactions_filter_by_category(self, db, test_user):
        """Test filtering transactions by category."""
        create_test_transaction(db, test_user.id, category="Food & Dining")
        create_test_transaction(db, test_user.id, category="Food & Dining")
        create_test_transaction(db, test_user.id, category="Transportation")

        # Get only Food & Dining
        food_transactions = get_transactions(db, test_user.id, category="Food & Dining")
        assert len(food_transactions) == 2
        assert all(t.category == "Food & Dining" for t in food_transactions)

    def test_get_transactions_ordered_by_date(self, db, test_user):
        """Test that transactions are ordered by date descending."""
        # Create transactions with different dates
        old_transaction = create_test_transaction(
            db, test_user.id,
            transaction_date=date.today() - timedelta(days=10),
            description="Old"
        )
        recent_transaction = create_test_transaction(
            db, test_user.id,
            transaction_date=date.today(),
            description="Recent"
        )

        transactions = get_transactions(db, test_user.id)

        # Most recent should be first
        assert transactions[0].id == recent_transaction.id
        assert transactions[1].id == old_transaction.id

    def test_get_transactions_isolation_between_users(self, db, test_user, test_user_2):
        """Test that users only see their own transactions."""
        # Create transactions for both users
        create_test_transaction(db, test_user.id, description="User 1 transaction")
        create_test_transaction(db, test_user_2.id, description="User 2 transaction")

        # Each user should only see their own
        user1_transactions = get_transactions(db, test_user.id)
        user2_transactions = get_transactions(db, test_user_2.id)

        assert len(user1_transactions) == 1
        assert len(user2_transactions) == 1
        assert user1_transactions[0].user_id == test_user.id
        assert user2_transactions[0].user_id == test_user_2.id


class TestGetTransactionCount:
    """Tests for get_transaction_count function."""

    def test_count_zero_transactions(self, db, test_user):
        """Test counting when no transactions exist."""
        count = get_transaction_count(db, test_user.id)
        assert count == 0

    def test_count_all_transactions(self, db, test_user):
        """Test counting all transactions."""
        for i in range(5):
            create_test_transaction(db, test_user.id)

        count = get_transaction_count(db, test_user.id)
        assert count == 5

    def test_count_filtered_by_type(self, db, test_user):
        """Test counting filtered transactions."""
        create_test_transaction(db, test_user.id, type="income")
        create_test_transaction(db, test_user.id, type="income")
        create_test_transaction(db, test_user.id, type="expense")

        income_count = get_transaction_count(db, test_user.id, type="income")
        assert income_count == 2


class TestGetTransactionById:
    """Tests for get_transaction_by_id function."""

    def test_get_existing_transaction(self, db, test_user):
        """Test getting an existing transaction."""
        created = create_test_transaction(db, test_user.id)

        retrieved = get_transaction_by_id(db, created.id, test_user.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_transaction(self, db, test_user):
        """Test getting non-existent transaction returns None."""
        transaction = get_transaction_by_id(db, 99999, test_user.id)

        assert transaction is None

    def test_get_transaction_wrong_user(self, db, test_user, test_user_2):
        """Test that users cannot access other users' transactions."""
        # User 2 creates a transaction
        created = create_test_transaction(db, test_user_2.id)

        # User 1 tries to access it
        retrieved = get_transaction_by_id(db, created.id, test_user.id)

        assert retrieved is None  # Should not be accessible


class TestCreateTransaction:
    """Tests for create_transaction function."""

    def test_create_transaction_success(self, db, test_user):
        """Test creating a transaction successfully."""
        transaction_data = TransactionCreate(
            amount=Decimal("75.50"),
            description="Groceries",
            type="expense",
            category="Food & Dining",
            transaction_date=date(2024, 1, 15),
        )

        transaction = create_transaction(db, transaction_data, test_user.id)

        assert transaction.id is not None
        assert transaction.user_id == test_user.id
        assert transaction.amount == Decimal("75.50")
        assert transaction.description == "Groceries"
        assert transaction.type == "expense"
        assert transaction.category == "Food & Dining"
        assert transaction.transaction_date == date(2024, 1, 15)

    def test_create_transaction_invalid_category(self, db, test_user):
        """Test creating transaction with invalid category fails."""
        transaction_data = TransactionCreate(
            amount=Decimal("50.00"),
            description="Test",
            type="expense",
            category="Invalid Category",  # Not in CATEGORIES
            transaction_date=date.today(),
        )

        with pytest.raises(HTTPException) as exc_info:
            create_transaction(db, transaction_data, test_user.id)

        assert exc_info.value.status_code == 400
        assert "Invalid category" in exc_info.value.detail


class TestUpdateTransaction:
    """Tests for update_transaction function."""

    def test_update_transaction_success(self, db, test_user):
        """Test updating a transaction."""
        # Create transaction
        transaction = create_test_transaction(db, test_user.id, amount=Decimal("50.00"))

        # Update amount and description
        update_data = TransactionUpdate(
            amount=Decimal("75.00"),
            description="Updated description"
        )

        updated = update_transaction(db, transaction.id, update_data, test_user.id)

        assert updated is not None
        assert updated.amount == Decimal("75.00")
        assert updated.description == "Updated description"

    def test_update_partial_fields(self, db, test_user):
        """Test updating only some fields."""
        transaction = create_test_transaction(
            db, test_user.id,
            amount=Decimal("50.00"),
            description="Original"
        )

        # Only update description
        update_data = TransactionUpdate(description="New description")

        updated = update_transaction(db, transaction.id, update_data, test_user.id)

        assert updated.description == "New description"
        assert updated.amount == Decimal("50.00")  # Unchanged

    def test_update_nonexistent_transaction(self, db, test_user):
        """Test updating non-existent transaction returns None."""
        update_data = TransactionUpdate(amount=Decimal("100.00"))

        updated = update_transaction(db, 99999, update_data, test_user.id)

        assert updated is None

    def test_update_transaction_wrong_user(self, db, test_user, test_user_2):
        """Test that users cannot update other users' transactions."""
        # User 2 creates a transaction
        transaction = create_test_transaction(db, test_user_2.id)

        # User 1 tries to update it
        update_data = TransactionUpdate(amount=Decimal("999.00"))
        updated = update_transaction(db, transaction.id, update_data, test_user.id)

        assert updated is None

    def test_update_transaction_invalid_category(self, db, test_user):
        """Test updating with invalid category fails."""
        transaction = create_test_transaction(db, test_user.id)

        update_data = TransactionUpdate(category="Invalid Category")

        with pytest.raises(HTTPException) as exc_info:
            update_transaction(db, transaction.id, update_data, test_user.id)

        assert exc_info.value.status_code == 400


class TestDeleteTransaction:
    """Tests for delete_transaction function."""

    def test_delete_transaction_success(self, db, test_user):
        """Test deleting a transaction."""
        transaction = create_test_transaction(db, test_user.id)

        result = delete_transaction(db, transaction.id, test_user.id)

        assert result is True

        # Verify it's deleted
        deleted = get_transaction_by_id(db, transaction.id, test_user.id)
        assert deleted is None

    def test_delete_nonexistent_transaction(self, db, test_user):
        """Test deleting non-existent transaction returns False."""
        result = delete_transaction(db, 99999, test_user.id)

        assert result is False

    def test_delete_transaction_wrong_user(self, db, test_user, test_user_2):
        """Test that users cannot delete other users' transactions."""
        # User 2 creates a transaction
        transaction = create_test_transaction(db, test_user_2.id)

        # User 1 tries to delete it
        result = delete_transaction(db, transaction.id, test_user.id)

        assert result is False

        # Verify it still exists for user 2
        still_exists = get_transaction_by_id(db, transaction.id, test_user_2.id)
        assert still_exists is not None


class TestGetDashboardSummary:
    """Tests for get_dashboard_summary function."""

    def test_dashboard_summary_no_transactions(self, db, test_user):
        """Test dashboard summary with no transactions."""
        summary = get_dashboard_summary(db, test_user.id)

        assert summary["total_income"] == Decimal("0.00")
        assert summary["total_expense"] == Decimal("0.00")
        assert summary["balance"] == Decimal("0.00")
        assert summary["recent_transactions"] == []
        assert summary["expenses_by_category"] == {}

    def test_dashboard_summary_with_transactions(self, db, test_user):
        """Test dashboard summary calculations."""
        # Create income transactions
        create_test_transaction(db, test_user.id, type="income", amount=Decimal("1000.00"))
        create_test_transaction(db, test_user.id, type="income", amount=Decimal("500.00"))

        # Create expense transactions
        create_test_transaction(db, test_user.id, type="expense", amount=Decimal("200.00"))
        create_test_transaction(db, test_user.id, type="expense", amount=Decimal("150.00"))

        summary = get_dashboard_summary(db, test_user.id)

        assert summary["total_income"] == Decimal("1500.00")
        assert summary["total_expense"] == Decimal("350.00")
        assert summary["balance"] == Decimal("1150.00")

    def test_dashboard_recent_transactions_limit(self, db, test_user):
        """Test that only 10 recent transactions are returned."""
        # Create 15 transactions
        for i in range(15):
            create_test_transaction(db, test_user.id, description=f"Trans {i}")

        summary = get_dashboard_summary(db, test_user.id)

        assert len(summary["recent_transactions"]) == 10

    def test_dashboard_expenses_by_category(self, db, test_user):
        """Test expense breakdown by category."""
        create_test_transaction(
            db, test_user.id,
            type="expense",
            category="Food & Dining",
            amount=Decimal("100.00")
        )
        create_test_transaction(
            db, test_user.id,
            type="expense",
            category="Food & Dining",
            amount=Decimal("50.00")
        )
        create_test_transaction(
            db, test_user.id,
            type="expense",
            category="Transportation",
            amount=Decimal("75.00")
        )

        summary = get_dashboard_summary(db, test_user.id)
        expenses_by_cat = summary["expenses_by_category"]

        # Check Food & Dining
        assert "Food & Dining" in expenses_by_cat
        assert expenses_by_cat["Food & Dining"] == Decimal("150.00")

        # Check Transportation
        assert "Transportation" in expenses_by_cat
        assert expenses_by_cat["Transportation"] == Decimal("75.00")

    def test_dashboard_excludes_income_from_category_breakdown(self, db, test_user):
        """Test that income is not included in category breakdown."""
        create_test_transaction(
            db, test_user.id,
            type="income",
            category="Income",
            amount=Decimal("1000.00")
        )

        summary = get_dashboard_summary(db, test_user.id)
        expenses_by_cat = summary["expenses_by_category"]

        # Income category should not appear in expenses breakdown
        assert "Income" not in expenses_by_cat
        assert len(expenses_by_cat) == 0

    def test_dashboard_isolation_between_users(self, db, test_user, test_user_2):
        """Test that dashboard only shows user's own data."""
        # User 1 transactions
        create_test_transaction(db, test_user.id, type="income", amount=Decimal("1000.00"))

        # User 2 transactions
        create_test_transaction(db, test_user_2.id, type="income", amount=Decimal("2000.00"))

        # Check user 1's dashboard
        summary1 = get_dashboard_summary(db, test_user.id)
        assert summary1["total_income"] == Decimal("1000.00")

        # Check user 2's dashboard
        summary2 = get_dashboard_summary(db, test_user_2.id)
        assert summary2["total_income"] == Decimal("2000.00")
