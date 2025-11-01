"""
Integration tests for dashboard API endpoint.

Tests the dashboard summary endpoint including:
- Summary calculations (income, expenses, balance)
- Recent transactions
- Expenses by category
- User isolation
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi import status


class TestDashboardSummary:
    """Tests for GET /api/v1/dashboard/summary endpoint."""

    def test_dashboard_empty(self, client, auth_headers):
        """Test dashboard summary with no transactions."""
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_income"] == "0.00"
        assert data["total_expense"] == "0.00"
        assert data["balance"] == "0.00"
        assert data["recent_transactions"] == []
        assert data["expenses_by_category"] == {}

    def test_dashboard_with_income_only(self, client, auth_headers, db, test_user):
        """Test dashboard with only income transactions."""
        from app.models.transaction import Transaction

        # Create income transactions
        income1 = Transaction(
            user_id=test_user.id,
            amount=Decimal("1000.00"),
            description="Salary",
            type="income",
            category="Income",
            transaction_date=date.today()
        )
        income2 = Transaction(
            user_id=test_user.id,
            amount=Decimal("500.00"),
            description="Bonus",
            type="income",
            category="Income",
            transaction_date=date.today()
        )
        db.add_all([income1, income2])
        db.commit()

        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_income"] == "1500.00"
        assert data["total_expense"] == "0.00"
        assert data["balance"] == "1500.00"
        assert len(data["recent_transactions"]) == 2
        assert data["expenses_by_category"] == {}

    def test_dashboard_with_expenses_only(self, client, auth_headers, db, test_user):
        """Test dashboard with only expense transactions."""
        from app.models.transaction import Transaction

        # Create expense transactions
        expense1 = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Lunch",
            type="expense",
            category="Food & Dining",
            transaction_date=date.today()
        )
        expense2 = Transaction(
            user_id=test_user.id,
            amount=Decimal("100.00"),
            description="Shopping",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add_all([expense1, expense2])
        db.commit()

        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_income"] == "0.00"
        assert data["total_expense"] == "150.00"
        assert data["balance"] == "-150.00"
        assert len(data["recent_transactions"]) == 2
        assert len(data["expenses_by_category"]) == 2

    def test_dashboard_with_mixed_transactions(self, client, auth_headers, db, test_user):
        """Test dashboard with both income and expenses."""
        from app.models.transaction import Transaction

        # Create mixed transactions
        income = Transaction(
            user_id=test_user.id,
            amount=Decimal("2000.00"),
            description="Salary",
            type="income",
            category="Income",
            transaction_date=date.today()
        )
        expense1 = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Groceries",
            type="expense",
            category="Food & Dining",
            transaction_date=date.today()
        )
        expense2 = Transaction(
            user_id=test_user.id,
            amount=Decimal("100.00"),
            description="Gas",
            type="expense",
            category="Transportation",
            transaction_date=date.today()
        )
        db.add_all([income, expense1, expense2])
        db.commit()

        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_income"] == "2000.00"
        assert data["total_expense"] == "150.00"
        assert data["balance"] == "1850.00"
        assert len(data["recent_transactions"]) == 3
        assert len(data["expenses_by_category"]) == 2

    def test_dashboard_recent_transactions_limit(self, client, auth_headers, db, test_user):
        """Test that recent transactions are limited to 10."""
        from app.models.transaction import Transaction

        # Create 15 transactions
        for i in range(15):
            trans = Transaction(
                user_id=test_user.id,
                amount=Decimal(f"{(i+1)*10}.00"),
                description=f"Transaction {i+1}",
                type="expense",
                category="Shopping",
                transaction_date=date.today() - timedelta(days=i)
            )
            db.add(trans)
        db.commit()

        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only return 10 most recent
        assert len(data["recent_transactions"]) == 10
        # Verify they're the most recent ones (ordered by date desc)
        assert data["recent_transactions"][0]["description"] == "Transaction 1"

    def test_dashboard_expenses_by_category(self, client, auth_headers, db, test_user):
        """Test expenses breakdown by category."""
        from app.models.transaction import Transaction

        # Create expenses in different categories
        food1 = Transaction(
            user_id=test_user.id,
            amount=Decimal("30.00"),
            description="Lunch",
            type="expense",
            category="Food & Dining",
            transaction_date=date.today()
        )
        food2 = Transaction(
            user_id=test_user.id,
            amount=Decimal("70.00"),
            description="Dinner",
            type="expense",
            category="Food & Dining",
            transaction_date=date.today()
        )
        shopping = Transaction(
            user_id=test_user.id,
            amount=Decimal("150.00"),
            description="Clothes",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add_all([food1, food2, shopping])
        db.commit()

        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        expenses_by_cat = data["expenses_by_category"]

        # Should have 2 categories
        assert len(expenses_by_cat) == 2

        # Check Food & Dining category
        assert "Food & Dining" in expenses_by_cat
        assert expenses_by_cat["Food & Dining"] == "100.00"  # 30 + 70

        # Check Shopping category
        assert "Shopping" in expenses_by_cat
        assert expenses_by_cat["Shopping"] == "150.00"

    def test_dashboard_excludes_income_from_category_breakdown(self, client, auth_headers, db, test_user):
        """Test that income is not included in expenses by category."""
        from app.models.transaction import Transaction

        # Create income and expense
        income = Transaction(
            user_id=test_user.id,
            amount=Decimal("1000.00"),
            description="Salary",
            type="income",
            category="Income",
            transaction_date=date.today()
        )
        expense = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Food",
            type="expense",
            category="Food & Dining",
            transaction_date=date.today()
        )
        db.add_all([income, expense])
        db.commit()

        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Income category should NOT appear in expenses breakdown
        expenses_by_cat = data["expenses_by_category"]
        assert len(expenses_by_cat) == 1
        assert "Food & Dining" in expenses_by_cat
        assert "Income" not in expenses_by_cat

        # But income should be counted in total_income
        assert data["total_income"] == "1000.00"

    def test_dashboard_user_isolation(self, client, auth_headers, db, test_user, test_user_2):
        """Test that users only see their own dashboard data."""
        from app.models.transaction import Transaction

        # Create transactions for user 1
        user1_trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("100.00"),
            description="User 1 Transaction",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )

        # Create transactions for user 2
        user2_trans = Transaction(
            user_id=test_user_2.id,
            amount=Decimal("500.00"),
            description="User 2 Transaction",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add_all([user1_trans, user2_trans])
        db.commit()

        # Get dashboard for user 1 (using auth_headers which is for test_user)
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should only show user 1's data
        assert data["total_expense"] == "100.00"
        assert len(data["recent_transactions"]) == 1
        assert data["recent_transactions"][0]["description"] == "User 1 Transaction"

    def test_dashboard_without_auth(self, client):
        """Test that dashboard requires authentication."""
        response = client.get("/api/v1/dashboard/summary")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dashboard_with_invalid_token(self, client):
        """Test dashboard with invalid token fails."""
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dashboard_data_types(self, client, auth_headers, db, test_user):
        """Test that dashboard returns correct data types."""
        from app.models.transaction import Transaction

        # Create a transaction
        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("123.45"),
            description="Test",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()

        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check data types
        assert isinstance(data["total_income"], str)
        assert isinstance(data["total_expense"], str)
        assert isinstance(data["balance"], str)
        assert isinstance(data["recent_transactions"], list)
        assert isinstance(data["expenses_by_category"], dict)

        # Check recent transaction structure
        recent = data["recent_transactions"][0]
        assert "id" in recent
        assert "amount" in recent
        assert "description" in recent
        assert "type" in recent
        assert "category" in recent
        assert "transaction_date" in recent

        # Check expenses by category structure (dict of category -> amount)
        assert len(data["expenses_by_category"]) > 0
        for category, amount in data["expenses_by_category"].items():
            assert isinstance(category, str)
            assert isinstance(amount, str)


class TestDashboardIntegration:
    """Integration tests for dashboard workflows."""

    def test_create_transaction_and_see_in_dashboard(self, client, auth_headers):
        """Test that newly created transactions appear in dashboard."""
        # Create a transaction
        create_response = client.post(
            "/api/v1/transactions/",
            headers=auth_headers,
            json={
                "amount": 75.50,
                "description": "New Transaction",
                "type": "expense",
                "category": "Food & Dining",
                "transaction_date": str(date.today())
            }
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # Check dashboard
        dashboard_response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
        assert dashboard_response.status_code == status.HTTP_200_OK

        data = dashboard_response.json()
        assert data["total_expense"] == "75.50"
        assert len(data["recent_transactions"]) == 1
        assert data["recent_transactions"][0]["description"] == "New Transaction"

    def test_delete_transaction_updates_dashboard(self, client, auth_headers, db, test_user):
        """Test that deleting a transaction updates dashboard."""
        from app.models.transaction import Transaction

        # Create a transaction
        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("100.00"),
            description="To Delete",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        # Verify it's in dashboard
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
        assert response.json()["total_expense"] == "100.00"

        # Delete the transaction
        delete_response = client.delete(f"/api/v1/transactions/{trans.id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Check dashboard is updated
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
        data = response.json()
        assert data["total_expense"] == "0.00"
        assert len(data["recent_transactions"]) == 0

    def test_update_transaction_updates_dashboard(self, client, auth_headers, db, test_user):
        """Test that updating a transaction updates dashboard."""
        from app.models.transaction import Transaction

        # Create a transaction
        trans = Transaction(
            user_id=test_user.id,
            amount=Decimal("50.00"),
            description="Original",
            type="expense",
            category="Shopping",
            transaction_date=date.today()
        )
        db.add(trans)
        db.commit()
        db.refresh(trans)

        # Update the amount
        update_response = client.put(
            f"/api/v1/transactions/{trans.id}",
            headers=auth_headers,
            json={"amount": 150.00}
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Check dashboard reflects new amount
        response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
        data = response.json()
        assert data["total_expense"] == "150.00"
